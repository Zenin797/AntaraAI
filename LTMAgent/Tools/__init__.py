"""
Tool implementations for the LTM application.
This module contains specialized tools that can be used by the LTM agent.
"""

from config.app_config import get_config

# Only expose the system memory manager by default
from Tools.SystemMemoryManager import get_memory_usage

allow_external = get_config("allow_external_requests", False)

if allow_external:
    try:
        from Tools.WeatherToolSample1 import weather
        from Tools.StackExcangeToolSample1 import stackexchange
        print("External API tools loaded")
    except ImportError as e:
        print(f"Failed to load external API tools: {e}")

__all__ = ["get_memory_usage"]