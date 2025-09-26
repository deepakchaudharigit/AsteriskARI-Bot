#!/usr/bin/env python3

import asyncio
import websockets
import json
from urllib.parse import urlencode

async def register_stasis_app():
    """Simple function to register Stasis application"""
    
    app_name = "openai-voice-assistant"
    username = "asterisk"
    password = "1234"
    
    # WebSocket URL with basic auth
    ws_url = f"ws://{username}:{password}@localhost:8088/asterisk/ari/events?{urlencode({'app': app_name})}"
    
    print(f"🔌 Connecting to: {ws_url}")
    print(f"📱 Registering Stasis app: {app_name}")
    
    try:
        async with websockets.connect(ws_url) as websocket:
            print("✅ Connected to ARI WebSocket")
            print(f"🎯 Stasis application '{app_name}' should now be registered")
            
            # Keep connection alive for a few seconds to ensure registration
            print("⏳ Keeping connection alive for 5 seconds...")
            await asyncio.sleep(5)
            
            print("✅ Registration complete")
            return True
            
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return False

async def main():
    """Main function"""
    success = await register_stasis_app()
    
    if success:
        print("\\n🎯 Testing registration...")
        print("Run this command to verify:")
        print("curl -s http://localhost:8088/asterisk/ari/applications -u asterisk:1234")
    else:
        print("❌ Registration failed")

if __name__ == "__main__":
    asyncio.run(main())