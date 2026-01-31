"""
Live audio/video session handler for the LTM application.
This module wraps the Google Gemini live session functionality into a callable class
that can be integrated into the main service.
"""

import os
import asyncio
import base64
import io
import traceback
from typing import Callable, Optional, Dict, Any

import cv2
import pyaudio
import PIL.Image
import mss

from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from config.prompt_templates import AGENT_SYSTEM_PROMPT
from core.memory_manager import db

FORMAT = pyaudio.paInt16
CHANNELS = 1
SEND_SAMPLE_RATE = 16000
RECEIVE_SAMPLE_RATE = 24000
CHUNK_SIZE = 1024

MODEL = "models/gemini-2.0-flash-live-001"

DEFAULT_MODE = "camera"

class LiveSessionManager:
    """Manages live audio/video sessions using Google Gemini API."""
    
    def __init__(self):
        """Initialize the live session manager."""
        self.client = genai.Client(
            http_options={"api_version": "v1beta"},
            api_key=os.environ.get("GEMINI_API_KEY"),
        )
        
        self.pya = pyaudio.PyAudio()
        self.active_sessions = {}
        
    def get_context_for_user(self, user_id: str) -> str:
        """Fetch memory context for a specific user."""
        semantic_mems = list(db["memories"].find({"user_id": user_id, "type": "semantic"}).limit(5))
        episodic_mems = list(db["memories"].find({"user_id": user_id, "type": "episodic"}).sort("timestamp", -1).limit(3))

        context_str = "RELATIONSHIPS/FACTS:\n" + "\n".join([m.get("content", "") for m in semantic_mems])
        context_str += "\n\nRECENT SESSIONS:\n" + "\n".join([m.get("content", "") for m in episodic_mems])
        
        return context_str
    
    def create_live_config(self, user_id: str) -> types.LiveConnectConfig:
        """Create a live connection configuration with user-specific context."""
        context_str = self.get_context_for_user(user_id)
        
        live_system_instruction = AGENT_SYSTEM_PROMPT + f"""

## MEMORY CONTEXT
{context_str}

## LIVE INTERACTION PROTOCOLS
1. EMOTION METADATA: Start every text response with a JSON object: {{"emotion": "detected_emotion", "confidence": 0.0-1.0}}.
2. VISUAL GUARDRAILS: If you see weapons, blood, or self-harm in the video input, IMMEDIATELY output "CRITICAL_VISUAL_ALERT" and switch to crisis intervention mode.
3. OUTPUT: Speak warmly and naturally.
"""
        
        return types.LiveConnectConfig(
            response_modalities=[
                "AUDIO",
            ],
            system_instruction=types.Content(parts=[types.Part(text=live_system_instruction)]),
            media_resolution="MEDIA_RESOLUTION_MEDIUM",
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Zephyr")
                )
            ),
            context_window_compression=types.ContextWindowCompressionConfig(
                trigger_tokens=25600,
                sliding_window=types.SlidingWindow(target_tokens=12800),
            ),
        )
    
    async def start_session(self, user_id: str, video_mode: str = DEFAULT_MODE, 
                           on_audio_receive: Optional[Callable[[bytes], None]] = None,
                           on_text_receive: Optional[Callable[[str], None]] = None,
                           on_visual_alert: Optional[Callable[[str], None]] = None) -> str:
        """Start a new live session for a user.
        
        Args:
            user_id: The ID of the user starting the session
            video_mode: Camera mode ('camera', 'screen', or 'none')
            on_audio_receive: Callback function to handle received audio
            on_text_receive: Callback function to handle received text
            on_visual_alert: Callback function to handle visual safety alerts
            
        Returns:
            Session ID for the created session
        """
        session_id = f"session_{user_id}_{hash(str(asyncio.current_task())) % 10000}"
        
        session_loop = AudioVideoLoop(
            client=self.client,
            session_id=session_id,
            user_id=user_id,
            video_mode=video_mode,
            on_audio_receive=on_audio_receive,
            on_text_receive=on_text_receive,
            on_visual_alert=on_visual_alert,
            pya=self.pya
        )
        
        # Store the session
        self.active_sessions[session_id] = session_loop
        
        # Start the session in the background
        asyncio.create_task(session_loop.run())
        
        return session_id
    
    def stop_session(self, session_id: str) -> bool:
        """Stop an active session.
        
        Args:
            session_id: The ID of the session to stop
            
        Returns:
            True if the session was stopped, False if it didn't exist
        """
        if session_id in self.active_sessions:
            self.active_sessions[session_id].stop()
            del self.active_sessions[session_id]
            return True
        return False
    
    def get_active_sessions(self) -> Dict[str, Any]:
        """Get information about all active sessions."""
        return {sid: {"active": loop.is_running()} for sid, loop in self.active_sessions.items()}


