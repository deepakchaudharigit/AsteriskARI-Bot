"""
Real-time ARI handler optimized for low-latency voice processing, immediate event response, and seamless telephony integration.

Real-time ARI handler with OpenAI Realtime API integration.
Implements the complete workflow for real-time conversational AI
with bidirectional audio streaming using Asterisk externalMedia.
"""

import asyncio
import logging
import json
import time
import uuid
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
import requests
from fastapi import FastAPI, Request, WebSocket, HTTPException
from pydantic import BaseModel

from config.settings import get_settings
from ..ai.ai_client_factory import create_ai_client, get_current_provider
# Using OpenAI client factory for AI integration
from ..ai.openai_realtime_client_enhanced import OpenAIRealtimeClientEnhanced, OpenAIRealtimeConfig
from ..core.session_manager import SessionManager, SessionState, CallDirection
from ..audio.realtime_audio_processor import RealTimeAudioProcessor, AudioConfig
from .external_media_handler import ExternalMediaHandler
from .call_transfer_handler import CallTransferHandler
from ..data.customer_data_manager import CustomerDataManager, InquiryType, Priority, ResolutionStatus
from ..audio.welcome_player import get_welcome_player, play_welcome_message
from ..utils.conversation_logger import start_conversation_session, end_conversation_session, log_system_event

logger = logging.getLogger(__name__)


class ARIEvent(BaseModel):
    """ARI event model"""
    type: str
    application: Optional[str] = None
    timestamp: str
    channel: Optional[Dict[str, Any]] = None
    bridge: Optional[Dict[str, Any]] = None
    recording: Optional[Dict[str, Any]] = None
    playback: Optional[Dict[str, Any]] = None


@dataclass
class RealTimeARIConfig:
    """Configuration for real-time ARI handler"""
    ari_base_url: str
    ari_username: str
    ari_password: str
    stasis_app: str = "openai-voice-assistant"
    external_media_host: str = "localhost"
    external_media_port: int = 8090
    auto_answer: bool = True
    enable_recording: bool = False
    max_call_duration: int = 3600  # 1 hour
    audio_format: str = "slin16"
    sample_rate: int = 16000


