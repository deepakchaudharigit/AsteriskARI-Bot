#!/usr/bin/env python3
"""
NPCL Voice Assistant Startup Script
Handles proper initialization and error checking
"""

import sys
import os
import asyncio
import logging
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Suppress warnings
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

def print_banner():
    """Print startup banner"""
    print("=" * 80)
    print("🚀 NPCL Asterisk ARI Voice Assistant - Enhanced Edition")
    print("🎯 100% Compliant Bridge/Snoop Pattern Implementation")
    print("🔗 Production-Ready Telephony Integration")
    print("=" * 80)

def check_openai_api_key():
    """Check OpenAI API key"""
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("❌ OpenAI API Key Missing!")
        print("📝 Please add your OpenAI API key to .env file:")
        print("   OPENAI_API_KEY=your_actual_api_key_here")
        print("🔗 Get your API key from: https://platform.openai.com/api-keys")
        return False
    
    if api_key.startswith('sk-proj-') and len(api_key) > 50:
        # Basic format check
        print("✅ OpenAI API Key: Format looks correct")
        return True
    else:
        print("⚠️  OpenAI API Key: Format may be incorrect")
        print("📝 Expected format: sk-proj-...")
        print("🔗 Get your API key from: https://platform.openai.com/api-keys")
        return False

def check_dependencies():
    """Check required dependencies"""
    print("\\n🔍 Checking Dependencies:")
    
    required_packages = [
        ('openai', 'OpenAI API client'),
        ('fastapi', 'FastAPI web framework'),
        ('uvicorn', 'ASGI server'),
        ('websockets', 'WebSocket support'),
        ('requests', 'HTTP requests'),
        ('pydantic', 'Data validation'),
        ('aiohttp', 'Async HTTP client'),
        ('numpy', 'Audio processing')
    ]
    
    missing_packages = []
    
    for package, description in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}: Available")
        except ImportError:
            print(f"❌ {package}: Missing ({description})")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\\n📦 Missing packages: {', '.join(missing_packages)}")
        print("💡 Install with: pip install -r requirements.txt")
        return False
    
    return True

def check_asterisk_connection():
    """Check Asterisk ARI connection"""
    print("\\n📞 Checking Asterisk ARI Connection:")
    
    try:
        import requests
        
        # Test ARI endpoint
        response = requests.get(
            "http://localhost:8088/ari/asterisk/info", 
            auth=("asterisk", "1234"), 
            timeout=5
        )
        
        if response.status_code == 200:
            print("✅ Asterisk ARI: Connected and responding")
            return True
        elif response.status_code == 401:
            print("⚠️  Asterisk ARI: Authentication failed")
            print("📝 Check ARI credentials in asterisk-config/ari.conf")
            return False
        else:
            print(f"⚠️  Asterisk ARI: Unexpected response ({response.status_code})")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Asterisk ARI: Connection failed")
        print("📝 Make sure Asterisk is running: sudo systemctl status asterisk")
        print("📝 Check HTTP server: asterisk-config/http.conf")
        return False
    except Exception as e:
        print(f"❌ Asterisk ARI: Error - {e}")
        return False

async def start_enhanced_server():
    """Start the enhanced voice assistant server"""
    try:
        print("\\n🚀 Starting Enhanced Voice Assistant Server...")
        
        # Import the enhanced server
        from run_realtime_server import create_app
        import uvicorn
        
        # Create the app
        app = create_app()
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Start server
        config = uvicorn.Config(
            app=app,
            host="0.0.0.0",
            port=8000,
            log_level="info",
            access_log=True
        )
        
        server = uvicorn.Server(config)
        
        print("✅ Enhanced Voice Assistant Server starting...")
        print("🌐 Server URL: http://localhost:8000")
        print("📚 API Docs: http://localhost:8000/docs")
        print("🏥 Health Check: http://localhost:8000/health")
        print("📊 ARI Status: http://localhost:8000/ari/status")
        print("\\n🎯 Ready for calls on extension 1000!")
        print("📞 Test with Zoiper: Username=1000, Password=1234, Server=localhost")
        print("\\n🔄 Enhanced Call Flow Active:")
        print("   Zoiper → Asterisk → Bridge → Snoop → ExternalMedia → OpenAI → Weather Tool")
        print("\\n⏹️  Press Ctrl+C to stop")
        
        await server.serve()
        
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return False

def main():
    """Main entry point"""
    print_banner()
    
    # Check OpenAI API key
    if not check_openai_api_key():
        print("\\n🛑 Cannot start without valid OpenAI API key")
        return 1
    
    # Check dependencies
    if not check_dependencies():
        print("\\n🛑 Cannot start with missing dependencies")
        return 1
    
    # Check Asterisk (optional - will warn but continue)
    asterisk_ok = check_asterisk_connection()
    if not asterisk_ok:
        print("\\n⚠️  Asterisk issues detected - server will start but calls may not work")
        print("💡 Fix Asterisk issues for full functionality")
    
    # Start server
    try:
        print("\\n" + "=" * 80)
        print("🎯 All Checks Complete - Starting Enhanced Voice Assistant")
        print("=" * 80)
        
        asyncio.run(start_enhanced_server())
        
    except KeyboardInterrupt:
        print("\\n\\n👋 Voice Assistant stopped by user")
        return 0
    except Exception as e:
        print(f"\\n❌ Voice Assistant failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())