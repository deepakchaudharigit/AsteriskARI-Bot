#!/usr/bin/env python3
"""
Basic ARI Handler - Handles Stasis calls without OpenAI
This provides voice responses using basic audio playback
"""

import asyncio
import websockets
import json
import requests
import logging
from urllib.parse import urlencode

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BasicARIHandler:
    def __init__(self):
        self.ari_base_url = "http://localhost:8088/asterisk/ari"
        self.username = "asterisk"
        self.password = "1234"
        self.app_name = "openai-voice-assistant"
        self.websocket = None
        self.running = False
        
    async def connect_websocket(self):
        """Connect to ARI WebSocket"""
        try:
            ws_url = f"ws://{self.username}:{self.password}@localhost:8088/asterisk/ari/events?{urlencode({'app': self.app_name})}"
            
            logger.info(f"Connecting to ARI WebSocket...")
            self.websocket = await websockets.connect(ws_url)
            self.running = True
            
            logger.info("✅ Connected to ARI WebSocket")
            logger.info(f"🎯 Stasis application '{self.app_name}' is registered and ready")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to ARI WebSocket: {e}")
            return False
    
    def ari_request(self, method, endpoint, **kwargs):
        """Make ARI HTTP request"""
        url = f"{self.ari_base_url}/{endpoint}"
        auth = (self.username, self.password)
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, auth=auth, **kwargs)
            elif method.upper() == "POST":
                response = requests.post(url, auth=auth, **kwargs)
            elif method.upper() == "DELETE":
                response = requests.delete(url, auth=auth, **kwargs)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            response.raise_for_status()
            return response.json() if response.content else {}
            
        except Exception as e:
            logger.error(f"ARI request failed: {e}")
            return None
    
    def answer_channel(self, channel_id):
        """Answer a channel"""
        logger.info(f"📞 Answering channel: {channel_id}")
        return self.ari_request("POST", f"channels/{channel_id}/answer")
    
    def play_sound(self, channel_id, sound_name):
        """Play a sound to the channel"""
        logger.info(f"🔊 Playing sound '{sound_name}' to channel: {channel_id}")
        data = {
            "media": f"sound:{sound_name}"
        }
        return self.ari_request("POST", f"channels/{channel_id}/play", json=data)
    
    def hangup_channel(self, channel_id):
        """Hangup a channel"""
        logger.info(f"📴 Hanging up channel: {channel_id}")
        return self.ari_request("DELETE", f"channels/{channel_id}")
    
    async def handle_stasis_start(self, event):
        """Handle StasisStart event"""
        channel = event.get("channel", {})
        channel_id = channel.get("id")
        caller_id = channel.get("caller", {}).get("number", "Unknown")
        
        logger.info(f"📞 CALL START: Channel {channel_id} from {caller_id}")
        
        try:
            # Answer the call
            self.answer_channel(channel_id)
            
            # Wait a moment
            await asyncio.sleep(1)
            
            # Play welcome message
            self.play_sound(channel_id, "demo-congrats")
            
            # Wait for playback to finish
            await asyncio.sleep(3)
            
            # Play another message
            self.play_sound(channel_id, "demo-thanks")
            
            # Wait for playback to finish
            await asyncio.sleep(3)
            
            # Inform about AI assistant status
            logger.info("🤖 AI Assistant would handle conversation here")
            logger.info("💡 To enable AI: Update OpenAI API key in .env and restart ari_bot.py")
            
            # Keep call alive for demonstration
            await asyncio.sleep(5)
            
            # Hangup
            self.hangup_channel(channel_id)
            
        except Exception as e:
            logger.error(f"Error handling call: {e}")
            # Try to hangup on error
            try:
                self.hangup_channel(channel_id)
            except:
                pass
    
    async def handle_stasis_end(self, event):
        """Handle StasisEnd event"""
        channel = event.get("channel", {})
        channel_id = channel.get("id", "Unknown")
        logger.info(f"📴 CALL END: Channel {channel_id}")
    
    async def handle_channel_state_change(self, event):
        """Handle ChannelStateChange event"""
        channel = event.get("channel", {})
        channel_id = channel.get("id", "Unknown")
        state = channel.get("state", "Unknown")
        logger.info(f"📡 CHANNEL STATE: {channel_id} -> {state}")
    
    async def listen_for_events(self):
        """Listen for ARI events and handle them"""
        logger.info("📡 Listening for ARI events...")
        
        try:
            while self.running and self.websocket:
                try:
                    message = await asyncio.wait_for(self.websocket.recv(), timeout=1.0)
                    event = json.loads(message)
                    
                    event_type = event.get("type", "Unknown")
                    
                    if event_type == "StasisStart":
                        await self.handle_stasis_start(event)
                    elif event_type == "StasisEnd":
                        await self.handle_stasis_end(event)
                    elif event_type == "ChannelStateChange":
                        await self.handle_channel_state_change(event)
                    else:
                        logger.debug(f"📡 Event: {event_type}")
                    
                except asyncio.TimeoutError:
                    # Timeout is normal, continue listening
                    continue
                except websockets.exceptions.ConnectionClosed:
                    logger.warning("🔌 WebSocket connection closed")
                    break
                    
        except Exception as e:
            logger.error(f"❌ Error listening for events: {e}")
    
    async def start(self):
        """Start the basic ARI handler"""
        logger.info("🚀 Starting Basic ARI Handler...")
        
        if await self.connect_websocket():
            logger.info("\\n📋 Basic ARI Handler is ready!")
            logger.info("\\n🧪 Test Instructions:")
            logger.info("1. Dial 1000 in Zoiper")
            logger.info("2. Call will be answered with demo messages")
            logger.info("3. Call will hangup after demonstration")
            logger.info("\\n💡 To enable full AI voice assistant:")
            logger.info("   - Update OpenAI API key in .env file")
            logger.info("   - Stop this handler (Ctrl+C)")
            logger.info("   - Run: python3 ari_bot.py")
            logger.info("\\nPress Ctrl+C to stop...")
            logger.info("-" * 50)
            
            await self.listen_for_events()
        else:
            logger.error("❌ Failed to start Basic ARI Handler")
    
    def stop(self):
        """Stop the handler"""
        self.running = False
        logger.info("\\n🛑 Stopping Basic ARI Handler...")

async def main():
    """Main function"""
    handler = BasicARIHandler()
    
    # Handle Ctrl+C gracefully
    import signal
    def signal_handler(sig, frame):
        handler.stop()
    
    signal.signal(signal.SIGINT, signal_handler)
    
    await handler.start()

if __name__ == "__main__":
    asyncio.run(main())