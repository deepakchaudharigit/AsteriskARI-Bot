#!/usr/bin/env python3
"""
Quick setup test for the voice chatbot
"""

import os
import sys
from dotenv import load_dotenv

def test_imports():
    """Test if all required modules can be imported."""
    print("🔍 Testing imports...")
    
    try:
        import openai
        print("  ✅ OpenAI")
    except ImportError as e:
        print(f"  ❌ OpenAI: {e}")
        return False
        
    try:
        import pyaudio
        print("  ✅ PyAudio")
    except ImportError as e:
        print(f"  ❌ PyAudio: {e}")
        return False
        
    try:
        import speech_recognition
        print("  ✅ SpeechRecognition")
    except ImportError as e:
        print(f"  ❌ SpeechRecognition: {e}")
        return False
        
    try:
        import pydub
        print("  ✅ Pydub")
    except ImportError as e:
        print(f"  ❌ Pydub: {e}")
        return False
        
    try:
        import colorama
        print("  ✅ Colorama")
    except ImportError as e:
        print(f"  ❌ Colorama: {e}")
        return False
        
    try:
        import numpy
        print("  ✅ NumPy")
    except ImportError as e:
        print(f"  ❌ NumPy: {e}")
        return False
        
    print("✅ All imports successful!")
    return True

def test_env_file():
    """Test if .env file exists and has API key."""
    print("\n🔍 Testing environment configuration...")
    
    if not os.path.exists('.env'):
        print("  ❌ .env file not found")
        return False
    
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("  ❌ OPENAI_API_KEY not found in .env file")
        return False
    
    if api_key == "your_openai_api_key_here":
        print("  ❌ Please replace the placeholder API key in .env file")
        return False
    
    print("  ✅ .env file configured")
    return True

def test_microphone():
    """Test microphone availability."""
    print("\n🔍 Testing microphone...")
    
    try:
        import pyaudio
        import speech_recognition as sr
        
        audio = pyaudio.PyAudio()
        
        # Check for input devices
        input_devices = []
        for i in range(audio.get_device_count()):
            device_info = audio.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                input_devices.append(device_info['name'])
        
        if input_devices:
            print(f"  ✅ Found {len(input_devices)} input device(s)")
            print(f"  📱 Default: {input_devices[0]}")
        else:
            print("  ❌ No input devices found")
            return False
        
        audio.terminate()
        return True
        
    except Exception as e:
        print(f"  ❌ Microphone test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Voice Chatbot Setup Test")
    print("=" * 40)
    
    tests = [
        ("Import Test", test_imports),
        ("Environment Test", test_env_file),
        ("Microphone Test", test_microphone)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 Test Results:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 Setup complete! You can now run the voice chatbot:")
        print("   source venv/bin/activate")
        print("   python3 voice_chatbot_simple.py")
    else:
        print("\n⚠️ Some tests failed. Please check the errors above.")
        if not results[1][1]:  # Environment test failed
            print("\n📝 To fix environment issues:")
            print("   1. Make sure .env file exists")
            print("   2. Add your OpenAI API key to .env file")
            print("   3. Get your API key from: https://platform.openai.com/api-keys")

if __name__ == "__main__":
    main()