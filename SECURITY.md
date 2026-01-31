# Security Policy

## Input Sanitization
Input sanitization is currently delegated to the LLM/Framework.

## Known Risks
- No prompt injection guardrails currently active
- Input validation relies on underlying LLM safety mechanisms
- Memory persistence depends on configured backend (currently using InMemoryStore in some cases)

## Authentication
- Basic authentication mechanisms not implemented
- API endpoints may be accessible without proper authorization

## Data Protection
- Sensitive data may be stored in plain text depending on configuration
- Encryption of stored memories not implemented by default