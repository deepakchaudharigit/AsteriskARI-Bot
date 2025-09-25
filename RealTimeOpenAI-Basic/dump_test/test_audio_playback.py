#!/usr/bin/env python3
"""
Test audio playback with different methods
"""

import os
import tempfile
import subprocess
from dotenv import load_dotenv
import openai

def test_audio_playback():
    # Clear any existing environment variable
    if 'OPENAI_API_KEY' in os.environ:
        del os.environ['OPENAI_API_KEY']
    load_dotenv()
    
    client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    print("🔊 Testing audio playback...")
    
    try:
        # Generate a short audio clip
        with client.audio.speech.with_streaming_response.create(
            model="tts-1",
            voice="alloy",
            input="Hello! This is a test of the audio playback system.",
            speed=1.0
        ) as response:
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_audio:
                for chunk in response.iter_bytes():
                    temp_audio.write(chunk)
                temp_audio.flush()
                
                print(f"✅ Audio file created: {temp_audio.name}")
                
                # Test afplay (macOS)
                try:
                    print("🎵 Testing afplay (macOS)...")
                    subprocess.run(["afplay", temp_audio.name], check=True, timeout=10)
                    print("✅ afplay works!")
                    return True
                except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
                    print(f"❌ afplay failed: {e}")
                
                # Clean up
                os.unlink(temp_audio.name)
                
    except Exception as e:
        print(f"❌ Audio generation failed: {e}")
        return False
    
    return False

if __name__ == "__main__":
    test_audio_playback()