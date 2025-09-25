#!/usr/bin/env python3
"""
Simple launcher for the Real-time Voice Chatbot
"""

import os
import sys
import subprocess
from pathlib import Path

def check_env_file():
    """Check if .env file exists and has API key."""
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found!")
        print("Run: python setup.py")
        return False
    
    content = env_file.read_text()
    if "your_openai_api_key_here" in content:
        print("❌ Please add your OpenAI API key to the .env file")
        print("Edit .env and replace 'your_openai_api_key_here' with your actual API key")
        return False
    
    return True

def main():
    """Main launcher function."""
    print("🚀 Real-time Voice Chatbot Launcher")
    print("=" * 40)
    
    # Check if setup is complete
    if not check_env_file():
        return
    
    # Check if dependencies are installed
    try:
        import openai
        import pyaudio
        import speech_recognition
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("Run: python setup.py")
        return
    
    print("✅ Environment check passed!")
    print("🎙️ Starting voice chatbot...\n")
    
    # Run the main chatbot
    try:
        subprocess.run([sys.executable, "voice_chatbot.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Chatbot stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Chatbot failed to start: {e}")

if __name__ == "__main__":
    main()