class AudioVideoLoop:
    """Handles the audio/video loop for a single session."""
    
    def __init__(self, client, session_id: str, user_id: str, video_mode: str,
                 on_audio_receive: Optional[Callable[[bytes], None]] = None,
                 on_text_receive: Optional[Callable[[str], None]] = None,
                 on_visual_alert: Optional[Callable[[str], None]] = None,
                 pya=None):
        """Initialize the audio/video loop."""
        self.client = client
        self.session_id = session_id
        self.user_id = user_id
        self.video_mode = video_mode
        self.on_audio_receive = on_audio_receive
        self.on_text_receive = on_text_receive
        self.on_visual_alert = on_visual_alert
        self.pya = pya
        
        self.audio_in_queue = None
        self.out_queue = None
        self.session = None
        self.audio_stream = None
        self.running = True
        
    def _get_frame(self, cap):
        """Get a frame from the camera."""
        ret, frame = cap.read()
        if not ret:
            return None
        # Convert BGR to RGB color space
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = PIL.Image.fromarray(frame_rgb)
        img.thumbnail([1024, 1024])

        image_io = io.BytesIO()
        img.save(image_io, format="jpeg")
        image_io.seek(0)

        mime_type = "image/jpeg"
        image_bytes = image_io.read()
        return {"mime_type": mime_type, "data": base64.b64encode(image_bytes).decode()}
    
    async def get_frames(self):
        """Get frames from the camera."""
        cap = await asyncio.to_thread(cv2.VideoCapture, 0)

        while self.running:
            frame = await asyncio.to_thread(self._get_frame, cap)
            if frame is None:
                break

            await asyncio.sleep(1.0)

            if not self.out_queue.full():
                await self.out_queue.put(frame)

        cap.release()

    def _get_screen(self):
        """Get a screenshot."""
        sct = mss.mss()
        monitor = sct.monitors[0]

        i = sct.grab(monitor)

        mime_type = "image/jpeg"
        image_bytes = mss.tools.to_png(i.rgb, i.size)
        img = PIL.Image.open(io.BytesIO(image_bytes))

        image_io = io.BytesIO()
        img.save(image_io, format="jpeg")
        image_io.seek(0)

        image_bytes = image_io.read()
        return {"mime_type": mime_type, "data": base64.b64encode(image_bytes).decode()}

    async def get_screen(self):
        """Get screen capture."""
        while self.running:
            frame = await asyncio.to_thread(self._get_screen)
            if frame is None:
                break

            await asyncio.sleep(1.0)

            if not self.out_queue.full():
                await self.out_queue.put(frame)

    async def send_realtime(self):
        """Send real-time data."""
        while self.running:
            msg = await self.out_queue.get()
            await self.session.send(input=msg)

    async def listen_audio(self):
        """Listen to audio from microphone."""
        mic_info = self.pya.get_default_input_device_info()
        self.audio_stream = await asyncio.to_thread(
            self.pya.open,
            format=FORMAT,
            channels=CHANNELS,
            rate=SEND_SAMPLE_RATE,
            input=True,
            input_device_index=mic_info["index"],
            frames_per_buffer=CHUNK_SIZE,
        )
        
        if __debug__:
            kwargs = {"exception_on_overflow": False}
        else:
            kwargs = {}
            
        while self.running:
            data = await asyncio.to_thread(self.audio_stream.read, CHUNK_SIZE, **kwargs)
            if not self.out_queue.full():
                await self.out_queue.put({"data": data, "mime_type": "audio/pcm"})

    async def receive_audio(self):
        """Receive audio from the model."""
        while self.running:
            turn = self.session.receive()
            async for response in turn:
                if data := response.data:
                    if self.on_audio_receive:
                        self.on_audio_receive(data)
                    continue
                if text := response.text:
                    if "CRITICAL_VISUAL_ALERT" in text:
                        print(f"\n\n!!! CRITICAL SAFETY ALERT DETECTED IN VISUAL FEED FOR USER {self.user_id} !!!\n")
                        if self.on_visual_alert:
                            self.on_visual_alert(text)
                    
                    if self.on_text_receive:
                        self.on_text_receive(text)
                    
                    # Print text response
                    print(text, end="")

            # Empty audio queue to prevent overflow
            while not self.audio_in_queue.empty():
                self.audio_in_queue.get_nowait()

    async def play_audio(self):
        """Play received audio."""
        stream = await asyncio.to_thread(
            self.pya.open,
            format=FORMAT,
            channels=CHANNELS,
            rate=RECEIVE_SAMPLE_RATE,
            output=True,
        )
        
        while self.running:
            bytestream = await self.audio_in_queue.get()
            await asyncio.to_thread(stream.write, bytestream)

    async def run(self):
        """Run the main session loop."""
        try:
            config = LiveSessionManager().create_live_config(self.user_id)
            async with (
                self.client.aio.live.connect(model=MODEL, config=config) as session,
                asyncio.TaskGroup() as tg,
            ):
                self.session = session

                self.audio_in_queue = asyncio.Queue()
                self.out_queue = asyncio.Queue(maxsize=5)

                tg.create_task(self.send_realtime())
                
                if self.video_mode == "camera":
                    tg.create_task(self.get_frames())
                elif self.video_mode == "screen":
                    tg.create_task(self.get_screen())

                tg.create_task(self.listen_audio())
                tg.create_task(self.receive_audio())
                tg.create_task(self.play_audio())

                # Keep the session running
                while self.running:
                    await asyncio.sleep(0.1)

        except asyncio.CancelledError:
            pass
        except ExceptionGroup as EG:
            if self.audio_stream:
                self.audio_stream.close()
            traceback.print_exception(EG)
        finally:
            self.stop()

    def stop(self):
        """Stop the session."""
        self.running = False
        if self.audio_stream:
            self.audio_stream.close()
    
    def is_running(self) -> bool:
        """Check if the session is running."""
        return self.running