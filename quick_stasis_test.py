#!/usr/bin/env python3
"""
Quick Stasis Registration Test
"""

import asyncio
import sys
import os

# Add virtual environment to path
venv_path = '/home/ameen/AsteriskARI-Bot/.venv/lib/python3.12/site-packages'
if venv_path not in sys.path:
    sys.path.insert(0, venv_path)

try:
    import websockets
    print("✅ websockets library available")
except ImportError:
    print("❌ websockets library not available")
    sys.exit(1)

import json
import base64
from urllib.parse import urlencode

async def quick_connect_test():
    """Quick connection test"""
    try:
        print("🔌 Testing WebSocket connection...")
        
        # Simple connection with api_key
        ws_url = "ws://localhost:8088/ari/events?app=openai-voice-assistant&api_key=asterisk:1234"
        
        print(f"📡 Connecting to: {ws_url}")
        
        # Connect with 5 second timeout
        websocket = await asyncio.wait_for(
            websockets.connect(ws_url),
            timeout=5.0
        )
        
        print("✅ WebSocket connected successfully!")
        print("🎯 Stasis app should now be registered")
        
        # Listen for one event or timeout
        try:
            message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
            event = json.loads(message)
            print(f"📨 Received event: {event.get('type', 'Unknown')}")
        except asyncio.TimeoutError:
            print("⏳ No immediate events (normal)")
        
        await websocket.close()
        print("🔌 Connection closed")
        return True
        
    except asyncio.TimeoutError:
        print("❌ Connection timeout")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

async def check_registration():
    """Check if Stasis app is registered"""
    import subprocess
    
    try:
        print("\\n🔍 Checking Stasis registration...")
        
        # Run asterisk command
        result = subprocess.run(
            ["sudo", "asterisk", "-rx", "ari show apps"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            output = result.stdout.strip()
            print(f"📋 ARI apps output:")
            print(output)
            
            if "openai-voice-assistant" in output:
                print("\\n✅ SUCCESS! Stasis app is registered!")
                return True
            else:
                print("\\n❌ Stasis app not found in output")
                return False
        else:
            print(f"❌ Command failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking registration: {e}")
        return False

async def main():
    """Main test"""
    print("🚀 QUICK STASIS REGISTRATION TEST")
    print("=" * 40)
    
    # Test WebSocket connection
    if await quick_connect_test():
        # Wait a moment for registration
        await asyncio.sleep(1)
        
        # Check registration
        if await check_registration():
            print("\\n🎉 COMPLETE SUCCESS!")
            print("📞 Try dialing 1000 in Zoiper")
            print("🎯 Voice assistant should now work!")
        else:
            print("\\n⚠️ Connection worked but registration unclear")
            print("💡 Try running: sudo asterisk -rx 'ari show apps'")
    else:
        print("\\n❌ WebSocket connection failed")
        print("💡 Check Asterisk and ARI configuration")

if __name__ == "__main__":
    asyncio.run(main())