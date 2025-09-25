"""
OpenAI Real-time API client for real-time conversational AI.
Handles WebSocket-based communication with OpenAI's Real-time API for
real-time speech-to-speech conversation with voice interruption and noise cancellation.
"""

import asyncio
import json
import logging
import time
import base64
import uuid
from typing import Optional, Dict, Any, Callable, List
from dataclasses import dataclass, asdict
from enum import Enum
import websockets
from websockets.exceptions import ConnectionClosed, WebSocketException
import numpy as np

from config.settings import get_settings
from ..audio.realtime_audio_processor import AudioConfig, RealTimeAudioProcessor
from ..tools.weather_tool import weather_tool

logger = logging.getLogger(__name__)


class OpenAIRealtimeEventType(Enum):
    """OpenAI Real-time API event types"""
    # Session events
    SESSION_UPDATE = "session.update"
    
    # Input events
    INPUT_AUDIO_BUFFER_APPEND = "input_audio_buffer.append"
    INPUT_AUDIO_BUFFER_COMMIT = "input_audio_buffer.commit"
    INPUT_AUDIO_BUFFER_CLEAR = "input_audio_buffer.clear"
    
    # Response events
    RESPONSE_CREATE = "response.create"
    RESPONSE_CANCEL = "response.cancel"
    
    # Server events
    ERROR = "error"
    SESSION_CREATED = "session.created"
    SESSION_UPDATED = "session.updated"
    INPUT_AUDIO_BUFFER_COMMITTED = "input_audio_buffer.committed"
    INPUT_AUDIO_BUFFER_CLEARED = "input_audio_buffer.cleared"
    INPUT_AUDIO_BUFFER_SPEECH_STARTED = "input_audio_buffer.speech_started"
    INPUT_AUDIO_BUFFER_SPEECH_STOPPED = "input_audio_buffer.speech_stopped"
    RESPONSE_CREATED = "response.created"
    RESPONSE_DONE = "response.done"
    RESPONSE_AUDIO_DELTA = "response.audio.delta"
    RESPONSE_AUDIO_DONE = "response.audio.done"
    RESPONSE_TEXT_DELTA = "response.text.delta"
    RESPONSE_TEXT_DONE = "response.text.done"


@dataclass
class OpenAIRealtimeConfig:
    """Configuration for OpenAI Real-time API"""
    model: str = "gpt-4o-realtime-preview-2024-10-01"
    voice: str = "alloy"  # alloy, echo, fable, onyx, nova, shimmer (enhanced quality)
    input_audio_format: str = "pcm16"
    output_audio_format: str = "pcm16"
    input_audio_transcription: Optional[Dict[str, Any]] = None
    turn_detection: Optional[Dict[str, Any]] = None
    tools: List[Dict[str, Any]] = None
    tool_choice: str = "auto"
    temperature: float = 0.8
    max_response_output_tokens: Optional[int] = 4096
    
    # Voice interruption settings
    enable_interruption: bool = True
    interruption_threshold: float = 0.5
    
    # Noise cancellation settings
    enable_noise_cancellation: bool = True
    noise_reduction_strength: float = 0.7
    
    def __post_init__(self):
        if self.input_audio_transcription is None:
            self.input_audio_transcription = {"model": "whisper-1"}
        
        if self.turn_detection is None:
            self.turn_detection = {
                "type": "server_vad",
                "threshold": 0.5,
                "prefix_padding_ms": 300,
                "silence_duration_ms": 500
            }
        
        if self.tools is None:
            # Add weather tool by default
            self.tools = [weather_tool.get_definition().to_openai_format()]


@dataclass
class ConversationItem:
    """Conversation item for OpenAI Real-time"""
    id: str
    type: str  # "message", "function_call", "function_call_output"
    role: str  # "user", "assistant", "system"
    content: List[Dict[str, Any]]
    status: str = "completed"  # "in_progress", "completed", "incomplete"


