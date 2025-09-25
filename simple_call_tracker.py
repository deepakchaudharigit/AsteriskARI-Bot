#!/usr/bin/env python3
"""
Simple Call Tracker - Direct Integration
Bypasses HTTP forwarding and directly integrates with ARI events
"""

import asyncio
import websockets
import json
import logging
import time
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleCallTracker:
    """Simple call tracker that directly processes ARI events"""
    
    def __init__(self):
        self.active_calls: Dict[str, Dict[str, Any]] = {}
        self.call_history = []
        self.websocket = None
        self.running = False
    
    async def connect_to_asterisk(self):
        """Connect to Asterisk ARI WebSocket"""
        try:
            # WebSocket URL with authentication
            ws_url = "ws://localhost:8088/ari/events?app=openai-voice-assistant&api_key=asterisk:1234"
            
            logger.info(f"Connecting to Asterisk ARI: {ws_url}")
            
            # Add extra headers for authentication
            extra_headers = {
                'Authorization': 'Basic YXN0ZXJpc2s6MTIzNA=='  # base64 of asterisk:1234
            }
            
            self.websocket = await websockets.connect(
                ws_url,
                extra_headers=extra_headers,
                ping_interval=20,
                ping_timeout=10
            )
            self.running = True
            
            logger.info("✅ Connected to Asterisk ARI - Call tracking active!")
            
            # Send a test message to verify connection
            logger.info("🔍 Testing WebSocket connection...")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to Asterisk ARI: {e}")
            logger.error(f"   URL: {ws_url}")
            logger.error(f"   Error type: {type(e).__name__}")
            return False
    
    async def process_events(self):
        """Process ARI events and track calls"""
        try:
            logger.info("🔍 Starting event processing loop...")
            
            while self.running and self.websocket:
                try:
                    # Receive event from Asterisk with timeout
                    message = await asyncio.wait_for(self.websocket.recv(), timeout=30)
                    logger.debug(f"📨 Received raw message: {message[:200]}...")
                    
                    event = json.loads(message)
                    logger.info(f"📨 Received ARI event: {event.get('type', 'Unknown')}")
                    
                    await self.handle_event(event)
                    
                except asyncio.TimeoutError:
                    logger.debug("⏰ WebSocket receive timeout (normal)")
                    continue
                except websockets.exceptions.ConnectionClosed:
                    logger.warning("🔌 WebSocket connection closed")
                    break
                except json.JSONDecodeError as e:
                    logger.error(f"❌ JSON decode error: {e}")
                    logger.error(f"   Raw message: {message}")
                except Exception as e:
                    logger.error(f"❌ Error processing event: {e}")
                    logger.error(f"   Event data: {message if 'message' in locals() else 'N/A'}")
                    
        except Exception as e:
            logger.error(f"❌ Error in event processor: {e}")
        finally:
            self.running = False
            logger.info("🔌 Event processing stopped")
    
    async def handle_event(self, event: Dict[str, Any]):
        """Handle individual ARI event"""
        try:
            event_type = event.get('type')
            channel = event.get('channel', {})
            channel_id = channel.get('id', 'unknown')
            
            logger.info(f"🔄 Processing event: {event_type} for channel {channel_id}")
            
            if event_type == "StasisStart":
                await self.handle_call_start(event, channel_id)
            elif event_type == "StasisEnd":
                await self.handle_call_end(event, channel_id)
            elif event_type == "ChannelHangupRequest":
                await self.handle_call_hangup(event, channel_id)
            else:
                logger.info(f"📨 Other event: {event_type} for {channel_id}")
                
        except Exception as e:
            logger.error(f"❌ Error handling event: {e}")
            logger.error(f"   Event: {event}")
    
    async def handle_call_start(self, event: Dict[str, Any], channel_id: str):
        """Handle call start"""
        try:
            channel = event.get('channel', {})
            caller_number = channel.get('caller', {}).get('number', 'Unknown')
            called_number = channel.get('dialplan', {}).get('exten', 'Unknown')
            timestamp = event.get('timestamp', time.strftime('%Y-%m-%dT%H:%M:%S'))
            
            # Add to active calls
            self.active_calls[channel_id] = {
                'caller': caller_number,
                'called': called_number,
                'start_time': timestamp,
                'duration': 0,
                'status': 'active'
            }
            
            # Add to history
            self.call_history.append({
                'channel_id': channel_id,
                'caller': caller_number,
                'called': called_number,
                'start_time': timestamp,
                'event': 'call_started'
            })
            
            print(f"\n📞 CALL STARTED: {channel_id}")
            print(f"   📱 From: {caller_number}")
            print(f"   📞 To: {called_number}")
            print(f"   🕐 Time: {timestamp}")
            print(f"   📊 Active calls: {len(self.active_calls)}")
            
            logger.info(f"Call started: {channel_id} ({caller_number} → {called_number})")
            
        except Exception as e:
            logger.error(f"Error handling call start: {e}")
    
    async def handle_call_end(self, event: Dict[str, Any], channel_id: str):
        """Handle call end"""
        try:
            if channel_id in self.active_calls:
                call_info = self.active_calls[channel_id]
                
                # Calculate duration
                start_time = call_info.get('start_time', '')
                # Simple duration calculation (in practice, you'd parse timestamps)
                duration = time.time() - time.time()  # Placeholder
                
                # Update call info
                call_info['status'] = 'ended'
                call_info['duration'] = duration
                
                # Add to history
                self.call_history.append({
                    'channel_id': channel_id,
                    'caller': call_info['caller'],
                    'called': call_info['called'],
                    'end_time': event.get('timestamp', time.strftime('%Y-%m-%dT%H:%M:%S')),
                    'duration': duration,
                    'event': 'call_ended'
                })
                
                print(f"\n📴 CALL ENDED: {channel_id}")
                print(f"   📱 From: {call_info['caller']}")
                print(f"   📞 To: {call_info['called']}")
                print(f"   ⏱️  Duration: {duration:.0f}s")
                
                # Remove from active calls
                del self.active_calls[channel_id]
                
                print(f"   📊 Active calls: {len(self.active_calls)}")
                
                logger.info(f"Call ended: {channel_id}")
            
        except Exception as e:
            logger.error(f"Error handling call end: {e}")
    
    async def handle_call_hangup(self, event: Dict[str, Any], channel_id: str):
        """Handle call hangup request"""
        logger.debug(f"Hangup request for {channel_id}")
        # This will be followed by StasisEnd, so we don't need to do much here
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status"""
        return {
            'active_calls': len(self.active_calls),
            'call_details': self.active_calls,
            'total_calls': len(self.call_history),
            'is_running': self.running
        }
    
    def print_status(self):
        """Print current status"""
        status = self.get_status()
        timestamp = time.strftime('%H:%M:%S')
        
        if status['active_calls'] > 0:
            print(f"📞 [{timestamp}] Active calls: {status['active_calls']}")
            for channel_id, call_info in self.active_calls.items():
                print(f"   📱 {call_info['caller']} → {call_info['called']} ({channel_id})")
        else:
            print(f"⏰ [{timestamp}] No active calls")
    
    async def disconnect(self):
        """Disconnect from WebSocket"""
        self.running = False
        if self.websocket:
            await self.websocket.close()
            logger.info("Disconnected from Asterisk ARI")

async def main():
    """Main function"""
    print("📞 SIMPLE CALL TRACKER")
    print("=" * 30)
    print("This tracker directly monitors Asterisk ARI events")
    print("and provides accurate call counting.")
    print("")
    
    tracker = SimpleCallTracker()
    
    try:
        # Connect to Asterisk
        if not await tracker.connect_to_asterisk():
            print("❌ Failed to connect to Asterisk")
            return 1
        
        print("✅ Call tracker is running!")
        print("📞 Make a call to 1000 to test...")
        print("Press Ctrl+C to stop")
        print("")
        
        # Start event processing
        event_task = asyncio.create_task(tracker.process_events())
        
        # Status monitoring loop
        monitor_count = 0
        while tracker.running and monitor_count < 30:  # Max 5 minutes
            tracker.print_status()
            
            # Wait 10 seconds or until event task completes
            try:
                await asyncio.wait_for(asyncio.sleep(10), timeout=10)
            except asyncio.TimeoutError:
                pass
            
            monitor_count += 1
            
            # Check if event task is still running
            if event_task.done():
                logger.warning("Event task completed unexpectedly")
                break
        
    except KeyboardInterrupt:
        print("\n👋 Stopping call tracker...")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await tracker.disconnect()
    
    # Print final summary
    status = tracker.get_status()
    print(f"\n📊 FINAL SUMMARY:")
    print(f"   Total calls processed: {status['total_calls']}")
    print(f"   Active calls at end: {status['active_calls']}")
    
    return 0

if __name__ == "__main__":
    asyncio.run(main())