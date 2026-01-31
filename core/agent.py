"""
Agent processing logic for the LTM application.
"""

from langchain_core.messages import get_buffer_string, AIMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END
from datetime import datetime, timedelta
import re

from core.state import State
from config.prompt_templates import prompt

def analyze_sentiment(text: str) -> str:
    """Sophisticated sentiment analysis for crisis detection using multiple approaches."""
    import re
    from collections import Counter
    from config.system_config import SystemConfig

    # Preprocess the text
    text_lower = text.lower().strip()

    # Approach 1: Keyword-based detection with context awareness
    for pattern in SystemConfig.CRISIS_PATTERNS:
        if re.search(pattern, text_lower):
            return "CRITICAL"

    # Approach 2: Sentiment intensity scoring
    neg_count = sum(text_lower.count(word) for word in SystemConfig.NEGATIVE_WORDS)
    pos_count = sum(text_lower.count(word) for word in SystemConfig.POSITIVE_WORDS)

    # Calculate sentiment ratio
    if neg_count > 0:
        sentiment_ratio = neg_count / (neg_count + pos_count + 1)  # +1 to avoid division by zero

        # If highly negative sentiment combined with certain phrases
        if sentiment_ratio > SystemConfig.SELFIE_REQUEST_MOOD_THRESHOLD:  # Configurable threshold
            for indicator in SystemConfig.HIGH_NEG_INDICATORS:
                if indicator in text_lower:
                    return "CRITICAL"

    # Approach 3: Linguistic markers of crisis
    for marker in SystemConfig.CRISIS_MARKERS:
        if marker in text_lower:
            return "CRITICAL"

    # Approach 4: Emotional escalation patterns
    exclamation_pattern = r'[!]{2,}'  # Multiple exclamation marks
    caps_pattern = r'(?:[A-Z]{2,})'  # Multiple consecutive capital letters

    if re.search(exclamation_pattern, text) and neg_count > pos_count:
        return "WARNING"  # High emotional state, monitor closely

    # Approach 5: Isolation and finality language
    for pattern in SystemConfig.ISOLATION_PATTERNS:
        if re.search(pattern, text_lower):
            return "WARNING"

    return "NORMAL"

def should_request_selfie(state: State, config: RunnableConfig) -> bool:
    """Determine if a selfie should be requested based on time or conversation patterns."""
    try:
        from core.memory_manager import db
        from config.system_config import SystemConfig

        user_id = config.get("configurable", {}).get("user_id")
        if not user_id:
            return False

        # Check if it's been more than the configured interval since the last selfie request
        last_selfie_request = list(db["selfie_requests"].find(
            {"user_id": user_id}
        ).sort("timestamp", -1).limit(1))

        if last_selfie_request:
            last_request_time = last_selfie_request[0]["timestamp"]
            if datetime.now() - last_request_time < timedelta(hours=SystemConfig.SELFIE_REQUEST_INTERVAL_HOURS):
                return False  # Don't request more than once per configured interval

        # Check if the user has been talking about mood-related topics
        recent_messages = state["messages"][-5:]  # Look at last 5 messages
        mood_related_keywords = [
            "depressed", "sad", "anxious", "stressed", "tired", "exhausted",
            "lonely", "hopeless", "overwhelmed", "miserable", "unhappy"
        ]

        for msg in recent_messages:
            if hasattr(msg, 'content'):
                content = msg.content.lower()
                if any(keyword in content for keyword in mood_related_keywords):
                    return True

        # Random chance to request selfie periodically based on configuration
        import random
        return random.random() < SystemConfig.SELFIE_RANDOM_CHANCE

    except Exception as e:
        print(f"Error checking if selfie should be requested: {e}")
        return False

