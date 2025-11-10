#!/usr/bin/env python3
"""
Run script for the Vagueness Detection System
Starts the Streamlit application
"""

import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'streamlit',
        'google.generativeai',
        'chromadb',
        'sentence_transformers',
        'pdfplumber'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nPlease install dependencies:")
        print("   pip install -r requirements.txt")
        return False
    
    return True

def check_env_file():
    """Check if .env file exists"""
    env_file = Path(__file__).parent / '.env'
    
    if not env_file.exists():
        print("⚠️  Warning: .env file not found")
        print("   You can either:")
        print("   1. Create a .env file with your GEMINI_API_KEY")
        print("   2. Enter the API key directly in the application")
        print()
        
        response = input("Continue anyway? (y/n): ")
        return response.lower() == 'y'
    
    return True

def create_directories():
    """Create necessary directories"""
    directories = [
        'data/raw_docs',
        'data/reference_docs',
        'data/embeddings',
        'outputs',
        'outputs/reports'
    ]
    
    base_path = Path(__file__).parent
    
    for directory in directories:
        dir_path = base_path / directory
        dir_path.mkdir(parents=True, exist_ok=True)
    
    print("✓ Directory structure verified")

def run_streamlit():
    """Run the Streamlit application"""
    app_path = Path(__file__).parent / 'src' / 'app' / 'streamlit_frontend.py'
    
    if not app_path.exists():
        print(f"❌ Error: Application file not found at {app_path}")
        return False
    
    print("\n" + "="*60)
    print("🚀 Starting Vagueness Detection System")
    print("="*60)
    print("\nThe application will open in your default browser")
    print("Press Ctrl+C to stop the server\n")
    
    try:
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run',
            str(app_path),
            '--server.headless', 'false'
        ])
    except KeyboardInterrupt:
        print("\n\n✓ Application stopped")
        return True
    except Exception as e:
        print(f"\n❌ Error running application: {str(e)}")
        return False
    
    return True

def main():
    """Main function"""
    print("="*60)
    print("MTP Version 2 - Vagueness Detection System")
    print("="*60)
    print()
    
    # Check dependencies
    print("Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    print("✓ All dependencies installed")
    
    # Check .env file
    if not check_env_file():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Run application
    success = run_streamlit()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
