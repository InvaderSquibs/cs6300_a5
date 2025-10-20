#!/usr/bin/env python3
"""
Deployment and environment setup script for Vector Template.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\\n{description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        if result.stdout:
            print(f"Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"Stdout: {e.stdout}")
        if e.stderr:
            print(f"Stderr: {e.stderr}")
        return False

def install_dependencies():
    """Install project dependencies."""
    print("="*60)
    print("INSTALLING DEPENDENCIES")
    print("="*60)
    
    # Try to install core dependencies
    commands = [
        ("pip install --upgrade pip", "Upgrading pip"),
        ("pip install fastapi uvicorn", "Installing FastAPI and Uvicorn"),
        ("pip install pandas numpy", "Installing data processing libraries"),
        ("pip install pydantic httpx python-multipart", "Installing utility libraries"),
    ]
    
    success_count = 0
    for cmd, desc in commands:
        if run_command(cmd, desc):
            success_count += 1
    
    # Try to install optional dependencies
    optional_commands = [
        ("pip install chromadb", "Installing ChromaDB (may take time)"),
        ("pip install smolagents", "Installing Smolagents"),
        ("pip install sentence-transformers", "Installing Sentence Transformers"),
    ]
    
    print("\\nInstalling optional dependencies:")
    for cmd, desc in optional_commands:
        run_command(cmd, desc)
    
    return success_count == len(commands)

def setup_environment():
    """Set up the development environment."""
    print("\\n" + "="*60)
    print("SETTING UP ENVIRONMENT")
    print("="*60)
    
    # Create data directories
    directories = ["data", "chroma_db", "logs"]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created directory: {directory}")
    
    # Install in development mode
    run_command("pip install -e .", "Installing package in development mode")
    
    return True

def run_tests():
    """Run project tests."""
    print("\\n" + "="*60)
    print("RUNNING TESTS")
    print("="*60)
    
    # Run structure test
    run_command("python test_structure.py", "Running structure tests")
    
    # Try to run pytest if available
    run_command("python -m pytest tests/ -v", "Running unit tests")
    
    return True

def start_demo():
    """Start the demo."""
    print("\\n" + "="*60)
    print("RUNNING DEMO")
    print("="*60)
    
    run_command("python demo.py", "Running comprehensive demo")
    
    return True

def main():
    """Main deployment function."""
    print("="*80)
    print("VECTOR TEMPLATE DEPLOYMENT SCRIPT")
    print("="*80)
    print("This script will set up the Vector Template environment.")
    print("It may take several minutes to complete.")
    
    response = input("\\nContinue with installation? (y/N): ")
    if response.lower() != 'y':
        print("Installation cancelled.")
        return
    
    steps = [
        ("Install Dependencies", install_dependencies),
        ("Setup Environment", setup_environment),
        ("Run Tests", run_tests),
        ("Start Demo", start_demo),
    ]
    
    completed_steps = 0
    for step_name, step_func in steps:
        print(f"\\n{'='*20} {step_name} {'='*20}")
        try:
            if step_func():
                completed_steps += 1
                print(f"✓ {step_name} completed")
            else:
                print(f"⚠️ {step_name} completed with warnings")
        except Exception as e:
            print(f"❌ {step_name} failed: {e}")
    
    print("\\n" + "="*80)
    print("DEPLOYMENT SUMMARY")
    print("="*80)
    print(f"Completed {completed_steps}/{len(steps)} steps")
    
    if completed_steps >= 2:  # At least dependencies and environment
        print("\\n🎉 Vector Template is ready to use!")
        print("\\nNext steps:")
        print("1. Try the CLI: python cli.py example")
        print("2. Start the API server: python cli.py serve")
        print("3. Interactive mode: python cli.py interactive")
        print("4. View documentation: python demo.py")
    else:
        print("\\n⚠️ Setup incomplete. Some features may not work.")
        print("Check the error messages above and try running manually:")
        print("pip install -r requirements.txt")

if __name__ == "__main__":
    main()