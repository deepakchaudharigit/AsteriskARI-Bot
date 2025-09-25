#!/usr/bin/env python3
"""
NPCL Voice Assistant - Based on your existing clean voice chatbot
Behaves as NPCL power issue support customer care
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
import random
from typing import Dict, Any
import pyaudio
from colorama import init, Fore, Style
from dotenv import load_dotenv
from weather_tool import weather_tool

init(autoreset=True)
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class NPCLVoiceAssistant:
    """NPCL Customer Care Voice Assistant using OpenAI Realtime API"""
    
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
        
        # NPCL specific
        self.customer_names = ["Ram"]
        self.default_complaint = "1234"
        self.selected_name = None
        self.conversation_started = False
        
        signal.signal(signal.SIGINT, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        print(f"\n{Fore.YELLOW}👋 NPCL Customer Care ended!")
        self.is_running = False
        self.is_connected = False
        self.waiting_for_response = False
        # Don't call sys.exit(0) here to avoid SystemExit in async tasks
        # Let the cleanup happen naturally
        
    def _print_status(self, message: str, status_type: str = "info"):
        colors = {
            "info": Fore.CYAN, "success": Fore.GREEN, "warning": Fore.YELLOW,
            "error": Fore.RED, "user": Fore.BLUE, "assistant": Fore.MAGENTA,
            "npcl": Fore.LIGHTCYAN_EX
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
                    "instructions": "Respond as NPCL customer care representative. Be helpful and professional."
                }
            }
            if self.websocket:
                await self.websocket.send(json.dumps(response_create))
        except Exception as e:
            logger.error(f"Error creating response: {e}")
        
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
                    if self.is_running and self.is_connected:
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
                    if self.is_running and self.is_connected:
                        logger.error(f"Audio output error: {e}")
                    break
        finally:
            stream.stop_stream()
            stream.close()
            
    async def _handle_realtime_event(self, event: Dict[str, Any]):
        event_type = event.get("type", "")
        
        # Only show weather function calls, hide other debug events
        if event_type == "response.output_item.added":
            item = event.get("item", {})
            if item.get("type") == "function_call" and item.get("name") == "get_weather":
                print(f"\n{Fore.YELLOW}🌤️ Checking weather...{Style.RESET_ALL}")
        
        if event_type == "session.created":
            self._print_status("✅ Connected to NPCL Customer Care", "success")
            
        elif event_type == "session.updated":
            self._print_status("🏢 NPCL Customer Care System Ready", "npcl")
            # Auto-start conversation with welcome message
            if not self.conversation_started:
                await self._start_npcl_welcome()
            
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
            
            # Always wait 10 seconds before creating response (except for very first greeting)
            # For all user inputs, wait 10 seconds
            asyncio.create_task(self._delayed_response())
            
        elif event_type == "conversation.item.input_audio_transcription.completed":
            transcript = event.get("transcript", "")
            if transcript.strip():  # Only show if there's actual content
                print(f"\r{Fore.BLUE}👤 You: {transcript}{Style.RESET_ALL}")
            else:
                print(f"\r{Fore.YELLOW}(No speech detected){Style.RESET_ALL}")
            
            # Check for quit commands
            if any(word in transcript.lower() for word in ['quit', 'exit', 'bye', 'goodbye', 'disconnect']):
                self._print_status("👋 Thank you for calling NPCL! Have a great day!", "npcl")
                self.is_running = False
                return
                
        elif event_type == "response.created":
            print(f"{Fore.LIGHTCYAN_EX}🏢 NPCL Agent: {Style.RESET_ALL}", end="", flush=True)
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
                print(f"{Fore.LIGHTCYAN_EX}{text_delta}{Style.RESET_ALL}", end="", flush=True)
                
        elif event_type == "response.audio_transcript.done":
            if self.is_ai_speaking:
                print()
                self.is_ai_speaking = False
            
        elif event_type == "response.output_item.added":
            # Function call events are handled above in the main event check
            pass
                
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
                            
                            # Handle both string and dict responses
                            if isinstance(weather_result, dict):
                                result_text = weather_result.get("result", "Weather information unavailable")
                            else:
                                result_text = str(weather_result)
                            
                            print(f"\n{Fore.GREEN}✅ Weather data: {result_text[:60]}...{Style.RESET_ALL}")
                            
                            # Send function result back to OpenAI
                            function_result = {
                                "type": "conversation.item.create",
                                "item": {
                                    "type": "function_call_output",
                                    "call_id": call_id,
                                    "output": result_text
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
                print()
                self.is_ai_speaking = False
            # Reset waiting state when response is complete
            self.waiting_for_response = False
            
        elif event_type == "response.cancelled":
            if self.is_ai_speaking:
                print(f"\n{Fore.YELLOW}🛑 [Customer interrupted]{Style.RESET_ALL}")
                self.is_ai_speaking = False
            
        elif event_type == "error":
            error_info = event.get("error", {})
            error_code = error_info.get("code", "unknown")
            error_message = error_info.get("message", "Unknown error")
            
            if "invalid_api_key" in error_code:
                self._print_status("❌ Invalid API key for Realtime API", "error")
                self._print_status("Please check your OpenAI API key", "info")
            elif "response in progress" not in error_message.lower():
                self._print_status(f"⚠️ {error_message}", "warning")
    
    async def _start_npcl_welcome(self):
        """Start with automatic NPCL welcome message"""
        try:
            await asyncio.sleep(1)  # Small delay
            
            # Select random name for this session
            self.selected_name = random.choice(self.customer_names)
            
            # Create immediate welcome response
            welcome_response = {
                "type": "response.create",
                "response": {
                    "modalities": ["text", "audio"],
                    "instructions": "Say exactly: 'Welcome to NPCL Customer Care, how may I help you today?'"
                }
            }
            
            await self.websocket.send(json.dumps(welcome_response))
            
            self.conversation_started = True
            logger.info("NPCL welcome message sent")
            
        except Exception as e:
            logger.error(f"Error starting NPCL welcome: {e}")
    
    async def _start_npcl_conversation(self):
        """Start the NPCL conversation automatically"""
        try:
            await asyncio.sleep(1)  # Small delay
            
            # Select random name for this session
            self.selected_name = random.choice(self.customer_names)
            
            # Send initial message to trigger NPCL greeting
            initial_message = {
                "type": "conversation.item.create",
                "item": {
                    "type": "message",
                    "role": "user",
                    "content": [{
                        "type": "input_text",
                        "text": "hello"
                    }]
                }
            }
            
            await self.websocket.send(json.dumps(initial_message))
            
            # Set waiting state and start delayed response for initial greeting
            self.waiting_for_response = True
            asyncio.create_task(self._delayed_response())
            
            self.conversation_started = True
            logger.info("NPCL conversation started")
            
        except Exception as e:
            logger.error(f"Error starting NPCL conversation: {e}")
                
    async def _realtime_connection_handler(self):
        try:
            self._print_status("🔌 Connecting to NPCL Customer Care System...", "info")
            
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
                
                # Configure session with NPCL instructions and weather function
                session_config = {
                    "type": "session.update",
                    "session": {
                        "modalities": ["text", "audio"],
                        "tools": [{
                            "type": "function",
                            "name": "get_weather",
                            "description": "Get real-time weather information for cities in India, especially NCR region served by NPCL. Provides current temperature, conditions, humidity, and wind information.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "location": {
                                        "type": "string",
                                        "description": "City name in India (Delhi, Mumbai, Bangalore, Chennai, Kolkata, Noida, Greater Noida, Ghaziabad, Faridabad, Gurugram, etc.)"
                                    }
                                },
                                "required": ["location"]
                            }
                        }],
                        "instructions": f"""You are a helpful and professional customer care representative for NPCL (Noida Power Corporation Limited).

