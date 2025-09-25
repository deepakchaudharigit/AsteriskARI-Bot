#!/usr/bin/env python3
"""
Fixed Real-time Voice Chatbot
Features:
- Prevents self-interruption during AI speech
- Real-time voice interaction with proper audio output
- Clean interruption handling
- Modern ChatGPT voice capabilities
"""

import os
import sys
import time
import threading
import queue
import tempfile
import wave
import audioop
import signal
from typing import Optional, List, Dict
from pathlib import Path

import pyaudio
import speech_recognition as sr
import numpy as np
from colorama import init, Fore, Back, Style
from dotenv import load_dotenv
import openai
import subprocess

# Initialize colorama for cross-platform colored output
init(autoreset=True)

class FixedVoiceChatbot:
    def __init__(self):
        """Initialize the fixed voice chatbot."""
        # Clear any existing environment variable to force loading from .env
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
        load_dotenv()
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # OpenAI Configuration
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.voice_model = os.getenv('VOICE_MODEL', 'alloy')
        self.speech_model = os.getenv('SPEECH_MODEL', 'whisper-1')
        self.tts_model = os.getenv('TTS_MODEL', 'tts-1')
        
        # Audio Configuration
        self.sample_rate = int(os.getenv('SAMPLE_RATE', 16000))
        self.chunk_size = int(os.getenv('CHUNK_SIZE', 1024))
        self.channels = int(os.getenv('CHANNELS', 1))
        
        # Audio components
        self.audio = pyaudio.PyAudio()
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone(sample_rate=self.sample_rate)
        
        # Voice Activity Detection parameters
        self.silence_threshold = 150
        self.speech_threshold = 450  # Even higher threshold for better stability
        self.min_speech_duration = 0.6  # Longer minimum to avoid false positives
        self.silence_duration = 1.0     # Longer silence for stability
        
        # Control flags
        self.is_listening = False
        self.is_speaking = False
        self.should_interrupt = False
        self.is_running = True
        self.continuous_listening = False
        self.processing_speech = False
        self.last_interrupt_time = 0
        self.audio_output_active = False  # NEW: Track when AI is outputting audio
        
        # Audio queues and buffers
        self.audio_queue = queue.Queue()
        self.speech_buffer = []
        self.current_audio_process = None
        
        # Conversation history
        self.conversation_history: List[Dict[str, str]] = [
            {"role": "system", "content": "You are a helpful AI assistant. Keep your responses brief and conversational for voice interaction. Respond in 1-2 sentences maximum."}
        ]
        
        # Threading events
        self.stop_speaking_event = threading.Event()
        self.speech_detected_event = threading.Event()
        
        # Calibrate microphone
        self._calibrate_microphone()
        
    def _signal_handler(self, signum, frame):
        """Handle Ctrl+C and other termination signals gracefully."""
        print(f"\n{Fore.YELLOW}\n🛑 Ctrl+C detected - Shutting down immediately...")
        self.is_running = False
        self.continuous_listening = False
        self.audio_output_active = False
        
        # Stop any ongoing audio immediately
        if self.current_audio_process:
            try:
                self.current_audio_process.terminate()
                self.current_audio_process.kill()  # Force kill if needed
            except:
                pass
        
        # Signal threads to stop
        self.stop_speaking_event.set()
        self.speech_detected_event.set()
        
        # Clean up audio immediately
        try:
            self.audio.terminate()
        except:
            pass
            
        print(f"{Fore.GREEN}👋 Goodbye! Voice chatbot terminated.")
        os._exit(0)  # Force exit immediately
        
    def _calibrate_microphone(self):
        """Calibrate microphone for optimal sensitivity."""
        print(f"{Fore.YELLOW}🎤 Calibrating microphone for voice interaction...")
        
        # Calibrate with speech_recognition
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
        
        # Measure ambient noise level
        print(f"{Fore.YELLOW}📊 Measuring ambient noise level...")
        noise_samples = []
        
        stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )
        
        for _ in range(int(2 * self.sample_rate / self.chunk_size)):  # 2 seconds
            data = stream.read(self.chunk_size, exception_on_overflow=False)
            rms = audioop.rms(data, 2)
            noise_samples.append(rms)
        
        stream.stop_stream()
        stream.close()
        
        # Set conservative thresholds to prevent self-interruption
        avg_noise = np.mean(noise_samples)
        max_noise = np.max(noise_samples)
        std_noise = np.std(noise_samples)
        
        # More conservative approach - higher threshold to avoid self-interruption
        self.silence_threshold = avg_noise + std_noise
        self.speech_threshold = max(avg_noise * 3.0, max_noise * 1.5, avg_noise + 4 * std_noise, 400)
        
        print(f"{Fore.GREEN}✅ Voice interaction calibration complete!")
        print(f"{Fore.CYAN}📈 Ambient noise: {avg_noise:.0f}, Speech threshold: {self.speech_threshold:.0f}")
        
    def _print_status(self, message: str, status_type: str = "info"):
        """Print colored status messages."""
        colors = {
            "info": Fore.CYAN,
            "success": Fore.GREEN,
            "warning": Fore.YELLOW,
            "error": Fore.RED,
            "user": Fore.BLUE,
            "assistant": Fore.MAGENTA,
            "listening": Fore.LIGHTBLUE_EX
        }
        color = colors.get(status_type, Fore.WHITE)
        print(f"{color}{message}{Style.RESET_ALL}")
        
    def _detect_voice_activity(self, audio_data: bytes) -> bool:
        """Voice activity detection with self-interruption prevention."""
        try:
            rms = audioop.rms(audio_data, 2)
            # Don't detect speech if AI is currently outputting audio
            if self.audio_output_active:
                return False
            return rms > self.speech_threshold
        except Exception:
            return False
            
    def _continuous_audio_monitor(self):
        """Continuously monitor audio with self-interruption prevention."""
        stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )
        
        speech_frames = []
        silence_frames = 0
        speech_detected = False
        last_detection_time = 0
        
        while self.continuous_listening and self.is_running:
            try:
                data = stream.read(self.chunk_size, exception_on_overflow=False)
                
                # Check for voice activity (with self-interruption prevention)
                has_voice = self._detect_voice_activity(data)
                
                if has_voice:
                    current_time = time.time()
                    if not speech_detected and current_time - last_detection_time > 2.0:
                        print(f"\n🎤 User speech detected!")
                        last_detection_time = current_time
                    speech_frames.append(data)
                    silence_frames = 0
                    
                    # Only interrupt if we're sure it's user speech (not AI output)
                    current_time = time.time()
                    if (self.is_speaking and not self.should_interrupt and not self.audio_output_active and
                        current_time - self.last_interrupt_time > 1.5):  # Even longer rate limit
                        self._print_status("🛑 User interruption detected!", "warning")
                        self.should_interrupt = True
                        self.stop_speaking_event.set()
                        self.last_interrupt_time = current_time
                        if self.current_audio_process:
                            try:
                                self.current_audio_process.terminate()
                            except:
                                pass
                    
                    speech_detected = True
                    
                else:
                    silence_frames += 1
                    
                    # If we had speech and now silence, process the speech
                    if speech_detected and silence_frames > int(self.silence_duration * self.sample_rate / self.chunk_size):
                        if len(speech_frames) > int(self.min_speech_duration * self.sample_rate / self.chunk_size) and not self.processing_speech:
                            print(f"\n✅ Processing user speech...")
                            # We have enough speech data
                            self.processing_speech = True
                            self.audio_queue.put(b''.join(speech_frames))
                            self.speech_detected_event.set()
                        
                        speech_frames = []
                        speech_detected = False
                        silence_frames = 0
                        
            except Exception as e:
                if self.is_running:
                    print(f"Audio monitoring error: {e}")
                break
                
        stream.stop_stream()
        stream.close()
        
    def listen_for_speech(self) -> Optional[str]:
        """Listen for speech with improved detection."""
        try:
            if not self.continuous_listening:
                # Start continuous monitoring
                self.continuous_listening = True
                self.audio_thread = threading.Thread(target=self._continuous_audio_monitor, daemon=True)
                self.audio_thread.start()
                self._print_status("🎤 Voice interaction ready...", "listening")
            
            # Clear any previous events and queue
            self.speech_detected_event.clear()
            self.processing_speech = False
            while not self.audio_queue.empty():
                try:
                    self.audio_queue.get_nowait()
                except:
                    break
            
            # Wait for speech detection
            self._print_status("👂 Listening for your voice...", "info")
            
            # Wait for speech with timeout
            if self.speech_detected_event.wait(timeout=15):
                # Get audio data from queue
                if not self.audio_queue.empty():
                    audio_data = self.audio_queue.get()
                    
                    # Save to temporary file for transcription
                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
                        wf = wave.open(temp_audio.name, 'wb')
                        wf.setnchannels(self.channels)
                        wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
                        wf.setframerate(self.sample_rate)
                        wf.writeframes(audio_data)
                        wf.close()
                        
                        # Transcribe using OpenAI Whisper
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
                else:
                    return None
            else:
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
                model="gpt-4",
                messages=self.conversation_history,
                max_tokens=60,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Add AI response to conversation history
            self.conversation_history.append({"role": "assistant", "content": ai_response})
            
            # Keep conversation history manageable
            if len(self.conversation_history) > 16:
                self.conversation_history = [self.conversation_history[0]] + self.conversation_history[-14:]
                
            return ai_response
            
        except Exception as e:
            self._print_status(f"❌ Error getting AI response: {e}", "error")
            return None
            
    def speak_response(self, text: str):
        """Convert text to speech and play it with proper audio handling."""
        try:
            self._print_status("🔊 AI Speaking...", "info")
            self.is_speaking = True
            self.should_interrupt = False
            self.stop_speaking_event.clear()
            
            # Generate speech using OpenAI TTS
            with self.client.audio.speech.with_streaming_response.create(
                model=self.tts_model,
                voice=self.voice_model,
                input=text,
                speed=1.0  # Normal speed for clarity
            ) as response:
                # Save to temporary file
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_audio:
                    for chunk in response.iter_bytes():
                        if self.should_interrupt or self.stop_speaking_event.is_set():
                            break
                        temp_audio.write(chunk)
                    temp_audio.flush()
                    
                    if not (self.should_interrupt or self.stop_speaking_event.is_set()):
                        # Mark audio output as active to prevent self-interruption
                        self.audio_output_active = True
                        
                        try:
                            self.current_audio_process = subprocess.Popen(
                                ["afplay", temp_audio.name],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL
                            )
                            
                            # Monitor for interruption
                            while self.current_audio_process.poll() is None:
                                if self.should_interrupt or self.stop_speaking_event.is_set():
                                    self.current_audio_process.terminate()
                                    self._print_status("🛑 AI speech interrupted by user!", "warning")
                                    break
                                time.sleep(0.1)
                            
                            # Wait a moment after audio finishes to prevent immediate detection
                            if not (self.should_interrupt or self.stop_speaking_event.is_set()):
                                time.sleep(0.5)  # Brief pause after AI speech
                                
                        except Exception as audio_error:
                            self._print_status(f"⚠️ Audio playback issue: {audio_error}", "warning")
                            self._print_status(f"💬 AI said: {text}", "assistant")
                        finally:
                            self.audio_output_active = False  # Always reset this flag
                    
                    # Clean up temporary file
                    try:
                        os.unlink(temp_audio.name)
                    except:
                        pass
                
        except Exception as e:
            self._print_status(f"❌ Error in text-to-speech: {e}", "error")
            self._print_status(f"💬 AI said: {text}", "assistant")
        finally:
            self.is_speaking = False
            self.current_audio_process = None
            self.audio_output_active = False
            
    def print_instructions(self):
        """Print usage instructions."""
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}🎙️  REAL-TIME VOICE CHATBOT (FIXED)")
        print(f"{Fore.CYAN}{'='*70}")
        print(f"{Fore.GREEN}Features:")
        print(f"{Fore.WHITE}• 🎤 Real voice interaction")
        print(f"{Fore.WHITE}• 🔊 AI speaks back to you")
        print(f"{Fore.WHITE}• 🛑 Interrupt AI by speaking")
        print(f"{Fore.WHITE}• 💬 Natural conversation flow")
        print(f"{Fore.YELLOW}Instructions:")
        print(f"{Fore.WHITE}• Speak naturally when prompted")
        print(f"{Fore.WHITE}• Listen to AI responses")
        print(f"{Fore.WHITE}• Interrupt AI by speaking while it talks")
        print(f"{Fore.WHITE}• Say any of these to exit:")
        print(f"{Fore.CYAN}  - {Fore.YELLOW}'quit'{Fore.CYAN}, {Fore.YELLOW}'exit'{Fore.CYAN}, {Fore.YELLOW}'bye'{Fore.CYAN}, {Fore.YELLOW}'goodbye'{Fore.CYAN}")
        print(f"{Fore.CYAN}  - {Fore.YELLOW}'ok quit'{Fore.CYAN}, {Fore.YELLOW}'okay exit'{Fore.CYAN}, {Fore.YELLOW}'stop now'{Fore.CYAN}")
        print(f"{Fore.CYAN}  - {Fore.YELLOW}'i'm done'{Fore.CYAN}, {Fore.YELLOW}'that's all'{Fore.CYAN}, {Fore.YELLOW}'finished'{Fore.CYAN}")
        print(f"{Fore.WHITE}• Press {Fore.RED}Ctrl+C{Fore.WHITE} for immediate exit")
        print(f"{Fore.CYAN}{'='*70}\n")
        
    def run(self):
        """Main conversation loop."""
        try:
            self.print_instructions()
            
            while self.is_running:
                try:
                    # Listen for user input
                    user_input = self.listen_for_speech()
                    
                    if user_input is None:
                        continue
                        
                    if not user_input.strip():
                        continue
                    
                    # Check for quit commands (enhanced detection)
                    quit_phrases = [
                        'quit', 'exit', 'goodbye', 'bye', 'stop', 'end', 'finish', 'done',
                        'ok quit', 'okay quit', 'ok exit', 'okay exit', 'ok bye', 'okay bye',
                        'quit now', 'exit now', 'stop now', 'end now', 'close', 'terminate',
                        'quit please', 'exit please', 'goodbye now', 'bye bye', 'see you later',
                        'that\'s all', 'i\'m done', 'we\'re done', 'finished', 'all done',
                        'shut down', 'shutdown', 'turn off', 'stop chatbot', 'end chat'
                    ]
                    
                    user_lower = user_input.lower().strip()
                    should_quit = False
                    
                    # Check exact matches
                    if user_lower in quit_phrases:
                        should_quit = True
                        self._print_status(f"✅ Quit command detected: '{user_input}'", "success")
                    
                    # Check if input contains quit phrases (more flexible)
                    if not should_quit:
                        for phrase in ['quit', 'exit', 'goodbye', 'bye', 'stop', 'end', 'done', 'finish']:
                            if phrase in user_lower and len(user_lower.split()) <= 4:
                                should_quit = True
                                self._print_status(f"✅ Quit phrase detected: '{phrase}' in '{user_input}'", "success")
                                break
                    
                    if should_quit:
                        self._print_status("👋 Goodbye! Thanks for chatting!", "success")
                        break
                        
                    # Display user input
                    self._print_status(f"👤 You: {user_input}", "user")
                    
                    # Get AI response
                    ai_response = self.get_ai_response(user_input)
                    
                    if ai_response is None:
                        continue
                        
                    # Display AI response
                    self._print_status(f"🤖 Assistant: {ai_response}", "assistant")
                    
                    # Speak the response (with proper audio handling)
                    self.speak_response(ai_response)
                    
                    print()  # Add spacing
                    
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
        self.continuous_listening = False
        self.audio_output_active = False
        
        # Stop any ongoing audio
        if self.current_audio_process:
            try:
                self.current_audio_process.terminate()
            except:
                pass
        
        # Signal threads to stop
        self.stop_speaking_event.set()
        self.speech_detected_event.set()
        
        # Clean up audio
        try:
            self.audio.terminate()
        except:
            pass
            
        self._print_status("\n👋 Goodbye! Thanks for chatting!", "success")

def main():
    """Main entry point."""
    # Check for required environment variables
    if not os.getenv('OPENAI_API_KEY'):
        print(f"{Fore.RED}❌ Error: OPENAI_API_KEY not found in environment variables.")
        print(f"{Fore.YELLOW}Please create a .env file with your OpenAI API key.")
        sys.exit(1)
        
    try:
        chatbot = FixedVoiceChatbot()
        chatbot.run()
    except Exception as e:
        print(f"{Fore.RED}❌ Failed to start chatbot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()