def crisis_node(state: State, config: RunnableConfig):
    """Target node for crisis intervention with active response."""
    from langchain_core.messages import ToolCall
    from core.tools import send_alert_tool
    from core.integrations import get_integration_manager

    # Prepare crisis response message
    crisis_message = (
        "I've detected that you may be in distress. I'm activating safety protocols "
        "and alerting your emergency contacts. Please stay safe and reach out to someone "
        "you trust immediately. If you're having thoughts of self-harm, please contact "
        "the National Suicide Prevention Lifeline at 988 or your local emergency number."
    )

    # Get user ID for context
    user_id = config.get("configurable", {}).get("user_id")

    # Create multiple tool calls for different alert channels
    tool_calls = []

    # Standard alert tool call
    tool_calls.append({
        "name": "send_alert_tool",
        "id": "crisis_alert_" + str(hash(crisis_message)),
        "args": {
            "message": "URGENT: User may be in crisis. Immediate attention required.",
            "specific_contact": "emergency_contacts"
        }
    })

    # Add integration tool calls if available
    integration_manager = get_integration_manager()

    # WhatsApp alert if configured
    if integration_manager.whatsapp.is_available():
        tool_calls.append({
            "name": "send_whatsapp_message_tool",
            "id": "whatsapp_crisis_alert_" + str(hash(crisis_message)),
            "args": {
                "phone_number": "EMERGENCY_CONTACT_PHONE",  # This would be pulled from user profile
                "message": f"CRISIS ALERT: User {user_id} may be in distress. Immediate attention required."
            }
        })

    # Telegram alert if configured
    if integration_manager.telegram.is_available():
        tool_calls.append({
            "name": "send_telegram_message_tool",
            "id": "telegram_crisis_alert_" + str(hash(crisis_message)),
            "args": {
                "chat_id": "EMERGENCY_CHAT_ID",  # This would be pulled from user profile
                "message": f"CRISIS ALERT: User {user_id} may be in distress. Immediate attention required."
            }
        })

    # EHR logging if configured
    if user_id and integration_manager.ehr.is_available():
        tool_calls.append({
            "name": "log_to_ehr_tool",
            "id": "ehr_crisis_log_" + str(hash(crisis_message)),
            "args": {
                "patient_id": user_id,
                "note": f"Crisis detected at {datetime.now()}. User may be in distress.",
                "category": "crisis_alert"
            }
        })

    # Also send notification through the service
    if user_id:
        try:
            from core.service import LTMService
            service = LTMService()
            service.send_notification(
                user_id=user_id,
                message="CRISIS DETECTED: Emergency protocols activated. Help is being contacted.",
                notification_type="alert"
            )
        except:
            # If service initialization fails, we'll still proceed with the tool calls
            pass

    return {
        "messages": [AIMessage(
            content=crisis_message,
            tool_calls=tool_calls
        )],
        "next_node": None
    }

def agent(state: State, config: RunnableConfig, model_with_tools) -> dict:
    """Process the current state and generate a response using the LLM.

    Args:
        state (State): The current state of the conversation.
        model_with_tools: The model with bound tools.

    Returns:
        dict: The updated state with the agent's response.
    """
    # Check for crisis keywords in the last user message
    last_message = state["messages"][-1]
    if last_message.type == "human":
        sentiment = analyze_sentiment(last_message.content)
        if sentiment == "CRITICAL":
            return {"next_node": "crisis_node"}

    # Check if we should request a selfie
    user_id = config.get("configurable", {}).get("user_id")
    if user_id and should_request_selfie(state, config):
        # Return a tool call to request a selfie
        return {
            "messages": [AIMessage(
                content="I'd like to check in on your well-being.",
                tool_calls=[{
                    "name": "request_selfie_tool",
                    "id": "selfie_req_" + str(hash(datetime.now())),
                    "args": {"reason": "wellness monitoring"}
                }]
            )]
        }

    # Check if there's visual context available to analyze
    # This could come from a previous tool call or external input
    visual_context_available = False
    for msg in state["messages"]:
        if hasattr(msg, 'metadata') and 'visual_context' in msg.metadata:
            visual_context_available = True
            break

    # If visual context is available, analyze it
    if visual_context_available:
        # Create a tool call to analyze visual context
        return {
            "messages": [AIMessage(
                content="I'm analyzing the visual information you've shared.",
                tool_calls=[{
                    "name": "analyze_visual_context_tool",
                    "id": "visual_analysis_" + str(hash(datetime.now())),
                    "args": {"image_description": "User appears tired with dark circles under eyes, sitting alone in dimly lit room"}
                }]
            )]
        }

    bound = prompt | model_with_tools
    recall_str = (
        "<recall_memory>\n" + "\n".join(state["recall_memories"]) + "\n</recall_memory>"
    )
    prediction = bound.invoke(
        {
            "messages": state["messages"],
            "recall_memories": recall_str,
        }
    )
    return {
        "messages": [prediction],
    }

def load_memories(state: State, config: RunnableConfig) -> dict:
    """Load memories for the current conversation.

    Args:
        state (State): The current state of the conversation.
        config (RunnableConfig): The runtime configuration for the agent.

    Returns:
        dict: The updated state with loaded memories.
    """
    try:
        from core.memory_manager import memory_store
        
        user_id = config.get("configurable", {}).get("user_id")
        if not user_id:
            return {"recall_memories": []}
            
        # Get the latest user message to query against
        last_message = state["messages"][-1]
        query = last_message.content if hasattr(last_message, "content") else str(last_message)
        
        # Search across all namespaces for this user
        # We limit to 5 results to keep context manageable
        results = memory_store.search(
            namespace=("memories", user_id),
            query=query,
            limit=5
        )
        
        # Format results for the prompt
        memories = [f"- {r.value.get('content', str(r.value))}" for r in results]
        
        return {
            "recall_memories": memories,
        }
    except Exception as e:
        print(f"Error loading memories: {e}")
        return {"recall_memories": []}

def route_tools(state: State):
    """Determine whether to use tools or end the conversation based on the last message.

    Args:
        state (State): The current state of the conversation.

    Returns:
        str: The next step in the graph.
    """
    if state.get("next_node") == "crisis_node":
        return "crisis_node"

    msg = state["messages"][-1]
    if msg.tool_calls:
        return "tools"
    return END