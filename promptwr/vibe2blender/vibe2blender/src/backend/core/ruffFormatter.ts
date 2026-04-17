import { execSync } from 'child_process';
import { writeFileSync, unlinkSync } from 'fs';
import { join } from 'path';
import { tmpdir } from 'os';

/**
 * Pipes AI-generated Python string through Ruff for formatting and linting.
 * This ensures whitespace-sensitive Python is clean before returning to the client.
 */
export const formatPythonCode = (code: string): string => {
  const tempFile = join(tmpdir(), `v2b_${Date.now()}.py`);
  
  try {
    writeFileSync(tempFile, code);
    
    // Using absolute path for ruff since it might not be in the global PATH
    const ruffPath = '/home/patraiswar05/.local/bin/ruff';
    
    // 1. Format the code
    execSync(`${ruffPath} format ${tempFile}`, { stdio: 'ignore' });
    
    // 2. Fix linting issues (auto-fixable ones)
    execSync(`${ruffPath} check --fix ${tempFile}`, { stdio: 'ignore' });
    
    const formattedCode = require('fs').readFileSync(tempFile, 'utf8');
    return formattedCode;
  } catch (error) {
    console.error('RUFF_FORMATTING_FAILED:', error);
    // If formatting fails, return original code as a fallback
    return code;
  } finally {
    try {
      unlinkSync(tempFile);
    } catch (e) {
      // Ignore cleanup errors
    }
  }
};
