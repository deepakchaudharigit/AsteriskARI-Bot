#!/usr/bin/env python3
"""
Live call monitor - Shows real-time ARI events and audio processing
"""

import asyncio
import websockets
import json
from datetime import datetime

async def live_monitor():
    """Monitor live ARI events"""
    print("🎙️ NPCL Voice Assistant - LIVE CALL MONITOR")
    print("=" * 60)
    print("📡 Connecting to Asterisk ARI WebSocket...")
    print("🎯 Monitoring for calls to extension 1000...")
    print("🔊 Tracking audio and voice processing...")
    print("=" * 60)
    
    try:
        uri = "ws://localhost:8088/ari/events?api_key=asterisk:1234&app=openai-voice-assistant"
        
        async with websockets.connect(uri) as websocket:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Connected to Asterisk ARI")
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 📞 Waiting for calls to extension 1000...")
            print()
            
            async for message in websocket:
                try:
                    event = json.loads(message)
                    event_type = event.get('type', 'unknown')
                    timestamp = datetime.now().strftime('%H:%M:%S')
                    
                    # Handle different event types
                    if event_type == 'StasisStart':
                        channel = event.get('channel', {})
                        channel_id = channel.get('id', 'unknown')
                        caller = channel.get('caller', {}).get('number', 'unknown')
                        exten = event.get('args', ['unknown'])[1] if len(event.get('args', [])) > 1 else 'unknown'
                        
                        print(f"[{timestamp}] 📞 INCOMING CALL!")
                        print(f"[{timestamp}]    📱 From: {caller}")
                        print(f"[{timestamp}]    📞 To: {exten}")
                        print(f"[{timestamp}]    🆔 Channel: {channel_id}")
                        print(f"[{timestamp}]    🎯 Entering Stasis app...")
                        
                    elif event_type == 'StasisEnd':
                        channel = event.get('channel', {})
                        channel_id = channel.get('id', 'unknown')
                        print(f"[{timestamp}] 📴 CALL ENDED: {channel_id}")
                        
                    elif event_type == 'ChannelStateChange':
                        channel = event.get('channel', {})
                        channel_id = channel.get('id', 'unknown')
                        new_state = channel.get('state', 'unknown')
                        print(f"[{timestamp}] 🔄 Channel {channel_id}: {new_state}")
                        
                    elif event_type == 'ChannelTalkingStarted':
                        channel = event.get('channel', {})
                        channel_id = channel.get('id', 'unknown')
                        print(f"[{timestamp}] 🎤 USER SPEAKING: {channel_id}")
                        
                    elif event_type == 'ChannelTalkingFinished':
                        channel = event.get('channel', {})
                        channel_id = channel.get('id', 'unknown')
                        print(f"[{timestamp}] 🔇 USER STOPPED: {channel_id}")
                        
                    elif event_type == 'PlaybackStarted':
                        playback = event.get('playback', {})
                        playback_id = playback.get('id', 'unknown')
                        print(f"[{timestamp}] 🔊 PLAYING AUDIO: {playback_id}")
                        
                    elif event_type == 'PlaybackFinished':
                        playback = event.get('playback', {})
                        playback_id = playback.get('id', 'unknown')
                        print(f"[{timestamp}] ✅ AUDIO FINISHED: {playback_id}")
                        
                    elif event_type == 'RecordingStarted':
                        recording = event.get('recording', {})
                        recording_name = recording.get('name', 'unknown')
                        print(f"[{timestamp}] 🎙️ RECORDING STARTED: {recording_name}")
                        
                    elif event_type == 'RecordingFinished':
                        recording = event.get('recording', {})
                        recording_name = recording.get('name', 'unknown')
                        print(f"[{timestamp}] 📁 RECORDING FINISHED: {recording_name}")
                        
                    else:
                        # Show other events with less detail
                        print(f"[{timestamp}] 📨 {event_type}")
                    
                except json.JSONDecodeError:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Invalid JSON received")
                except Exception as e:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Error processing event: {e}")
                    
    except websockets.exceptions.ConnectionClosed:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔌 Connection closed")
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Connection failed: {e}")
        print("🔧 Make sure Asterisk is running and ARI is enabled")

if __name__ == "__main__":
    print("🎯 Starting live call monitor...")
    print("📞 Call extension 1000 to see real-time events!")
    print("⏹️  Press Ctrl+C to stop monitoring")
    print()
    
    try:
        asyncio.run(live_monitor())
    except KeyboardInterrupt:
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 👋 Monitoring stopped")