#!/usr/bin/env python3
"""
Audio System Test Script
Tests microphone, speakers, and audio dependencies.
"""

import sys
import time
import tempfile
import wave
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported."""
    print("🔍 Testing imports...")
    
    modules = [
        ('pyaudio', 'PyAudio'),
        ('speech_recognition', 'SpeechRecognition'),
        ('openai', 'OpenAI'),
        ('pydub', 'Pydub'),
        ('numpy', 'NumPy'),
        ('colorama', 'Colorama'),
        ('keyboard', 'Keyboard'),
        ('webrtcvad', 'WebRTC VAD'),
        ('dotenv', 'Python-dotenv')
    ]
    
    failed_imports = []
    
    for module_name, display_name in modules:
        try:
            __import__(module_name)
            print(f"  ✅ {display_name}")
        except ImportError as e:
            print(f"  ❌ {display_name}: {e}")
            failed_imports.append(module_name)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("✅ All imports successful!")
    return True

def test_microphone():
    """Test microphone functionality."""
    print("\n🎤 Testing microphone...")
    
    try:
        import pyaudio
        import speech_recognition as sr
        
        # Initialize components
        audio = pyaudio.PyAudio()
        recognizer = sr.Recognizer()
        
        # List available microphones
        print("Available microphones:")
        for i in range(audio.get_device_count()):
            device_info = audio.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                print(f"  {i}: {device_info['name']}")
        
        # Test default microphone
        try:
            microphone = sr.Microphone()
            with microphone as source:
                print("🔧 Calibrating microphone...")
                recognizer.adjust_for_ambient_noise(source, duration=1)
            
            print("✅ Microphone test successful!")
            
        except Exception as e:
            print(f"❌ Microphone test failed: {e}")
            return False
        
        finally:
            audio.terminate()
            
    except Exception as e:
        print(f"❌ Microphone setup failed: {e}")
        return False
    
    return True

def test_audio_recording():
    """Test audio recording functionality."""
    print("\n🔴 Testing audio recording...")
    
    try:
        import pyaudio
        import wave
        
        # Audio parameters
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        RECORD_SECONDS = 2
        
        audio = pyaudio.PyAudio()
        
        print("Recording 2 seconds of audio...")
        
        stream = audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )
        
        frames = []
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)
        
        stream.stop_stream()
        stream.close()
        audio.terminate()
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            wf = wave.open(temp_file.name, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
            wf.close()
            
            # Check file size
            file_size = Path(temp_file.name).stat().st_size
            if file_size > 1000:  # Should be at least 1KB for 2 seconds
                print(f"✅ Audio recording successful! ({file_size} bytes)")
                Path(temp_file.name).unlink()  # Clean up
                return True
            else:
                print(f"❌ Audio recording failed - file too small ({file_size} bytes)")
                return False
                
    except Exception as e:
        print(f"❌ Audio recording test failed: {e}")
        return False

def test_audio_playback():
    """Test audio playback functionality."""
    print("\n🔊 Testing audio playback...")
    
    try:
        import pyaudio
        import numpy as np
        
        # Generate a simple tone
        SAMPLE_RATE = 44100
        DURATION = 1  # seconds
        FREQUENCY = 440  # A4 note
        
        # Generate sine wave
        t = np.linspace(0, DURATION, int(SAMPLE_RATE * DURATION), False)
        wave_data = np.sin(2 * np.pi * FREQUENCY * t)
        
        # Convert to 16-bit integers
        audio_data = (wave_data * 32767).astype(np.int16)
        
        # Play the tone
        audio = pyaudio.PyAudio()
        
        stream = audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=SAMPLE_RATE,
            output=True
        )
        
        print("Playing test tone (440Hz for 1 second)...")
        stream.write(audio_data.tobytes())
        
        stream.stop_stream()
        stream.close()
        audio.terminate()
        
        print("✅ Audio playback test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Audio playback test failed: {e}")
        return False

def test_openai_connection():
    """Test OpenAI API connection."""
    print("\n🤖 Testing OpenAI connection...")
    
    try:
        import openai
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        api_key = os.getenv('OPENAI_API_KEY')
        
        if not api_key:
            print("❌ OPENAI_API_KEY not found in .env file")
            print("Please add your API key to the .env file")
            return False
        
        if api_key == "your_openai_api_key_here":
            print("❌ Please replace the placeholder API key in .env file")
            return False
        
        # Test API connection
        client = openai.OpenAI(api_key=api_key)
        
        # Simple test request
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        
        print("✅ OpenAI API connection successful!")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI API test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Audio System Test Suite")
    print("=" * 40)
    
    tests = [
        ("Import Test", test_imports),
        ("Microphone Test", test_microphone),
        ("Audio Recording Test", test_audio_recording),
        ("Audio Playback Test", test_audio_playback),
        ("OpenAI API Test", test_openai_connection)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except KeyboardInterrupt:
            print("\n⏹️ Tests interrupted by user")
            break
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 Test Results Summary:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your system is ready for the voice chatbot.")
    else:
        print("⚠️ Some tests failed. Please check the errors above and install missing dependencies.")
        print("Run: python setup.py")

if __name__ == "__main__":
    main()