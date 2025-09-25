#!/usr/bin/env python3
"""
System Status Check for NPCL Voice Assistant with OpenAI Real-time API
"""

import sys
import os
from pathlib import Path

def check_system_status():
    """Check the complete system status"""
    print("🔍 NPCL Voice Assistant - System Status Check")
    print("=" * 50)
    
    status_ok = True
    
    # Check virtual environment
    if 'VIRTUAL_ENV' in os.environ:
        venv_path = os.environ['VIRTUAL_ENV']
        print(f"✅ Virtual Environment: {venv_path}")
    else:
        print("❌ Virtual Environment: Not activated")
        print("   Run: source .venv/bin/activate")
        status_ok = False
    
    # Check .env file
    env_file = Path('.env')
    if env_file.exists():
        print("✅ Configuration File: .env exists")
        
        # Check key settings
        with open(env_file, 'r') as f:
            content = f.read()
            
        if 'AI_PROVIDER=openai' in content:
            print("✅ AI Provider: OpenAI configured")
        else:
            print("❌ AI Provider: Not set to OpenAI")
            status_ok = False
            
        if 'OPENAI_API_KEY=sk-' in content:
            print("✅ OpenAI API Key: Configured")
        else:
            print("❌ OpenAI API Key: Not configured")
            status_ok = False
            
        if 'ENABLE_VOICE_INTERRUPTION=true' in content:
            print("✅ Voice Interruption: Enabled")
        else:
            print("❌ Voice Interruption: Not enabled")
            status_ok = False
            
    else:
        print("❌ Configuration File: .env not found")
        status_ok = False
    
    # Check key files
    key_files = [
        'src/voice_assistant/ai/openai_realtime_client_enhanced.py',
        'src/voice_assistant/ai/ai_client_factory.py',
        'setup_environment.sh',
        'activate_and_start.sh',
        'test_openai_integration.py'
    ]
    
    print("\n📁 Key Files:")
    for file_path in key_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            status_ok = False
    
    # Check dependencies (if in venv)
    if 'VIRTUAL_ENV' in os.environ:
        print("\n📦 Dependencies:")
        try:
            import pydantic_settings
            print("✅ pydantic_settings")
        except ImportError:
            print("❌ pydantic_settings")
            status_ok = False
            
        try:
            import openai
            print("✅ openai")
        except ImportError:
            print("❌ openai")
            status_ok = False
            
        try:
            import websockets
            print("✅ websockets")
        except ImportError:
            print("❌ websockets")
            status_ok = False
            
        try:
            import fastapi
            print("✅ fastapi")
        except ImportError:
            print("❌ fastapi")
            status_ok = False
    
    # Test AI client creation
    if status_ok and 'VIRTUAL_ENV' in os.environ:
        print("\n🤖 AI Client Test:")
        try:
            sys.path.insert(0, '.')
            from src.voice_assistant.ai.ai_client_factory import create_ai_client, get_current_provider
            
            provider = get_current_provider()
            print(f"✅ Current Provider: {provider}")
            
            client = create_ai_client()
            print(f"✅ AI Client Created: {type(client).__name__}")
            
        except Exception as e:
            print(f"❌ AI Client Creation Failed: {e}")
            status_ok = False
    
    # Final status
    print("\n" + "=" * 50)
    if status_ok:
        print("🎉 System Status: ✅ ALL SYSTEMS READY")
        print("\n🚀 To start your voice assistant:")
        print("   ./activate_and_start.sh")
        print("\n🧪 To test the integration:")
        print("   source .venv/bin/activate")
        print("   python3 test_openai_integration.py")
        print("\n📡 To start the server:")
        print("   source .venv/bin/activate")
        print("   python3 src/run_realtime_server.py")
    else:
        print("❌ System Status: ISSUES DETECTED")
        print("\n🔧 To fix issues:")
        print("   1. Run: ./setup_environment.sh")
        print("   2. Activate: source .venv/bin/activate")
        print("   3. Test: python3 test_openai_integration.py")
    
    print("\n📚 Documentation:")
    print("   • INTEGRATION_COMPLETE.md - Complete status")
    print("   • QUICK_START.md - Setup guide")
    print("   • README_ENHANCED_OPENAI.md - Detailed documentation")
    
    return status_ok

if __name__ == "__main__":
    success = check_system_status()
    sys.exit(0 if success else 1)