🗂️ Scalable & Controllable Directory ArchitectureIn an AI-augmented workflow (Vibe Coding), your file management structure acts as the physical boundaries for the AI's context window. A poorly organized repository leads to token bloat, hallucinations, and cascading bugs.To achieve high controllability and scalability, we enforce a Feature-Driven (Vertical Slice) Architecture combined with Context Isolation.1. The Core Repository TreeThis structure separates concerns strictly, ensuring that when the AI is working on the frontend, it doesn't accidentally ingest or modify backend database schemas unless explicitly instructed./project-root
├── .github/                  # CI/CD Pipelines (main.yml)
├── docs/                     # 🧠 The AI's Brain (PRD, Security, Architecture)
│   ├── PRD.md
│   ├── SECURITY.md
│   ├── VIBE_CODING_GUIDE.md
│   └── DIRECTORY_STRUCTURE.md
├── infrastructure/           # 🐳 Deployment & Orchestration (Phase 5)
│   ├── docker-compose.yml
│   ├── Dockerfile.frontend
│   └── Dockerfile.backend
├── backend/                  # ⚙️ Server, API, and Database
│   ├── src/
│   │   ├── core/             # Shared logic (rate limiters, error handling)
│   │   ├── features/         # 🚀 VERTICAL SLICES (Domain Logic)
│   │   │   ├── auth/         # (Routes, controllers, and services for Auth only)
│   │   │   ├── generation/   # (Logic specifically for script/asset generation)
│   │   │   └── chat/         # (Ollama routing and prompt sanitization)
│   │   └── server.js         # Entry point
│   ├── prisma/               # Database schemas and migrations
│   └── package.json
├── frontend/                 # 🖥️ User Interface
│   ├── src/
│   │   ├── assets/           # Static images, fonts
│   │   ├── components/       # Dumb/Reusable UI components (Buttons, Modals)
│   │   ├── features/         # Complex, domain-specific UI (e.g., ChatWindow)
│   │   ├── pages/            # Top-level routing views
│   │   └── App.jsx           # UI Entry point
│   ├── tailwind.config.js
│   └── package.json
└── scripts/                  # 🐍 Isolated Python/Blender Generation Scripts
    └── templates/            # Base templates the AI uses to compile final outputs
2. Rules for AI ControllabilityTo maintain control over the AI agent as the codebase scales, enforce the following file management rules:A. The "Small Files" MandateAI agents struggle with files over 300-500 lines of code. If a controller or component gets too large, you must instruct the AI to break it down.Bad: /frontend/src/pages/Dashboard.jsx (1,200 lines)Good: Extracting logic into /frontend/src/components/Sidebar.jsx and /frontend/src/features/chat/ChatService.js.B. Feature-Driven Isolation (Vertical Slices)Notice the /features/ folders in both the frontend and backend. Instead of grouping all controllers together and all models together, group files by the feature they belong to.If the AI needs to fix the "Chat" feature, it only needs to read the /backend/src/features/chat/ directory, keeping its context window clean and laser-focused.C. Semantic Naming ConventionsThe AI heavily relies on file names to infer purpose without having to read the file contents. Use highly descriptive, semantic naming.Avoid: utils.js, helper.py, misc.cssUse: rateLimiter.js, blenderMeshHelper.py, chatAnimations.cssD. The /docs Folder is SacredThe /docs directory is the single source of truth. Whenever you start a new session with Google Antigravity, you should point the agent to this folder first so it understands the architectural constraints before writing a single line of code.