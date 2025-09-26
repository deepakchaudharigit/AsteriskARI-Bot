#!/usr/bin/env python3

import asyncio
import websockets
import json
from urllib.parse import urlencode
import signal
import sys

class PersistentStasisClient:
    def __init__(self):
        self.app_name = "openai-voice-assistant"
        self.username = "asterisk"
        self.password = "1234"
        self.running = True
        self.websocket = None
    
    async def connect_and_listen(self):
        """Connect to ARI WebSocket and keep listening"""
        
        ws_url = f"ws://{self.username}:{self.password}@localhost:8088/asterisk/ari/events?{urlencode({'app': self.app_name})}"
        
        print(f"🔌 Connecting to: ws://localhost:8088/asterisk/ari/events")
        print(f"📱 Registering Stasis app: {self.app_name}")
        
        try:
            async with websockets.connect(ws_url) as websocket:
                self.websocket = websocket
                print("✅ Connected to ARI WebSocket")
                print(f"🎯 Stasis application '{self.app_name}' is now registered")
                print("\\n📋 Application is ready to receive calls!")
                print("\\n🧪 Test Instructions:")
                print("1. Configure Zoiper with:")
                print("   - Username: 1000")
                print("   - Password: 1234") 
                print("   - Domain: 192.168.0.212")
                print("2. Dial 1000 to test the voice assistant")
                print("3. Dial 1010 to test basic extension")
                print("\\n📡 Listening for ARI events...")
                print("Press Ctrl+C to stop")
                print("-" * 50)
                
                while self.running:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                        event = json.loads(message)
                        
                        event_type = event.get("type", "Unknown")
                        
                        if event_type == "StasisStart":
                            channel = event.get("channel", {})
                            channel_id = channel.get("id", "Unknown")
                            caller_id = channel.get("caller", {}).get("number", "Unknown")
                            print(f"📞 CALL START: Channel {channel_id} from {caller_id}")
                            
                        elif event_type == "StasisEnd":
                            channel = event.get("channel", {})
                            channel_id = channel.get("id", "Unknown")
                            print(f"📴 CALL END: Channel {channel_id}")
                            
                        elif event_type == "ChannelStateChange":
                            channel = event.get("channel", {})
                            channel_id = channel.get("id", "Unknown")
                            state = channel.get("state", "Unknown")
                            print(f"📡 CHANNEL STATE: {channel_id} -> {state}")
                            
                        else:
                            print(f"📡 Event: {event_type}")
                        
                    except asyncio.TimeoutError:
                        # Timeout is normal, continue listening
                        continue
                    except websockets.exceptions.ConnectionClosed:
                        print("🔌 WebSocket connection closed")
                        break
                        
        except Exception as e:
            print(f"❌ Failed to connect: {e}")
            return False
        
        return True
    
    def stop(self):
        """Stop the client"""
        self.running = False
        print("\\n🛑 Stopping Stasis client...")

async def main():
    """Main function"""
    client = PersistentStasisClient()
    
    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        client.stop()
    
    signal.signal(signal.SIGINT, signal_handler)
    
    await client.connect_and_listen()

if __name__ == "__main__":
    asyncio.run(main())