You have access to real-time weather information through the get_weather function. Use this when customers ask about weather conditions, especially in relation to power outages or service issues.

NATURAL CONVERSATION FLOW:
1. START with a warm, natural greeting: "Welcome to NPCL Customer Care, how may I help you today?"

2. LISTEN to the customer's concern and respond appropriately:
   - If they mention power outage/cut: Ask for their area/connection details
   - If they have a complaint number: Ask them to provide it for status check
   - If they want to register a complaint: Take their details and register it
   - If they ask about bills/payments: Guide them appropriately

3. WHEN NEEDED, ask for information naturally:
   - "Could you please provide your name for verification?"
   - "Which area are you calling from?"
   - "Do you have a complaint number I can check for you?"
   - "What exactly is the issue you're facing?"

4. HELPFUL RESPONSES:
   - For complaint status: "Let me check that for you... Your complaint [number] is being worked on by our technical team"
   - For new complaints: "I'll register this complaint for you. Your complaint number is [number]"
   - For general issues: Provide helpful guidance and next steps

SPEAKING STYLE - Natural Indian English:
- Use conversational phrases like "Let me check that for you", "I understand", "No problem at all"
- Be warm and patient: "I'm here to help you", "Don't worry, we'll sort this out"
- Speak clearly and at a comfortable pace
- When reading numbers, say each digit clearly: "zero zero zero five four three two one"
- Use respectful terms like "Sir/Madam" when appropriate
- Show empathy: "I understand how frustrating power cuts can be"

