#!/usr/bin/env python3
"""
Voice Testing Script for NPCL Voice Assistant
Tests all available OpenAI TTS voices with sample NPCL content
"""

import os
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Set API key
os.environ['OPENAI_API_KEY'] = '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'

def test_npcl_voices():
    """Test all voices with NPCL-specific content"""
    
    try:
        from voice_assistant.audio.enhanced_tts import EnhancedTTS
        
        print("🎤 NPCL Voice Assistant - Voice Testing")
        print("=" * 50)
        print("Testing OpenAI TTS-1-HD voices with NPCL content")
        print()
        
        # Initialize TTS
        tts = EnhancedTTS()
        
        # NPCL test messages
        test_messages = [
            "Welcome to NPCL Customer Service. I am your voice assistant.",
            "Your complaint number is NPCL-2024-001. Our technical team will address this within 24 hours.",
            "For new power connections, please visit our customer service center with required documents.",
            "Thank you for contacting NPCL. Have a great day!"
        ]
        
        # Get available voices
        voices = tts.get_available_voices()
        
        print(f"Available voices: {len(voices)}")
        print()
        
        for i, (voice, description) in enumerate(voices.items(), 1):
            print(f"🔊 Voice {i}: {voice.upper()}")
            print(f"   Description: {description}")
            print(f"   Testing with NPCL content...")
            
            try:
                # Test with first message
                success = tts.speak_text_enhanced(test_messages[0], voice=voice)
                
                if success:
                    print(f"   ✅ {voice} voice test successful")
                    
                    # Ask user if they want to hear more
                    choice = input(f"   🎧 Hear more samples with {voice}? (y/n): ").strip().lower()
                    
                    if choice in ['y', 'yes']:
                        for j, message in enumerate(test_messages[1:], 2):
                            print(f"   🔊 Sample {j}: {message[:50]}...")
                            tts.speak_text_enhanced(message, voice=voice)
                            time.sleep(0.5)
                else:
                    print(f"   ❌ {voice} voice test failed")
                    
            except Exception as e:
                print(f"   ❌ Error testing {voice}: {e}")
            
            print()
            
            # Pause between voices
            if i < len(voices):
                input("   Press Enter to test next voice...")
                print()
        
        print("=" * 50)
        print("🎉 Voice testing completed!")
        print()
        
        # Ask user to select preferred voice
        print("🎯 Which voice would you like to set as default?")
        voice_list = list(voices.keys())
        
        for i, voice in enumerate(voice_list, 1):
            print(f"{i}. {voice} - {voices[voice]}")
        
        try:
            choice = input(f"\nEnter choice (1-{len(voice_list)}) or press Enter to keep current: ").strip()
            
            if choice and choice.isdigit():
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(voice_list):
                    selected_voice = voice_list[choice_idx]
                    
                    # Update .env file
                    update_voice_in_env(selected_voice)
                    
                    print(f"✅ Voice set to: {selected_voice}")
                    print(f"🔊 Testing selected voice...")
                    
                    tts.speak_text_enhanced(
                        f"Voice successfully changed to {selected_voice}. "
                        f"Welcome to NPCL Customer Service with your new voice assistant.",
                        voice=selected_voice
                    )
                else:
                    print("❌ Invalid choice")
            else:
                print("ℹ️  Keeping current voice settings")
                
        except Exception as e:
            print(f"❌ Error setting voice: {e}")
        
    except ImportError as e:
        print(f"❌ Enhanced TTS not available: {e}")
        print("💡 Make sure to install required packages:")
        print("   pip install openai pygame")
    except Exception as e:
        print(f"❌ Voice testing failed: {e}")

def update_voice_in_env(voice: str):
    """Update voice setting in .env file"""
    try:
        env_file = Path('.env')
        if env_file.exists():
            # Read current content
            with open(env_file, 'r') as f:
                lines = f.readlines()
            
            # Update voice settings
            updated = False
            for i, line in enumerate(lines):
                if line.startswith('VOICE_MODEL='):
                    lines[i] = f'VOICE_MODEL={voice}\n'
                    updated = True
                elif line.startswith('OPENAI_VOICE='):
                    lines[i] = f'OPENAI_VOICE={voice}\n'
                    updated = True
            
            # Add voice settings if not found
            if not updated:
                lines.append(f'\n# Updated voice settings\n')
                lines.append(f'VOICE_MODEL={voice}\n')
                lines.append(f'OPENAI_VOICE={voice}\n')
            
            # Write back to file
            with open(env_file, 'w') as f:
                f.writelines(lines)
            
            print(f"✅ Updated .env file with voice: {voice}")
        else:
            print("⚠️  .env file not found")
            
    except Exception as e:
        print(f"❌ Failed to update .env file: {e}")

def quick_voice_test():
    """Quick test of current voice settings"""
    try:
        from voice_assistant.audio.enhanced_tts import speak_text_enhanced
        
        print("🔊 Quick Voice Test")
        print("=" * 30)
        
        test_message = "Hello! This is NPCL Voice Assistant. I'm testing the current voice configuration."
        
        print(f"Testing: {test_message}")
        success = speak_text_enhanced(test_message)
        
        if success:
            print("✅ Voice test successful!")
        else:
            print("❌ Voice test failed!")
            
    except Exception as e:
        print(f"❌ Quick voice test failed: {e}")

if __name__ == "__main__":
    print("🎤 NPCL Voice Assistant - Voice Configuration")
    print("=" * 50)
    print("1. 🧪 Test all voices")
    print("2. 🔊 Quick test current voice")
    print("3. ❌ Exit")
    print()
    
    try:
        choice = input("Enter your choice (1-3): ").strip()
        
        if choice == '1':
            test_npcl_voices()
        elif choice == '2':
            quick_voice_test()
        elif choice == '3':
            print("👋 Goodbye!")
        else:
            print("❌ Invalid choice")
            
    except KeyboardInterrupt:
        print("\n👋 Voice testing interrupted")
    except Exception as e:
        print(f"❌ Error: {e}")