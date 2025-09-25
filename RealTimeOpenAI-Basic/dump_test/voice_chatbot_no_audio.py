#!/usr/bin/env python3
"""
Real-time Voice Chatbot with OpenAI (No Audio Playback Version)
Features:
- Real-time voice input
- Text responses (no audio output to avoid ffmpeg dependency)
- Modern ChatGPT capabilities
- Terminal-based interface
"""

import os
import sys
import time
import tempfile
import wave
from typing import Optional, List, Dict
from pathlib import Path

import pyaudio
import speech_recognition as sr
import numpy as np
from colorama import init, Fore, Back, Style
from dotenv import load_dotenv
import openai

# Initialize colorama for cross-platform colored output
init(autoreset=True)

class VoiceChatbot:
    def __init__(self):
        """Initialize the voice chatbot with OpenAI and audio configurations."""
        # Clear any existing environment variable to force loading from .env
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
        load_dotenv()
        
        # OpenAI Configuration
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.voice_model = os.getenv('VOICE_MODEL', 'alloy')
        self.speech_model = os.getenv('SPEECH_MODEL', 'whisper-1')
        self.tts_model = os.getenv('TTS_MODEL', 'tts-1-hd')
        
        # Audio Configuration
        self.sample_rate = int(os.getenv('SAMPLE_RATE', 16000))
        self.chunk_size = int(os.getenv('CHUNK_SIZE', 1024))
        self.channels = int(os.getenv('CHANNELS', 1))
        
        # Audio components
        self.audio = pyaudio.PyAudio()
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone(sample_rate=self.sample_rate)
        
        # Control flags
        self.is_listening = False
        self.is_speaking = False
        self.is_running = True
        
        # Conversation history
        self.conversation_history: List[Dict[str, str]] = [
            {"role": "system", "content": "You are a helpful AI assistant. Keep your responses conversational and concise for voice interaction. Respond naturally as if having a spoken conversation."}
        ]
        
        # Calibrate microphone
        self._calibrate_microphone()
        
    def _calibrate_microphone(self):
        """Calibrate microphone for ambient noise."""
        print(f"{Fore.YELLOW}🎤 Calibrating microphone for ambient noise...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
        print(f"{Fore.GREEN}✅ Microphone calibrated!")
        
    def _print_status(self, message: str, status_type: str = "info"):
        """Print colored status messages."""
        colors = {
            "info": Fore.CYAN,
            "success": Fore.GREEN,
            "warning": Fore.YELLOW,
            "error": Fore.RED,
            "user": Fore.BLUE,
            "assistant": Fore.MAGENTA
        }
        color = colors.get(status_type, Fore.WHITE)
        print(f"{color}{message}{Style.RESET_ALL}")
        
    def listen_for_speech(self) -> Optional[str]:
        """Listen for speech input with timeout."""
        try:
            self._print_status("🎤 Listening for speech... (speak now, 5 second timeout)", "info")
            
            with self.microphone as source:
                # Listen for audio with timeout
                try:
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                except sr.WaitTimeoutError:
                    self._print_status("⏰ No speech detected within timeout", "warning")
                    return None
                
            # Transcribe audio using OpenAI Whisper
            self._print_status("🔄 Transcribing...", "info")
            
            # Save audio to temporary file for OpenAI
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
                with wave.open(temp_audio.name, 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)  # 16-bit
                    wf.setframerate(self.sample_rate)
                    wf.writeframes(audio.get_wav_data())
                
                # Transcribe using OpenAI Whisper
                with open(temp_audio.name, 'rb') as audio_file:
                    transcript = self.client.audio.transcriptions.create(
                        model=self.speech_model,
                        file=audio_file,
                        language="en"
                    )
                
                # Clean up temporary file
                os.unlink(temp_audio.name)
                
                return transcript.text.strip()
                
        except sr.UnknownValueError:
            self._print_status("❌ Could not understand audio", "error")
            return None
        except sr.RequestError as e:
            self._print_status(f"❌ Error with speech recognition: {e}", "error")
            return None
        except Exception as e:
            self._print_status(f"❌ Error in speech recognition: {e}", "error")
            return None
            
    def get_ai_response(self, user_input: str) -> Optional[str]:
        """Get AI response from OpenAI."""
        try:
            # Add user message to conversation history
            self.conversation_history.append({"role": "user", "content": user_input})
            
            self._print_status("🤖 Thinking...", "info")
            
            # Get response from OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4",  # Use GPT-4 for better responses
                messages=self.conversation_history,
                max_tokens=150,  # Keep responses concise for voice
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Add AI response to conversation history
            self.conversation_history.append({"role": "assistant", "content": ai_response})
            
            # Keep conversation history manageable
            if len(self.conversation_history) > 20:
                # Keep system message and last 18 messages
                self.conversation_history = [self.conversation_history[0]] + self.conversation_history[-18:]
                
            return ai_response
            
        except Exception as e:
            self._print_status(f"❌ Error getting AI response: {e}", "error")
            return None
            
    def print_instructions(self):
        """Print usage instructions."""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}🎙️  REAL-TIME VOICE CHATBOT (Voice Input Only)")
        print(f"{Fore.CYAN}{'='*60}")
        print(f"{Fore.GREEN}Instructions:")
        print(f"{Fore.WHITE}• The bot will listen for 5 seconds after each prompt")
        print(f"{Fore.WHITE}• Speak clearly when prompted")
        print(f"{Fore.WHITE}• AI responses will be displayed as text")
        print(f"{Fore.WHITE}• Say {Fore.YELLOW}'quit'{Fore.WHITE} or {Fore.YELLOW}'exit'{Fore.WHITE} to end the conversation")
        print(f"{Fore.WHITE}• Press {Fore.RED}Ctrl+C{Fore.WHITE} to force quit")
        print(f"{Fore.CYAN}{'='*60}\n")
        
    def run(self):
        """Main conversation loop."""
        try:
            self.print_instructions()
            
            while self.is_running:
                try:
                    # Listen for user input
                    user_input = self.listen_for_speech()
                    
                    if user_input is None:
                        # Ask if user wants to continue
                        print(f"{Fore.YELLOW}No speech detected. Press Enter to try again, or type 'quit' to exit:")
                        user_choice = input().strip().lower()
                        if user_choice in ['quit', 'exit', 'q']:
                            break
                        continue
                        
                    if not user_input.strip():
                        self._print_status("⚠️ No speech detected, please try again.", "warning")
                        continue
                    
                    # Check for quit commands
                    if user_input.lower().strip() in ['quit', 'exit', 'goodbye', 'bye']:
                        self._print_status("👋 Goodbye! Thanks for chatting!", "success")
                        break
                        
                    # Display user input
                    self._print_status(f"👤 You: {user_input}", "user")
                    
                    # Get AI response
                    ai_response = self.get_ai_response(user_input)
                    
                    if ai_response is None:
                        self._print_status("⚠️ Failed to get AI response, please try again.", "warning")
                        continue
                        
                    # Display AI response (text only, no audio)
                    self._print_status(f"🤖 Assistant: {ai_response}", "assistant")
                    
                    print()  # Add spacing between conversations
                    
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    self._print_status(f"❌ Unexpected error: {e}", "error")
                    
        except KeyboardInterrupt:
            pass
        finally:
            self.cleanup()
            
    def cleanup(self):
        """Clean up resources."""
        self.is_running = False
        self.audio.terminate()
        self._print_status("\n👋 Goodbye! Thanks for chatting!", "success")

def main():
    """Main entry point."""
    # Check for required environment variables
    if not os.getenv('OPENAI_API_KEY'):
        print(f"{Fore.RED}❌ Error: OPENAI_API_KEY not found in environment variables.")
        print(f"{Fore.YELLOW}Please create a .env file with your OpenAI API key.")
        print(f"{Fore.YELLOW}See .env.example for reference.")
        sys.exit(1)
        
    try:
        chatbot = VoiceChatbot()
        chatbot.run()
    except Exception as e:
        print(f"{Fore.RED}❌ Failed to start chatbot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()