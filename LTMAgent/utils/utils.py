from langchain_core.runnables import RunnableConfig
import requests
from typing_extensions import TypedDict


class KnowledgeTriple(TypedDict):
    subject: str
    predicate: str
    object_: str


def get_user_id(config: RunnableConfig) -> str:
    """Get the user ID from the runtime configuration.
    
    Args:
        config: Runtime configuration object
        
    Returns:
        str: User ID
        
    Raises:
        ValueError: If user ID is not provided in the configuration
    """
    user_id = config["configurable"].get("user_id")
    if user_id is None:
        raise ValueError("User ID needs to be provided to save a memory.")
    return user_id


def get_thread_id(config: RunnableConfig) -> str:
    """Get the thread ID from the runtime configuration.
    
    Args:
        config: Runtime configuration object
        
    Returns:
        str: Thread ID or None if not provided
    """
    return config["configurable"].get("thread_id", "default")


# This function is kept for your personal use case but is not used in the main application
def get_token():
    """
    Get the ngrok token from the token server.
    This function is defined for specific use cases and is not used in the standard application.
    """
    timeout = 10
    server_url = 'http://144.24.151.240:11434/get_message'
    
    try:
        response = requests.get(server_url, timeout=timeout)
        response.raise_for_status()
        return response.text
    except requests.exceptions.Timeout:
        raise Exception(f"Token server request timed out after {timeout} seconds")
    except requests.exceptions.HTTPError as e:
        raise Exception(f"Token server returned an error: {e}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error connecting to token server: {e}")