#!/usr/bin/env python3
"""
WebSocket Real-Time Voice Chatbot
Features:
- True real-time streaming with WebSocket
- Built-in interruption support
- No temporary files
- Lower latency
- Bidirectional audio streaming
"""

import asyncio
import websockets
import websockets.client
import json
import base64
import os
import sys
import signal
import threading
import queue
import time
from typing import Optional, Dict, Any
import pyaudio
import audioop
import numpy as np
from colorama import init, Fore, Style
from dotenv import load_dotenv

# Initialize colorama
init(autoreset=True)

class WebSocketVoiceChatbot:
    def __init__(self):
        """Initialize WebSocket-based real-time voice chatbot."""
        # Load environment variables
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
        load_dotenv()
        
        # OpenAI Configuration
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        # WebSocket endpoint for OpenAI Real-time API
        self.websocket_url = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01"
        
        # Audio Configuration
        self.sample_rate = 24000  # Required by OpenAI Real-time API
        self.chunk_size = 1024
        self.channels = 1
        self.format = pyaudio.paInt16
        
        # Audio components
        self.audio = pyaudio.PyAudio()
        
        # Voice Activity Detection
        self.speech_threshold = 500
        self.silence_threshold = 200
        self.min_speech_duration = 0.3
        
        # Control flags
        self.is_running = True
        self.is_connected = False
        self.is_speaking = False
        self.websocket = None
        
        # Audio queues
        self.audio_input_queue = queue.Queue()
        self.audio_output_queue = queue.Queue()
        
        # Interruption keywords
        self.interruption_keywords = [
            'stop', 'halt', 'pause', 'wait', 'hold', 'hold on',
            'excuse me', 'sorry', 'pardon', 'one moment',
            'ok', 'okay', 'yes', 'yeah', 'got it',
            'quit', 'exit', 'bye', 'goodbye', 'done'
        ]
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully."""
        print(f"\n{Fore.YELLOW}🛑 Shutting down WebSocket chatbot...")
        self.is_running = False
        if self.websocket:
            asyncio.create_task(self.websocket.close())
        sys.exit(0)
        
    def _print_status(self, message: str, status_type: str = "info"):
        """Print colored status messages."""
        colors = {
            "info": Fore.CYAN,
            "success": Fore.GREEN,
            "warning": Fore.YELLOW,
            "error": Fore.RED,
            "user": Fore.BLUE,
            "assistant": Fore.MAGENTA,
            "websocket": Fore.LIGHTMAGENTA_EX
        }
        color = colors.get(status_type, Fore.WHITE)
        print(f"{color}{message}{Style.RESET_ALL}")
        
    def _detect_voice_activity(self, audio_data: bytes) -> bool:
        """Detect voice activity in audio data."""
        try:
            rms = audioop.rms(audio_data, 2)
            return rms > self.speech_threshold
        except Exception:
            return False
            
    def _check_interruption_keywords(self, text: str) -> bool:
        """Check if text contains interruption keywords."""
        text_lower = text.lower().strip()
        for keyword in self.interruption_keywords:
            if keyword in text_lower:
                return True
        return False
        
    async def _audio_input_handler(self):
        """Capture audio and send to WebSocket."""
        stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )
        
        self._print_status("🎤 Audio input started...", "info")
        
        try:
            while self.is_running and self.is_connected:
                try:
                    # Read audio data
                    audio_data = stream.read(self.chunk_size, exception_on_overflow=False)
                    
                    # Check for voice activity
                    if self._detect_voice_activity(audio_data):
                        # Encode audio as base64
                        encoded_audio = base64.b64encode(audio_data).decode('utf-8')
                        
                        # Send audio to WebSocket
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
                        self._print_status(f"Audio input error: {e}", "error")
                    break
                    
        finally:
            stream.stop_stream()
            stream.close()
            
    async def _audio_output_handler(self):
        """Handle audio output from WebSocket."""
        stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.sample_rate,
            output=True,
            frames_per_buffer=self.chunk_size
        )
        
        self._print_status("🔊 Audio output started...", "info")
        
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
                        self._print_status(f"Audio output error: {e}", "error")
                    break
                    
        finally:
            stream.stop_stream()
            stream.close()
            
    async def _handle_websocket_message(self, message: str):
        """Handle incoming WebSocket messages."""
        try:
            data = json.loads(message)
            message_type = data.get("type", "")
            
            # Debug: Print all message types
            if message_type not in ["response.audio.delta", "input_audio_buffer.append"]:
                self._print_status(f"📨 Received: {message_type}", "info")
            
            if message_type == "session.created":
                self._print_status("✅ WebSocket session created", "success")
                
            elif message_type == "input_audio_buffer.speech_started":
                self._print_status("🎤 Speech detected", "info")
                
            elif message_type == "input_audio_buffer.speech_stopped":
                self._print_status("🔄 Processing speech...", "info")
                # Commit the audio buffer for processing
                commit_message = {"type": "input_audio_buffer.commit"}
                await self.websocket.send(json.dumps(commit_message))
                
                # Create response immediately after committing
                self._print_status("🤖 Creating AI response...", "info")
                response_message = {
                    "type": "response.create",
                    "response": {
                        "modalities": ["text", "audio"],
                        "instructions": "You are a helpful AI assistant. Keep responses brief and conversational for voice interaction. Respond in 1-2 sentences maximum."
                    }
                }
                await self.websocket.send(json.dumps(response_message))
                
            elif message_type == "conversation.item.input_audio_transcription.completed":
                transcript = data.get("transcript", "")
                self._print_status(f"👤 You: {transcript}", "user")
                
                # Check for interruption keywords
                if self._check_interruption_keywords(transcript):
                    if any(word in transcript.lower() for word in ['quit', 'exit', 'bye', 'goodbye']):
                        self._print_status("👋 Goodbye! Thanks for chatting!", "success")
                        self.is_running = False
                        return
                    else:
                        # Send interruption signal
                        interrupt_message = {"type": "response.cancel"}
                        await self.websocket.send(json.dumps(interrupt_message))
                        self._print_status(f"🛑 Interruption: '{transcript}'", "warning")
                        return
                
                # Response already created after speech_stopped, just log the transcription
                
            elif message_type == "response.audio.delta":
                # Receive audio response
                audio_b64 = data.get("delta", "")
                if audio_b64:
                    audio_data = base64.b64decode(audio_b64)
                    self.audio_output_queue.put(audio_data)
                    
            elif message_type == "response.audio_transcript.delta":
                # Show AI response text
                text_delta = data.get("delta", "")
                if text_delta:
                    print(f"{Fore.MAGENTA}{text_delta}{Style.RESET_ALL}", end="", flush=True)
                    
            elif message_type == "response.audio_transcript.done":
                print()  # New line after complete response
                
            elif message_type == "response.done":
                self._print_status("✅ Response complete", "success")
                
            elif message_type == "error":
                error_info = data.get("error", {})
                error_code = error_info.get("code", "unknown")
                error_msg = error_info.get("message", "Unknown error")
                
                if "invalid_api_key" in error_code:
                    self._print_status("❌ Real-time API Access Required!", "error")
                    self._print_status("Your API key doesn't have Real-time API access.", "warning")
                    self._print_status("The Real-time API is currently in preview/beta.", "info")
                    self._print_status("\n📝 Recommendation: Use option 2 (Real-time FIXED) instead!", "success")
                    self._print_status("It provides excellent voice interaction with your current API key.", "info")
                    self._print_status("\n🚀 Run: ./start_chatbot.sh and choose option 2", "success")
                else:
                    self._print_status(f"❌ WebSocket error: {error_msg}", "error")
                
                # Stop the chatbot after API key error
                if "invalid_api_key" in error_code:
                    self.is_running = False
                
        except json.JSONDecodeError:
            self._print_status(f"❌ Invalid JSON received: {message}", "error")
        except Exception as e:
            self._print_status(f"❌ Message handling error: {e}", "error")
            
    async def _websocket_handler(self):
        """Main WebSocket connection handler."""
        try:
            self._print_status("🔌 Connecting to OpenAI Real-time API...", "websocket")
            
            # Create connection with proper headers
            async with websockets.connect(
                self.websocket_url,
                additional_headers=[
                    ("Authorization", f"Bearer {self.api_key}"),
                    ("OpenAI-Beta", "realtime=v1")
                ]
            ) as websocket:
                self.websocket = websocket
                self.is_connected = True
                
                self._print_status("✅ WebSocket connected!", "success")
                
                # Configure session
                session_config = {
                    "type": "session.update",
                    "session": {
                        "modalities": ["text", "audio"],
                        "instructions": "You are a helpful AI assistant. Keep responses brief and conversational for voice interaction. Respond in 1-2 sentences maximum.",
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
                            "silence_duration_ms": 500
                        }
                    }
                }
                await websocket.send(json.dumps(session_config))
                
                # Start audio handlers
                audio_input_task = asyncio.create_task(self._audio_input_handler())
                audio_output_task = asyncio.create_task(self._audio_output_handler())
                
                # Listen for messages
                while self.is_running and self.is_connected:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=0.1)
                        await self._handle_websocket_message(message)
                    except asyncio.TimeoutError:
                        continue
                    except websockets.exceptions.ConnectionClosed:
                        self._print_status("🔌 WebSocket connection closed", "warning")
                        break
                        
                # Cancel audio tasks
                audio_input_task.cancel()
                audio_output_task.cancel()
                
        except Exception as e:
            self._print_status(f"❌ WebSocket connection error: {e}", "error")
        finally:
            self.is_connected = False
            self.websocket = None
            
    def print_instructions(self):
        """Print usage instructions."""
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}🌐 WEBSOCKET REAL-TIME VOICE CHATBOT")
        print(f"{Fore.CYAN}{'='*70}")
        print(f"{Fore.GREEN}Features:")
        print(f"{Fore.WHITE}• 🌐 True WebSocket streaming")
        print(f"{Fore.WHITE}• 🎤 Real-time bidirectional audio")
        print(f"{Fore.WHITE}• 🛑 Built-in interruption support")
        print(f"{Fore.WHITE}• ⚡ Ultra-low latency")
        print(f"{Fore.WHITE}• 📁 No temporary files")
        print(f"{Fore.YELLOW}Interruption Commands:")
        print(f"{Fore.WHITE}• Say {Fore.RED}'stop'{Fore.WHITE}, {Fore.RED}'hold on'{Fore.WHITE}, {Fore.RED}'wait'{Fore.WHITE} to interrupt")
        print(f"{Fore.WHITE}• Say {Fore.RED}'ok'{Fore.WHITE}, {Fore.RED}'yes'{Fore.WHITE}, {Fore.RED}'got it'{Fore.WHITE} to acknowledge")
        print(f"{Fore.YELLOW}Exit Commands:")
        print(f"{Fore.WHITE}• Say {Fore.YELLOW}'quit'{Fore.WHITE}, {Fore.YELLOW}'exit'{Fore.WHITE}, {Fore.YELLOW}'bye'{Fore.WHITE}, {Fore.YELLOW}'goodbye'{Fore.WHITE}")
        print(f"{Fore.WHITE}• Press {Fore.RED}Ctrl+C{Fore.WHITE} for immediate exit")
        print(f"{Fore.CYAN}{'='*70}\n")
        
    async def run(self):
        """Main run method."""
        try:
            self.print_instructions()
            await self._websocket_handler()
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
            
        self._print_status("\n👋 WebSocket voice chatbot ended!", "success")

async def main():
    """Main entry point."""
    try:
        chatbot = WebSocketVoiceChatbot()
        await chatbot.run()
    except Exception as e:
        print(f"{Fore.RED}❌ Failed to start WebSocket chatbot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())