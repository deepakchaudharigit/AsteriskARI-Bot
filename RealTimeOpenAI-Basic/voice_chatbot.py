#!/usr/bin/env python3
"""
OpenAI Realtime API Voice Chatbot - CLEAN VERSION
Clean conversation output with minimal debug information
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
from weather_tool import weather_tool

init(autoreset=True)
logging.basicConfig(level=logging.WARNING)  # Reduce logging
logger = logging.getLogger(__name__)

class RealtimeVoiceChatbot:
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
        self.is_listening = False
        self.is_ai_speaking = False
        self.waiting_for_response = False
        self.response_delay_seconds = 10
        
        self.quit_keywords = ['quit', 'exit', 'bye', 'goodbye', 'stop chatbot', 'end chat']
        
        signal.signal(signal.SIGINT, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        print(f"\n{Fore.YELLOW}👋 Goodbye!")
        self.is_running = False
        self.is_connected = False
        self.waiting_for_response = False
        # Don't call sys.exit(0) here to avoid SystemExit in async tasks
        
    def _print_status(self, message: str, status_type: str = "info"):
        colors = {
            "info": Fore.CYAN, "success": Fore.GREEN, "warning": Fore.YELLOW,
            "error": Fore.RED, "user": Fore.BLUE, "assistant": Fore.MAGENTA,
            "listening": Fore.LIGHTBLUE_EX
        }
        color = colors.get(status_type, Fore.WHITE)
        print(f"{color}{message}{Style.RESET_ALL}")
        
    async def _delayed_response(self):
        """Wait for specified delay then create response"""
        try:
            # Show listening state for the delay period
            for i in range(self.response_delay_seconds):
                if not self.is_running or not self.waiting_for_response:
                    return
                print(f"\r{Fore.LIGHTBLUE_EX}Listening...{Style.RESET_ALL}", end="", flush=True)
                await asyncio.sleep(1)
            
            # After delay, create the response
            if self.waiting_for_response and self.is_running:
                await self._create_response()
                
        except Exception as e:
            logger.error(f"Error in delayed response: {e}")
            
    async def _create_response(self):
        """Create response to user input"""
        try:
            self.waiting_for_response = False
            response_create = {
                "type": "response.create",
                "response": {
                    "modalities": ["text", "audio"],
                    "instructions": "Respond briefly and conversationally to the user's input."
                }
            }
            if self.websocket:
                await self.websocket.send(json.dumps(response_create))
        except Exception as e:
            logger.error(f"Error creating response: {e}")
        
    def _check_quit_keywords(self, text: str) -> bool:
        text_lower = text.lower().strip()
        return any(keyword in text_lower for keyword in self.quit_keywords)
        
    async def _audio_input_handler(self):
        stream = self.audio.open(
            format=self.format, channels=self.channels, rate=self.sample_rate,
            input=True, frames_per_buffer=self.chunk_size
        )
        
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
        
        # Debug function-related events
        if "function" in event_type.lower() or "tool" in event_type.lower() or "output_item" in event_type:
            print(f"\n{Fore.CYAN}🔧 Event: {event_type}{Style.RESET_ALL}")
        
        if event_type == "session.created":
            self._print_status("✅ Connected to OpenAI Realtime API", "success")
            
        elif event_type == "session.updated":
            self._print_status("🎙️ Ready for conversation - speak naturally!", "success")
            
        elif event_type == "input_audio_buffer.speech_started":
            # Cancel any waiting response if user starts speaking again
            if self.waiting_for_response:
                self.waiting_for_response = False
                
            if not self.is_listening:
                print(f"\n{Fore.LIGHTGREEN_EX}🎤 You are speaking...{Style.RESET_ALL}", end="", flush=True)
                self.is_listening = True
            
        elif event_type == "input_audio_buffer.speech_stopped":
            if self.is_listening:
                print(f"\r{Fore.LIGHTBLUE_EX}Listening...{Style.RESET_ALL}", end="", flush=True)
                self.is_listening = False
                self.waiting_for_response = True
            
            # Wait 10 seconds before creating response
            asyncio.create_task(self._delayed_response())
            
        elif event_type == "conversation.item.input_audio_transcription.completed":
            transcript = event.get("transcript", "")
            if transcript.strip():  # Only show if there's actual content
                print(f"\r{Fore.BLUE}👤 You: {transcript}{Style.RESET_ALL}")
            else:
                print(f"\r{Fore.YELLOW}(No speech detected){Style.RESET_ALL}")
            
            if self._check_quit_keywords(transcript):
                self._print_status("👋 Goodbye! Thanks for chatting!", "success")
                self.is_running = False
                return
                
        elif event_type == "response.created":
            print(f"{Fore.MAGENTA}🤖 Assistant: {Style.RESET_ALL}", end="", flush=True)
            self.is_ai_speaking = True
            
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
            if text_delta and self.is_ai_speaking:
                print(f"{Fore.MAGENTA}{text_delta}{Style.RESET_ALL}", end="", flush=True)
                
        elif event_type == "response.audio_transcript.done":
            if self.is_ai_speaking:
                print()  # New line after complete response
                self.is_ai_speaking = False
        
        elif event_type == "response.output_item.added":
            # Handle function call output items
            item = event.get("item", {})
            if item.get("type") == "function_call":
                function_name = item.get("name", "")
                call_id = item.get("call_id", "")
                print(f"\n{Fore.YELLOW}🔧 Calling function: {function_name}{Style.RESET_ALL}")
                
        elif event_type == "response.output_item.done":
            # Function call completed
            item = event.get("item", {})
            if item.get("type") == "function_call":
                function_name = item.get("name", "")
                call_id = item.get("call_id", "")
                arguments = item.get("arguments", "")
                
                if function_name == "get_weather":
                    try:
                        args = json.loads(arguments)
                        location = args.get("location", "")
                        if location:
                            print(f"\n{Fore.YELLOW}🌤️ Getting weather for {location}...{Style.RESET_ALL}")
                            
                            # Execute weather lookup
                            weather_result = await weather_tool.execute(location)
                            
                            # Send function result back to OpenAI
                            function_result = {
                                "type": "conversation.item.create",
                                "item": {
                                    "type": "function_call_output",
                                    "call_id": call_id,
                                    "output": weather_result
                                }
                            }
                            await self.websocket.send(json.dumps(function_result))
                            
                            # Create response with weather data
                            await self._create_response()
                            
                    except Exception as e:
                        logger.error(f"Weather function error: {e}")
                        # Send error response
                        error_result = {
                            "type": "conversation.item.create",
                            "item": {
                                "type": "function_call_output",
                                "call_id": call_id,
                                "output": "Sorry, I couldn't get the weather information right now."
                            }
                        }
                        await self.websocket.send(json.dumps(error_result))
                        await self._create_response()
            
        elif event_type == "response.done":
            if self.is_ai_speaking:
                print()  # Ensure new line
                self.is_ai_speaking = False
            # Reset waiting state when response is complete
            self.waiting_for_response = False
            
        elif event_type == "response.cancelled":
            if self.is_ai_speaking:
                print(f"\n{Fore.YELLOW}🛑 [Interrupted]{Style.RESET_ALL}")
                self.is_ai_speaking = False
            
        elif event_type == "error":
            error_info = event.get("error", {})
            error_code = error_info.get("code", "unknown")
            error_message = error_info.get("message", "Unknown error")
            
            # Only show important errors, not "response in progress" errors
            if "invalid_api_key" in error_code:
                self._print_status("❌ Invalid API key for Realtime API", "error")
                self._print_status("Try option 3 (Real-time FIXED) instead", "info")
            elif "response in progress" not in error_message.lower():
                self._print_status(f"⚠️ {error_message}", "warning")
                
    async def _realtime_connection_handler(self):
        try:
            self._print_status("🔌 Connecting to OpenAI Realtime API...", "info")
            
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
                
                # Configure session with weather function
                session_config = {
                    "type": "session.update",
                    "session": {
                        "modalities": ["text", "audio"],
                        "tools": [weather_tool.get_function_definition()],
                        "instructions": "You are a helpful and friendly AI assistant with access to real-time weather information. Engage in natural conversation, be responsive to the user's needs, and keep responses conversational and helpful. When users ask about weather, use the get_weather function to provide current, accurate information. Show empathy when appropriate and ask clarifying questions if needed.",
                        "voice": "alloy",
                        "input_audio_format": "pcm16",
                        "output_audio_format": "pcm16",
                        "input_audio_transcription": {"model": "whisper-1"},
                        "turn_detection": {
                            "type": "server_vad",
                            "threshold": 0.8,
                            "prefix_padding_ms": 200,
                            "silence_duration_ms": 4000
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
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}🎙️  REALTIME VOICE CHATBOT")
        print(f"{Fore.CYAN}{'='*60}")
        print(f"{Fore.GREEN}• Have natural conversations with AI")
        print(f"{Fore.GREEN}• AI responds empathetically and helpfully")
        print(f"{Fore.GREEN}• Ask about weather in any city (real-time data)")
        print(f"{Fore.GREEN}• Assistant waits 10 seconds before responding (shows 'Listening...')")
        print(f"{Fore.GREEN}• Interrupt anytime by speaking during the listening period")
        print(f"{Fore.YELLOW}• Say 'quit', 'exit', 'bye' to end")
        print(f"{Fore.YELLOW}• Press Ctrl+C for immediate exit")
        print(f"{Fore.CYAN}{'='*60}\n")
        
    async def run(self):
        try:
            self.print_instructions()
            await self._realtime_connection_handler()
        except KeyboardInterrupt:
            self.is_running = False
            self.is_connected = False
            self.waiting_for_response = False
        finally:
            self.cleanup()
            
    def cleanup(self):
        self.is_running = False
        self.is_connected = False
        try:
            self.audio.terminate()
        except:
            pass
        print(f"\n{Fore.GREEN}👋 Chat ended!{Style.RESET_ALL}")

async def main():
    try:
        chatbot = RealtimeVoiceChatbot()
        await chatbot.run()
    except Exception as e:
        print(f"{Fore.RED}❌ Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())