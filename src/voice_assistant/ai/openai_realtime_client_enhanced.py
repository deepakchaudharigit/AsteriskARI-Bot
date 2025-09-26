#!/usr/bin/env python3
"""
Enhanced OpenAI Real-time API client with proper voice interruption support
Based on the working RealTimeOpenAI-Basic implementation
"""

import asyncio
import websockets
import json
import base64
import os
import signal
import queue
import logging
import time
import uuid
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass
import numpy as np
import audioop

from config.settings import get_settings
from .npcl_support_prompts import get_enhanced_system_prompt
from ..utils.conversation_logger import log_caller_speech, log_bot_response, log_system_event

logger = logging.getLogger(__name__)


@dataclass
class OpenAIRealtimeConfig:
    """Configuration for OpenAI Real-time API"""
    model: str = "gpt-4o-realtime-preview-2024-10-01"
    voice: str = "alloy"  # alloy, echo, fable, onyx, nova, shimmer
    input_audio_format: str = "pcm16"
    output_audio_format: str = "pcm16"
    sample_rate: int = 24000  # OpenAI optimal rate
    chunk_size: int = 1024
    channels: int = 1
    
    # Voice interruption settings
    enable_interruption: bool = True
    interruption_threshold: float = 0.8
    
    # VAD settings for OpenAI
    vad_threshold: float = 0.8
    prefix_padding_ms: int = 200
    silence_duration_ms: int = 4000
    
    # Response timing
    response_delay_seconds: int = 10
    
    # Audio processing
    target_rms: int = 1000
    enable_audio_normalization: bool = True


