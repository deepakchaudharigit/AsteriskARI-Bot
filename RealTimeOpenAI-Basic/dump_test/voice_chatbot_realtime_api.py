#!/usr/bin/env python3
"""
OpenAI Realtime API Voice Chatbot
Official implementation using OpenAI's Realtime API with WebSockets
Features:
- True real-time bidirectional audio streaming
- Built-in Voice Activity Detection (VAD)
- Automatic interruption handling
- Low-latency speech-to-speech conversation
- Production-ready implementation
"""

import asyncio
import websockets
import json
import base64
import os
import sys
import signal
import threading
import queue
import time
import logging
from typing import Optional, Dict, Any, List
import pyaudio
import audioop
import numpy as np
from colorama import init, Fore, Style
from dotenv import load_dotenv

# Initialize colorama
init(autoreset=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenAIRealtimeVoiceChatbot:
    def __init__(self):
        """Initialize OpenAI Realtime API voice chatbot."""
        # Load environment variables
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
        load_dotenv()
        
        # OpenAI Configuration
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        # Official OpenAI Realtime API endpoint
        self.websocket_url = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01"
        
        # Audio Configuration (as per Realtime API requirements)
        self.sample_rate = 24000  # Required by Realtime API
        self.chunk_size = 1024
        self.channels = 1
        self.format = pyaudio.paInt16
        
        # Audio components
        self.audio = pyaudio.PyAudio()
        
        # Voice Activity Detection (handled by server, but we need local detection for input)
        self.speech_threshold = 300
        self.silence_threshold = 150
        
        # Control flags
        self.is_running = True
        self.is_connected = False
        self.is_speaking = False
        self.websocket = None
        self.session_id = None
        
        # Audio queues
        self.audio_output_queue = queue.Queue()
        
        # Conversation state
        self.conversation_items = []
        self.current_response_id = None
        
        # Interruption keywords for local handling
        self.quit_keywords = ['quit', 'exit', 'bye', 'goodbye', 'stop chatbot', 'end chat']
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully."""
        print(f"\n{Fore.YELLOW}🛑 Shutting down Realtime API chatbot...")
        self.is_running = False
        if self.websocket:
            asyncio.create_task(self._close_connection())
        sys.exit(0)
        
    async def _close_connection(self):
        """Close WebSocket connection gracefully."""
        if self.websocket:
            try:
                await self.websocket.close()
            except:
                pass
        
    def _print_status(self, message: str, status_type: str = "info"):
        """Print colored status messages."""
        colors = {
            "info": Fore.CYAN,
            "success": Fore.GREEN,
            "warning": Fore.YELLOW,
            "error": Fore.RED,
            "user": Fore.BLUE,
            "assistant": Fore.MAGENTA,
            "realtime": Fore.LIGHTMAGENTA_EX,
            "audio": Fore.LIGHTGREEN_EX
        }
        color = colors.get(status_type, Fore.WHITE)
        print(f"{color}{message}{Style.RESET_ALL}")
        
    def _detect_voice_activity(self, audio_data: bytes) -> bool:
        """Local voice activity detection for input gating."""
        try:
            rms = audioop.rms(audio_data, 2)
            return rms > self.speech_threshold
        except Exception:
            return False
            
    def _check_quit_keywords(self, text: str) -> bool:
        """Check if text contains quit keywords."""
        text_lower = text.lower().strip()
        return any(keyword in text_lower for keyword in self.quit_keywords)
        
    async def _audio_input_handler(self):
        """Capture and stream audio to Realtime API."""
        stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )
        
        self._print_status("🎤 Audio input streaming started", "audio")
        
        try:
            while self.is_running and self.is_connected:
                try:
                    # Read audio data
                    audio_data = stream.read(self.chunk_size, exception_on_overflow=False)
                    
                    # Optional: Gate audio input based on local VAD
                    # The server has its own VAD, but this can reduce unnecessary data
                    if self._detect_voice_activity(audio_data):
                        # Encode as base64 and send to Realtime API
                        encoded_audio = base64.b64encode(audio_data).decode('utf-8')
                        
                        if self.websocket:
                            message = {
                                "type": "input_audio_buffer.append",
                                "audio": encoded_audio
                            }
                            await self.websocket.send(json.dumps(message))
                    
                    # Small delay to prevent overwhelming
                    await asyncio.sleep(0.01)
                    
                except Exception as e:
                    if self.is_running:
                        logger.error(f"Audio input error: {e}")
                    break
                    
        finally:
            stream.stop_stream()
            stream.close()
            
    async def _audio_output_handler(self):
        """Handle audio output from Realtime API."""
        stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.sample_rate,
            output=True,
            frames_per_buffer=self.chunk_size
        )
        
        self._print_status("🔊 Audio output streaming started", "audio")
        
        try:
            while self.is_running and self.is_connected:
                try:
                    if not self.audio_output_queue.empty():
                        audio_data = self.audio_output_queue.get_nowait()
                        stream.write(audio_data)
                    else:
                        await asyncio.sleep(0.01)
                        
                except Exception as e:
                    if self.is_running:
                        logger.error(f"Audio output error: {e}")
                    break
                    
        finally:
            stream.stop_stream()
            stream.close()
            
    async def _handle_realtime_event(self, event: Dict[str, Any]):
        """Handle events from OpenAI Realtime API."""
        event_type = event.get("type", "")
        
        # Session events
        if event_type == "session.created":
            self.session_id = event.get("session", {}).get("id")
            self._print_status(f"✅ Realtime session created", "success")
            
        elif event_type == "session.updated":
            self._print_status("🔧 Session configuration updated", "info")
            
        # Input audio events
        elif event_type == "input_audio_buffer.speech_started":
            self._print_status("🎤 Speech detected by server VAD", "info")
            
        elif event_type == "input_audio_buffer.speech_stopped":
            self._print_status("🔄 Speech ended, processing...", "info")
            
        elif event_type == "input_audio_buffer.committed":
            self._print_status("✅ Audio buffer committed for processing", "info")
            
        # Conversation events
        elif event_type == "conversation.item.created":
            item = event.get("item", {})
            if item.get("type") == "message" and item.get("role") == "user":
                self._print_status("📝 User message created in conversation", "info")
                
        elif event_type == "conversation.item.input_audio_transcription.completed":
            transcript = event.get("transcript", "")
            self._print_status(f"👤 You: {transcript}", "user")
            
            # Check for quit commands
            if self._check_quit_keywords(transcript):
                self._print_status("👋 Goodbye! Thanks for chatting!", "success")
                self.is_running = False
                return
                
        # Response events
        elif event_type == "response.created":
            self.current_response_id = event.get("response", {}).get("id")
            self._print_status("🤖 AI response started", "info")
            
        elif event_type == "response.output_item.added":
            item = event.get("item", {})
            if item.get("type") == "audio":
                self._print_status("🔊 Audio response item added", "audio")
                
        elif event_type == "response.audio.delta":
            # Receive audio response chunks
            audio_b64 = event.get("delta", "")
            if audio_b64:
                try:
                    audio_data = base64.b64decode(audio_b64)
                    self.audio_output_queue.put(audio_data)
                except Exception as e:
                    logger.error(f"Audio decode error: {e}")
                    
        elif event_type == "response.audio_transcript.delta":
            # Show AI response text as it's generated
            text_delta = event.get("delta", "")
            if text_delta:
                print(f"{Fore.MAGENTA}{text_delta}{Style.RESET_ALL}", end="", flush=True)
                
        elif event_type == "response.audio_transcript.done":
            print()  # New line after complete response
            
        elif event_type == "response.done":
            self._print_status("✅ Response completed", "success")
            self.current_response_id = None
            
        # Interruption events
        elif event_type == "response.cancelled":
            self._print_status("🛑 Response cancelled (interrupted)", "warning")
            self.current_response_id = None
            
        # Error events
        elif event_type == "error":
            error_info = event.get("error", {})
            error_code = error_info.get("code", "unknown")
            error_message = error_info.get("message", "Unknown error")
            
            if "invalid_api_key" in error_code:
                self._print_status("❌ Invalid API key for Realtime API", "error")
                self._print_status("Please check your OpenAI API key has Realtime API access", "warning")
                self._print_status("📝 Try option 2 (Real-time FIXED) if Realtime API isn't available", "info")
            else:
                self._print_status(f"❌ Realtime API error: {error_message}", "error")
                
            # Log full error for debugging
            logger.error(f"Realtime API error: {event}")
            
        # Rate limit events
        elif event_type == "rate_limits.updated":
            rate_limits = event.get("rate_limits", [])
            for limit in rate_limits:
                name = limit.get("name", "unknown")
                remaining = limit.get("remaining", 0)
                if remaining < 10:  # Warn when getting low
                    self._print_status(f"⚠️ Rate limit warning: {name} has {remaining} remaining", "warning")
                    
        else:
            # Log unknown events for debugging
            logger.debug(f"Unknown event type: {event_type}")
            
    async def _realtime_connection_handler(self):
        """Main Realtime API connection handler."""
        try:
            self._print_status("🔌 Connecting to OpenAI Realtime API...", "realtime")
            
            # Connect with proper authentication
            async with websockets.connect(
                self.websocket_url,
                additional_headers=[
                    ("Authorization", f"Bearer {self.api_key}"),
                    ("OpenAI-Beta", "realtime=v1")
                ],
                ping_interval=20,
                ping_timeout=10
            ) as websocket:
                self.websocket = websocket
                self.is_connected = True
                
                self._print_status("✅ Connected to Realtime API!", "success")
                
                # Configure the session
                session_config = {
                    "type": "session.update",
                    "session": {
                        "modalities": ["text", "audio"],
                        "instructions": (
                            "You are a helpful AI assistant. Keep responses brief and conversational. "
                            "You can be interrupted at any time, so speak naturally and be ready to stop. "
                            "Respond in 1-2 sentences when possible."
                        ),
                        "voice": "alloy",
                        "input_audio_format": "pcm16",
                        "output_audio_format": "pcm16",
                        "input_audio_transcription": {
                            "model": "whisper-1"
                        },
                        "turn_detection": {
                            "type": "server_vad",
                            "threshold": 0.5,
                            "prefix_padding_ms": 300,
                            "silence_duration_ms": 200
                        },
                        "tools": [],
                        "tool_choice": "none",
                        "temperature": 0.8,
                        "max_response_output_tokens": 4096
                    }
                }
                
                await websocket.send(json.dumps(session_config))
                self._print_status("🔧 Session configured", "info")
                
                # Start audio handlers
                audio_input_task = asyncio.create_task(self._audio_input_handler())
                audio_output_task = asyncio.create_task(self._audio_output_handler())
                
                # Main event loop
                while self.is_running and self.is_connected:
                    try:
                        # Receive events from Realtime API
                        message = await asyncio.wait_for(websocket.recv(), timeout=0.1)
                        event = json.loads(message)
                        await self._handle_realtime_event(event)
                        
                    except asyncio.TimeoutError:
                        continue
                    except websockets.exceptions.ConnectionClosed:
                        self._print_status("🔌 Realtime API connection closed", "warning")
                        break
                    except json.JSONDecodeError as e:
                        logger.error(f"JSON decode error: {e}")
                        continue
                        
                # Cancel audio tasks
                audio_input_task.cancel()
                audio_output_task.cancel()
                
                try:
                    await audio_input_task
                except asyncio.CancelledError:
                    pass
                    
                try:
                    await audio_output_task
                except asyncio.CancelledError:
                    pass
                
        except Exception as e:
            self._print_status(f"❌ Realtime API connection error: {e}", "error")
            logger.error(f"Connection error: {e}", exc_info=True)
        finally:
            self.is_connected = False
            self.websocket = None
            
    def print_instructions(self):
        """Print usage instructions."""
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"{Fore.CYAN}🎙️  OPENAI REALTIME API VOICE CHATBOT")
        print(f"{Fore.CYAN}{'='*80}")
        print(f"{Fore.GREEN}Features:")
        print(f"{Fore.WHITE}• 🌐 Official OpenAI Realtime API")
        print(f"{Fore.WHITE}• 🎤 True real-time bidirectional audio streaming")
        print(f"{Fore.WHITE}• 🛑 Built-in Voice Activity Detection (VAD)")
        print(f"{Fore.WHITE}• ⚡ Automatic interruption handling")
        print(f"{Fore.WHITE}• 🔊 Low-latency speech-to-speech")
        print(f"{Fore.WHITE}• 📁 No temporary files")
        print(f"{Fore.YELLOW}Natural Interaction:")
        print(f"{Fore.WHITE}• Just speak naturally - the AI will respond")
        print(f"{Fore.WHITE}• Interrupt anytime by speaking while AI is talking")
        print(f"{Fore.WHITE}• Server-side VAD automatically detects your speech")
        print(f"{Fore.YELLOW}Exit Commands:")
        print(f"{Fore.WHITE}• Say {Fore.YELLOW}'quit'{Fore.WHITE}, {Fore.YELLOW}'exit'{Fore.WHITE}, {Fore.YELLOW}'bye'{Fore.WHITE}, {Fore.YELLOW}'goodbye'{Fore.WHITE}")
        print(f"{Fore.WHITE}• Press {Fore.RED}Ctrl+C{Fore.WHITE} for immediate exit")
        print(f"{Fore.CYAN}{'='*80}\n")
        
    async def run(self):
        """Main run method."""
        try:
            self.print_instructions()
            await self._realtime_connection_handler()
        except KeyboardInterrupt:
            pass
        finally:
            self.cleanup()
            
    def cleanup(self):
        """Clean up resources."""
        self.is_running = False
        self.is_connected = False
        
        try:
            self.audio.terminate()
        except:
            pass
            
        self._print_status("\n👋 Realtime API voice chatbot ended!", "success")

async def main():
    """Main entry point."""
    try:
        chatbot = OpenAIRealtimeVoiceChatbot()
        await chatbot.run()
    except Exception as e:
        print(f"{Fore.RED}❌ Failed to start Realtime API chatbot: {e}")
        logger.error(f"Startup error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())