class RealTimeARIHandler:
    """
    Real-time ARI handler with full OpenAI Realtime integration.
    Implements the complete workflow from call handling to AI conversation.
    """
    
    def __init__(self, config: RealTimeARIConfig = None):
        self.settings = get_settings()
        self.config = config or RealTimeARIConfig(
            ari_base_url=self.settings.ari_base_url,
            ari_username=self.settings.ari_username,
            ari_password=self.settings.ari_password
        )
        
        # Core components
        self.session_manager = SessionManager()
        
        # Create AI client based on configuration
        self.ai_client = create_ai_client()
        self.ai_provider = get_current_provider()
        
        self.external_media_handler = ExternalMediaHandler(
            self.session_manager, 
            self.ai_client
        )
        self.call_transfer_handler = CallTransferHandler()
        self.customer_data_manager = CustomerDataManager()
        
        # ARI connection
        self.ari_auth = (self.config.ari_username, self.config.ari_password)
        
        # State tracking
        self.active_calls: Dict[str, Dict[str, Any]] = {}
        self.is_running = False
        
        # Event handlers
        self.event_handlers: Dict[str, List[Callable]] = {
            "call_started": [],
            "call_ended": [],
            "speech_detected": [],
            "response_generated": [],
            "error": []
        }
        
        # Setup event handlers
        self._setup_event_handlers()
        
        # Add transfer and data collection methods
        self._add_enhanced_methods()
        
        logger.info("Real-time ARI Handler initialized")
    
    def _add_enhanced_methods(self):
        """Add enhanced methods for transfer and data collection"""
        from .ari_handler_extensions import add_transfer_methods
        add_transfer_methods(self)
    
    def _setup_event_handlers(self):
        """Setup internal event handlers"""
        # Session manager events
        self.session_manager.register_event_handler(
            "session_created", self._handle_session_created
        )
        self.session_manager.register_event_handler(
            "session_ended", self._handle_session_ended
        )
        
        # AI client events (OpenAI)
        self.ai_client.register_event_handler(
            "audio_response", self._handle_ai_audio_response
        )
        self.ai_client.register_event_handler(
            "speech_started", self._handle_user_speech_started
        )
        self.ai_client.register_event_handler(
            "speech_stopped", self._handle_user_speech_stopped
        )
        self.ai_client.register_event_handler(
            "error", self._handle_ai_error
        )
        
        # External media events
        self.external_media_handler.register_event_handler(
            "connection_established", self._handle_media_connection_established
        )
        self.external_media_handler.register_event_handler(
            "connection_lost", self._handle_media_connection_lost
        )
    
    async def start(self) -> bool:
        """Start the real-time ARI handler"""
        try:
            logger.info("Starting Real-time ARI Handler...")
            
            # Start session manager cleanup
            await self.session_manager.start_cleanup_task()
            
            # Connect to AI client (OpenAI)
            if not await self.ai_client.connect():
                raise RuntimeError(f"Failed to connect to {self.ai_provider} API")
            
            # Start external media server
            if not await self.external_media_handler.start_server(
                self.config.external_media_host,
                self.config.external_media_port
            ):
                raise RuntimeError("Failed to start external media server")
            
            self.is_running = True
            logger.info("Real-time ARI Handler started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start Real-time ARI Handler: {e}")
            await self.stop()
            return False
    
    async def stop(self):
        """Stop the real-time ARI handler"""
        try:
            logger.info("Stopping Real-time ARI Handler...")
            
            self.is_running = False
            
            # End all active calls
            for channel_id in list(self.active_calls.keys()):
                await self._end_call(channel_id)
            
            # Stop components
            await self.external_media_handler.stop_server()
            await self.ai_client.disconnect()
            await self.session_manager.stop_cleanup_task()
            
            logger.info("Real-time ARI Handler stopped")
            
        except Exception as e:
            logger.error(f"Error stopping Real-time ARI Handler: {e}")
    
    async def handle_ari_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming ARI event"""
        try:
            event = ARIEvent(**event_data)
            logger.debug(f"Received ARI event: {event.type}")
            
            # Route to appropriate handler
            if event.type == "StasisStart":
                return await self._handle_stasis_start(event)
            elif event.type == "StasisEnd":
                return await self._handle_stasis_end(event)
            elif event.type == "ChannelStateChange":
                return await self._handle_channel_state_change(event)
            elif event.type == "ChannelHangupRequest":
                return await self._handle_hangup_request(event)
            else:
                logger.debug(f"Unhandled event type: {event.type}")
                return {"status": "ignored", "event_type": event.type}
                
        except Exception as e:
            logger.error(f"Error handling ARI event: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _handle_stasis_start(self, event: ARIEvent) -> Dict[str, Any]:
        """Handle Stasis start event (call enters application)"""
        try:
            if not event.channel:
                return {"status": "error", "message": "No channel in event"}
            
            channel_id = event.channel["id"]
            caller_number = event.channel.get("caller", {}).get("number", "Unknown")
            called_number = event.channel.get("dialplan", {}).get("exten", "Unknown")
            
            print(f"\n📞 INCOMING CALL: {channel_id}")
            print(f"   📱 From: {caller_number}")
            print(f"   📞 To: {called_number}")
            print(f"   🕐 Time: {time.strftime('%H:%M:%S')}")
            logger.info(f"Call started: {channel_id} from {caller_number} to {called_number}")
            
            # Create session
            session_id = await self.session_manager.create_session(
                channel_id=channel_id,
                caller_number=caller_number,
                called_number=called_number,
                direction=CallDirection.INBOUND,
                config={
                    "audio_format": self.config.audio_format,
                    "sample_rate": self.config.sample_rate
                }
            )
            
            # Start customer data session
            call_id = await self.customer_data_manager.start_call_session(
                session_id=session_id,
                phone_number=caller_number,
                language="en-IN"  # Default, can be detected later
            )
            
            # Track active call
            self.active_calls[channel_id] = {
                "session_id": session_id,
                "call_id": call_id,
                "start_time": time.time(),
                "state": "initializing"
            }
            
            # Answer the call if auto-answer is enabled
            if self.config.auto_answer:
                await self._answer_call(channel_id)
            
            # Start external media for bidirectional audio
            await self._start_external_media(channel_id)
            
            # Start AI conversation
            await self.ai_client.start_conversation()
            
            # Start conversation logging session
            start_conversation_session(session_id, caller_number)
            log_system_event(f"Call started from {caller_number} to {called_number}", session_id)
            
            # Welcome message disabled - direct AI conversation
            # asyncio.create_task(self._play_welcome_via_openai(channel_id, session_id))
            log_system_event("Welcome message disabled - ready for direct AI conversation", session_id)
            
            # Trigger call started event
            await self._trigger_event_handlers("call_started", {
                "channel_id": channel_id,
                "session_id": session_id,
                "caller_number": caller_number,
                "called_number": called_number
            })
            
            return {"status": "handled", "action": "call_started", "session_id": session_id}
            
        except Exception as e:
            logger.error(f"Error handling Stasis start: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _handle_stasis_end(self, event: ARIEvent) -> Dict[str, Any]:
        """Handle Stasis end event (call leaves application)"""
        try:
            if not event.channel:
                return {"status": "error", "message": "No channel in event"}
            
            channel_id = event.channel["id"]
            await self._end_call(channel_id)
            
            return {"status": "handled", "action": "call_ended"}
            
        except Exception as e:
            logger.error(f"Error handling Stasis end: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _handle_channel_state_change(self, event: ARIEvent) -> Dict[str, Any]:
        """Handle channel state change"""
        try:
            if not event.channel:
                return {"status": "ignored"}
            
            channel_id = event.channel["id"]
            new_state = event.channel.get("state", "Unknown")
            
            logger.debug(f"Channel {channel_id} state changed to: {new_state}")
            
            # Update call state
            if channel_id in self.active_calls:
                self.active_calls[channel_id]["state"] = new_state.lower()
            
            return {"status": "handled", "action": "state_updated"}
            
        except Exception as e:
            logger.error(f"Error handling channel state change: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _handle_hangup_request(self, event: ARIEvent) -> Dict[str, Any]:
        """Handle hangup request"""
        try:
            if not event.channel:
                return {"status": "ignored"}
            
            channel_id = event.channel["id"]
            logger.info(f"Hangup requested for channel: {channel_id}")
            
            await self._end_call(channel_id)
            
            return {"status": "handled", "action": "hangup_processed"}
            
        except Exception as e:
            logger.error(f"Error handling hangup request: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _answer_call(self, channel_id: str) -> bool:
        """Answer incoming call"""
        try:
            url = f"{self.config.ari_base_url}/channels/{channel_id}/answer"
            response = requests.post(url, auth=self.ari_auth, timeout=10)
            response.raise_for_status()
            
            print(f"✅ CALL ANSWERED: {channel_id}")
            logger.info(f"Answered call: {channel_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to answer call {channel_id}: {e}")
            return False
    
    async def _start_external_media(self, channel_id: str) -> bool:
        """Start external media for bidirectional audio streaming"""
        try:
            # Create external media URL
            external_media_url = f"ws://{self.config.external_media_host}:{self.config.external_media_port}/external_media/{channel_id}"
            
            # Start external media on channel
            url = f"{self.config.ari_base_url}/channels/{channel_id}/externalMedia"
            data = {
                "app": self.config.stasis_app,
                "external_host": external_media_url,
                "format": self.config.audio_format,
                "direction": "both"
            }
            
            response = requests.post(url, json=data, auth=self.ari_auth, timeout=10)
            response.raise_for_status()
            
            print(f"🌐 EXTERNAL MEDIA STARTED: {channel_id}")
            print(f"   🔊 Audio streaming: {self.config.audio_format} @ {self.config.sample_rate}Hz")
            logger.info(f"Started external media for channel: {channel_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start external media for {channel_id}: {e}")
            return False
    
    async def _play_welcome_message_delayed(self, channel_id: str):
        """Play welcome message after a short delay to ensure media connection is ready"""
        try:
            # Wait for external media connection to be established
            await asyncio.sleep(2.0)  # 2 second delay
            
            # Check if call is still active
            if channel_id not in self.active_calls:
                logger.debug(f"Call {channel_id} ended before welcome message could play")
                return
            
            logger.info(f"Playing welcome message for channel {channel_id}")
            
            # Get welcome player
            welcome_player = get_welcome_player()
            
            if not welcome_player.is_loaded():
                logger.warning("Welcome audio not loaded, skipping welcome message")
                return
            
            # Create audio sender function for this channel
            async def send_audio_to_channel(audio_data: bytes) -> bool:
                return await self.external_media_handler.send_audio_to_channel(channel_id, audio_data)
            
            # Play welcome message
            success = await welcome_player.stream_welcome_audio(send_audio_to_channel)
            
            if success:
                print(f"🎵 WELCOME MESSAGE PLAYED: {channel_id}")
                logger.info(f"Welcome message played successfully for channel {channel_id}")
            else:
                logger.warning(f"Failed to play welcome message for channel {channel_id}")
                
        except Exception as e:
            logger.error(f"Error playing welcome message for channel {channel_id}: {e}")
    
    async def _play_welcome_via_openai(self, channel_id: str, session_id: str):
        """Play welcome message through OpenAI TTS after external media is established"""
        try:
            # Wait for external media connection to be established
            await asyncio.sleep(3.0)  # 3 second delay for connection setup
            
            # Check if call is still active
            if channel_id not in self.active_calls:
                logger.debug(f"Call {channel_id} ended before OpenAI welcome could play")
                return
            
            logger.info(f"Playing welcome message via OpenAI for channel {channel_id}")
            log_system_event("Playing welcome message via OpenAI TTS", session_id)
            
            # Create welcome message for OpenAI to speak
            welcome_text = "Welcome to NPCL Customer Care! I'm here to provide comprehensive support for all your power-related concerns. How may I assist you today?"
            
            # Send welcome message to OpenAI for TTS conversion
            if hasattr(self.ai_client, 'send_text_for_speech'):
                await self.ai_client.send_text_for_speech(welcome_text)
            else:
                # Alternative: Create a response with the welcome message
                await self.ai_client.create_response()
            
            print(f"🎵 OPENAI WELCOME MESSAGE INITIATED: {channel_id}")
            logger.info(f"OpenAI welcome message initiated for channel {channel_id}")
            
        except Exception as e:
            logger.error(f"Error playing OpenAI welcome message for channel {channel_id}: {e}")
            # Fallback to original welcome player if OpenAI fails
            await self._play_welcome_message_delayed(channel_id)
    
    async def _end_call(self, channel_id: str):
        """End call and cleanup resources"""
        try:
            print(f"\n📴 CALL ENDING: {channel_id}")
            logger.info(f"Ending call: {channel_id}")
            
            # Get call info
            call_info = self.active_calls.get(channel_id, {})
            session_id = call_info.get("session_id")
            
            # End customer data session
            if session_id:
                await self.customer_data_manager.end_call_session(
                    session_id=session_id,
                    call_outcome="completed",
                    conversation_summary="Call completed via telephonic bot"
                )
                
            # End conversation logging session
            if session_id:
                log_system_event(f"Call ended - Duration: {time.time() - call_info.get('start_time', time.time()):.1f}s", session_id)
                end_conversation_session(session_id)
            
            # End session
            if session_id:
                await self.session_manager.end_session(session_id)
            
            # Remove from active calls
            if channel_id in self.active_calls:
                del self.active_calls[channel_id]
            
            # Trigger call ended event
            await self._trigger_event_handlers("call_ended", {
                "channel_id": channel_id,
                "session_id": session_id,
                "call_info": call_info
            })
            
        except Exception as e:
            logger.error(f"Error ending call {channel_id}: {e}")
    
    # Event handlers for integrated components
    
    async def _handle_session_created(self, event_data: Dict[str, Any]):
        """Handle session created event"""
        session_id = event_data["session_id"]
        logger.debug(f"Session created: {session_id}")
    
    async def _handle_session_ended(self, event_data: Dict[str, Any]):
        """Handle session ended event"""
        session_id = event_data["session_id"]
        summary = event_data["summary"]
        logger.info(f"Session ended: {session_id}, turns: {summary['metrics']['total_turns']}")
    
    async def _handle_ai_audio_response(self, event_data: Dict[str, Any]):
        """Handle audio response from AI client (OpenAI)"""
        try:
            audio_data = event_data["audio_data"]
            is_delta = event_data.get("is_delta", False)
            
            # Find the channel for current conversation
            # In a real implementation, you'd track which session is active
            for channel_id, call_info in self.active_calls.items():
                # Send audio to channel via external media
                await self.external_media_handler.send_audio_to_channel(
                    channel_id, audio_data
                )
                break  # For now, send to first active call
            
            # Trigger response generated event
            await self._trigger_event_handlers("response_generated", {
                "audio_size": len(audio_data),
                "is_delta": is_delta
            })
            
        except Exception as e:
            logger.error(f"Error handling OpenAI audio response: {e}")
    
    async def _handle_user_speech_started(self, event_data: Dict[str, Any]):
        """Handle user speech started"""
        print(f"🎤 USER SPEAKING...")
        logger.debug("User speech started")
        
        # Update session states
        for call_info in self.active_calls.values():
            session_id = call_info.get("session_id")
            if session_id:
                await self.session_manager.update_session_audio_state(
                    session_id, is_user_speaking=True
                )
        
        await self._trigger_event_handlers("speech_detected", {
            "type": "started"
        })
    
    async def _handle_user_speech_stopped(self, event_data: Dict[str, Any]):
        """Handle user speech stopped"""
        print(f"🔇 USER STOPPED SPEAKING - Processing...")
        logger.debug("User speech stopped")
        
        # Commit audio buffer for processing
        await self.ai_client.commit_audio_buffer()
        
        # Request response generation
        await self.ai_client.create_response()
        
        # Update session states
        for call_info in self.active_calls.values():
            session_id = call_info.get("session_id")
            if session_id:
                await self.session_manager.update_session_audio_state(
                    session_id, is_user_speaking=False, is_processing=True
                )
        
        await self._trigger_event_handlers("speech_detected", {
            "type": "stopped"
        })
    
    async def _handle_ai_error(self, event_data: Dict[str, Any]):
        """Handle AI client error"""
        error_info = event_data.get("error", {})
        logger.error(f"{self.ai_provider} API error: {error_info}")
        
        await self._trigger_event_handlers("error", {
            "source": self.ai_provider,
            "error": error_info
        })
    
    async def _handle_media_connection_established(self, event_data: Dict[str, Any]):
        """Handle external media connection established"""
        channel_id = event_data["channel_id"]
        logger.info(f"External media connection established for: {channel_id}")
        
        # Update call state
        if channel_id in self.active_calls:
            self.active_calls[channel_id]["state"] = "media_connected"
    
    async def _handle_media_connection_lost(self, event_data: Dict[str, Any]):
        """Handle external media connection lost"""
        channel_id = event_data["channel_id"]
        logger.warning(f"External media connection lost for: {channel_id}")
        
        # End the call
        await self._end_call(channel_id)
    
    async def _handle_audio_from_asterisk(self, event_data: Dict[str, Any]):
        """Handle incoming audio from Asterisk via external media"""
        try:
            channel_id = event_data.get("channel_id")
            audio_data = event_data.get("audio_data", b"")
            
            if not channel_id or not audio_data:
                logger.warning("Invalid audio event data received")
                return
            
            # Find the session for this channel
            call_info = self.active_calls.get(channel_id)
            if not call_info:
                logger.warning(f"No active call found for channel: {channel_id}")
                return
            
            session_id = call_info.get("session_id")
            if not session_id:
                logger.warning(f"No session ID for channel: {channel_id}")
                return
            
            # Send audio to AI client
            await self.ai_client.send_audio_chunk(audio_data)
            
            # Update session with audio activity
            await self.session_manager.update_session_audio_state(
                session_id, 
                has_audio_activity=True
            )
            
            print(f"🔊 AUDIO RECEIVED: {len(audio_data)} bytes from {channel_id}")
            logger.debug(f"Processed audio chunk for channel {channel_id}: {len(audio_data)} bytes")
            
        except Exception as e:
            logger.error(f"Error handling audio from Asterisk: {e}")
            await self._trigger_event_handlers("error", {
                "source": "audio_processing",
                "error": str(e),
                "channel_id": event_data.get("channel_id")
            })
    
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
    
    def register_event_handler(self, event_type: str, handler: Callable):
        """Register event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
        logger.debug(f"Registered handler for event: {event_type}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            "is_running": self.is_running,
            "active_calls": len(self.active_calls),
            "calls": list(self.active_calls.keys()),
            "session_stats": self.session_manager.get_session_stats(),
            "ai_client_status": self.ai_client.get_connection_status(),
            "ai_provider": self.ai_provider,
            "external_media_stats": self.external_media_handler.get_server_stats(),
            "config": {
                "stasis_app": self.config.stasis_app,
                "external_media_host": self.config.external_media_host,
                "external_media_port": self.config.external_media_port,
                "audio_format": self.config.audio_format,
                "sample_rate": self.config.sample_rate
            }
        }
    
    def get_call_info(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """Get information about specific call"""
        call_info = self.active_calls.get(channel_id)
        if not call_info:
            return None
        
        session_id = call_info.get("session_id")
        session = self.session_manager.get_session(session_id) if session_id else None
        
        return {
            "call_info": call_info,
            "session_summary": session.get_session_summary() if session else None,
            "external_media": self.external_media_handler.get_connection_info(channel_id)
        }


def create_realtime_ari_app() -> FastAPI:
    """Create FastAPI application for real-time ARI handling"""
    app = FastAPI(title="Real-time OpenAI Voice Assistant ARI Handler")
    
    # Initialize handler
    ari_handler = RealTimeARIHandler()
    
    @app.on_event("startup")
    async def startup_event():
        """Start the ARI handler on application startup"""
        await ari_handler.start()
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """Stop the ARI handler on application shutdown"""
        await ari_handler.stop()
    
    @app.post("/events")
    async def handle_ari_event(request: Request):
        """Handle incoming ARI events"""
        event_data = await request.json()
        return await ari_handler.handle_ari_event(event_data)
    
    @app.get("/status")
    async def get_status():
        """Get system status"""
        return ari_handler.get_system_status()
    
    @app.get("/calls")
    async def get_active_calls():
        """Get active calls"""
        return {
            "active_calls": list(ari_handler.active_calls.keys()),
            "call_count": len(ari_handler.active_calls)
        }
    
    @app.get("/calls/{channel_id}")
    async def get_call_info(channel_id: str):
        """Get information about specific call"""
        call_info = ari_handler.get_call_info(channel_id)
        if not call_info:
            raise HTTPException(status_code=404, detail="Call not found")
        return call_info
    
    @app.post("/calls/{channel_id}/hangup")
    async def hangup_call(channel_id: str):
        """Manually hangup a call"""
        await ari_handler._end_call(channel_id)
        return {"status": "call_ended", "channel_id": channel_id}
    
    @app.post("/calls/{channel_id}/transfer/agent")
    async def transfer_to_agent(channel_id: str, agent_id: str = "agent1"):
        """Transfer call to agent"""
        transfer_id = await ari_handler.transfer_call_to_agent(channel_id, agent_id)
        if transfer_id:
            return {"status": "success", "transfer_id": transfer_id}
        else:
            raise HTTPException(status_code=400, detail="Transfer failed")
    
    @app.post("/calls/{channel_id}/transfer/queue")
    async def transfer_to_queue(channel_id: str, queue_name: str):
        """Transfer call to queue"""
        transfer_id = await ari_handler.transfer_call_to_queue(channel_id, queue_name)
        if transfer_id:
            return {"status": "success", "transfer_id": transfer_id}
        else:
            raise HTTPException(status_code=400, detail="Transfer failed")
    
    @app.post("/calls/{channel_id}/transfer/supervisor")
    async def transfer_to_supervisor(channel_id: str):
        """Transfer call to supervisor"""
        transfer_id = await ari_handler.transfer_call_to_supervisor(channel_id)
        if transfer_id:
            return {"status": "success", "transfer_id": transfer_id}
        else:
            raise HTTPException(status_code=400, detail="Transfer failed")
    
    @app.post("/calls/{channel_id}/inquiry")
    async def update_inquiry(channel_id: str, inquiry_type: str, description: str):
        """Update customer inquiry type"""
        await ari_handler.update_inquiry_type(channel_id, inquiry_type, description)
        return {"status": "updated"}
    
    @app.post("/calls/{channel_id}/note")
    async def add_note(channel_id: str, note: str, note_type: str = "agent"):
        """Add conversation note"""
        await ari_handler.add_conversation_note(channel_id, note, note_type)
        return {"status": "added"}
    
    @app.post("/calls/{channel_id}/satisfaction")
    async def set_satisfaction(channel_id: str, rating: int):
        """Set customer satisfaction rating (1-5)"""
        if not 1 <= rating <= 5:
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
        await ari_handler.set_customer_satisfaction(channel_id, rating)
        return {"status": "updated", "rating": rating}
    
    @app.get("/transfers")
    async def get_transfers():
        """Get active transfers"""
        return ari_handler.call_transfer_handler.get_active_transfers()
    
    @app.get("/transfers/stats")
    async def get_transfer_stats():
        """Get transfer statistics"""
        return ari_handler.call_transfer_handler.get_transfer_statistics()
    
    @app.get("/customer-data/stats")
    async def get_customer_stats():
        """Get customer data statistics"""
        return ari_handler.customer_data_manager.get_statistics()
    
    @app.get("/customer-data/{phone_number}/history")
    async def get_customer_history(phone_number: str, limit: int = 10):
        """Get customer call history"""
        history = await ari_handler.customer_data_manager.get_customer_history(phone_number, limit)
        return {"phone_number": phone_number, "history": history}
    
    @app.post("/start")
    async def manual_start():
        """Manually start the ARI handler"""
        if ari_handler.is_running:
            return {"status": "already_running", "message": "ARI handler is already running"}
        
        success = await ari_handler.start()
        if success:
            return {"status": "started", "message": "ARI handler started successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to start ARI handler")
    
    @app.post("/stop")
    async def manual_stop():
        """Manually stop the ARI handler"""
        if not ari_handler.is_running:
            return {"status": "already_stopped", "message": "ARI handler is not running"}
        
        await ari_handler.stop()
        return {"status": "stopped", "message": "ARI handler stopped successfully"}
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "service": "realtime-openai-voice-assistant-ari",
            "is_running": ari_handler.is_running,
            "features": {
                "call_transfer": True,
                "customer_data": True,
                "queue_management": True,
                "conversation_tracking": True
            }
        }
    
    return app