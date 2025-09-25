#!/usr/bin/env python3
"""
NPCL ARI Bot Startup Script
Simple script to start the Asterisk ARI Voice Assistant Bot
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Start the ARI bot"""
    print("🚀 Starting NPCL Asterisk ARI Voice Assistant Bot...")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("src/main.py").exists():
        print("❌ Error: src/main.py not found")
        print("💡 Please run this script from the project root directory")
        return 1
    
    # Check if virtual environment is available
    venv_python = Path(".venv/bin/python3")
    if venv_python.exists():
        python_cmd = str(venv_python)
        print("✅ Using virtual environment")
    else:
        python_cmd = "python3"
        print("⚠️  Virtual environment not found, using system Python")
    
    # Start the ARI bot
    try:
        print("🎤 Starting Enhanced Voice Assistant...")
        result = subprocess.run([
            python_cmd, "src/main.py", "--ari-bot"
        ])
        return result.returncode
    except KeyboardInterrupt:
        print("\n👋 ARI Bot stopped by user")
        return 0
    except Exception as e:
        print(f"❌ Failed to start ARI bot: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())