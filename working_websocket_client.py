#!/usr/bin/env python3
"""
Working WebSocket Client for Stasis Registration
Uses the virtual environment's websockets library
"""

import asyncio
import websockets
import json
import base64
from urllib.parse import urlencode

class WorkingARIWebSocketClient:
    """Working ARI WebSocket client"""
    
    def __init__(self):
        self.ari_url = "ws://localhost:8088"
        self.username = "asterisk"
        self.password = "1234"
        self.app = "openai-voice-assistant"
        self.websocket = None
        self.running = False
    
    async def connect(self):
        """Connect to ARI WebSocket"""
        try:
            # Method 1: Try with api_key parameter
            ws_url = f"{self.ari_url}/ari/events?{urlencode({'app': self.app, 'api_key': f'{self.username}:{self.password}'})}"
            
            print(f"🔌 Connecting to ARI WebSocket...")
            print(f"📡 URL: {ws_url}")
            print(f"📱 App: {self.app}")
            
            try:
                self.websocket = await websockets.connect(ws_url)
                self.running = True
                print("✅ Connected to ARI WebSocket (Method 1: api_key)")
                return True
            except Exception as e1:
                print(f"⚠️ Method 1 failed: {e1}")
                
                # Method 2: Try with Authorization header
                try:
                    auth_string = base64.b64encode(f"{self.username}:{self.password}".encode()).decode()
                    headers = {"Authorization": f"Basic {auth_string}"}
                    ws_url2 = f"{self.ari_url}/ari/events?{urlencode({'app': self.app})}"
                    
                    print(f"🔌 Trying Method 2 with Authorization header...")
                    print(f"📡 URL: {ws_url2}")
                    
                    # For newer websockets library, use additional_headers
                    self.websocket = await websockets.connect(ws_url2, additional_headers=headers)
                    self.running = True
                    print("✅ Connected to ARI WebSocket (Method 2: Auth header)")
                    return True
                    
                except Exception as e2:
                    print(f"⚠️ Method 2 failed: {e2}")
                    
                    # Method 3: Try basic connection
                    try:
                        ws_url3 = f"{self.ari_url}/ari/events?app={self.app}&api_key={self.username}:{self.password}"
                        print(f"🔌 Trying Method 3 with inline auth...")
                        print(f"📡 URL: {ws_url3}")
                        
                        self.websocket = await websockets.connect(ws_url3)
                        self.running = True
                        print("✅ Connected to ARI WebSocket (Method 3: Inline auth)")
                        return True
                        
                    except Exception as e3:
                        print(f"❌ All connection methods failed:")
                        print(f"   Method 1: {e1}")
                        print(f"   Method 2: {e2}")
                        print(f"   Method 3: {e3}")
                        return False
                        
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    async def listen_for_events(self):
        """Listen for ARI events"""
        try:
            print("👂 Listening for ARI events...")
            event_count = 0
            
            while self.running and self.websocket:
                try:
                    # Wait for message with timeout
                    message = await asyncio.wait_for(self.websocket.recv(), timeout=2.0)
                    event = json.loads(message)
                    event_count += 1
                    
                    event_type = event.get("type", "Unknown")
                    print(f"📨 Event #{event_count}: {event_type}")
                    
                    # Print important events with details
                    if event_type == "StasisStart":
                        channel_id = event.get("channel", {}).get("id", "Unknown")
                        caller = event.get("channel", {}).get("caller", {}).get("number", "Unknown")
                        print(f"📞 STASIS START: Channel {channel_id} from {caller}")
                    elif event_type == "StasisEnd":
                        channel_id = event.get("channel", {}).get("id", "Unknown")
                        print(f"📴 STASIS END: Channel {channel_id}")
                    elif event_type == "ChannelStateChange":
                        channel_id = event.get("channel", {}).get("id", "Unknown")
                        state = event.get("channel", {}).get("state", "Unknown")
                        print(f"🔄 CHANNEL STATE: {channel_id} → {state}")
                    
                except asyncio.TimeoutError:
                    # Timeout is normal, continue listening
                    print("⏳ Waiting for events... (connection alive)")
                    continue
                except websockets.exceptions.ConnectionClosed:
                    print("🔌 WebSocket connection closed")
                    break
                except json.JSONDecodeError:
                    print(f"⚠️ Invalid JSON received: {message}")
                    continue
                    
        except Exception as e:
            print(f"❌ Error listening for events: {e}")
    
    async def disconnect(self):
        """Disconnect from WebSocket"""
        self.running = False
        if self.websocket:
            await self.websocket.close()
            print("🔌 Disconnected from ARI WebSocket")

async def check_stasis_registration():
    """Check if Stasis app is registered"""
    import aiohttp
    
    try:
        async with aiohttp.ClientSession() as session:
            auth = aiohttp.BasicAuth("asterisk", "1234")
            async with session.get("http://localhost:8088/ari/applications", auth=auth) as response:
                if response.status == 200:
                    apps = await response.json()
                    app_names = [app.get('name', '') for app in apps]
                    
                    print(f"📋 Registered applications: {app_names}")
                    
                    if 'openai-voice-assistant' in app_names:
                        print("✅ Stasis app 'openai-voice-assistant' is registered!")
                        return True
                    else:
                        print("❌ Stasis app 'openai-voice-assistant' NOT registered")
                        return False
                else:
                    print(f"❌ Failed to check applications: {response.status}")
                    return False
    except ImportError:
        print("⚠️ aiohttp not available, skipping registration check")
        return None
    except Exception as e:
        print(f"❌ Error checking registration: {e}")
        return False

async def main():
    """Main function"""
    print("🚀 WORKING WEBSOCKET CLIENT FOR STASIS REGISTRATION")
    print("=" * 60)
    
    # Check initial status
    print("🔍 Checking initial Stasis registration...")
    initial_status = await check_stasis_registration()
    
    if initial_status:
        print("\\n✅ Stasis app already registered!")
        print("📞 Try dialing 1000 in Zoiper")
        return
    
    # Create and connect WebSocket client
    client = WorkingARIWebSocketClient()
    
    if await client.connect():
        print("\\n🎯 WebSocket connected! Stasis app should now be registered.")
        print("\\n📋 In another terminal, run:")
        print("sudo asterisk -rx 'ari show apps'")
        print("\\n📞 Test by dialing 1000 in Zoiper")
        print("\\n⏳ Keeping connection alive... Press Ctrl+C to stop")
        
        try:
            await client.listen_for_events()
        except KeyboardInterrupt:
            print("\\n🛑 Stopping WebSocket client...")
        finally:
            await client.disconnect()
            
        # Check final status
        print("\\n🔍 Checking final Stasis registration...")
        final_status = await check_stasis_registration()
        
        if final_status:
            print("🎉 SUCCESS! Stasis app is registered")
        else:
            print("⚠️ Stasis app registration unclear")
            
    else:
        print("\\n❌ Failed to connect to ARI WebSocket")
        print("\\n💡 Troubleshooting:")
        print("1. Check Asterisk: sudo systemctl status asterisk")
        print("2. Check ARI config: sudo cat /etc/asterisk/ari.conf")
        print("3. Check HTTP server: sudo asterisk -rx 'http show status'")

if __name__ == "__main__":
    # Make sure we're using the virtual environment
    import sys
    if '/home/ameen/AsteriskARI-Bot/.venv' not in sys.path:
        print("⚠️ Make sure to activate virtual environment:")
        print("source .venv/bin/activate")
    
    asyncio.run(main())