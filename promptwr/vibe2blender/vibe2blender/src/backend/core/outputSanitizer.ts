/**
 * Output Sanitizer (Phase 3)
 *
 * Regex utility to strip markdown code blocks, conversational filler,
 * and non-Python content from LLM output. Ensures the result is raw,
 * executable Python code ready for Ruff formatting.
 */
export const sanitizeOutput = (aiOutput: string): string => {
  // 1. Extract code from Markdown fences (```python ... ``` or ``` ... ```)
  const codeBlockRegex = /```(?:python|py)?\s*([\s\S]*?)```/gi;
  const matches: string[] = [];
  let match: RegExpExecArray | null;

  while ((match = codeBlockRegex.exec(aiOutput)) !== null) {
    matches.push(match[1]);
  }

  // If we found code blocks, join them; otherwise use the full output
  let cleanedCode = matches.length > 0 ? matches.join('\n\n') : aiOutput;

  // 2. Remove common conversational filler lines the LLM might inject
  const fillerPatterns = [
    /^Here(?:'s| is) (?:the|a|your).*:?\s*$/gim,
    /^This (?:script|code|program).*:?\s*$/gim,
    /^(?:Sure|Okay|Of course|Certainly|Absolutely)[!,.].*$/gim,
    /^Note:.*$/gim,
    /^Explanation:.*$/gim,
    /^Let me.*$/gim,
    /^I(?:'ve| have).*$/gim,
  ];

  for (const pattern of fillerPatterns) {
    cleanedCode = cleanedCode.replace(pattern, '');
  }

  // 3. Remove any remaining isolated markdown formatting
  cleanedCode = cleanedCode.replace(/^#+\s+.*$/gm, ''); // Remove headings
  cleanedCode = cleanedCode.replace(/\*\*([^*]+)\*\*/g, '$1'); // Remove bold
  cleanedCode = cleanedCode.replace(/\*([^*]+)\*/g, '$1'); // Remove italic

  // 4. Collapse excessive blank lines (3+ → 2)
  cleanedCode = cleanedCode.replace(/\n{3,}/g, '\n\n');

  // 5. Trim
  cleanedCode = cleanedCode.trim();

  return cleanedCode;
};
