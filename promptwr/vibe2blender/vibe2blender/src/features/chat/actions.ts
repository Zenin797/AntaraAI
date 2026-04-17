import { type Chat } from 'wasp/server/operations';
import { HttpError } from 'wasp/server';
import axios from 'axios';
import { checkRateLimit, CHAT_LIMIT } from '../../backend/core/rateLimiter';
import { ChatInputSchema } from '../../backend/core/validators';
import { guardPrompt } from '../../backend/core/promptGuard';

type ChatPayload = {
  message: string;
}

const OLLAMA_HOST = process.env.OLLAMA_HOST || 'http://localhost:11434';
const OLLAMA_MODEL = 'qwen2.5'; // As specified in docs

export const chat: Chat<ChatPayload, { role: string; content: string }> = async (args, context) => {
  if (!context.user) {
    throw new HttpError(401, 'AUTHENTICATION_REQUIRED');
  }

  // 1. Validate Input
  const result = ChatInputSchema.safeParse(args);
  if (!result.success) {
    throw new HttpError(400, 'INVALID_INPUT', { errors: result.error.format() });
  }

  // 2. Enforce Rate Limit
  checkRateLimit(`chat:${context.user.id}`, CHAT_LIMIT);

  // 3. Guard against Prompt Injection
  const guardedPrompt = guardPrompt(args.message);

  // 4. Call Local Ollama (Qwen)
  try {
    const response = await axios.post(`${OLLAMA_HOST}/api/chat`, {
      model: OLLAMA_MODEL,
      messages: [
        {
          role: 'system',
          content: "You are a specialized 3D Technical Artist Interviewer. Your goal is to help users refine vague ideas into structured prompts for generating Blender Python (bpy) scripts. Ask focused questions about geometry, modifiers, and materials. Be concise and professional."
        },
        { role: 'user', content: guardedPrompt }
      ],
      stream: false,
    });

    return {
      role: 'assistant',
      content: response.data.message.content,
    };
  } catch (error) {
    console.error('OLLAMA_API_ERROR:', error);
    // Fallback if Ollama is not running (e.g., during development without local AI)
    if (process.env.NODE_ENV === 'development') {
      return {
        role: 'assistant',
        content: "I am unable to reach the local AI interviewer (Ollama/Qwen). Please ensure Ollama is running and has the qwen2.5 model pulled.",
      };
    }
    throw new HttpError(500, 'AI_SERVICE_UNAVAILABLE');
  }
};
