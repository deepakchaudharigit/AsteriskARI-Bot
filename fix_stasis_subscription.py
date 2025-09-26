#!/usr/bin/env python3
"""
Fix Stasis Application Subscription
Add WebSocket connection to register the Stasis application with Asterisk
"""

import asyncio
import websockets
import json
import base64
from urllib.parse import urlencode

def create_ari_websocket_client():
    """Create ARI WebSocket client to register Stasis application"""
    
    websocket_code = '''
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
        print("\\n🎯 Testing Stasis registration...")
        print("Run this command in another terminal:")
        print("sudo asterisk -rx 'ari show apps'")
        print("You should now see: openai-voice-assistant")
        print("\\n📞 Test by dialing 1000 in Zoiper")
        print("\\nPress Ctrl+C to stop...")
        
        try:
            await client.listen_for_events()
        except KeyboardInterrupt:
            print("\\n🛑 Stopping ARI WebSocket client...")
        finally:
            await client.disconnect()
    else:
        print("❌ Failed to connect to ARI WebSocket")

if __name__ == "__main__":
    asyncio.run(main())
'''
    
    # Write the WebSocket client code
    with open("ari_websocket_client.py", 'w') as f:
        f.write(websocket_code)
    
    print("✅ Created ari_websocket_client.py")

def create_integrated_fix():
    """Create integrated fix for the ARI handler"""
    
    fix_code = '''
# Add this to the start() method in EnhancedRealTimeARIHandler

async def start(self) -> bool:
    """Start the enhanced ARI handler with WebSocket subscription"""
    try:
        logger.info("Starting Enhanced Real-time ARI Handler...")
        
        await self.session_manager.start_cleanup_task()
        
        if not await self.ai_client.connect():
            raise RuntimeError(f"Failed to connect to {self.ai_provider} API")
        
        if not await self.external_media_handler.start_server(
            self.config.external_media_host,
            self.config.external_media_port
        ):
            raise RuntimeError("Failed to start external media server")
        
        # NEW: Start ARI WebSocket connection to register Stasis app
        if not await self._start_ari_websocket():
            raise RuntimeError("Failed to connect to ARI WebSocket")
        
        self.is_running = True
        logger.info("Enhanced Real-time ARI Handler started successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to start Enhanced ARI Handler: {e}")
        await self.stop()
        return False

async def _start_ari_websocket(self):
    """Start ARI WebSocket connection to register Stasis application"""
    try:
        import websockets
        import base64
        from urllib.parse import urlencode
        
        # Create WebSocket URL with authentication and app subscription
        auth_string = f"{self.config.ari_username}:{self.config.ari_password}"
        auth_encoded = base64.b64encode(auth_string.encode()).decode()
        
        # ARI WebSocket endpoint with app subscription
        ws_url = f"ws://localhost:8088/ari/events?{urlencode({'app': self.config.stasis_app})}"
        
        headers = {
            "Authorization": f"Basic {auth_encoded}"
        }
        
        print(f"🔌 Connecting to ARI WebSocket for Stasis registration...")
        print(f"📱 Subscribing to Stasis app: {self.config.stasis_app}")
        
        # Connect to WebSocket (this registers the Stasis app)
        self.ari_websocket = await websockets.connect(ws_url, extra_headers=headers)
        
        print(f"✅ ARI WebSocket connected - Stasis app registered")
        
        # Start listening for events in background
        asyncio.create_task(self._listen_ari_events())
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to start ARI WebSocket: {e}")
        return False

async def _listen_ari_events(self):
    """Listen for ARI events from WebSocket"""
    try:
        while self.is_running and self.ari_websocket:
            try:
                message = await asyncio.wait_for(self.ari_websocket.recv(), timeout=1.0)
                event = json.loads(message)
                
                # Handle the event using existing handler
                await self.handle_ari_event(event)
                
            except asyncio.TimeoutError:
                continue
            except websockets.exceptions.ConnectionClosed:
                logger.warning("ARI WebSocket connection closed")
                break
                
    except Exception as e:
        logger.error(f"Error listening for ARI events: {e}")
'''
    
    with open("ari_handler_fix.py", 'w') as f:
        f.write(fix_code)
    
    print("✅ Created ari_handler_fix.py with integration code")

def provide_quick_test():
    """Provide quick test instructions"""
    
    instructions = '''
# 🚀 QUICK TEST: Register Stasis Application

## Option 1: Test WebSocket Connection (Recommended)

1. **Run the WebSocket client:**
   ```bash
   python3 ari_websocket_client.py
   ```

2. **Check Stasis registration:**
   ```bash
   sudo asterisk -rx 'ari show apps'
   ```
   Should show: openai-voice-assistant

3. **Test with Zoiper:**
   Dial 1000 - should now transfer to AI

## Option 2: Quick Manual Test

1. **Test WebSocket connection manually:**
   ```bash
   # Install wscat if not available
   npm install -g wscat
   
   # Connect to ARI WebSocket
   wscat -c "ws://localhost:8088/ari/events?app=openai-voice-assistant" -H "Authorization: Basic YXN0ZXJpc2s6MTIzNA=="
   ```

2. **Check registration:**
   ```bash
   sudo asterisk -rx 'ari show apps'
   ```

## Expected Results

✅ **WebSocket connects successfully**
✅ **Stasis app appears in 'ari show apps'**
✅ **Extension 1000 transfers to AI**
✅ **Voice conversation works**

## Why This Fixes It

Your ARI bot was missing the WebSocket subscription to Asterisk's ARI events endpoint. Without this subscription:
- Asterisk doesn't know about your Stasis application
- Calls to Stasis() fail and disconnect
- No ARI events reach your bot

The WebSocket connection with `?app=openai-voice-assistant` parameter registers your Stasis application with Asterisk.
'''
    
    with open("QUICK_STASIS_TEST.md", 'w') as f:
        f.write(instructions)
    
    print("✅ Created QUICK_STASIS_TEST.md")

def main():
    """Main function"""
    print("🔧 FIX STASIS APPLICATION SUBSCRIPTION")
    print("=" * 60)
    print("Issue: ARI bot not subscribing to Stasis application via WebSocket")
    print("Solution: Add WebSocket connection to register Stasis app")
    print()
    
    # Create WebSocket client
    create_ari_websocket_client()
    
    # Create integration fix
    create_integrated_fix()
    
    # Provide quick test
    provide_quick_test()
    
    print("\n" + "=" * 60)
    print("🎯 IMMEDIATE ACTION")
    print("=" * 60)
    print("1. Test WebSocket connection:")
    print("   python3 ari_websocket_client.py")
    print()
    print("2. Check Stasis registration:")
    print("   sudo asterisk -rx 'ari show apps'")
    print()
    print("3. Test voice assistant:")
    print("   Dial 1000 in Zoiper")
    print("=" * 60)

if __name__ == "__main__":
    main()