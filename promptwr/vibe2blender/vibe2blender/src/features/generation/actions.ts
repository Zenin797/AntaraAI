import { type GenerateScript } from 'wasp/server/operations';
import { HttpError } from 'wasp/server';
import { GoogleGenerativeAI } from '@google/generative-ai';
import { checkRateLimit, GENERATE_LIMIT } from '../../backend/core/rateLimiter';
import { GenerationInputSchema } from '../../backend/core/validators';
import { guardPrompt } from '../../backend/core/promptGuard';
import { sanitizeOutput } from '../../backend/core/outputSanitizer';
import { formatPythonCode } from '../../backend/core/ruffFormatter';

type GenerateScriptPayload = {
  refinedPrompt: string;
  originalPrompt: string;
}

const API_KEY = process.env.GEMINI_API_KEY || '';
const genAI = new GoogleGenerativeAI(API_KEY);
const model = genAI.getGenerativeModel({ model: 'gemini-1.5-flash' });

export const generateScript: GenerateScript<GenerateScriptPayload> = async (args, context) => {
  if (!context.user) {
    throw new HttpError(401, 'AUTHENTICATION_REQUIRED');
  }

  // 1. Validate Input
  const result = GenerationInputSchema.safeParse({ refinedPrompt: args.refinedPrompt });
  if (!result.success) {
    throw new HttpError(400, 'INVALID_INPUT', { errors: result.error.format() });
  }

  // 2. Enforce Rate Limit
  checkRateLimit(`generate:${context.user.id}`, GENERATE_LIMIT);

  // 3. Guard against Prompt Injection
  const guardedPrompt = guardPrompt(args.refinedPrompt);

  // 4. Multi-Stage System Prompt
  const SYSTEM_INSTRUCTIONS = `
You are a "Blender Python Expert Techie". Generate clean, production-ready Python scripts for the Blender bpy API based on the user's prompt. 
Follow this mandatory structure:
1. Base Mesh: Use bpy.ops.mesh for primitive geometry.
2. Modifiers: Apply non-destructive modifiers (Bevel, Subdivision Surface) for refinement.
3. Materials/Effects: Build Principled BSDF node trees and assign them.
Ensure NO conversational filler. Return ONLY valid Python code.
  `;

  try {
    const geminiResult = await model.generateContent({
      contents: [{ role: 'user', parts: [{ text: `${SYSTEM_INSTRUCTIONS}\n\nUSER_CONCEPT: ${guardedPrompt}` }] }],
    });

    const rawOutput = geminiResult.response.text();

    // 5. Post-Processing Pipeline
    // A. Sanitize (remove markdown and filler)
    const sanitizedCode = sanitizeOutput(rawOutput);
    
    // B. Format (Ruff cleanup)
    const formattedCode = formatPythonCode(sanitizedCode);

    // 6. Persistence Flow
    const newScript = await context.entities.BlenderScript.create({
      data: {
        userId: context.user.id,
        originalPrompt: args.originalPrompt,
        refinedPrompt: args.refinedPrompt,
        generatedCode: formattedCode,
      }
    });

    return newScript;
  } catch (error) {
    console.error('GEMINI_API_ERROR:', error);
    // Fallback for development if API key is missing
    if (!API_KEY && process.env.NODE_ENV === 'development') {
      const mockScript = `# FALLBACK_MOCK_SCRIPT (GEMINI_API_KEY_MISSING)
import bpy
bpy.ops.mesh.primitive_monkey_add(size=2)
print("Fallback monkey generated!")`;
      
      const newScript = await context.entities.BlenderScript.create({
        data: {
          userId: context.user.id,
          originalPrompt: args.originalPrompt,
          refinedPrompt: args.refinedPrompt,
          generatedCode: mockScript,
        }
      });
      return newScript;
    }
    throw new HttpError(500, 'AI_GENERATION_FAILED');
  }
};