COMMON SCENARIOS TO HANDLE:
- Power outages and cuts
- Complaint registration and status
- Billing inquiries
- Connection issues
- Technical problems
- Weather-related inquiries (use get_weather function for current conditions)

WEATHER INTEGRATION:
- When customers ask about weather, use the get_weather function to provide real-time information
- Connect weather conditions to power service reliability
- For NPCL service areas (Noida, Greater Noida, Ghaziabad, Faridabad, Gurugram), mention power stability
- Examples: "What's the weather like?", "Is it raining in Noida?", "Weather in Delhi?"

Be responsive to what the customer actually says rather than following a script. Keep responses helpful, brief, and conversational. Always aim to resolve their issue or guide them to the right solution.""",
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
                        "temperature": 0.7  # Slightly higher for more natural responses
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
        print(f"{Fore.CYAN}🏢 NPCL CUSTOMER CARE VOICE ASSISTANT")
        print(f"{Fore.CYAN}{'='*70}")
        print(f"{Fore.GREEN}🎯 Natural Customer Support Experience")
        print(f"{Fore.WHITE}• Starts with natural greeting: 'Welcome to NPCL Customer Care, how may I help you?'")
        print(f"{Fore.WHITE}• Responds naturally to your actual concerns")
        print(f"{Fore.WHITE}• Asks for information when needed (name, area, complaint number)")
        print(f"{Fore.WHITE}• Handles power outages, complaints, billing inquiries, and weather information")
        print(f"{Fore.YELLOW}📞 Customer Interaction:")
        print(f"{Fore.WHITE}• Speak naturally about your power issues")
        print(f"{Fore.WHITE}• Mention complaint numbers, power cuts, billing questions, or ask about weather")
        print(f"{Fore.WHITE}• Assistant waits 10 seconds before responding (shows 'Listening...')")
        print(f"{Fore.WHITE}• Interrupt anytime by speaking during the listening period")
        print(f"{Fore.YELLOW}🚪 Exit Commands:")
        print(f"{Fore.WHITE}• Say 'quit', 'bye', 'disconnect' to end call")
        print(f"{Fore.WHITE}• Press Ctrl+C for immediate exit")
        print(f"{Fore.CYAN}{'='*70}\n")
        
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
        print(f"\n{Fore.GREEN}📞 NPCL Customer Care call ended!{Style.RESET_ALL}")

async def main():
    try:
        assistant = NPCLVoiceAssistant()
        await assistant.run()
    except Exception as e:
        print(f"{Fore.RED}❌ Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())