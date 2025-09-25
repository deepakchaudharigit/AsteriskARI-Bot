#!/usr/bin/env python3
"""
Asterisk ARI Integration for NPCL Voice Assistant
"""

import asyncio
import aiohttp
import json
import logging
import websockets
from typing import Dict, Optional, Callable

logger = logging.getLogger(__name__)

class AsteriskARIHandler:
    """Handles Asterisk ARI connections and call management"""
    
    def __init__(self, voice_assistant_callback: Callable):
        self.ari_url = "http://localhost:8088"
        self.username = "asterisk"
        self.password = "asterisk"
        self.app_name = "npcl_assistant"
        self.voice_assistant_callback = voice_assistant_callback
        
        # Connection management
        self.session = None
        self.websocket = None
        self.running = False
        
        # Call management
        self.active_calls: Dict[str, Dict] = {}
        self.audio_streams: Dict[str, Dict] = {}
        
    async def start(self):
        """Start the ARI handler"""
        logger.info("Starting Asterisk ARI handler...")
        
        # Create HTTP session
        auth = aiohttp.BasicAuth(self.username, self.password)
        self.session = aiohttp.ClientSession(auth=auth)
        
        # Start WebSocket connection for events
        await self._connect_websocket()
        
        self.running = True
        logger.info(f"ARI handler started for app: {self.app_name}")
    
    async def _connect_websocket(self):
        """Connect to Asterisk ARI WebSocket for events"""
        ws_url = f"{self.ari_url.replace('http', 'ws')}/ari/events"
        ws_params = {
            'app': self.app_name,
            'api_key': f"{self.username}:{self.password}"
        }
        
        try:
            # Build WebSocket URL with parameters
            param_string = '&'.join([f"{k}={v}" for k, v in ws_params.items()])
            full_ws_url = f"{ws_url}?{param_string}"
            
            logger.info(f"Connecting to ARI WebSocket: {full_ws_url}")
            self.websocket = await websockets.connect(full_ws_url)
            
            # Start event handler
            asyncio.create_task(self._handle_ari_events())
            
            logger.info("Connected to Asterisk ARI WebSocket")
            
        except Exception as e:
            logger.error(f"Failed to connect to ARI WebSocket: {e}")
            raise
    
    async def _handle_ari_events(self):
        """Handle incoming ARI events"""
        try:
            async for message in self.websocket:
                try:
                    event = json.loads(message)
                    await self._process_ari_event(event)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to decode ARI event: {e}")
                except Exception as e:
                    logger.error(f"Error processing ARI event: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.warning("ARI WebSocket connection closed")
        except Exception as e:
            logger.error(f"ARI WebSocket error: {e}")
    
    async def _process_ari_event(self, event: Dict):
        """Process individual ARI events"""
        event_type = event.get('type')
        
        if event_type == 'StasisStart':
            await self._handle_call_start(event)
        elif event_type == 'StasisEnd':
            await self._handle_call_end(event)
        elif event_type == 'ChannelDtmfReceived':
            await self._handle_dtmf(event)
    
    async def _handle_call_start(self, event: Dict):
        """Handle incoming call"""
        channel = event.get('channel', {})
        channel_id = channel.get('id')
        caller_number = channel.get('caller', {}).get('number', 'Unknown')
        
        logger.info(f"Incoming call from {caller_number} on channel {channel_id}")
        
        # Store call information
        self.active_calls[channel_id] = {
            'channel_id': channel_id,
            'caller_number': caller_number,
            'start_time': asyncio.get_event_loop().time(),
            'answered': False
        }
        
        # Answer the call
        await self._answer_call(channel_id)
        
        # Start voice assistant for this call
        await self._start_voice_assistant(channel_id)
    
    async def _answer_call(self, channel_id: str):
        """Answer an incoming call"""
        try:
            url = f"{self.ari_url}/ari/channels/{channel_id}/answer"
            async with self.session.post(url) as response:
                if response.status == 204:
                    logger.info(f"Call answered on channel {channel_id}")
                    if channel_id in self.active_calls:
                        self.active_calls[channel_id]['answered'] = True
                else:
                    logger.error(f"Failed to answer call: {response.status}")
                    
        except Exception as e:
            logger.error(f"Error answering call {channel_id}: {e}")
    
    async def _start_voice_assistant(self, channel_id: str):
        """Start voice assistant for a call"""
        try:
            # Create audio stream handlers
            audio_stream = {
                'channel_id': channel_id,
                'write': self._create_audio_writer(channel_id),
                'read': self._create_audio_reader(channel_id)
            }
            
            self.audio_streams[channel_id] = audio_stream
            
            # Start voice assistant with callback
            await self.voice_assistant_callback(channel_id, audio_stream)
            
            logger.info(f"Voice assistant started for channel {channel_id}")
            
        except Exception as e:
            logger.error(f"Error starting voice assistant for {channel_id}: {e}")
    
    def _create_audio_writer(self, channel_id: str):
        """Create audio writer function for a channel"""
        async def write_audio(pcm_data: bytes):
            try:
                logger.debug(f"Writing {len(pcm_data)} bytes to channel {channel_id}")
            except Exception as e:
                logger.error(f"Error writing audio to channel {channel_id}: {e}")
        
        return write_audio