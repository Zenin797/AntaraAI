import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

/**
 * Ruff Formatting Pipeline (Phase 3)
 *
 * LLMs frequently mess up Python's strict whitespace rules.
 * This utility pipes AI-generated Python code through `ruff format -`
 * via stdin, which avoids temp file management entirely.
 *
 * Fallback Behavior:
 *   If Ruff throws an error (the AI wrote fundamentally broken syntax),
 *   the raw AI output is returned with a warning comment prepended,
 *   so the user can still see and manually fix the output.
 */
export const formatPythonCode = async (code: string): Promise<string> => {
  try {
    // Pipe code through ruff format via stdin (the `-` flag reads from stdin)
    const { stdout } = await execAsync('ruff format -', {
      input: code,
      timeout: 10_000, // 10s timeout — formatting should be near-instant
    });

    return stdout;
  } catch (primaryError: any) {
    console.warn('RUFF_STDIN_FORMAT_FAILED:', primaryError?.message);

    // Fallback: Try using ruff check --fix via stdin to at least fix imports
    try {
      const { stdout } = await execAsync('ruff check --fix -', {
        input: code,
        timeout: 10_000,
      });
      return stdout || code;
    } catch (fallbackError: any) {
      console.warn('RUFF_CHECK_ALSO_FAILED:', fallbackError?.message);

      // Final fallback: return the raw code with a warning comment
      return `# ⚠️ RUFF_FORMAT_WARNING: Auto-formatting failed. The code below may have syntax issues.\n# Please review indentation and syntax before running in Blender.\n\n${code}`;
    }
  }
};
