🛡️ Application Security & API Defense

In an AI-augmented workflow (Vibe Coding), security is no longer just about protecting user data or stopping traditional web exploits; it is fundamentally about protecting our infrastructure, preserving our API token quotas, and preventing autonomous agents from being manipulated via prompt injection attacks. Because AI coding agents dynamically process unstructured inputs, they introduce entirely new attack surfaces that require a layered, defense-in-depth strategy.

1. API Rate Limiting & Resource Protection

To prevent malicious users, botnets, or runaway client-side loops from rapidly draining our expensive cloud LLM credits, we strictly enforce multi-tiered rate limiting on all public-facing endpoints.

The Leaky Bucket Algorithm: We implement a Leaky Bucket middleware strategy for our heaviest endpoints. Think of a bucket with a hole at the bottom: incoming requests are poured into the bucket (bursts of traffic), but they are processed and forwarded to the LLM at a strict, constant rate (the leak). If traffic spikes and the bucket fills to capacity, excess requests are instantly discarded or queued. This prevents our backend from overwhelming the LLM provider and smooths out unpredictable traffic spikes.

Token-Based vs. Request-Based Limits: Because LLMs bill by the token, limiting raw requests (RPM) is not always enough. We enforce Tokens Per Minute (TPM) limits on the backend to safeguard against adversaries submitting massive walls of text designed to maximize our compute costs.

Granular Thresholds:

/api/chat (Local Ollama Routing): Max 20 requests/minute per IP. (Since this is local compute, the limit is higher, but still capped to prevent CPU starvation).

/api/generate-script (Heavy Cloud Model): Max 5 requests/minute per IP.

/api/auth: Max 10 requests/minute per IP to prevent brute-force attacks.

Response Handling: When limits are exceeded, the API must return a standard 429 Too Many Requests status, optionally accompanied by a Retry-After header to inform the client when they can attempt the request again.

2. Input Sanitization & Prompt Injection Defense

Prompt injection occurs when a user provides malicious input that tricks the LLM into ignoring its original instructions and executing unauthorized actions. We must treat the LLM as any other user and adopt a zero-trust approach to its inputs and outputs.

Strict Schema Validation (Zod): Never pass raw, unvalidated user input to the cloud LLM. All incoming requests MUST be validated against strict Zod schemas to ensure data types and expected formats are absolutely correct before processing.

Context Window & Character Limits: Enforce hard character limitations (e.g., Max 500 characters) on user prompts. This not only prevents context window overflow and saves on token costs, but it also disrupts payload-splitting injection attacks where attackers try to smuggle lengthy malicious instructions into the system.

Input Delimiters & Role Separation: When constructing the final prompt for the AI, strictly separate the system instructions from the user data. Use explicit delimiters (e.g., wrapping user input in <<<USER_INPUT>>> and <<<END_USER_INPUT>>> tags) so the LLM can clearly distinguish between the developer's core directives and the untrusted user variables.

The Dual-Model Buffer (Active Defense): Route all initial user inputs through the local, free Ollama (Qwen) instance first. This model acts as a sanitizer and a firewall. It refines the intent, strips out suspicious commands (like "ignore previous instructions"), and structures the data safely before sending a single, highly optimized super-prompt to the expensive Cloud compiler.

Improper Output Handling Prevention: If the LLM generates code, markdown, or JSON that is returned to the user, it must be encoded and sanitized to prevent Cross-Site Scripting (XSS). Never pass LLM output directly into an eval() or system shell command.

3. Secrets Management & Environment Isolation

AI coding agents have unprecedented access to the development environment. We must ensure they cannot accidentally leak credentials into the codebase or expose tokens in public logs.

The Golden Rule: Never commit API keys, database connection strings, or passwords.

Implementation: * Use .env files exclusively for local development configuration.

Ensure your .gitignore is comprehensive (including .env, node_modules/, __pycache__/, and .DS_Store).

When migrating to Phase 5 (Dockerization), inject environment variables securely at runtime rather than baking them into the Docker image itself.

Least Privilege Access: If your application uses Google Cloud Run or AWS, ensure the service account running the application has only the exact permissions needed to execute. It should not have root access to the entire cloud project.