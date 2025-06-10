#!/usr/bin/env python3
"""
Forex Strategist Frontend Runner
"""
import os
import sys
import subprocess
from pathlib import Path

def check_node_installed():
    """Check if Node.js is installed"""
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Node.js version: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    
    print("Error: Node.js is not installed or not in PATH")
    print("Please install Node.js from https://nodejs.org/")
    return False

def check_npm_installed():
    """Check if npm is installed"""
    try:
        result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"npm version: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    
    print("Error: npm is not installed or not in PATH")
    return False

def install_dependencies():
    """Install frontend dependencies"""
    print("Installing frontend dependencies...")
    frontend_path = Path("frontend")
    
    try:
        subprocess.run(["npm", "install"], cwd=frontend_path, check=True)
        print("Dependencies installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        sys.exit(1)

def check_dependencies():
    """Check if node_modules exists"""
    node_modules = Path("frontend/node_modules")
    return node_modules.exists()

def run_development_server():
    """Run the React development server"""
    print("Starting Forex Strategist frontend development server...")
    print("Frontend will be available at: http://localhost:3000")
    print("Press Ctrl+C to stop the server")
    
    frontend_path = Path("frontend")
    
    try:
        subprocess.run(["npm", "start"], cwd=frontend_path, check=True)
    except KeyboardInterrupt:
        print("\nShutting down development server...")
    except subprocess.CalledProcessError as e:
        print(f"Error running development server: {e}")
        sys.exit(1)

def build_production():
    """Build production version"""
    print("Building production version...")
    frontend_path = Path("frontend")
    
    try:
        subprocess.run(["npm", "run", "build"], cwd=frontend_path, check=True)
        print("Production build completed successfully!")
        print("Build files are in frontend/build/")
    except subprocess.CalledProcessError as e:
        print(f"Error building production version: {e}")
        sys.exit(1)

def main():
    """Main function"""
    print("🎨 Forex Strategist Frontend Setup")
    print("=" * 40)
    
    # Check if Node.js and npm are installed
    if not check_node_installed() or not check_npm_installed():
        sys.exit(1)
    
    # Check if dependencies are installed
    if not check_dependencies() or "--install" in sys.argv:
        install_dependencies()
    
    # Determine action
    if "--build" in sys.argv:
        build_production()
    else:
        run_development_server()

if __name__ == "__main__":
    main()