class AudioProcessor:
    """Audio processing utilities for voice assistant"""
    
    def __init__(self, target_rms: int = 1000):
        self.target_rms = target_rms
        
    def resample_pcm_24khz_to_16khz(self, pcm_24khz: bytes) -> bytes:
        """Resample PCM audio from 24kHz to 16kHz for Asterisk"""
        try:
            # Convert bytes to numpy array
            audio_array = np.frombuffer(pcm_24khz, dtype=np.int16)
            
            # Simple decimation (take every 3rd sample: 24000/16000 = 1.5, so we approximate)
            resampled = audio_array[::3]  # Take every 3rd sample
            
            # Convert back to bytes
            return resampled.astype(np.int16).tobytes()
            
        except Exception as e:
            logger.error(f"Error resampling audio: {e}")
            return pcm_24khz  # Return original if resampling fails
    
    def resample_pcm_16khz_to_24khz(self, pcm_16khz: bytes) -> bytes:
        """Resample PCM audio from 16kHz to 24kHz for OpenAI"""
        try:
            # Convert bytes to numpy array
            audio_array = np.frombuffer(pcm_16khz, dtype=np.int16)
            
            # Simple upsampling by repeating samples
            upsampled = np.repeat(audio_array, 3)[:len(audio_array) * 3 // 2]
            
            # Convert back to bytes
            return upsampled.astype(np.int16).tobytes()
            
        except Exception as e:
            logger.error(f"Error upsampling audio: {e}")
            return pcm_16khz  # Return original if upsampling fails
    
    def normalize_audio(self, pcm_buffer: bytes, target_rms: int = None) -> tuple[bytes, float]:
        """Normalize audio to target RMS level"""
        if target_rms is None:
            target_rms = self.target_rms
            
        try:
            # Calculate current RMS
            current_rms = audioop.rms(pcm_buffer, 2)
            
            if current_rms == 0:
                return pcm_buffer, 0.0
            
            # Calculate scaling factor
            scale_factor = target_rms / current_rms
            
            # Apply scaling (but limit to prevent clipping)
            scale_factor = min(scale_factor, 4.0)  # Max 4x amplification
            
            # Apply the scaling
            normalized = audioop.mul(pcm_buffer, 2, scale_factor)
            
            return normalized, current_rms
            
        except Exception as e:
            logger.error(f"Error normalizing audio: {e}")
            return pcm_buffer, 0.0
    
    def is_silence(self, pcm_buffer: bytes, threshold: int = 100) -> bool:
        """Quick silence detection"""
        try:
            rms = audioop.rms(pcm_buffer, 2)
            return rms < threshold
        except:
            return False


class OpenAIRealtimeSession:
    """Manages an OpenAI Real-time conversation session"""
    
    def __init__(self, config: OpenAIRealtimeConfig):
        self.config = config
        self.session_id = str(uuid.uuid4())
        self.is_active = False
        self.created_at = time.time()
        
        # Audio state
        self.is_user_speaking = False
        self.is_assistant_speaking = False
        self.waiting_for_response = False
        self.current_response_id = None
        
        # Interruption handling
        self.can_be_interrupted = True
        self.interruption_detected = False
        
        # Audio queues
        self.audio_output_queue = queue.Queue()
        
        logger.info(f"Created OpenAI Real-time session: {self.session_id}")


class OpenAIRealtimeClientEnhanced:
    """Enhanced OpenAI Real-time API client with proper voice interruption"""
    
    def __init__(self, api_key: str = None, config: OpenAIRealtimeConfig = None):
        self.settings = get_settings()
        self.api_key = api_key or getattr(self.settings, 'openai_api_key', None)
        self.config = config or OpenAIRealtimeConfig()
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        # WebSocket connection
        self.websocket_url = f"wss://api.openai.com/v1/realtime?model={self.config.model}"
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.is_connected = False
        self.connection_task: Optional[asyncio.Task] = None
        
        # Session management
        self.session: Optional[OpenAIRealtimeSession] = None
        
        # Event handlers
        self.event_handlers: Dict[str, List[Callable]] = {}
        
        # Audio processing
        self.audio_processor = AudioProcessor(self.config.target_rms)
        
        # State tracking
        self.is_processing_audio = False
        self.last_audio_timestamp = 0
        
        # Control flags
        self.is_running = True
        
        logger.info("Enhanced OpenAI Real-time client initialized")
    
    def register_event_handler(self, event_type: str, handler: Callable):
        """Register event handler for specific event type"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
        logger.debug(f"Registered handler for event: {event_type}")
    
    async def connect(self) -> bool:
        """Connect to OpenAI Real-time API"""
        try:
            logger.info(f"Connecting to OpenAI Real-time API...")
            logger.info(f"Model: {self.config.model}")
            logger.info(f"Voice: {self.config.voice}")
            
            # Create WebSocket connection with authentication
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "OpenAI-Beta": "realtime=v1"
            }
            
            self.websocket = await asyncio.wait_for(
                websockets.connect(
                    self.websocket_url,
                    additional_headers=headers,
                    ping_interval=20,
                    ping_timeout=10
                ),
                timeout=15.0
            )
            
            logger.info("WebSocket connection established")
            self.is_connected = True
            
            # Start connection handler
            self.connection_task = asyncio.create_task(self._connection_handler())
            
            # Setup session
            await asyncio.wait_for(self._setup_session(), timeout=10.0)
            
            logger.info("Connected to OpenAI Real-time API successfully")
            return True
            
        except asyncio.TimeoutError:
            logger.error("Connection timeout - Real-time API may not be available")
            self.is_connected = False
            return False
        except websockets.exceptions.InvalidStatusCode as e:
            logger.error(f"Invalid status code: {e.status_code} - Check API key and permissions")
            self.is_connected = False
            return False
        except Exception as e:
            logger.error(f"Failed to connect to OpenAI Real-time API: {e}")
            self.is_connected = False
            return False
    
    async def disconnect(self):
        """Disconnect from OpenAI Real-time API"""
        try:
            self.is_connected = False
            self.is_running = False
            
            if self.connection_task:
                self.connection_task.cancel()
                try:
                    await self.connection_task
                except asyncio.CancelledError:
                    pass
            
            if self.websocket:
                await self.websocket.close()
                self.websocket = None
            
            if self.session:
                self.session.is_active = False
            
            logger.info("Disconnected from OpenAI Real-time API")
            
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")
    
    async def start_conversation(self) -> str:
        """Start a new conversation session"""
        if not self.is_connected:
            raise RuntimeError("Not connected to OpenAI Real-time API")
        
        self.session = OpenAIRealtimeSession(self.config)
        self.session.is_active = True
        
        logger.info(f"Started conversation session: {self.session.session_id}")
        return self.session.session_id
    
    async def end_conversation(self):
        """End current conversation session"""
        if self.session:
            self.session.is_active = False
            logger.info(f"Ended conversation session: {self.session.session_id}")
    
    async def send_audio_chunk(self, audio_data: bytes) -> bool:
        """Send audio chunk to OpenAI Real-time API"""
        if not self.is_connected or not self.websocket:
            logger.warning("Cannot send audio: not connected")
            return False
        
        try:
            # Convert from Asterisk format (16kHz) to OpenAI format (24kHz)
            processed_audio = self.audio_processor.resample_pcm_16khz_to_24khz(audio_data)
            
            # Normalize audio if enabled
            if self.config.enable_audio_normalization:
                processed_audio, _ = self.audio_processor.normalize_audio(processed_audio)
            
            # Encode as base64
            audio_base64 = base64.b64encode(processed_audio).decode('utf-8')
            
            # Send to OpenAI
            event = {
                "type": "input_audio_buffer.append",
                "audio": audio_base64
            }
            
            await self._send_event(event)
            
            self.last_audio_timestamp = time.time()
            return True
            
        except Exception as e:
            logger.error(f"Error sending audio chunk: {e}")
            return False
    
    async def commit_audio_buffer(self) -> bool:
        """Commit the current audio buffer for processing"""
        # OpenAI Real-time API processes audio automatically
        # This method is kept for compatibility
        logger.debug("Audio buffer commit (automatic in OpenAI Real-time API)")
        return True
    
    async def clear_audio_buffer(self) -> bool:
        """Clear the current audio buffer"""
        if not self.is_connected or not self.websocket:
            return False
        
        try:
            event = {
                "type": "input_audio_buffer.clear"
            }
            
            await self._send_event(event)
            logger.debug("Audio buffer cleared")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing audio buffer: {e}")
            return False
    
    async def create_response(self) -> bool:
        """Request OpenAI to create a response"""
        if not self.is_connected or not self.websocket:
            return False
        
        try:
            if self.session:
                self.session.waiting_for_response = False
            
            response_create = {
                "type": "response.create",
                "response": {
                    "modalities": ["text", "audio"],
                    "instructions": "Continue the conversation as a comprehensive NPCL customer care representative. Provide detailed, helpful responses and engage in extended conversations to fully resolve customer concerns. Ask follow-up questions when needed and provide thorough explanations."
                }
            }
            
            await self._send_event(response_create)
            logger.debug("Response creation requested")
            return True
            
        except Exception as e:
            logger.error(f"Error creating response: {e}")
            return False
    
    async def cancel_response(self) -> bool:
        """Cancel current response generation"""
        if not self.is_connected or not self.websocket:
            return False
        
        try:
            event = {
                "type": "response.cancel"
            }
            
            await self._send_event(event)
            
            if self.session:
                self.session.current_response_id = None
                self.session.is_assistant_speaking = False
                self.session.interruption_detected = True
            
            logger.debug("Response cancelled due to interruption")
            return True
            
        except Exception as e:
            logger.error(f"Error cancelling response: {e}")
            return False
    
    async def _delayed_response(self):
        """Wait for specified delay then create response"""
        try:
            # Wait for the configured delay
            for i in range(self.config.response_delay_seconds):
                if not self.is_running or not self.session or not self.session.waiting_for_response:
                    return
                await asyncio.sleep(1)
            
            # After delay, create the response
            if self.session and self.session.waiting_for_response and self.is_running:
                await self.create_response()
                
        except Exception as e:
            logger.error(f"Error in delayed response: {e}")
    
    async def _setup_session(self):
        """Setup initial session with OpenAI Real-time API"""
        try:
            session_config = {
                "type": "session.update",
                "session": {
                    "modalities": ["text", "audio"],
                    "instructions": get_enhanced_system_prompt(),
                    "voice": self.config.voice,
                    "input_audio_format": self.config.input_audio_format,
                    "output_audio_format": self.config.output_audio_format,
                    "input_audio_transcription": {"model": "whisper-1"},
                    "turn_detection": {
                        "type": "server_vad",
                        "threshold": self.config.vad_threshold,
                        "prefix_padding_ms": self.config.prefix_padding_ms,
                        "silence_duration_ms": self.config.silence_duration_ms
                    },
                    "temperature": 0.7
                }
            }
            
            await self._send_event(session_config)
            logger.info("Session setup sent")
            
        except Exception as e:
            logger.error(f"Error setting up session: {e}")
            raise
    
    async def _send_event(self, event: Dict[str, Any]):
        """Send event to OpenAI Real-time API"""
        if not self.websocket:
            raise RuntimeError("WebSocket not connected")
        
        try:
            message = json.dumps(event)
            await self.websocket.send(message)
            logger.debug(f"Sent event: {event.get('type', 'unknown')}")
            
        except Exception as e:
            logger.error(f"Error sending event: {e}")
            raise
    
    async def _connection_handler(self):
        """Handle WebSocket connection and incoming messages"""
        try:
            while self.is_running and self.is_connected and self.websocket:
                try:
                    message = await asyncio.wait_for(self.websocket.recv(), timeout=0.1)
                    event = json.loads(message)
                    await self._handle_realtime_event(event)
                    
                except asyncio.TimeoutError:
                    continue
                except websockets.exceptions.ConnectionClosed:
                    logger.warning("WebSocket connection closed")
                    break
                except Exception as e:
                    logger.error(f"WebSocket error: {e}")
                    break
                    
        except Exception as e:
            logger.error(f"Connection handler error: {e}")
        finally:
            self.is_connected = False
    
    async def _handle_realtime_event(self, event: Dict[str, Any]):
        """Handle incoming message from OpenAI Real-time API"""
        try:
            event_type = event.get("type", "")
            
            logger.debug(f"Received event type: {event_type}")
            
            # Handle specific events
            if event_type == "session.created":
                await self._handle_session_created(event)
            elif event_type == "session.updated":
                await self._handle_session_updated(event)
            elif event_type == "input_audio_buffer.speech_started":
                await self._handle_input_speech_started(event)
            elif event_type == "input_audio_buffer.speech_stopped":
                await self._handle_input_speech_stopped(event)
            elif event_type == "conversation.item.input_audio_transcription.completed":
                await self._handle_input_transcription_completed(event)
            elif event_type == "response.created":
                await self._handle_response_created(event)
            elif event_type == "response.audio.delta":
                await self._handle_response_audio_delta(event)
            elif event_type == "response.audio_transcript.delta":
                await self._handle_response_transcript_delta(event)
            elif event_type == "response.audio.done":
                await self._handle_response_audio_done(event)
            elif event_type == "response.done":
                await self._handle_response_done(event)
            elif event_type == "response.cancelled":
                await self._handle_response_cancelled(event)
            elif event_type == "error":
                await self._handle_error(event)
            
            # Trigger registered event handlers
            await self._trigger_event_handlers(event_type or "unknown", event)
            
        except Exception as e:
            logger.error(f"Error handling message: {e}")
    
    async def _handle_session_created(self, event: Dict[str, Any]):
        """Handle session created event"""
        logger.info("OpenAI Real-time session created")
        await self._trigger_event_handlers("session_created", event)
    
    async def _handle_session_updated(self, event: Dict[str, Any]):
        """Handle session updated event"""
        logger.info("OpenAI Real-time session updated - ready for conversation")
        await self._trigger_event_handlers("session_updated", event)
    
    async def _handle_input_speech_started(self, event: Dict[str, Any]):
        """Handle input speech started event"""
        if self.session:
            # Cancel any waiting response if user starts speaking again
            if self.session.waiting_for_response:
                self.session.waiting_for_response = False
                
            # If assistant is speaking and interruption is enabled, cancel response
            if (self.session.is_assistant_speaking and self.config.enable_interruption):
                await self.cancel_response()
                logger.info("Voice interruption detected - cancelling assistant response")
            
            self.session.is_user_speaking = True
        
        await self._trigger_event_handlers("speech_started", event)
    
    async def _handle_input_speech_stopped(self, event: Dict[str, Any]):
        """Handle input speech stopped event"""
        if self.session:
            self.session.is_user_speaking = False
            self.session.waiting_for_response = True
        
        # Wait configured delay before creating response
        asyncio.create_task(self._delayed_response())
        
        await self._trigger_event_handlers("speech_stopped", event)
    
    async def _handle_input_transcription_completed(self, event: Dict[str, Any]):
        """Handle input transcription completed event"""
        transcript = event.get("transcript", "")
        if transcript.strip():
            logger.debug(f"User said: {transcript}")
            # Log caller speech to conversation log
            log_caller_speech(transcript, self.session.session_id if self.session else None)
        
        await self._trigger_event_handlers("transcription_completed", event)
    
    async def _handle_response_created(self, event: Dict[str, Any]):
        """Handle response created event"""
        response = event.get("response", {})
        response_id = response.get("id")
        
        if self.session:
            self.session.current_response_id = response_id
            self.session.is_assistant_speaking = True
            self.session.waiting_for_response = False
        
        logger.debug(f"Response created: {response_id}")
        await self._trigger_event_handlers("response_created", event)
    
    async def _handle_response_audio_delta(self, event: Dict[str, Any]):
        """Handle response audio delta event"""
        delta = event.get("delta", "")
        if delta and self.session:
            # Decode base64 audio data
            audio_data = base64.b64decode(delta)
            
            # Convert from OpenAI format (24kHz) to Asterisk format (16kHz)
            processed_audio = self.audio_processor.resample_pcm_24khz_to_16khz(audio_data)
            
            # Add to output queue
            self.session.audio_output_queue.put(processed_audio)
            
            # Trigger audio response handler
            await self._trigger_event_handlers("audio_response", {
                "audio_data": processed_audio,
                "is_delta": True
            })
    
    async def _handle_response_transcript_delta(self, event: Dict[str, Any]):
        """Handle response transcript delta event"""
        text_delta = event.get("delta", "")
        if text_delta:
            logger.debug(f"Assistant: {text_delta}")
            # Accumulate bot response text for logging
            if not hasattr(self, '_current_bot_response'):
                self._current_bot_response = ""
            self._current_bot_response += text_delta
        
        await self._trigger_event_handlers("transcript_delta", event)
    
    async def _handle_response_audio_done(self, event: Dict[str, Any]):
        """Handle response audio done event"""
        logger.debug("Response audio completed")
        await self._trigger_event_handlers("audio_response_done", event)
    
    async def _handle_response_done(self, event: Dict[str, Any]):
        """Handle response done event"""
        if self.session:
            self.session.current_response_id = None
            self.session.is_assistant_speaking = False
            self.session.interruption_detected = False
            self.session.waiting_for_response = False
        
        # Log complete bot response
        if hasattr(self, '_current_bot_response') and self._current_bot_response.strip():
            log_bot_response(self._current_bot_response.strip(), self.session.session_id if self.session else None)
            self._current_bot_response = ""  # Reset for next response
        
        logger.debug("Response completed")
        await self._trigger_event_handlers("response_done", event)
    
    async def _handle_response_cancelled(self, event: Dict[str, Any]):
        """Handle response cancelled event"""
        if self.session:
            self.session.current_response_id = None
            self.session.is_assistant_speaking = False
            self.session.interruption_detected = True
        
        logger.info("Response cancelled due to interruption")
        await self._trigger_event_handlers("response_cancelled", event)
    
    async def _handle_error(self, event: Dict[str, Any]):
        """Handle error event"""
        error = event.get("error", {})
        error_message = error.get("message", "Unknown error")
        error_type = error.get("type", "unknown")
        
        # Only log important errors, not "response in progress" errors
        if "response in progress" not in error_message.lower():
            logger.error(f"OpenAI Real-time API error [{error_type}]: {error_message}")
        
        await self._trigger_event_handlers("error", event)
    
    async def _trigger_event_handlers(self, event_type: str, event_data: Dict[str, Any]):
        """Trigger registered event handlers"""
        handlers = self.event_handlers.get(event_type, [])
        
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event_data)
                else:
                    handler(event_data)
            except Exception as e:
                logger.error(f"Error in event handler for {event_type}: {e}")
    
    def get_session_info(self) -> Optional[Dict[str, Any]]:
        """Get current session information"""
        if not self.session:
            return None
        
        return {
            "session_id": self.session.session_id,
            "is_active": self.session.is_active,
            "created_at": self.session.created_at,
            "is_user_speaking": self.session.is_user_speaking,
            "is_assistant_speaking": self.session.is_assistant_speaking,
            "current_response_id": self.session.current_response_id,
            "waiting_for_response": self.session.waiting_for_response,
            "interruption_detected": self.session.interruption_detected,
            "can_be_interrupted": self.session.can_be_interrupted,
            "audio_queue_size": self.session.audio_output_queue.qsize()
        }
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Get connection status information"""
        return {
            "is_connected": self.is_connected,
            "websocket_state": str(self.websocket.state) if self.websocket else "None",
            "last_audio_timestamp": self.last_audio_timestamp,
            "is_processing_audio": self.is_processing_audio,
            "config": {
                "model": self.config.model,
                "voice": self.config.voice,
                "input_format": self.config.input_audio_format,
                "output_format": self.config.output_audio_format,
                "sample_rate": self.config.sample_rate,
                "enable_interruption": self.config.enable_interruption,
                "response_delay": self.config.response_delay_seconds
            }
        }
    
    def get_audio_output(self) -> Optional[bytes]:
        """Get audio output from queue"""
        if self.session and not self.session.audio_output_queue.empty():
            try:
                return self.session.audio_output_queue.get_nowait()
            except queue.Empty:
                return None
        return None