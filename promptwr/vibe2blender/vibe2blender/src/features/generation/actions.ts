import { type GenerateScript } from 'wasp/server/operations';
import { HttpError } from 'wasp/server';
import { GoogleGenerativeAI } from '@google/generative-ai';
import { checkRateLimit, GENERATE_LIMIT } from '../../backend/core/rateLimiter';
import { GenerationInputSchema } from '../../backend/core/validators';
import { guardPrompt } from '../../backend/core/promptGuard';
import { sanitizeOutput } from '../../backend/core/outputSanitizer';
import { formatPythonCode } from '../../backend/core/ruffFormatter';

// ─── Type Definitions ───────────────────────────────────────────────
type GenerateScriptPayload = {
  refinedPrompt: string;
  originalPrompt: string;
}

// ─── Gemini Client Setup ────────────────────────────────────────────
const API_KEY = process.env.GEMINI_API_KEY || '';
const genAI = new GoogleGenerativeAI(API_KEY);
const model = genAI.getGenerativeModel({ model: 'gemini-1.5-flash' });

/**
 * Phase 3 System Prompt — The "Compiler" persona.
 * This is the 3-Step mandatory prompt that instructs Gemini to
 * generate executable, clean Blender Python (bpy) scripts.
 */
const COMPILER_SYSTEM_PROMPT = `You are an elite Blender Python (bpy) developer. Convert the user's description into a fully executable bpy script.
Step 1: Delete default objects and create the base mesh using bpy.ops.mesh.
Step 2: Apply necessary modifiers (e.g., Bevel, Subdivision) non-destructively.
Step 3: Create a basic Principled BSDF material and assign it.
ONLY output valid Python code. No markdown formatting. No conversational text.`;

// ─── Wasp Action ────────────────────────────────────────────────────
export const generateScript: GenerateScript<GenerateScriptPayload> = async (args, context) => {
  if (!context.user) {
    throw new HttpError(401, 'AUTHENTICATION_REQUIRED');
  }

  // 1. Validate Input
  const result = GenerationInputSchema.safeParse({ refinedPrompt: args.refinedPrompt });
  if (!result.success) {
    throw new HttpError(400, 'INVALID_INPUT', { errors: result.error.format() });
  }

  // 2. Enforce Rate Limit (5 RPM)
  checkRateLimit(`generate:${context.user.id}`, GENERATE_LIMIT);

  // 3. Guard against Prompt Injection
  const guardedPrompt = guardPrompt(args.refinedPrompt);

  // 4. Call Gemini with the 3-Step System Prompt
  try {
    const geminiResult = await model.generateContent({
      contents: [{
        role: 'user',
        parts: [{ text: `${COMPILER_SYSTEM_PROMPT}\n\nUser request: ${guardedPrompt}` }],
      }],
    });

    const rawOutput = geminiResult.response.text();

    // 5. Post-Processing Pipeline
    // A. Sanitize — strip markdown fences, conversational filler
    const sanitizedCode = sanitizeOutput(rawOutput);

    // B. Format — pipe through Ruff for Python formatting + lint fixes
    const formattedCode = await formatPythonCode(sanitizedCode);

    // 6. Persist to database
    const newScript = await context.entities.BlenderScript.create({
      data: {
        userId: context.user.id,
        originalPrompt: args.originalPrompt,
        refinedPrompt: args.refinedPrompt,
        generatedCode: formattedCode,
      }
    });

    return newScript;
  } catch (error: any) {
    console.error('GEMINI_API_ERROR:', error?.message || error);

    // Provide a mock fallback in development if API key is not set
    if (!API_KEY && process.env.NODE_ENV === 'development') {
      const mockScript = `# FALLBACK_MOCK_SCRIPT (GEMINI_API_KEY not configured)
import bpy

# Step 1: Clear scene and create base mesh
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.mesh.primitive_monkey_add(size=2, location=(0, 0, 0))
obj = bpy.context.active_object

# Step 2: Apply Subdivision Surface modifier
mod = obj.modifiers.new(name="Subdivision", type='SUBSURF')
mod.levels = 2
mod.render_levels = 3

# Step 3: Create and assign a Principled BSDF material
mat = bpy.data.materials.new(name="MonkeyMaterial")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.8, 0.2, 0.1, 1.0)
obj.data.materials.append(mat)

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
