#!/usr/bin/env python3
"""
Test Enhanced TTS with Config Fix
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_enhanced_tts():
    """Test the enhanced TTS with config"""
    print("🧪 Testing Enhanced TTS with Config Fix")
    print("=" * 50)
    
    try:
        # Test simple enhanced TTS
        from voice_assistant.audio.simple_enhanced_tts import SimpleEnhancedTTS
        
        print("✅ Successfully imported SimpleEnhancedTTS")
        
        # Initialize TTS
        tts = SimpleEnhancedTTS()
        
        print(f"✅ Enhanced TTS initialized successfully")
        print(f"🎵 Voice: {tts.voice_model} - {tts.available_voices[tts.voice_model]}")
        print(f"🎛️  Model: {tts.tts_model}")
        
        # Test voice (without actually playing audio)
        print("\n🔊 Testing voice generation...")
        
        # Just test the API call without playing audio
        try:
            response = tts.client.audio.speech.create(
                model=tts.tts_model,
                voice=tts.voice_model,
                input="Test message for NPCL Voice Assistant",
                response_format="mp3",
                speed=1.0
            )
            
            if response.content:
                print("✅ Voice generation successful!")
                print(f"📊 Audio data size: {len(response.content)} bytes")
            else:
                print("❌ Voice generation failed - no audio data")
                
        except Exception as e:
            print(f"❌ Voice generation failed: {e}")
            return False
        
        print("\n🎉 Enhanced TTS test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_enhanced_tts()
    if success:
        print("\n✅ Enhanced TTS is ready for ARI bot!")
    else:
        print("\n❌ Enhanced TTS needs more work")
    
    sys.exit(0 if success else 1)