import { z } from 'zod';

export const ChatInputSchema = z.object({
  message: z.string()
    .trim()
    .min(1, 'PROMPT_EMPTY')
    .max(1000, 'PROMPT_TOO_LONG'),
});

export const GenerationInputSchema = z.object({
  refinedPrompt: z.string()
    .trim()
    .min(10, 'PROMPT_TOO_SHORT')
    .max(500, 'PROMPT_TOO_LONG'),
});
