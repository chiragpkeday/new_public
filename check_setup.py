#!/usr/bin/env python3
"""
Setup verification script for ISEC Contract Note Extractor Streamlit App
Checks if all dependencies and files are properly configured.
"""

import sys
import os
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.8 or higher."""
    print("Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Need 3.8 or higher")
        return False

def check_dependencies():
    """Check if all required packages are installed."""
    print("\nChecking dependencies...")
    required_packages = [
        'streamlit',
        'openai',
        'pypdf',
        'dotenv'
    ]
    
    all_installed = True
    for package in required_packages:
        try:
            if package == 'dotenv':
                __import__('dotenv')
            else:
                __import__(package)
            print(f"✅ {package} - Installed")
        except ImportError:
            print(f"❌ {package} - Not installed")
            all_installed = False
    
    return all_installed

def check_files():
    """Check if all required files exist."""
    print("\nChecking required files...")
    required_files = [
        'app.py',
        'config.json',
        'system_prompt.md',
        'minimal_system_prompt.md',
        'compact_schema.json',
        'chirag_both.json',
        'requirements.txt'
    ]
    
    all_exist = True
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file} - Found")
        else:
            print(f"❌ {file} - Missing")
            all_exist = False
    
    return all_exist

def check_env_file():
    """Check if .env file exists and has API key."""
    print("\nChecking environment configuration...")
    
    env_exists = Path('.env').exists()
    if env_exists:
        print("✅ .env file - Found")
        
        # Try to load and check for API key
        try:
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                print(f"✅ OPENAI_API_KEY - Set (length: {len(api_key)} chars)")
                return True
            else:
                print("⚠️  OPENAI_API_KEY - Not set in .env file")
                return False
        except Exception as e:
            print(f"⚠️  Error loading .env: {e}")
            return False
    else:
        print("⚠️  .env file - Not found")
        print("   Create a .env file with: OPENAI_API_KEY=your_key_here")
        
        # Check if API key is set in environment
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            print(f"✅ OPENAI_API_KEY - Set in environment (length: {len(api_key)} chars)")
            return True
        else:
            print("❌ OPENAI_API_KEY - Not set in environment")
            return False

def check_streamlit():
    """Check if Streamlit can be run."""
    print("\nChecking Streamlit installation...")
    try:
        import streamlit as st
        print(f"✅ Streamlit version: {st.__version__}")
        return True
    except ImportError:
        print("❌ Streamlit not installed")
        return False

def main():
    """Run all checks."""
    print("=" * 60)
    print("ISEC Contract Note Extractor - Setup Verification")
    print("=" * 60)
    
    checks = {
        "Python Version": check_python_version(),
        "Dependencies": check_dependencies(),
        "Required Files": check_files(),
        "Environment Config": check_env_file(),
        "Streamlit": check_streamlit()
    }
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for check_name, passed in checks.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{check_name:.<40} {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n🎉 All checks passed! You're ready to run the app.")
        print("\nTo start the application, run:")
        print("  streamlit run app.py")
        print("\nOr use the convenience scripts:")
        print("  Windows: run_app.bat")
        print("  Linux/Mac: ./run_app.sh")
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        print("\nTo install missing dependencies:")
        print("  pip install -r requirements.txt")
        print("\nTo set up API key:")
        print("  Create a .env file with: OPENAI_API_KEY=your_key_here")
    
    print()
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())

