#!/usr/bin/env python3
"""
Forex Strategist Backend Runner
"""
import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        sys.exit(1)

def check_virtual_environment():
    """Check if virtual environment exists"""
    venv_path = Path("venv")
    if not venv_path.exists():
        print("Virtual environment not found. Creating one...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("Virtual environment created successfully!")
        return False
    return True

def install_dependencies():
    """Install backend dependencies"""
    print("Installing backend dependencies...")
    
    # Determine pip executable
    if os.name == 'nt':  # Windows
        pip_path = "venv/Scripts/pip"
        python_path = "venv/Scripts/python"
    else:  # Unix/Linux/Mac
        pip_path = "venv/bin/pip"
        python_path = "venv/bin/python"
    
    try:
        subprocess.run([pip_path, "install", "-r", "backend/requirements.txt"], check=True)
        print("Dependencies installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        sys.exit(1)

def setup_environment():
    """Setup environment configuration"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        print("Creating .env file from .env.example...")
        import shutil
        shutil.copy(env_example, env_file)
        print("⚠️  Please edit .env file with your API keys before running the application")
        return False
    
    return True

def run_server():
    """Run the FastAPI server"""
    print("Starting Forex Strategist backend server...")
    print("Server will be available at: http://localhost:8000")
    print("API documentation: http://localhost:8000/docs")
    print("Press Ctrl+C to stop the server")
    
    # Determine python executable
    if os.name == 'nt':  # Windows
        python_path = "venv/Scripts/python"
    else:  # Unix/Linux/Mac
        python_path = "venv/bin/python"
    
    try:
        subprocess.run([
            python_path, "-m", "uvicorn", 
            "backend.app.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ], check=True)
    except KeyboardInterrupt:
        print("\nShutting down server...")
    except subprocess.CalledProcessError as e:
        print(f"Error running server: {e}")
        sys.exit(1)

def main():
    """Main function"""
    print("🚀 Forex Strategist Backend Setup")
    print("=" * 40)
    
    # Check Python version
    check_python_version()
    
    # Check/create virtual environment
    venv_exists = check_virtual_environment()
    
    # Install dependencies
    if not venv_exists or "--install" in sys.argv:
        install_dependencies()
    
    # Setup environment
    env_ready = setup_environment()
    
    if not env_ready:
        print("\n⚠️  Please configure your .env file with API keys and run again")
        return
    
    # Run server
    run_server()

if __name__ == "__main__":
    main()