#!/usr/bin/env python3
"""
Setup script for the Complete Visual Search Engine
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, cwd=None):
    """Run a command and return the result"""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    print(f"Success: {result.stdout}")
    return True

def main():
    print("🚀 Setting up Complete Visual Search Engine")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("backend").exists():
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    print("\n📦 Installing Python dependencies...")
    python_deps = [
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0", 
        "python-multipart==0.0.6",
        "pydantic==2.5.0",
        "torch==2.1.0",
        "torchvision==0.16.0",
        "pillow==10.1.0",
        "numpy==1.24.3",
        "python-dotenv==1.0.0"
    ]
    
    for dep in python_deps:
        if not run_command(f"pip install {dep}"):
            print(f"❌ Failed to install {dep}")
            sys.exit(1)
    
    print("\n📦 Installing Node.js dependencies...")
    if not run_command("npm install", cwd="frontend"):
        print("❌ Failed to install Node.js dependencies")
        sys.exit(1)
    
    print("\n✅ Setup completed successfully!")
    print("\n🎯 Next steps:")
    print("1. Start the backend: python backend/main_complete.py")
    print("2. Start the frontend: cd frontend && npm start")
    print("3. Open http://localhost:3000 in your browser")
    print("\n📚 API Documentation: http://localhost:8000/docs")

if __name__ == "__main__":
    main()



