"""
Enhanced Text-to-Speech module with OpenAI TTS-1-HD for high-quality voice output
Supports multiple voices and improved audio quality for NPCL Voice Assistant
"""

import os
import io
import logging
import tempfile
import time
import sys
from typing import Optional, Dict, Any
from pathlib import Path
import pygame
import openai

# Add project root to path for config import
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Try multiple import paths for config
try:
    from config.settings import get_settings
except ImportError:
    try:
        # Try relative import
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        from config.settings import get_settings
    except ImportError:
        try:
            # Try absolute import from project root
            import sys
            import os
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            sys.path.insert(0, project_root)
            from config.settings import get_settings
        except ImportError:
            # Fallback if config not available
            def get_settings():
                class MockSettings:
                    def __init__(self):
                        self.openai_api_key = os.getenv('OPENAI_API_KEY')
                        self.voice_model = os.getenv('VOICE_MODEL', 'fable')
                        self.tts_model = os.getenv('TTS_MODEL', 'tts-1-hd')
                        self.sample_rate = int(os.getenv('SAMPLE_RATE', '16000'))
                        self.channels = int(os.getenv('CHANNELS', '1'))
                return MockSettings()

logger = logging.getLogger(__name__)

class EnhancedTTS:
    """Enhanced Text-to-Speech using OpenAI TTS-1-HD"""
    
    def __init__(self):
        # Get API key from environment or settings
        api_key = os.getenv('OPENAI_API_KEY')
        
        # Try to get settings
        try:
            self.settings = get_settings()
            if not api_key:
                api_key = self.settings.openai_api_key
            
            # Get voice configuration from settings
            self.voice_model = getattr(self.settings, 'voice_model', os.getenv('VOICE_MODEL', 'fable'))
            self.tts_model = getattr(self.settings, 'tts_model', os.getenv('TTS_MODEL', 'tts-1-hd'))
            self.sample_rate = getattr(self.settings, 'sample_rate', int(os.getenv('SAMPLE_RATE', '16000')))
            self.channels = getattr(self.settings, 'channels', int(os.getenv('CHANNELS', '1')))
            
        except Exception as e:
            logger.warning(f"Could not load settings: {e}, using environment variables")
            # Fallback to environment variables
            if not api_key:
                raise ValueError("OpenAI API key not found in environment or settings")
            
            self.voice_model = os.getenv('VOICE_MODEL', 'fable')
            self.tts_model = os.getenv('TTS_MODEL', 'tts-1-hd')
            self.sample_rate = int(os.getenv('SAMPLE_RATE', '16000'))
            self.channels = int(os.getenv('CHANNELS', '1'))
        
        if not api_key:
            raise ValueError("OpenAI API key not found in environment or settings")
        
        self.client = openai.OpenAI(api_key=api_key)
        
        # Initialize pygame mixer for audio playback
        self._init_audio()
        
        # Voice options with descriptions
        self.available_voices = {
            'alloy': 'Neutral, balanced voice - good for professional use',
            'echo': 'Clear, crisp voice - good for announcements',
            'fable': 'Warm, friendly voice - good for customer service',
            'onyx': 'Deep, authoritative voice - good for formal content',
            'nova': 'Energetic, youthful voice - good for engaging content',
            'shimmer': 'Soft, gentle voice - good for calm interactions'
        }
        
        logger.info(f"Enhanced TTS initialized with voice: {self.voice_model}, model: {self.tts_model}")
    
    def _init_audio(self):
        """Initialize pygame audio system"""
        try:
            pygame.mixer.pre_init(
                frequency=self.sample_rate,
                size=-16,  # 16-bit signed
                channels=self.channels,
                buffer=1024
            )
            pygame.mixer.init()
            logger.info(f"Audio system initialized: {self.sample_rate}Hz, {self.channels} channel(s)")
        except Exception as e:
            logger.error(f"Failed to initialize audio system: {e}")
            raise
    
    def speak_text_enhanced(self, text: str, language_code: str = "en-IN", voice: Optional[str] = None) -> bool:
        """
        Enhanced text-to-speech with high-quality OpenAI TTS
        
        Args:
            text: Text to speak
            language_code: Language code (for future language-specific voice selection)
            voice: Voice to use (overrides default)
            
        Returns:
            True if successful, False otherwise
        """
        if not text or not text.strip():
            logger.warning("Empty text provided to TTS")
            return False
        
        # Use provided voice or default
        selected_voice = voice or self.voice_model
        
        # Validate voice
        if selected_voice not in self.available_voices:
            logger.warning(f"Invalid voice '{selected_voice}', using 'alloy'")
            selected_voice = 'alloy'
        
        try:
            logger.info(f"Generating speech with voice '{selected_voice}' for: {text[:50]}...")
            
            # Generate speech using OpenAI TTS
            start_time = time.time()
            
            response = self.client.audio.speech.create(
                model=self.tts_model,
                voice=selected_voice,
                input=text,
                response_format="mp3",
                speed=1.0  # Normal speed for clarity
            )
            
            generation_time = time.time() - start_time
            logger.debug(f"Speech generation took {generation_time:.2f}s")
            
            # Play the audio
            return self._play_audio_stream(response.content)
            
        except Exception as e:
            logger.error(f"Enhanced TTS failed: {e}")
            return self._fallback_tts(text, language_code)
    
    def _play_audio_stream(self, audio_data: bytes) -> bool:
        """Play audio data using pygame"""
        try:
            # Create a temporary file for the audio
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            try:
                # Load and play the audio
                pygame.mixer.music.load(temp_file_path)
                pygame.mixer.music.play()
                
                # Wait for playback to complete
                while pygame.mixer.music.get_busy():
                    pygame.time.wait(100)
                
                logger.debug("Audio playback completed successfully")
                return True
                
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file_path)
                except Exception as e:
                    logger.warning(f"Failed to delete temp file: {e}")
            
        except Exception as e:
            logger.error(f"Audio playback failed: {e}")
            return False
    
    def _fallback_tts(self, text: str, language_code: str = "en-IN") -> bool:
        """Fallback to basic TTS if enhanced TTS fails"""
        try:
            logger.info("Using fallback TTS (pyttsx3)")
            import pyttsx3
            
            # Initialize engine
            engine = pyttsx3.init()
            
            # Configure engine
            engine.setProperty('rate', 150)  # Slower for clarity
            engine.setProperty('volume', 0.9)
            
            # Set voice if available
            voices = engine.getProperty('voices')
            if voices:
                # Try to find a good voice
                for voice in voices:
                    if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                        engine.setProperty('voice', voice.id)
                        break
                else:
                    engine.setProperty('voice', voices[0].id)
            
            # Speak the text
            engine.say(text)
            engine.runAndWait()
            
            # Cleanup
            try:
                engine.stop()
                del engine
            except:
                pass
            
            return True
            
        except Exception as e:
            logger.error(f"Fallback TTS also failed: {e}")
            return False
    
    def set_voice(self, voice: str) -> bool:
        """
        Set the voice for TTS
        
        Args:
            voice: Voice name (alloy, echo, fable, onyx, nova, shimmer)
            
        Returns:
            True if voice is valid and set
        """
        if voice in self.available_voices:
            self.voice_model = voice
            logger.info(f"Voice changed to: {voice} - {self.available_voices[voice]}")
            return True
        else:
            logger.warning(f"Invalid voice: {voice}. Available voices: {list(self.available_voices.keys())}")
            return False
    
    def get_available_voices(self) -> Dict[str, str]:
        """Get available voices with descriptions"""
        return self.available_voices.copy()
    
    def test_voice(self, voice: str) -> bool:
        """Test a specific voice"""
        test_text = f"Hello, this is a test of the {voice} voice from NPCL Voice Assistant."
        return self.speak_text_enhanced(test_text, voice=voice)
    
    def get_voice_info(self) -> Dict[str, Any]:
        """Get current voice configuration info"""
        return {
            'current_voice': self.voice_model,
            'tts_model': self.tts_model,
            'sample_rate': self.sample_rate,
            'channels': self.channels,
            'available_voices': self.available_voices,
            'voice_description': self.available_voices.get(self.voice_model, 'Unknown voice')
        }
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            pygame.mixer.quit()
            logger.info("Enhanced TTS cleanup completed")
        except Exception as e:
            logger.warning(f"TTS cleanup warning: {e}")

