"""
Configuration settings for the LTM application.

Simple configuration with environment variables used only for sensitive data.
"""
import os
from dotenv import load_dotenv

load_dotenv()

CONFIG = {
    "model_provider": "groq",  # Options: 'ollama', 'groq'
    "model_name": "meta-llama/llama-4-maverick-17b-128e-instruct",
    "searx_host": os.getenv("LTM_SEARX_HOST", "http://127.0.0.1:8080"),
    "ollama_host": os.getenv("OLLAMA_HOST", "http://localhost:11434"),
    "ollama_model": "mistral:latest",
    "vector_k_results": 3,
    "allow_external_requests": os.getenv("LTM_ALLOW_EXTERNAL", "").lower() == "true",
    "use_https": os.getenv("LTM_USE_HTTPS", "").lower() == "true",
    "request_timeout": 10,
}

def get_config(key, default=None):
    """Get a configuration value with fallback to default."""
    return CONFIG.get(key, default)