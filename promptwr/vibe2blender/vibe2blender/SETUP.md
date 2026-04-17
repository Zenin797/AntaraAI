# Vibe2Blender — Local Setup Guide

This guide walks you through setting up the Vibe2Blender application locally. The project uses the [Wasp framework](https://wasp-lang.dev) (React + Node.js + Prisma) to manage the full-stack architecture seamlessly.

---

## 1. Prerequisites

Before scaling the app locally, ensure you have the following installed:

1. **Node.js** (v18.x or later recommended)
2. **NPM** (v9.x or later)
3. **WSL (Windows Subsystem for Linux)**
   - *Note for Windows Users*: The Wasp CLI currently requires Linux/macOS. If you are developing on Windows, you **must** use WSL. Please clone and develop inside your WSL file system (e.g., `~/projects/...`).
4. **PostgreSQL**
   - You need a running PostgreSQL instance locally or via Docker.
5. **Ollama** (Local AI)
   - Ensure Ollama is installed and running locally with the `qwen2.5` model.
   - Command: `ollama run qwen2.5`

---

## 2. Install Wasp CLI

Wasp versions 0.21 and later are installed via NPM. **Run this inside your WSL or Linux/macOS terminal:**

```bash
npm install -g @wasp.sh/wasp-cli
```
*(Verify installation by running `wasp version` in your terminal)*

---

## 3. Environment Variables

1. Copy the example `.env` file to create your local `.env`:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and fill in your correct credentials:
   ```env
   # Database Connection String
   DATABASE_URL=postgresql://<user>:<password>@localhost:5432/vibe2blender
   
   # Cloud Model setup
   GEMINI_API_KEY=your_actual_gemini_api_key
   
   # Local Model setup
   OLLAMA_HOST=http://localhost:11434
   ```

---

## 4. Install Dependencies & Build

Navigate to the root directory where `main.wasp` is located, then install NPM packages:

```bash
npm install
```

---

## 5. Database Migration

Before starting the app, run the Wasp database migration to establish your PostgreSQL schema (`User` and `BlenderScript` tables):

```bash
wasp db migrate-dev
```

*Note: You can use `wasp db studio` to visually inspect your tables via Prisma Studio.*

---

## 6. Run the Application

Start the development server. Wasp will concurrently boot up your React frontend and Node.js backend:

```bash
wasp start
```

- **Frontend Application**: `http://localhost:3000`
- **Backend API**: `http://localhost:3001`

---

## Alternative Frontend Check (No Wasp CLI locally)

If you have already compiled `.wasp/out/web-app` and only want to start the React UI on Windows without installing Wasp CLI, you can start Vite directly via:

```powershell
npx vite .wasp/out/web-app --port 3000
```
