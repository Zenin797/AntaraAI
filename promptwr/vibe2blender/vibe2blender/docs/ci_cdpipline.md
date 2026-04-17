name: Vibe2Blender CI/CD Pipeline

on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

# NOTE: This pipeline runs checks but mocks external APIs to save cloud credits.
jobs:
  build-and-test:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout Repository
      uses: actions/checkout@v4

    - name: Setup Node.js (Frontend & API)
      uses: actions/setup-node@v4
      with:
        node-version: '20'
        cache: 'npm'

    - name: Install Node Dependencies
      run: npm ci

    - name: Setup Python (For Ruff Script Formatting)
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'

    - name: Install Ruff Linter
      run: pip install ruff

    - name: Lint Python Output Scripts
      # Ruff ensures the AI-generated python code is mechanically clean
      run: ruff check .

    - name: Run Tests (Mocked AI Responses)
      # WARNING: Ensure tests use mocked LLM responses so CI doesn't burn API credits!
      run: npm run test

    - name: Docker Build Test
      # Verifies Phase 5 Orchestration constraints
      run: docker-compose build