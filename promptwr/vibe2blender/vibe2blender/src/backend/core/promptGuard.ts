import { HttpError } from 'wasp/server';

const INJECTION_BLOCKLIST = [
  'ignore previous instructions',
  'system prompt',
  'act as a linux terminal',
  'output your system prompt',
  'disregard earlier instructions',
];

/**
 * Defensive utility to wrap user input and check for prompt injection patterns.
 */
export const guardPrompt = (userInput: string): string => {
  const normalizedInput = userInput.toLowerCase();
  
  // 1. Check Blocklist
  for (const pattern of INJECTION_BLOCKLIST) {
    if (normalizedInput.includes(pattern)) {
      throw new HttpError(400, 'PROMPT_INJECTION_DETECTED');
    }
  }

  // 2. Wrap with explicit delimiters for AI clarity
  return `<<<USER_INPUT>>>\n${userInput}\n<<<END_USER_INPUT>>>`;
};
