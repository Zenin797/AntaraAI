Vibe2Blender: Project Workflow & Git Strategy

This document outlines the strict "Vertical Slice" workflow for building the Vibe2Blender application. Designed specifically for the rapid, high-pressure environment of the PromptWars hackathon, this methodology relies heavily on constraint-driven development. By strictly managing our AI models, our design choices, and our testing intervals, we ensure that the "vibe coding" process results in a production-ready application rather than a tangled mess of hallucinated code. Every change MUST be tested locally and verified before moving to the next step to prevent cascading errors.

1. Development Philosophy

Token Efficiency & Specialized Local AI (The Dual-Model Approach): To avoid burning through expensive cloud API credits during the ideation phase, we employ a dual-model architecture. We use a locally hosted Ollama instance running a small-parameter model (like Qwen 2.5) for all user chat, prompt refinement, and conversational routing. This model must be trained, fine-tuned, or augmented (via RAG) specifically on Blender creation data and 3D modeling terminology. It acts as the "Interviewer." Only when the user's concept is fully fleshed out and validated do we send the final, optimized super-prompt to the heavy, expensive cloud model (Gemini/OpenAI). This heavy model acts as the "Compiler," solely responsible for generating the complex, final Blender Python (bpy) script.

API Rate Limiting & Security Defenses: AI applications are prime targets for abuse, which can lead to massive cost overruns or depleted API key quotas. We must strictly limit API calls on both the local and cloud endpoints. This involves implementing robust middleware (like leaky bucket or sliding window algorithms) to throttle user requests. Additionally, all user inputs must be aggressively sanitized to prevent prompt injection attacks that could trick the AI into ignoring its primary directives or exposing internal system prompts.

Monochrome UI & Zero-Distraction Design: During a hackathon, time spent debating color palettes is time wasted. We will stick strictly to a stark black-and-white color palette. This monochrome constraint forces us to focus entirely on layout (using standard CSS Flexbox/Grid), clear typography, and a seamless user experience. By removing color from the equation, we reduce cognitive load for both the developer and the AI generating the UI components, ensuring the spotlight remains firmly on the generated 3D Python code and the conversational interface.

Check After Every Change (The Isolation Principle): LLM-assisted coding can introduce subtle bugs that compound over time. To counteract this, we mandate running wasp start (or your respective dev server) after EVERY single file modification. Do not stack unverified changes. If a database schema is updated, it must be migrated and verified in Prisma Studio before writing the API that uses it. Isolating variables via frequent testing is the only way to maintain a stable foundation in an AI-augmented workflow.

2. Step-by-Step Implementation Strategy (The Vertical Slice)

The Vertical Slice methodology means we do not build the entire database, then the entire backend, then the entire frontend. Instead, we build one feature completely from the database up to the UI before moving to the next.

Phase 1: Foundation & Data Layer

The goal of this phase is to establish the absolute minimum infrastructure required to store users and their generated scripts. We rely on Wasp to handle the boilerplate plumbing between the database and the server.

Initialize project structure: Run wasp new vibe2blender to scaffold the React frontend, Node.js backend, and database connection.

Define database models: Open schema.prisma and define the User and BlenderScript models. Keep relationships simple and explicit.

Generate and apply migrations: Run the Wasp database migration commands to push the schema to the PostgreSQL instance.

Test: Open Prisma Studio (wasp db studio) and manually verify that the tables exist and can accept mock data.

Git Commit: git commit -m "chore: setup project, wasp foundation, and postgres database schema"

Phase 2: Core API, Validation & Rate Limiting

Before connecting the AI, we must build a fortified gateway. This phase ensures that bad data cannot crash the application and that our endpoints are secure.

Implement Zod validation: Set up Zod schemas for all incoming prompt requests. Enforce strict character limits (e.g., max 500 characters) to prevent context window overflow.

Create the Local Chat Endpoint: Scaffold the POST /api/chat endpoint. Integrate the local Ollama instance, ensuring it returns proper JSON structures.

