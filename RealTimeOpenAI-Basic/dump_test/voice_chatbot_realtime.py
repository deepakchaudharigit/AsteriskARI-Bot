#!/usr/bin/env python3
"""
Real-Time Voice Chatbot with Modern Interruption Support
Features:
- Instant interruption with keywords like "stop", "hold on", "ok"
- Real-time audio termination
- Modern voice assistant behavior
- Immediate response to interruption commands
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
import re
from typing import Optional, List, Dict, Tuple
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

class RealTimeVoiceChatbot:
    def __init__(self):
        """Initialize the real-time voice chatbot with modern interruption."""
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
        self.chunk_size = int(os.getenv('CHUNK_SIZE', 512))  # Smaller for faster detection
        self.channels = int(os.getenv('CHANNELS', 1))
        
        # Audio components
        self.audio = pyaudio.PyAudio()
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone(sample_rate=self.sample_rate)
        
        # Real-time Voice Activity Detection parameters
        self.silence_threshold = 150
        self.speech_threshold = 300  # Balanced for real-time detection
        self.min_speech_duration = 0.2  # Very short for instant detection
        self.silence_duration = 0.3     # Very short for responsiveness
        
        # Interruption keywords (modern voice assistant style)
        self.interruption_keywords = [
            # Immediate stop commands
            'stop', 'halt', 'pause', 'wait', 'hold', 'hold on', 'hold up',
            # Polite interruptions
            'excuse me', 'sorry', 'pardon', 'one moment', 'just a sec',
            # Quick acknowledgments that should stop AI
            'ok', 'okay', 'yes', 'yeah', 'yep', 'right', 'got it',
            # Quit commands
            'quit', 'exit', 'bye', 'goodbye', 'done', 'finished', 'end',
            'stop chatbot', 'end chat', 'shut down', 'turn off'
        ]
        
        # Control flags
        self.is_listening = False
        self.is_speaking = False
        self.should_interrupt = False
        self.is_running = True
        self.continuous_listening = False
        self.processing_speech = False
        self.last_interrupt_time = 0
        self.audio_output_active = False
        self.real_time_monitoring = True
        
        # Audio queues and buffers
        self.audio_queue = queue.Queue()
        self.interrupt_queue = queue.Queue()
        self.speech_buffer = []
        self.current_audio_process = None
        
        # Conversation history
        self.conversation_history: List[Dict[str, str]] = [
            {"role": "system", "content": "You are a helpful AI assistant. Keep responses brief and conversational. You can be interrupted at any time, so keep sentences short and natural."}
        ]
        
        # Threading events
        self.stop_speaking_event = threading.Event()
        self.speech_detected_event = threading.Event()
        self.interrupt_detected_event = threading.Event()
        
        # Calibrate microphone
        self._calibrate_microphone()
        
    def _signal_handler(self, signum, frame):
        """Handle Ctrl+C and other termination signals gracefully."""
        print(f"\n{Fore.YELLOW}\n🛑 Ctrl+C detected - Immediate shutdown...")
        self.is_running = False
        self.continuous_listening = False
        self.real_time_monitoring = False
        self.audio_output_active = False
        
        # Stop any ongoing audio immediately
        if self.current_audio_process:
            try:
                self.current_audio_process.terminate()
                self.current_audio_process.kill()
            except:
                pass
        
        # Signal all threads to stop
        self.stop_speaking_event.set()
        self.speech_detected_event.set()
        self.interrupt_detected_event.set()
        
        # Clean up audio immediately
        try:
            self.audio.terminate()
        except:
            pass
            
        print(f"{Fore.GREEN}👋 Real-time voice chatbot terminated.")
        os._exit(0)
        
    def _calibrate_microphone(self):
        """Calibrate microphone for real-time interaction."""
        print(f"{Fore.YELLOW}🎤 Calibrating for real-time voice interaction...")
        
        # Quick calibration for responsiveness
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        
        # Measure ambient noise level
        print(f"{Fore.YELLOW}📊 Measuring ambient noise...")
        noise_samples = []
        
        stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )
        
        for _ in range(int(1.5 * self.sample_rate / self.chunk_size)):
            data = stream.read(self.chunk_size, exception_on_overflow=False)
            rms = audioop.rms(data, 2)
            noise_samples.append(rms)
        
        stream.stop_stream()
        stream.close()
        
        # Set real-time optimized thresholds
        avg_noise = np.mean(noise_samples)
        max_noise = np.max(noise_samples)
        std_noise = np.std(noise_samples)
        
        # Optimized for real-time interruption detection
        self.silence_threshold = avg_noise + std_noise * 0.5
        self.speech_threshold = max(avg_noise * 2.5, max_noise * 1.2, 250)
        
        print(f"{Fore.GREEN}✅ Real-time calibration complete!")
        print(f"{Fore.CYAN}📈 Ambient: {avg_noise:.0f}, Speech threshold: {self.speech_threshold:.0f}")
        
    def _print_status(self, message: str, status_type: str = "info"):
        """Print colored status messages."""
        colors = {
            "info": Fore.CYAN,
            "success": Fore.GREEN,
            "warning": Fore.YELLOW,
            "error": Fore.RED,
            "user": Fore.BLUE,
            "assistant": Fore.MAGENTA,
            "listening": Fore.LIGHTBLUE_EX,
            "interrupt": Fore.RED
        }
        color = colors.get(status_type, Fore.WHITE)
        print(f"{color}{message}{Style.RESET_ALL}")
        
    def _detect_voice_activity(self, audio_data: bytes) -> bool:
        """Real-time voice activity detection."""
        try:
            rms = audioop.rms(audio_data, 2)
            return rms > self.speech_threshold
        except Exception:
            return False
            
    def _check_for_interruption_keywords(self, text: str) -> Tuple[bool, str]:
        """Check if text contains interruption keywords."""
        text_lower = text.lower().strip()
        
        # Check for exact matches first
        for keyword in self.interruption_keywords:
            if keyword in text_lower:
                return True, keyword
                
        # Check for partial matches in short phrases
        words = text_lower.split()
        if len(words) <= 3:
            for word in words:
                if word in ['stop', 'ok', 'wait', 'hold', 'pause', 'quit', 'exit', 'bye']:
                    return True, word
                    
        return False, ""
        
    def _real_time_interrupt_monitor(self):
        """Monitor for real-time interruptions during AI speech."""
        stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )
        
        interrupt_frames = []
        silence_frames = 0
        
        while self.real_time_monitoring and self.is_running:
            try:
                if not self.is_speaking:
                    time.sleep(0.1)
                    continue
                    
                data = stream.read(self.chunk_size, exception_on_overflow=False)
                has_voice = self._detect_voice_activity(data)
                
                if has_voice:
                    interrupt_frames.append(data)
                    silence_frames = 0
                else:
                    silence_frames += 1
                    
                    # Quick processing for interruption detection
                    if len(interrupt_frames) > int(0.3 * self.sample_rate / self.chunk_size):
                        # We have enough audio for quick transcription
                        try:
                            # Quick transcription for interruption detection
                            audio_data = b''.join(interrupt_frames)
                            
                            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
                                wf = wave.open(temp_audio.name, 'wb')
                                wf.setnchannels(self.channels)
                                wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
                                wf.setframerate(self.sample_rate)
                                wf.writeframes(audio_data)
                                wf.close()
                                
                                # Quick transcription
                                with open(temp_audio.name, 'rb') as audio_file:
                                    transcript = self.client.audio.transcriptions.create(
                                        model=self.speech_model,
                                        file=audio_file,
                                        language="en"
                                    )
                                
                                os.unlink(temp_audio.name)
                                
                                # Check for interruption keywords
                                is_interrupt, keyword = self._check_for_interruption_keywords(transcript.text)
                                
                                if is_interrupt:
                                    self._print_status(f"🛑 INTERRUPT: '{keyword}' detected!", "interrupt")
                                    self.should_interrupt = True
                                    self.stop_speaking_event.set()
                                    
                                    if self.current_audio_process:
                                        try:
                                            self.current_audio_process.terminate()
                                        except:
                                            pass
                                    
                                    # Check if it's a quit command
                                    if keyword in ['quit', 'exit', 'bye', 'goodbye', 'done', 'finished', 'end']:
                                        self.interrupt_queue.put(('quit', transcript.text))
                                    else:
                                        self.interrupt_queue.put(('interrupt', transcript.text))
                                        
                                    self.interrupt_detected_event.set()
                                    
                        except Exception as e:
                            pass  # Ignore transcription errors for interruption detection
                        
                        interrupt_frames = []
                        
            except Exception as e:
                if self.is_running:
                    pass  # Ignore errors in interrupt monitoring
                    
        stream.stop_stream()
        stream.close()
        
    def _continuous_audio_monitor(self):
        """Monitor audio for regular speech detection."""
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
        
        while self.continuous_listening and self.is_running:
            try:
                if self.is_speaking:  # Don't process regular speech while AI is speaking
                    time.sleep(0.1)
                    continue
                    
                data = stream.read(self.chunk_size, exception_on_overflow=False)
                has_voice = self._detect_voice_activity(data)
                
                if has_voice:
                    if not speech_detected:
                        print(f"\n🎤 User speaking...")
                    speech_frames.append(data)
                    silence_frames = 0
                    speech_detected = True
                else:
                    silence_frames += 1
                    
                    # Process speech when silence is detected
                    if speech_detected and silence_frames > int(self.silence_duration * self.sample_rate / self.chunk_size):
                        if len(speech_frames) > int(self.min_speech_duration * self.sample_rate / self.chunk_size) and not self.processing_speech:
                            print(f"\n✅ Processing speech...")
                            self.processing_speech = True
                            self.audio_queue.put(b''.join(speech_frames))
                            self.speech_detected_event.set()
                        
                        speech_frames = []
                        speech_detected = False
                        silence_frames = 0
                        
            except Exception as e:
                if self.is_running:
                    pass
                    
        stream.stop_stream()
        stream.close()
        
    def listen_for_speech(self) -> Optional[str]:
        """Listen for speech with real-time interruption support."""
        try:
            if not self.continuous_listening:
                # Start continuous monitoring
                self.continuous_listening = True
                self.audio_thread = threading.Thread(target=self._continuous_audio_monitor, daemon=True)
                self.audio_thread.start()
                
                # Start real-time interrupt monitoring
                self.interrupt_thread = threading.Thread(target=self._real_time_interrupt_monitor, daemon=True)
                self.interrupt_thread.start()
                
                self._print_status("🎤 Real-time voice interaction ready...", "listening")
            
            # Clear previous events and queue
            self.speech_detected_event.clear()
            self.processing_speech = False
            while not self.audio_queue.empty():
                try:
                    self.audio_queue.get_nowait()
                except:
                    break
            
            # Wait for speech detection
            self._print_status("👂 Listening...", "info")
            
            # Wait for speech with timeout
            if self.speech_detected_event.wait(timeout=15):
                if not self.audio_queue.empty():
                    audio_data = self.audio_queue.get()
                    
                    # Save and transcribe
                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
                        wf = wave.open(temp_audio.name, 'wb')
                        wf.setnchannels(self.channels)
                        wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
                        wf.setframerate(self.sample_rate)
                        wf.writeframes(audio_data)
                        wf.close()
                        
                        self._print_status("🔄 Transcribing...", "info")
                        with open(temp_audio.name, 'rb') as audio_file:
                            transcript = self.client.audio.transcriptions.create(
                                model=self.speech_model,
                                file=audio_file,
                                language="en"
                            )
                        
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
            self.conversation_history.append({"role": "user", "content": user_input})
            self._print_status("🤖 Thinking...", "info")
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=self.conversation_history,
                max_tokens=50,  # Keep responses short for better interruption
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content.strip()
            self.conversation_history.append({"role": "assistant", "content": ai_response})
            
            # Keep conversation history manageable
            if len(self.conversation_history) > 16:
                self.conversation_history = [self.conversation_history[0]] + self.conversation_history[-14:]
                
            return ai_response
            
        except Exception as e:
            self._print_status(f"❌ Error getting AI response: {e}", "error")
            return None
            
    def speak_response(self, text: str):
        """Speak response with real-time interruption support."""
        try:
            self._print_status("🔊 AI Speaking...", "info")
            self.is_speaking = True
            self.should_interrupt = False
            self.stop_speaking_event.clear()
            
            # Generate speech
            with self.client.audio.speech.with_streaming_response.create(
                model=self.tts_model,
                voice=self.voice_model,
                input=text,
                speed=1.0
            ) as response:
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_audio:
                    for chunk in response.iter_bytes():
                        if self.should_interrupt or self.stop_speaking_event.is_set():
                            break
                        temp_audio.write(chunk)
                    temp_audio.flush()
                    
                    if not (self.should_interrupt or self.stop_speaking_event.is_set()):
                        try:
                            self.current_audio_process = subprocess.Popen(
                                ["afplay", temp_audio.name],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL
                            )
                            
                            # Monitor for interruption very frequently
                            while self.current_audio_process.poll() is None:
                                if self.should_interrupt or self.stop_speaking_event.is_set():
                                    self.current_audio_process.terminate()
                                    self._print_status("🛑 AI speech interrupted!", "warning")
                                    break
                                time.sleep(0.05)  # Very frequent checking
                                
                        except Exception as audio_error:
                            self._print_status(f"💬 AI said: {text}", "assistant")
                    
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
            
    def print_instructions(self):
        """Print usage instructions."""
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}🎙️  REAL-TIME VOICE CHATBOT (MODERN INTERRUPTION)")
        print(f"{Fore.CYAN}{'='*70}")
        print(f"{Fore.GREEN}Features:")
        print(f"{Fore.WHITE}• 🎤 Real-time voice interaction")
        print(f"{Fore.WHITE}• 🛑 Instant interruption with keywords")
        print(f"{Fore.WHITE}• 🔊 AI speaks back naturally")
        print(f"{Fore.WHITE}• ⚡ Modern voice assistant behavior")
        print(f"{Fore.YELLOW}Interruption Commands:")
        print(f"{Fore.WHITE}• Say {Fore.RED}'stop'{Fore.WHITE}, {Fore.RED}'hold on'{Fore.WHITE}, {Fore.RED}'wait'{Fore.WHITE} to pause AI")
        print(f"{Fore.WHITE}• Say {Fore.RED}'ok'{Fore.WHITE}, {Fore.RED}'yes'{Fore.WHITE}, {Fore.RED}'got it'{Fore.WHITE} to acknowledge and stop")
        print(f"{Fore.WHITE}• Say {Fore.RED}'excuse me'{Fore.WHITE}, {Fore.RED}'sorry'{Fore.WHITE} to politely interrupt")
        print(f"{Fore.YELLOW}Exit Commands:")
        print(f"{Fore.WHITE}• Say {Fore.YELLOW}'quit'{Fore.WHITE}, {Fore.YELLOW}'exit'{Fore.WHITE}, {Fore.YELLOW}'bye'{Fore.WHITE}, {Fore.YELLOW}'goodbye'{Fore.WHITE}")
        print(f"{Fore.WHITE}• Press {Fore.RED}Ctrl+C{Fore.WHITE} for immediate exit")
        print(f"{Fore.CYAN}{'='*70}\n")
        
    def run(self):
        """Main conversation loop with real-time interruption."""
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
                    
                    # Check for quit commands
                    is_quit, quit_word = self._check_for_interruption_keywords(user_input)
                    if is_quit and quit_word in ['quit', 'exit', 'bye', 'goodbye', 'done', 'finished', 'end']:
                        self._print_status(f"✅ Quit command: '{quit_word}' detected!", "success")
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
                    
                    # Speak the response (can be interrupted in real-time)
                    self.speak_response(ai_response)
                    
                    # Check for interruptions that occurred during speech
                    while not self.interrupt_queue.empty():
                        try:
                            interrupt_type, interrupt_text = self.interrupt_queue.get_nowait()
                            if interrupt_type == 'quit':
                                self._print_status(f"✅ Quit interrupt: '{interrupt_text}'", "success")
                                self._print_status("👋 Goodbye! Thanks for chatting!", "success")
                                return
                            else:
                                self._print_status(f"🛑 Interrupted with: '{interrupt_text}'", "warning")
                        except:
                            break
                    
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
        self.real_time_monitoring = False
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
        self.interrupt_detected_event.set()
        
        # Clean up audio
        try:
            self.audio.terminate()
        except:
            pass
            
        self._print_status("\n👋 Real-time voice chatbot ended!", "success")

def main():
    """Main entry point."""
    if not os.getenv('OPENAI_API_KEY'):
        print(f"{Fore.RED}❌ Error: OPENAI_API_KEY not found.")
        sys.exit(1)
        
    try:
        chatbot = RealTimeVoiceChatbot()
        chatbot.run()
    except Exception as e:
        print(f"{Fore.RED}❌ Failed to start chatbot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()