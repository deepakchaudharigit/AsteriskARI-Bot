
import asyncio
import websockets
import json
import base64
import logging
from urllib.parse import urlencode

logger = logging.getLogger(__name__)

class ARIWebSocketClient:
    """ARI WebSocket client for Stasis application registration"""
    
    def __init__(self, ari_url="ws://localhost:8088", username="asterisk", password="1234", app="openai-voice-assistant"):
        self.ari_url = ari_url
        self.username = username
        self.password = password
        self.app = app
        self.websocket = None
        self.running = False
    
    async def connect(self):
        """Connect to ARI WebSocket and register Stasis application"""
        try:
            # Create WebSocket URL with authentication and app subscription
            auth_string = f"{self.username}:{self.password}"
            auth_encoded = base64.b64encode(auth_string.encode()).decode()
            
            # ARI WebSocket endpoint with app subscription
            ws_url = f"{self.ari_url}/ari/events?{urlencode({'app': self.app})}"
            
            headers = {
                "Authorization": f"Basic {auth_encoded}"
            }
            
            print(f"🔌 Connecting to ARI WebSocket: {ws_url}")
            print(f"📱 Subscribing to Stasis app: {self.app}")
            
            self.websocket = await websockets.connect(ws_url, extra_headers=headers)
            self.running = True
            
            print(f"✅ Connected to ARI WebSocket")
            print(f"🎯 Stasis application '{self.app}' should now be registered")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to connect to ARI WebSocket: {e}")
            return False
    
    async def listen_for_events(self):
        """Listen for ARI events"""
        try:
            while self.running and self.websocket:
                try:
                    message = await asyncio.wait_for(self.websocket.recv(), timeout=1.0)
                    event = json.loads(message)
                    
                    # Print important events
                    if event.get("type") == "StasisStart":
                        channel_id = event.get("channel", {}).get("id", "Unknown")
                        print(f"📞 STASIS START: Channel {channel_id} entered Stasis app")
                    elif event.get("type") == "StasisEnd":
                        channel_id = event.get("channel", {}).get("id", "Unknown")
                        print(f"📴 STASIS END: Channel {channel_id} left Stasis app")
                    
                except asyncio.TimeoutError:
                    # Timeout is normal, continue listening
                    continue
                except websockets.exceptions.ConnectionClosed:
                    print("🔌 WebSocket connection closed")
                    break
                    
        except Exception as e:
            print(f"❌ Error listening for events: {e}")
    
    async def disconnect(self):
        """Disconnect from ARI WebSocket"""
        self.running = False
        if self.websocket:
            await self.websocket.close()
            print("🔌 Disconnected from ARI WebSocket")

async def main():
    """Main function to test ARI WebSocket connection"""
    client = ARIWebSocketClient()
    
    if await client.connect():
        print("\n🎯 Testing Stasis registration...")
        print("Run this command in another terminal:")
        print("sudo asterisk -rx 'ari show apps'")
        print("You should now see: openai-voice-assistant")
        print("\n📞 Test by dialing 1000 in Zoiper")
        print("\nPress Ctrl+C to stop...")
        
        try:
            await client.listen_for_events()
        except KeyboardInterrupt:
            print("\n🛑 Stopping ARI WebSocket client...")
        finally:
            await client.disconnect()
    else:
        print("❌ Failed to connect to ARI WebSocket")

if __name__ == "__main__":
    asyncio.run(main())
