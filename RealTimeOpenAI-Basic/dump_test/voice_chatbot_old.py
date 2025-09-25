#!/usr/bin/env python3
"""
Real-time Voice Chatbot with OpenAI
Features:
- Real-time voice input/output
- Interruptive support
- Modern ChatGPT voice capabilities
- Terminal-based interface
"""

import os
import sys
import time
import threading
import queue
import tempfile
import wave
import json
from typing import Optional, List, Dict, Any
from pathlib import Path

import pyaudio
import speech_recognition as sr
import keyboard
import numpy as np
from colorama import init, Fore, Back, Style
from dotenv import load_dotenv
import openai
from pydub import AudioSegment
from pydub.playback import play
import webrtcvad

# Initialize colorama for cross-platform colored output
init(autoreset=True)

class VoiceChatbot:
    def __init__(self):
        """Initialize the voice chatbot with OpenAI and audio configurations."""
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
        
        # Voice Activity Detection
        self.vad = webrtcvad.Vad(2)  # Aggressiveness level 0-3
        
        # Control flags
        self.is_listening = False
        self.is_speaking = False
        self.should_interrupt = False
        self.is_running = True
        
        # Conversation history
        self.conversation_history: List[Dict[str, str]] = [
            {"role": "system", "content": "You are a helpful AI assistant. Keep your responses conversational and concise for voice interaction. Respond naturally as if having a spoken conversation."}
        ]
        
        # Audio queues for threading
        self.audio_queue = queue.Queue()
        self.response_queue = queue.Queue()
        
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
        
    def _detect_voice_activity(self, audio_data: bytes) -> bool:
        """Detect voice activity in audio data."""
        try:
            # Convert audio data to the format expected by webrtcvad
            # webrtcvad expects 16-bit PCM audio at 8kHz, 16kHz, or 32kHz
            return self.vad.is_speech(audio_data, self.sample_rate)
        except Exception:
            return False
            
    def listen_for_speech(self) -> Optional[str]:
        """Listen for speech input with voice activity detection."""
        try:
            self._print_status("🎤 Listening... (Press SPACE to start speaking, ESC to quit)", "info")
            
            # Wait for space key to start recording
            while self.is_running:
                if keyboard.is_pressed('space'):
                    break
                if keyboard.is_pressed('esc'):
                    return None
                time.sleep(0.1)
                
            if not self.is_running:
                return None
                
            self._print_status("🔴 Recording... (Release SPACE to stop)", "warning")
            self.is_listening = True
            
            # Record audio while space is held
            frames = []
            stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            while keyboard.is_pressed('space') and self.is_running:
                data = stream.read(self.chunk_size, exception_on_overflow=False)
                frames.append(data)
                
            stream.stop_stream()
            stream.close()
            self.is_listening = False
            
            if not frames:
                return None
                
            # Save audio to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
                wf = wave.open(temp_audio.name, 'wb')
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
                wf.setframerate(self.sample_rate)
                wf.writeframes(b''.join(frames))
                wf.close()
                
                # Transcribe audio using OpenAI Whisper
                self._print_status("🔄 Transcribing...", "info")
                with open(temp_audio.name, 'rb') as audio_file:
                    transcript = self.client.audio.transcriptions.create(
                        model=self.speech_model,
                        file=audio_file,
                        language="en"
                    )
                
                # Clean up temporary file
                os.unlink(temp_audio.name)
                
                return transcript.text.strip()
                
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
            
    def speak_response(self, text: str):
        """Convert text to speech and play it."""
        try:
            self._print_status("🔊 Speaking...", "info")
            self.is_speaking = True
            self.should_interrupt = False
            
            # Generate speech using OpenAI TTS
            response = self.client.audio.speech.create(
                model=self.tts_model,
                voice=self.voice_model,
                input=text,
                speed=1.0
            )
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_audio:
                response.stream_to_file(temp_audio.name)
                
                # Load and play audio with interruption support
                audio_segment = AudioSegment.from_mp3(temp_audio.name)
                
                # Convert to raw audio data for chunk-by-chunk playback
                raw_data = audio_segment.raw_data
                frame_rate = audio_segment.frame_rate
                channels = audio_segment.channels
                sample_width = audio_segment.sample_width
                
                # Calculate chunk size for ~100ms chunks
                chunk_duration_ms = 100
                bytes_per_ms = (frame_rate * channels * sample_width) // 1000
                chunk_size = bytes_per_ms * chunk_duration_ms
                
                # Play audio in chunks to allow interruption
                stream = self.audio.open(
                    format=self.audio.get_format_from_width(sample_width),
                    channels=channels,
                    rate=frame_rate,
                    output=True
                )
                
                for i in range(0, len(raw_data), chunk_size):
                    if self.should_interrupt or not self.is_running:
                        break
                        
                    chunk = raw_data[i:i + chunk_size]
                    stream.write(chunk)
                    
                    # Check for interruption (space key pressed)
                    if keyboard.is_pressed('space'):
                        self.should_interrupt = True
                        self._print_status("⏹️ Speech interrupted!", "warning")
                        break
                        
                stream.stop_stream()
                stream.close()
                
                # Clean up temporary file
                os.unlink(temp_audio.name)
                
        except Exception as e:
            self._print_status(f"❌ Error in text-to-speech: {e}", "error")
        finally:
            self.is_speaking = False
            
    def print_instructions(self):
        """Print usage instructions."""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}🎙️  REAL-TIME VOICE CHATBOT")
        print(f"{Fore.CYAN}{'='*60}")
        print(f"{Fore.GREEN}Instructions:")
        print(f"{Fore.WHITE}• Press and hold {Fore.YELLOW}SPACE{Fore.WHITE} to record your voice")
        print(f"{Fore.WHITE}• Release {Fore.YELLOW}SPACE{Fore.WHITE} to stop recording and send")
        print(f"{Fore.WHITE}• Press {Fore.YELLOW}SPACE{Fore.WHITE} while AI is speaking to interrupt")
        print(f"{Fore.WHITE}• Press {Fore.RED}ESC{Fore.WHITE} to quit the application")
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
                        if keyboard.is_pressed('esc'):
                            break
                        continue
                        
                    if not user_input.strip():
                        self._print_status("⚠️ No speech detected, please try again.", "warning")
                        continue
                        
                    # Display user input
                    self._print_status(f"👤 You: {user_input}", "user")
                    
                    # Get AI response
                    ai_response = self.get_ai_response(user_input)
                    
                    if ai_response is None:
                        self._print_status("⚠️ Failed to get AI response, please try again.", "warning")
                        continue
                        
                    # Display AI response
                    self._print_status(f"🤖 Assistant: {ai_response}", "assistant")
                    
                    # Speak the response
                    self.speak_response(ai_response)
                    
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