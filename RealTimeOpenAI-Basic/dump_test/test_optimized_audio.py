#!/usr/bin/env python3
"""
Test audio playback in optimized chatbot
"""

import os
import sys
import tempfile
import subprocess
from dotenv import load_dotenv
import openai

def test_optimized_audio():
    # Clear any existing environment variable
    if 'OPENAI_API_KEY' in os.environ:
        del os.environ['OPENAI_API_KEY']
    load_dotenv()
    
    client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    print("🔊 Testing optimized chatbot audio...")
    
    try:
        # Generate speech using the same method as optimized chatbot
        with client.audio.speech.with_streaming_response.create(
            model="tts-1",
            voice="alloy",
            input="Hello! This is a test of the optimized chatbot audio system.",
            speed=1.1
        ) as response:
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_audio:
                for chunk in response.iter_bytes():
                    temp_audio.write(chunk)
                temp_audio.flush()
                
                print(f"✅ Audio file created: {temp_audio.name}")
                
                # Test afplay (same as optimized chatbot)
                try:
                    print("🎵 Testing afplay (optimized method)...")
                    process = subprocess.Popen(
                        ["afplay", temp_audio.name],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                    
                    # Wait for completion
                    process.wait()
                    print("✅ Optimized audio playback works!")
                    return True
                    
                except Exception as e:
                    print(f"❌ Optimized audio playback failed: {e}")
                    return False
                finally:
                    # Clean up
                    try:
                        os.unlink(temp_audio.name)
                    except:
                        pass
                
    except Exception as e:
        print(f"❌ Audio generation failed: {e}")
        return False

if __name__ == "__main__":
    test_optimized_audio()