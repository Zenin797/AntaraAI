"""
Script to start the LTMAgent API server.
"""

import subprocess
import sys
import os

def install_dependencies():
    """Install required dependencies."""
    print("Installing dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "fastapi", "uvicorn"])

def run_api_server():
    """Run the API server."""
    print("Starting LTMAgent API server...")
    print("API documentation available at: http://localhost:8000/docs")
    
    try:
        subprocess.run(["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000", "--reload"])
    except KeyboardInterrupt:
        print("\nShutting down API server...")
    except FileNotFoundError:
        print("uvicorn not found. Installing dependencies...")
        install_dependencies()
        subprocess.run(["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000", "--reload"])

if __name__ == "__main__":
    # Change to the LTMAgent directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    run_api_server()