"""
Simple Enhanced TTS - Fixed version without config dependencies
High-quality OpenAI TTS for NPCL Voice Assistant
"""

import os
import tempfile
import logging
import pygame
import openai
from typing import Optional

logger = logging.getLogger(__name__)

class SimpleEnhancedTTS:
    """Simple Enhanced TTS without config dependencies"""
    
    def __init__(self):
        # Get API key from environment
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        self.client = openai.OpenAI(api_key=api_key)
        
        # Voice settings from environment or defaults
        self.voice_model = os.getenv('VOICE_MODEL', 'fable')
        self.tts_model = os.getenv('TTS_MODEL', 'tts-1-hd')
        
        # Available voices for reference
        self.available_voices = {
            'alloy': 'Neutral, balanced voice - good for professional use',
            'echo': 'Clear, crisp voice - good for announcements', 
            'fable': 'Warm, friendly voice - good for customer service',
            'onyx': 'Deep, authoritative voice - good for formal content',
            'nova': 'Energetic, youthful voice - good for engaging content',
            'shimmer': 'Soft, gentle voice - good for calm interactions'
        }
        
        # Initialize pygame for audio
        try:
            pygame.mixer.pre_init(frequency=16000, size=-16, channels=1, buffer=1024)
            pygame.mixer.init()
            logger.info("✅ Enhanced TTS initialized successfully")
            logger.info(f"🎵 Voice: {self.voice_model} - Warm, friendly voice - good for customer service")
            logger.info(f"🎛️  Model: {self.tts_model}")
        except Exception as e:
            logger.error(f"Failed to initialize audio: {e}")
            raise
    
    def speak_text_enhanced(self, text: str, voice: Optional[str] = None) -> bool:
        """Generate and play high-quality speech"""
        if not text or not text.strip():
            return False
        
        selected_voice = voice or self.voice_model
        
        try:
            logger.info(f"🔊 Generating speech: {text[:50]}...")
            
            # Generate speech
            response = self.client.audio.speech.create(
                model=self.tts_model,
                voice=selected_voice,
                input=text,
                response_format="mp3"
            )
            
            # Play audio
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                temp_file.write(response.content)
                temp_file_path = temp_file.name
            
            try:
                pygame.mixer.music.load(temp_file_path)
                pygame.mixer.music.play()
                
                # Wait for completion
                while pygame.mixer.music.get_busy():
                    pygame.time.wait(100)
                
                logger.info("✅ Enhanced TTS: Working perfectly")
                return True
                
            finally:
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
            
        except Exception as e:
            logger.error(f"Enhanced TTS failed: {e}")
            return self._fallback_tts(text)
    
    def _fallback_tts(self, text: str) -> bool:
        """Fallback to basic TTS"""
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
            engine.setProperty('volume', 0.9)
            engine.say(text)
            engine.runAndWait()
            engine.stop()
            return True
        except Exception as e:
            logger.error(f"Fallback TTS failed: {e}")
            return False

# Global instance
_tts_instance = None

def get_tts():
    """Get TTS instance"""
    global _tts_instance
    if _tts_instance is None:
        _tts_instance = SimpleEnhancedTTS()
    return _tts_instance

def speak_text_enhanced(text: str, voice: Optional[str] = None) -> bool:
    """Enhanced TTS function"""
    try:
        tts = get_tts()
        return tts.speak_text_enhanced(text, voice)
    except Exception as e:
        logger.error(f"TTS failed: {e}")
        return False

if __name__ == "__main__":
    # Test the TTS
    print("🧪 Testing Simple Enhanced TTS...")
    try:
        success = speak_text_enhanced("NPCL Enhanced TTS is working perfectly!")
        if success:
            print("✅ Simple Enhanced TTS test successful!")
        else:
            print("❌ Test failed")
    except Exception as e:
        print(f"❌ Test error: {e}")