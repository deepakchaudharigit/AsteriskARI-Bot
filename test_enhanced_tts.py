#!/usr/bin/env python3
"""
Quick test for Enhanced TTS in main application
"""

import os
import sys
from pathlib import Path

# Set API key
os.environ['OPENAI_API_KEY'] = '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'

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_main_tts():
    """Test TTS functions from main.py"""
    
    print("🧪 Testing Enhanced TTS Integration")
    print("=" * 40)
    
    try:
        # Import the functions from main.py
        from main import speak_text_enhanced, speak_text_robust
        
        print("✅ Successfully imported TTS functions from main.py")
        
        # Test enhanced TTS
        print("\n🔊 Testing Enhanced TTS...")
        test_message = "Hello! This is a test of the enhanced TTS system from the main application."
        
        success = speak_text_enhanced(test_message)
        
        if success:
            print("✅ Enhanced TTS test successful!")
        else:
            print("❌ Enhanced TTS test failed!")
        
        # Test robust TTS (should use enhanced internally)
        print("\n🔊 Testing Robust TTS (should use enhanced)...")
        test_message2 = "This is a test of the robust TTS function which should use enhanced TTS internally."
        
        success2 = speak_text_robust(test_message2)
        
        if success2:
            print("✅ Robust TTS test successful!")
        else:
            print("❌ Robust TTS test failed!")
        
        print("\n🎉 TTS integration test completed!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you're in the project root directory")
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_main_tts()