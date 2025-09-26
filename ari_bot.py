#!/usr/bin/env python3
"""
NPCL Asterisk ARI Bot - Direct Entry Point
Starts the Asterisk ARI server for telephony integration with enhanced OpenAI TTS
"""

import sys
import os
import asyncio
import logging
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Don't hardcode API key - use .env file instead

# Suppress warnings
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

def print_banner():
    """Print ARI bot banner"""
    print("=" * 70)
    print("📞 NPCL Asterisk ARI Voice Assistant Bot")
    print("🎤 Enhanced OpenAI TTS with Whisper Speech Recognition")
    print("🔗 Asterisk PBX Integration")
    print("=" * 70)

def check_dependencies():
    """Check required dependencies"""
    print("🔍 Checking Dependencies:")
    
    # Check OpenAI
    try:
        import openai
        print(f"✅ OpenAI: v{openai.__version__}")
    except ImportError:
        print("❌ OpenAI: Not installed")
        print("💡 Install with: pip install openai")
        return False
    
    # Check Enhanced TTS
    try:
        from voice_assistant.audio.enhanced_tts import EnhancedTTS
        print("✅ Enhanced TTS: Available")
    except ImportError:
        print("❌ Enhanced TTS: Not available")
        print("💡 Install with: pip install pygame")
        return False
    
    # Check FastAPI
    try:
        import fastapi
        print(f"✅ FastAPI: Available")
    except ImportError:
        print("❌ FastAPI: Not installed")
        print("💡 Install with: pip install fastapi uvicorn")
        return False
    
    # Check Asterisk connectivity
    try:
        import requests
        response = requests.get("http://localhost:8088/ari/asterisk/info", 
                              auth=("asterisk", "1234"), timeout=5)
        if response.status_code == 200:
            print("✅ Asterisk ARI: Connected")
        else:
            print("⚠️  Asterisk ARI: Not responding")
    except Exception:
        print("⚠️  Asterisk ARI: Not available (will start anyway)")
    
    return True

def setup_enhanced_voice():
    """Setup enhanced voice system"""
    print("\n🎤 Setting up Enhanced Voice System:")
    
    try:
        from voice_assistant.audio.enhanced_tts import EnhancedTTS
        
        # Initialize enhanced TTS
        tts = EnhancedTTS()
        
        # Test voice
        print("🔊 Testing Enhanced TTS...")
        success = tts.speak_text_enhanced(
            "NPCL Asterisk ARI Bot is ready with enhanced voice quality!", 
            voice="fable"  # Use warm, customer-friendly voice
        )
        
        if success:
            print("✅ Enhanced TTS: Working perfectly")
            print(f"🎵 Voice: {tts.voice_model} ({tts.available_voices[tts.voice_model]})")
            print(f"🎛️  Model: {tts.tts_model}")
        else:
            print("❌ Enhanced TTS: Failed")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Enhanced TTS setup failed: {e}")
        return False

async def start_ari_server():
    """Start the Asterisk ARI server"""
    try:
        print("\n🚀 Starting Asterisk ARI Server...")
        
        # Import the ARI server factory
        from run_realtime_server import create_app
        import uvicorn
        
        # Create the app instance
        app = create_app()
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger("ari_bot")
        
        logger.info("NPCL ARI Bot starting...")
        logger.info("Enhanced OpenAI TTS enabled")
        logger.info("Whisper speech recognition enabled")
        
        # Start the server
        config = uvicorn.Config(
            app=app,
            host="0.0.0.0",
            port=8000,
            log_level="info",
            access_log=True
        )
        
        server = uvicorn.Server(config)
        
        print("✅ ARI Server starting on http://localhost:8000")
        print("📞 Ready to handle Asterisk calls")
        print("🎤 Enhanced voice quality enabled")
        print("\n📋 Available Endpoints:")
        print("  • http://localhost:8000/docs - API Documentation")
        print("  • http://localhost:8000/health - Health Check")
        print("  • http://localhost:8000/ari/health - ARI Health")
        print("  • http://localhost:8000/ari/status - ARI Status")
        print("\n🔗 Asterisk Configuration:")
        print("  • Extension: 1000")
        print("  • Stasis App: openai-voice-assistant")
        print("  • ARI Endpoint: http://localhost:8088/ari")
        
        await server.serve()
        
    except Exception as e:
        print(f"❌ Failed to start ARI server: {e}")
        return False

def main():
    """Main entry point for ARI bot"""
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Dependency check failed!")
        print("Please install missing dependencies and try again.")
        return 1
    
    # Setup enhanced voice
    if not setup_enhanced_voice():
        print("\n⚠️  Enhanced voice setup failed, continuing with basic voice...")
    
    # Start ARI server
    try:
        print("\n" + "=" * 70)
        print("🎯 NPCL ARI Bot - Ready for Asterisk Integration")
        print("=" * 70)
        
        # Run the async server
        asyncio.run(start_ari_server())
        
    except KeyboardInterrupt:
        print("\n👋 ARI Bot stopped by user")
        return 0
    except Exception as e:
        print(f"\n❌ ARI Bot failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())