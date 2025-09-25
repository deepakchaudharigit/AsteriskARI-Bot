#!/usr/bin/env python3
"""
Quick start script for NPCL Voice Assistant with OpenAI Real-time API
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    try:
        import pydantic_settings
        import openai
        import websockets
        import fastapi
        print("✅ Core dependencies found")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("")
        print("🔧 Please set up the virtual environment first:")
        print("   ./setup_environment.sh")
        print("   source .venv/bin/activate")
        print("   python3 start_openai_assistant.py")
        print("")
        return False

def start_server():
    """Start the OpenAI Real-time server"""
    print("\n🚀 Starting NPCL Voice Assistant with OpenAI Real-time API...")
    print("=" * 60)
    
    # Check if .env file exists
    if not Path('.env').exists():
        print("❌ .env file not found!")
        print("📝 Please copy .env.example to .env and configure your API keys")
        return False
    
    # Check dependencies
    if not check_dependencies():
        return False
    
    # Start the server
    try:
        print("\n🌟 Features enabled:")
        print("   🎙️ Voice Interruption")
        print("   🔇 Noise Cancellation") 
        print("   🤖 OpenAI Real-time API")
        print("   📞 Asterisk ARI Integration")
        print("\n📡 Starting server on http://localhost:8000")
        print("📚 API Documentation: http://localhost:8000/docs")
        print("🔍 System Status: http://localhost:8000/status")
        print("\n⚠️  Press Ctrl+C to stop the server")
        print("=" * 60)
        
        # Run the server
        subprocess.run([sys.executable, "src/run_realtime_server.py"])
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False
    
    return True

def main():
    """Main entry point"""
    print("🎯 NPCL Voice Assistant - OpenAI Real-time API")
    print("=" * 60)
    
    # Verify we're in the right directory
    if not Path('src/run_realtime_server.py').exists():
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Start the server
    if not start_server():
        sys.exit(1)

if __name__ == "__main__":
    main()