class OpenAIRealtimeSession:
    """Manages an OpenAI Real-time conversation session"""
    
    def __init__(self, config: OpenAIRealtimeConfig):
        self.config = config
        self.session_id = str(uuid.uuid4())
        self.conversation: List[ConversationItem] = []
        self.is_active = False
        self.created_at = time.time()
        
        # Audio state
        self.input_audio_buffer = bytearray()
        self.is_user_speaking = False
        self.is_assistant_speaking = False
        self.current_response_id = None
        
        # Interruption handling
        self.can_be_interrupted = True
        self.interruption_detected = False
        
        logger.info(f"Created OpenAI Real-time session: {self.session_id}")
    
    def add_conversation_item(self, item: ConversationItem):
        """Add item to conversation history"""
        self.conversation.append(item)
        logger.debug(f"Added conversation item: {item.type} from {item.role}")
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get conversation history as list of dictionaries"""
        return [asdict(item) for item in self.conversation]
    
    def clear_conversation(self):
        """Clear conversation history"""
        self.conversation.clear()
        logger.info("Conversation history cleared")


class OpenAIRealtimeClient:
    """Client for OpenAI Real-time API with advanced features"""
    
    def __init__(self, api_key: str = None, config: OpenAIRealtimeConfig = None):
        self.settings = get_settings()
        self.api_key = api_key or getattr(self.settings, 'openai_api_key', None)
        self.config = config or OpenAIRealtimeConfig()
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        # WebSocket connection
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.is_connected = False
        self.connection_task: Optional[asyncio.Task] = None
        
        # Session management
        self.session: Optional[OpenAIRealtimeSession] = None
        
        # Event handlers
        self.event_handlers: Dict[str, List[Callable]] = {}
        
        # Audio processing
        self.audio_processor = RealTimeAudioProcessor()
        
        # State tracking
        self.is_processing_audio = False
        self.last_audio_timestamp = 0
        self.response_audio_buffer = bytearray()
        
        # API endpoint
        self.api_url = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01"
        
        logger.info("OpenAI Real-time client initialized")
    
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
                    self.api_url,
                    extra_headers=headers,
                    ping_interval=30,
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
        """Send audio chunk to OpenAI Real-time API with noise cancellation"""
        if not self.is_connected or not self.websocket:
            logger.warning("Cannot send audio: not connected")
            return False
        
        try:
            # Apply basic noise reduction if enabled
            processed_audio = audio_data
            if self.config.enable_noise_cancellation:
                processed_audio = self._apply_noise_reduction(audio_data)
            
            # Encode as base64
            audio_base64 = base64.b64encode(processed_audio).decode('utf-8')
            
            # Send to OpenAI
            event = {
                "type": "input_audio_buffer.append",
                "audio": audio_base64
            }
            
            await self._send_event(event)
            
            # Update session state
            if self.session:
                self.session.input_audio_buffer.extend(processed_audio)
            
            self.last_audio_timestamp = time.time()
            return True
            
        except Exception as e:
            logger.error(f"Error sending audio chunk: {e}")
            return False
    
    def _apply_noise_reduction(self, audio_data: bytes) -> bytes:
        """Apply basic noise reduction to audio data"""
        try:
            # Convert to numpy array
            audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32)
            
            # Simple high-pass filter to remove low-frequency noise
            # This is a basic implementation - can be enhanced
            if len(audio_array) > 1:
                filtered = audio_array[1:] - 0.95 * audio_array[:-1]
                filtered = np.concatenate([[audio_array[0]], filtered])
                
                # Apply gain reduction to reduce noise
                filtered = filtered * self.config.noise_reduction_strength
                
                # Convert back to int16
                return filtered.astype(np.int16).tobytes()
            
            return audio_data
            
        except Exception as e:
            logger.warning(f"Noise reduction failed: {e}")
            return audio_data
    
    async def commit_audio_buffer(self) -> bool:
        """Commit the current audio buffer for processing"""
        if not self.is_connected or not self.websocket:
            return False
        
        try:
            event = {
                "type": "input_audio_buffer.commit"
            }
            
            await self._send_event(event)
            logger.debug("Audio buffer committed")
            return True
            
        except Exception as e:
            logger.error(f"Error committing audio buffer: {e}")
            return False
    
    async def clear_audio_buffer(self) -> bool:
        """Clear the current audio buffer"""
        if not self.is_connected or not self.websocket:
            return False
        
        try:
            event = {
                "type": "input_audio_buffer.clear"
            }
            
            await self._send_event(event)
            
            if self.session:
                self.session.input_audio_buffer.clear()
            
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
            event = {
                "type": "response.create",
                "response": {
                    "modalities": ["text", "audio"],
                    "instructions": f"You are {self.settings.assistant_name}, a helpful voice assistant for NPCL (Noida Power Corporation Limited) with access to real-time weather information. When users ask about weather, use the get_weather function to provide current, accurate information. Respond naturally and conversationally. Keep responses concise but helpful."
                }
            }
            
            await self._send_event(event)
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
            
            logger.debug("Response cancelled")
            return True
            
        except Exception as e:
            logger.error(f"Error cancelling response: {e}")
            return False
    
    async def _setup_session(self):
        """Setup initial session with OpenAI Real-time API"""
        try:
            session_update = {
                "type": "session.update",
                "session": {
                    "modalities": ["text", "audio"],
                    "instructions": f"You are {self.settings.assistant_name}, a helpful voice assistant for NPCL (Noida Power Corporation Limited) with access to real-time weather information. When users ask about weather, use the get_weather function to provide current, accurate information. Respond naturally and conversationally. Keep responses concise but helpful.",
                    "voice": self.config.voice,
                    "input_audio_format": self.config.input_audio_format,
                    "output_audio_format": self.config.output_audio_format,
                    "input_audio_transcription": self.config.input_audio_transcription,
                    "turn_detection": self.config.turn_detection,
                    "tools": self.config.tools,
                    "tool_choice": self.config.tool_choice,
                    "temperature": self.config.temperature,
                    "max_response_output_tokens": self.config.max_response_output_tokens
                }
            }
            
            await self._send_event(session_update)
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
            while self.is_connected and self.websocket:
                try:
                    message = await self.websocket.recv()
                    await self._handle_message(message)
                    
                except ConnectionClosed:
                    logger.warning("WebSocket connection closed")
                    break
                except WebSocketException as e:
                    logger.error(f"WebSocket error: {e}")
                    break
                    
        except Exception as e:
            logger.error(f"Connection handler error: {e}")
        finally:
            self.is_connected = False
    
    async def _handle_message(self, message: str):
        """Handle incoming message from OpenAI Real-time API"""
        try:
            event = json.loads(message)
            event_type = event.get("type")
            
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
            elif event_type == "response.created":
                await self._handle_response_created(event)
            elif event_type == "response.audio.delta":
                await self._handle_response_audio_delta(event)
            elif event_type == "response.audio.done":
                await self._handle_response_audio_done(event)
            elif event_type == "response.output_item.added":
                await self._handle_output_item_added(event)
            elif event_type == "response.output_item.done":
                await self._handle_output_item_done(event)
            elif event_type == "response.done":
                await self._handle_response_done(event)
            elif event_type == "error":
                await self._handle_error(event)
            
            # Trigger registered event handlers
            await self._trigger_event_handlers(event_type or "unknown", event)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON message: {e}")
        except Exception as e:
            logger.error(f"Error handling message: {e}")
    
    async def _handle_session_created(self, event: Dict[str, Any]):
        """Handle session created event"""
        logger.info("OpenAI Real-time session created")
        await self._trigger_event_handlers("session_created", event)
    
    async def _handle_session_updated(self, event: Dict[str, Any]):
        """Handle session updated event"""
        logger.info("OpenAI Real-time session updated")
        await self._trigger_event_handlers("session_updated", event)
    
    async def _handle_input_speech_started(self, event: Dict[str, Any]):
        """Handle input speech started event"""
        if self.session:
            self.session.is_user_speaking = True
            
            # If assistant is speaking and interruption is enabled, cancel response
            if (self.session.is_assistant_speaking and self.config.enable_interruption):
                await self.cancel_response()
                self.session.interruption_detected = True
                logger.info("Interruption detected - cancelling assistant response")
        
        await self._trigger_event_handlers("speech_started", event)
    
    async def _handle_input_speech_stopped(self, event: Dict[str, Any]):
        """Handle input speech stopped event"""
        if self.session:
            self.session.is_user_speaking = False
        await self._trigger_event_handlers("speech_stopped", event)
    
    async def _handle_response_created(self, event: Dict[str, Any]):
        """Handle response created event"""
        response = event.get("response", {})
        response_id = response.get("id")
        
        if self.session:
            self.session.current_response_id = response_id
            self.session.is_assistant_speaking = True
        
        logger.debug(f"Response created: {response_id}")
        await self._trigger_event_handlers("response_created", event)
    
    async def _handle_response_audio_delta(self, event: Dict[str, Any]):
        """Handle response audio delta event"""
        delta = event.get("delta", "")
        if delta:
            # Decode base64 audio data
            audio_data = base64.b64decode(delta)
            self.response_audio_buffer.extend(audio_data)
            
            # Trigger audio response handler
            await self._trigger_event_handlers("audio_response", {
                "audio_data": audio_data,
                "is_delta": True
            })
    
    async def _handle_response_audio_done(self, event: Dict[str, Any]):
        """Handle response audio done event"""
        logger.debug("Response audio completed")
        await self._trigger_event_handlers("audio_response_done", event)
    
    async def _handle_output_item_added(self, event: Dict[str, Any]):
        """Handle output item added event (function calls)"""
        item = event.get("item", {})
        if item.get("type") == "function_call":
            function_name = item.get("name", "")
            logger.info(f"Function call detected: {function_name}")
            await self._trigger_event_handlers("function_call_started", event)
    
    async def _handle_output_item_done(self, event: Dict[str, Any]):
        """Handle output item done event (function call completion)"""
        item = event.get("item", {})
        if item.get("type") == "function_call":
            function_name = item.get("name", "")
            call_id = item.get("call_id", "")
            arguments = item.get("arguments", "")
            
            logger.info(f"Executing function call: {function_name}")
            
            try:
                # Parse arguments
                import json
                args = json.loads(arguments) if arguments else {}
                
                # Execute weather function
                if function_name == "get_weather":
                    location = args.get("location", "")
                    if location:
                        # Execute weather lookup
                        weather_result = await weather_tool.execute(location)
                        result_text = weather_result.get("result", "Weather information unavailable")
                        
                        # Send function result back to OpenAI
                        function_result = {
                            "type": "conversation.item.create",
                            "item": {
                                "type": "function_call_output",
                                "call_id": call_id,
                                "output": result_text
                            }
                        }
                        
                        await self._send_event(function_result)
                        
                        # Create response with weather data
                        await self.create_response()
                        
                        logger.info(f"Weather function executed successfully for {location}")
                        await self._trigger_event_handlers("function_call_completed", {
                            "function_name": function_name,
                            "result": result_text
                        })
                    else:
                        logger.error("No location provided for weather function")
                else:
                    logger.warning(f"Unknown function call: {function_name}")
                    
            except Exception as e:
                logger.error(f"Error executing function {function_name}: {e}")
                # Send error response
                error_result = {
                    "type": "conversation.item.create",
                    "item": {
                        "type": "function_call_output",
                        "call_id": call_id,
                        "output": f"Sorry, I couldn't execute the {function_name} function right now."
                    }
                }
                await self._send_event(error_result)
                await self.create_response()
    
    async def _handle_response_done(self, event: Dict[str, Any]):
        """Handle response done event"""
        if self.session:
            self.session.current_response_id = None
            self.session.is_assistant_speaking = False
            self.session.interruption_detected = False
        
        logger.debug("Response completed")
        await self._trigger_event_handlers("response_done", event)
    
    async def _handle_error(self, event: Dict[str, Any]):
        """Handle error event"""
        error = event.get("error", {})
        error_message = error.get("message", "Unknown error")
        error_type = error.get("type", "unknown")
        
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
            "conversation_length": len(self.session.conversation),
            "is_user_speaking": self.session.is_user_speaking,
            "is_assistant_speaking": self.session.is_assistant_speaking,
            "current_response_id": self.session.current_response_id,
            "audio_buffer_size": len(self.session.input_audio_buffer),
            "interruption_detected": self.session.interruption_detected,
            "can_be_interrupted": self.session.can_be_interrupted
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
                "enable_interruption": self.config.enable_interruption,
                "enable_noise_cancellation": self.config.enable_noise_cancellation
            }
        }