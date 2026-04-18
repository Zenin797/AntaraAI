import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const dest = path.join(__dirname, '..', 'node_modules', 'wasp', 'client');
const filePath = path.join(dest, 'operations.js');

fs.mkdirSync(dest, { recursive: true });

const content = `export const chat = Symbol('chat');
export const generateScript = Symbol('generateScript');

export function useAction(action) {
  return async (payload) => {
    await new Promise((r) => setTimeout(r, 200));

    if (action === chat) {
      const msg = payload?.message || (payload?.messages && payload.messages[0]?.content) || '';
      return { content: \`Postinstall mock assistant reply to: \${String(msg).slice(0, 200)}\` };
    }

    if (action === generateScript) {
      const refined = payload?.refinedPrompt || '';
      return { generatedCode: \`# Postinstall mock Blender Python\\n# Refined prompt: \${refined.slice(0,120)}\\nprint(\\\"This is a postinstall mock Blender script\\\")\` };
    }

    return {};
  };
}
`;

fs.writeFileSync(filePath, content, 'utf8');
console.log('Wasp stub written to', filePath);