# Global instance for easy access
_enhanced_tts = None

def get_enhanced_tts() -> EnhancedTTS:
    """Get global enhanced TTS instance"""
    global _enhanced_tts
    if _enhanced_tts is None:
        _enhanced_tts = EnhancedTTS()
    return _enhanced_tts

def speak_text_enhanced(text: str, language_code: str = "en-IN", voice: Optional[str] = None) -> bool:
    """
    Enhanced text-to-speech function for easy import
    
    Args:
        text: Text to speak
        language_code: Language code
        voice: Voice to use (optional)
        
    Returns:
        True if successful
    """
    try:
        tts = get_enhanced_tts()
        return tts.speak_text_enhanced(text, language_code, voice)
    except Exception as e:
        logger.error(f"Enhanced TTS function failed: {e}")
        return False

def set_voice(voice: str) -> bool:
    """Set the global TTS voice"""
    try:
        tts = get_enhanced_tts()
        return tts.set_voice(voice)
    except Exception as e:
        logger.error(f"Failed to set voice: {e}")
        return False

def test_all_voices():
    """Test all available voices"""
    try:
        tts = get_enhanced_tts()
        voices = tts.get_available_voices()
        
        print("🎤 Testing all OpenAI TTS voices:")
        print("=" * 50)
        
        for voice, description in voices.items():
            print(f"\n🔊 Testing voice: {voice}")
            print(f"Description: {description}")
            success = tts.test_voice(voice)
            if success:
                print(f"✅ {voice} voice test successful")
            else:
                print(f"❌ {voice} voice test failed")
            
            # Small pause between tests
            time.sleep(1)
        
        print("\n" + "=" * 50)
        print("🎉 Voice testing completed!")
        
    except Exception as e:
        logger.error(f"Voice testing failed: {e}")
        print(f"❌ Voice testing failed: {e}")

if __name__ == "__main__":
    # Test the enhanced TTS
    test_all_voices()