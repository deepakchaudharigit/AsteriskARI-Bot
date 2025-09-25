#!/usr/bin/env python3
"""
Fix ARI Registration Issue
Establishes WebSocket connection to Asterisk ARI to register the stasis application
"""

import asyncio
import websockets
import json
import logging
import requests
from urllib.parse import urlencode

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ARIWebSocketClient:
    """WebSocket client to register stasis application with Asterisk ARI"""
    
    def __init__(self, ari_url="ws://localhost:8088/ari/events", username="asterisk", password="1234", app_name="openai-voice-assistant"):
        self.ari_url = ari_url
        self.username = username
        self.password = password
        self.app_name = app_name
        self.websocket = None
        self.running = False
    
    async def connect(self):
        """Connect to Asterisk ARI WebSocket"""
        try:
            # Build WebSocket URL with authentication and app registration
            params = {
                'app': self.app_name,
                'api_key': f"{self.username}:{self.password}"
            }
            ws_url = f"{self.ari_url}?{urlencode(params)}"
            
            logger.info(f"Connecting to Asterisk ARI WebSocket: {ws_url}")
            
            # Connect to WebSocket
            self.websocket = await websockets.connect(
                ws_url,
                extra_headers={
                    'Authorization': f'Basic {self.username}:{self.password}'
                }
            )
            
            self.running = True
            logger.info(f"✅ Connected to Asterisk ARI - Stasis app '{self.app_name}' registered!")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to Asterisk ARI: {e}")
            return False
    
    async def listen_for_events(self):
        """Listen for ARI events and forward to our ARI handler"""
        try:
            while self.running and self.websocket:
                try:
                    # Receive event from Asterisk
                    message = await self.websocket.recv()
                    event = json.loads(message)
                    
                    logger.info(f"📨 Received ARI event: {event.get('type', 'Unknown')}")
                    
                    # Forward event to our ARI handler
                    await self.forward_event_to_handler(event)
                    
                except websockets.exceptions.ConnectionClosed:
                    logger.warning("WebSocket connection closed")
                    break
                except Exception as e:
                    logger.error(f"Error receiving event: {e}")
                    
        except Exception as e:
            logger.error(f"Error in event listener: {e}")
        finally:
            self.running = False
    
    async def forward_event_to_handler(self, event):
        """Forward ARI event to our HTTP handler"""
        try:
            # Try multiple possible endpoints
            endpoints = [
                "http://localhost:8000/ari/events",
                "http://localhost:8000/events", 
                "http://localhost:8000/ari/handle_event"
            ]
            
            success = False
            for endpoint in endpoints:
                try:
                    response = requests.post(
                        endpoint,
                        json=event,
                        timeout=5
                    )
                    
                    if response.status_code == 200:
                        logger.debug(f"✅ Event forwarded successfully to {endpoint}: {event.get('type')}")
                        success = True
                        break
                    elif response.status_code == 404:
                        continue  # Try next endpoint
                    else:
                        logger.warning(f"⚠️ Event forward failed to {endpoint}: HTTP {response.status_code}")
                        
                except requests.exceptions.RequestException:
                    continue  # Try next endpoint
            
            if not success:
                # Direct processing since HTTP forwarding failed
                await self.process_event_directly(event)
                
        except Exception as e:
            logger.error(f"❌ Failed to forward event: {e}")
    
    async def process_event_directly(self, event):
        """Process ARI event directly when HTTP forwarding fails"""
        try:
            event_type = event.get('type')
            channel = event.get('channel', {})
            channel_id = channel.get('id', 'unknown')
            
            logger.info(f"🔄 Processing event directly: {event_type} for channel {channel_id}")
            
            if event_type == "StasisStart":
                caller_number = channel.get('caller', {}).get('number', 'Unknown')
                called_number = channel.get('dialplan', {}).get('exten', 'Unknown')
                
                print(f"\n📞 INCOMING CALL DETECTED: {channel_id}")
                print(f"   📱 From: {caller_number}")
                print(f"   📞 To: {called_number}")
                print(f"   🕐 Time: {event.get('timestamp')}")
                print(f"   ⚠️  Note: Direct processing - HTTP handler not available")
                
            elif event_type == "StasisEnd":
                print(f"\n📴 CALL ENDED: {channel_id}")
                
            elif event_type == "ChannelHangupRequest":
                print(f"\n📞 HANGUP REQUEST: {channel_id}")
                
            else:
                logger.debug(f"📨 Event processed: {event_type}")
                
        except Exception as e:
            logger.error(f"❌ Error processing event directly: {e}")
    
    async def disconnect(self):
        """Disconnect from WebSocket"""
        self.running = False
        if self.websocket:
            await self.websocket.close()
            logger.info("Disconnected from Asterisk ARI")

async def test_ari_connection():
    """Test ARI connection and registration"""
    print("🔍 Testing Asterisk ARI Connection...")
    
    # Test HTTP ARI first
    try:
        response = requests.get(
            "http://localhost:8088/ari/asterisk/info",
            auth=("asterisk", "1234"),
            timeout=5
        )
        if response.status_code == 200:
            print("✅ Asterisk ARI HTTP: Connected")
            asterisk_info = response.json()
            print(f"   📋 Asterisk Version: {asterisk_info.get('version', 'Unknown')}")
        else:
            print(f"❌ Asterisk ARI HTTP: Failed (HTTP {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Asterisk ARI HTTP: Not reachable - {e}")
        return False
    
    # Test WebSocket connection
    client = ARIWebSocketClient()
    
    if await client.connect():
        print("✅ Asterisk ARI WebSocket: Connected")
        print(f"✅ Stasis App Registered: {client.app_name}")
        
        # Listen for events for a short time to test
        print("🔍 Testing event reception (5 seconds)...")
        try:
            await asyncio.wait_for(client.listen_for_events(), timeout=5.0)
        except asyncio.TimeoutError:
            print("⏰ Event test completed (timeout)")
        
        await client.disconnect()
        return True
    else:
        print("❌ Asterisk ARI WebSocket: Failed to connect")
        return False

async def run_ari_bridge():
    """Run the ARI bridge to keep stasis app registered"""
    print("🌉 Starting ARI Bridge...")
    print("   This will keep the stasis application registered with Asterisk")
    print("   Press Ctrl+C to stop")
    
    client = ARIWebSocketClient()
    
    try:
        if await client.connect():
            print("✅ ARI Bridge active - Stasis app registered!")
            print("📞 Ready to receive calls on extension 1000")
            
            # Keep listening for events
            await client.listen_for_events()
        else:
            print("❌ Failed to start ARI Bridge")
            return False
            
    except KeyboardInterrupt:
        print("\n👋 Stopping ARI Bridge...")
    except Exception as e:
        print(f"❌ ARI Bridge error: {e}")
    finally:
        await client.disconnect()
    
    return True

def main():
    """Main function"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Test mode
        print("🧪 ARI CONNECTION TEST")
        print("=" * 40)
        result = asyncio.run(test_ari_connection())
        if result:
            print("\n✅ ARI connection test PASSED!")
            print("💡 You can now run: python3 fix_ari_registration.py")
        else:
            print("\n❌ ARI connection test FAILED!")
            print("💡 Check that Asterisk is running and ARI is enabled")
    else:
        # Bridge mode
        print("🌉 ARI BRIDGE MODE")
        print("=" * 40)
        asyncio.run(run_ari_bridge())

if __name__ == "__main__":
    main()