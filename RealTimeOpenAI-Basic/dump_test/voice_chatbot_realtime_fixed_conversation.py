#!/usr/bin/env python3
"""
OpenAI Realtime API Voice Chatbot - FIXED CONVERSATION
FIXED: Proper response creation after speech detection
"""

import asyncio
import websockets
import json
import base64
import os
import sys
import signal
import queue
import logging
from typing import Dict, Any
import pyaudio
from colorama import init, Fore, Style
from dotenv import load_dotenv

init(autoreset=True)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealtimeVoiceChatbotFixed:
    def __init__(self):
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
        load_dotenv()
        
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found")
        
        self.websocket_url = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01"
        
        # Audio config
        self.sample_rate = 24000
        self.chunk_size = 1024
        self.channels = 1
        self.format = pyaudio.paInt16
        self.audio = pyaudio.PyAudio()
        
        # Control flags
        self.is_running = True
        self.is_connected = False
        self.websocket = None
        self.audio_output_queue = queue.Queue()
        
        self.quit_keywords = ['quit', 'exit', 'bye', 'goodbye', 'stop chatbot', 'end chat']
        
        signal.signal(signal.SIGINT, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        print(f"\n{Fore.YELLOW}🛑 Shutting down...")
        self.is_running = False
        sys.exit(0)
        
    def _print_status(self, message: str, status_type: str = "info"):
        colors = {
            "info": Fore.CYAN, "success": Fore.GREEN, "warning": Fore.YELLOW,
            "error": Fore.RED, "user": Fore.BLUE, "assistant": Fore.MAGENTA,
            "realtime": Fore.LIGHTMAGENTA_EX, "audio": Fore.LIGHTGREEN_EX
        }
        color = colors.get(status_type, Fore.WHITE)
        print(f"{color}{message}{Style.RESET_ALL}")
        
    def _check_quit_keywords(self, text: str) -> bool:
        text_lower = text.lower().strip()
        return any(keyword in text_lower for keyword in self.quit_keywords)
        
    async def _audio_input_handler(self):
        stream = self.audio.open(
            format=self.format, channels=self.channels, rate=self.sample_rate,
            input=True, frames_per_buffer=self.chunk_size
        )
        
        self._print_status("🎤 Audio input streaming started", "audio")
        
        try:
            while self.is_running and self.is_connected:
                try:
                    audio_data = stream.read(self.chunk_size, exception_on_overflow=False)
                    encoded_audio = base64.b64encode(audio_data).decode('utf-8')
                    
                    if self.websocket:
                        message = {"type": "input_audio_buffer.append", "audio": encoded_audio}
                        await self.websocket.send(json.dumps(message))
                    
                    await asyncio.sleep(0.01)
                except Exception as e:
                    if self.is_running:
                        logger.error(f"Audio input error: {e}")
                    break
        finally:
            stream.stop_stream()
            stream.close()
            
    async def _audio_output_handler(self):
        stream = self.audio.open(
            format=self.format, channels=self.channels, rate=self.sample_rate,
            output=True, frames_per_buffer=self.chunk_size
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
        event_type = event.get("type", "")
        
        # Only show essential events for clean conversation flow
        
        if event_type == "session.created":
            self._print_status("✅ Realtime session created", "success")
            
        elif event_type == "session.updated":
            self._print_status("🔧 Session configured", "info")
            
        elif event_type == "input_audio_buffer.speech_started":
            self._print_status("🎤 Speech detected", "info")
            
        elif event_type == "input_audio_buffer.speech_stopped":
            self._print_status("🔄 Speech ended, creating response...", "info")
            # FIXED: Create response immediately after speech stops
            response_create = {
                "type": "response.create",
                "response": {
                    "modalities": ["text", "audio"],
                    "instructions": "Respond briefly and conversationally to the user's input."
                }
            }
            if self.websocket:
                await self.websocket.send(json.dumps(response_create))
                self._print_status("🤖 AI response requested", "info")
            
        elif event_type == "conversation.item.input_audio_transcription.completed":
            transcript = event.get("transcript", "")
            self._print_status(f"👤 You: {transcript}", "user")
            
            if self._check_quit_keywords(transcript):
                self._print_status("👋 Goodbye!", "success")
                self.is_running = False
                return
                
        elif event_type == "response.created":
            self._print_status("🤖 AI response started", "info")
            
        elif event_type == "response.audio.delta":
            audio_b64 = event.get("delta", "")
            if audio_b64:
                try:
                    audio_data = base64.b64decode(audio_b64)
                    self.audio_output_queue.put(audio_data)
                except Exception as e:
                    logger.error(f"Audio decode error: {e}")
                    
        elif event_type == "response.audio_transcript.delta":
            text_delta = event.get("delta", "")
            if text_delta:
                print(f"{Fore.MAGENTA}{text_delta}{Style.RESET_ALL}", end="", flush=True)
                
        elif event_type == "response.audio_transcript.done":
            print()
            
        elif event_type == "response.done":
            self._print_status("✅ Response completed", "success")
            
        elif event_type == "response.cancelled":
            self._print_status("🛑 Response interrupted", "warning")
            
        elif event_type == "error":
            error_info = event.get("error", {})
            error_code = error_info.get("code", "unknown")
            error_message = error_info.get("message", "Unknown error")
            
            if "invalid_api_key" in error_code:
                self._print_status("❌ Invalid API key for Realtime API", "error")
                self._print_status("Try option 2 (Real-time FIXED) instead", "info")
            else:
                self._print_status(f"❌ Error: {error_message}", "error")
                
    async def _realtime_connection_handler(self):
        try:
            self._print_status("🔌 Connecting to OpenAI Realtime API...", "realtime")
            
            async with websockets.connect(
                self.websocket_url,
                additional_headers=[
                    ("Authorization", f"Bearer {self.api_key}"),
                    ("OpenAI-Beta", "realtime=v1")
                ],
                ping_interval=20, ping_timeout=10
            ) as websocket:
                self.websocket = websocket
                self.is_connected = True
                
                self._print_status("✅ Connected!", "success")
                
                # Configure session
                session_config = {
                    "type": "session.update",
                    "session": {
                        "modalities": ["text", "audio"],
                        "instructions": "You are a helpful AI assistant. Keep responses brief and conversational.",
                        "voice": "alloy",
                        "input_audio_format": "pcm16",
                        "output_audio_format": "pcm16",
                        "input_audio_transcription": {"model": "whisper-1"},
                        "turn_detection": {
                            "type": "server_vad",
                            "threshold": 0.5,
                            "prefix_padding_ms": 300,
                            "silence_duration_ms": 500
                        },
                        "temperature": 0.8
                    }
                }
                
                await websocket.send(json.dumps(session_config))
                
                # Start audio handlers
                audio_input_task = asyncio.create_task(self._audio_input_handler())
                audio_output_task = asyncio.create_task(self._audio_output_handler())
                
                # Main event loop
                while self.is_running and self.is_connected:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=0.1)
                        event = json.loads(message)
                        await self._handle_realtime_event(event)
                    except asyncio.TimeoutError:
                        continue
                    except websockets.exceptions.ConnectionClosed:
                        self._print_status("🔌 Connection closed", "warning")
                        break
                        
                # Cancel tasks
                audio_input_task.cancel()
                audio_output_task.cancel()
                
        except Exception as e:
            self._print_status(f"❌ Connection error: {e}", "error")
        finally:
            self.is_connected = False
            self.websocket = None
            
    def print_instructions(self):
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}🎙️  REALTIME API VOICE CHATBOT (FIXED)")
        print(f"{Fore.CYAN}{'='*70}")
        print(f"{Fore.GREEN}✅ FIXED: Proper conversation flow")
        print(f"{Fore.WHITE}• Just speak naturally - AI will respond")
        print(f"{Fore.WHITE}• Interrupt anytime by speaking")
        print(f"{Fore.WHITE}• Say 'quit', 'exit', 'bye' to end")
        print(f"{Fore.CYAN}{'='*70}\n")
        
    async def run(self):
        try:
            self.print_instructions()
            await self._realtime_connection_handler()
        except KeyboardInterrupt:
            pass
        finally:
            self.cleanup()
            
    def cleanup(self):
        self.is_running = False
        self.is_connected = False
        try:
            self.audio.terminate()
        except:
            pass
        self._print_status("\n👋 Ended!", "success")

async def main():
    try:
        chatbot = RealtimeVoiceChatbotFixed()
        await chatbot.run()
    except Exception as e:
        print(f"{Fore.RED}❌ Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())