Create the Generation Endpoint: Scaffold the POST /api/generate-script endpoint. This will handle the hand-off to the heavy LLM (Gemini).

Implement Rate-Limiting: Add middleware to throttle requests. For example, limit /api/chat to 20 requests per minute per IP, and /api/generate-script to 5 requests per minute, returning a 429 Too Many Requests status when exceeded.

Test: Use Postman or cURL to hammer the API endpoints with mock data, verifying that the Zod validators reject bad inputs and the rate limiters block excessive requests.

Git Commit: git commit -m "feat: implement zod validation, secure rate limiting, and core AI API endpoints"

Phase 3: The 3D Tech Artist Prompting Pipeline & Ruff Formatting

This is the core "brain" of the application. The prompts must be structured to force the AI to think like a technical artist, and the output must be mechanically cleaned to prevent Python indentation errors.

Implement the multi-stage system prompt: Structure the heavy LLM's instructions into discrete, sequential steps:

Step 1: Base Mesh: Instruct the AI to use bpy.ops.mesh to establish the primitive geometry based on the user's prompt.

Step 2: Modifiers: Instruct the AI to apply non-destructive modifiers (Bevel, Subdivision Surface) to refine the shape.

Step 3: Materials/Effects: Instruct the AI to build node trees for materials (e.g., Principled BSDF, Emission) and assign them to the mesh.

Ruff Implementation: Because Python is whitespace-sensitive and LLMs often output inconsistent indentation, integrate ruff (the fast Python linter/formatter). Pipe the AI-generated string through a background Ruff process to automatically format, lint, and clean the script before returning it to the client.

Test: Send a text prompt through the API, let Ruff format the output, copy the resulting string, and run it inside Blender's scripting environment. It must execute without throwing any syntax or indentation errors.

Git Commit: git commit -m "feat: integrate 3D expert techie prompt chain and post-generation Ruff formatting"

Phase 4: Frontend (Black & White UI) & Onboarding

With the backend completely secure and functional, we build the user-facing interface. The focus here is on a sleek, high-contrast, distraction-free environment that teaches the user how to succeed.

Build the layout shell: Construct a CSS Grid/Flexbox layout featuring a collapsible sidebar for chat history and a main dual-pane area (one half for the chat interface, one half for the generated code block).

Implement the local chatbot UI: Create the message bubbles, typing indicators, and input fields for interacting with the local Qwen model.

New User Onboarding & Stock Examples: Blank slates are intimidating. Implement a dynamic welcome screen containing "Recommendation Stock Examples" (e.g., "Generate a low-poly neon sword", "Create a sci-fi cyberpunk crate", "Make a smooth ceramic vase"). Clicking these should instantly populate the chat, directly teaching new users the most effective ways to prompt the system.

Implement Code UI: Add syntax highlighting (e.g., using PrismJS or Highlight.js) for the outputted Python code, and include a crucial "Copy to Clipboard" button.

Test: Verify UI responsiveness across different screen sizes, test state management during long chat sessions, and ensure the onboarding flow is intuitive.

Git Commit: git commit -m "feat: implement monochrome frontend UI, code highlighting, and stock example onboarding"

Phase 5: Dockerization & Deployment

The final step ensures that the application is reproducible and easy for hackathon judges to evaluate without dealing with local dependency nightmares.

Create the Application Dockerfile: Write a Dockerfile for the main Wasp web application and Node server.

Create the Orchestration (docker-compose): Write a docker-compose.yml file to spin up the entire ecosystem simultaneously. This must include the Web App container, the PostgreSQL Database container, and the local Ollama container pre-loaded with the Qwen model.

Environment Variable Mapping: Ensure that all .env variables (Database URLs, API keys, internal ports) are securely mapped and injected into the containers.

Test: Stop all local dev servers. Run docker-compose up --build and verify the entire stack functions flawlessly from a clean, containerized slate, proving the "it works on my machine" problem is solved.

Git Commit: git commit -m "chore: dockerize application, database, and local AI services for reproducible deployment"