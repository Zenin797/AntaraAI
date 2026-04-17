/**
 * Regex utility to strip markdown code blocks and conversational filler from LLM output.
 * Ensures the result is raw, executable Python code.
 */
export const sanitizeOutput = (aiOutput: string): string => {
  // 1. Remove Markdown Fencing (e.g., ```python ... ```)
  const codeBlockRegex = /```(?:python)?\s*([\s\S]*?)```/gi;
  const match = codeBlockRegex.exec(aiOutput);
  let cleanedCode = match ? match[1] : aiOutput;

  // 2. Trim whitespace
  cleanedCode = cleanedCode.trim();

  // 3. Remove leading/trailing conversational phrases if any (aggressive filter)
  // This is a simplified version, in Phase 3 we'll rely on Ruff to help cleanup.
  
  return cleanedCode;
};
