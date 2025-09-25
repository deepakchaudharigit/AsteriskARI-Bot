#!/usr/bin/env python3
"""
Voice Configuration Utility for NPCL Voice Assistant
Allows easy configuration of voice settings and testing
"""

import os
import sys
from pathlib import Path

# Set API key
os.environ['OPENAI_API_KEY'] = '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'

def print_banner():
    """Print configuration banner"""
    print("🎤 NPCL Voice Assistant - Voice Configuration")
    print("=" * 55)
    print("Configure high-quality OpenAI TTS voices")
    print()

def show_voice_options():
    """Show available voice options with descriptions"""
    voices = {
        'alloy': '🎯 Neutral, balanced voice - Professional and clear',
        'echo': '📢 Clear, crisp voice - Great for announcements',
        'fable': '😊 Warm, friendly voice - Perfect for customer service',
        'onyx': '🎩 Deep, authoritative voice - Formal and commanding',
        'nova': '⚡ Energetic, youthful voice - Engaging and dynamic',
        'shimmer': '🌟 Soft, gentle voice - Calm and soothing'
    }
    
    print("🎵 Available OpenAI TTS Voices:")
    print("-" * 40)
    
    for i, (voice, description) in enumerate(voices.items(), 1):
        print(f"{i}. {voice.upper():<8} - {description}")
    
    print()
    return voices

def get_current_settings():
    """Get current voice settings from .env file"""
    try:
        env_file = Path('.env')
        if env_file.exists():
            with open(env_file, 'r') as f:
                content = f.read()
                
            current_voice = None
            current_tts_model = None
            
            for line in content.split('\n'):
                if line.startswith('VOICE_MODEL='):
                    current_voice = line.split('=', 1)[1].strip()
                elif line.startswith('TTS_MODEL='):
                    current_tts_model = line.split('=', 1)[1].strip()
            
            return current_voice, current_tts_model
        else:
            return None, None
    except Exception as e:
        print(f"⚠️  Error reading settings: {e}")
        return None, None

def update_voice_settings(voice: str, tts_model: str = "tts-1-hd"):
    """Update voice settings in .env file"""
    try:
        env_file = Path('.env')
        if env_file.exists():
            # Read current content
            with open(env_file, 'r') as f:
                lines = f.readlines()
            
            # Update existing lines or add new ones
            voice_updated = False
            tts_updated = False
            openai_voice_updated = False
            
            for i, line in enumerate(lines):
                if line.startswith('VOICE_MODEL='):
                    lines[i] = f'VOICE_MODEL={voice}\n'
                    voice_updated = True
                elif line.startswith('TTS_MODEL='):
                    lines[i] = f'TTS_MODEL={tts_model}\n'
                    tts_updated = True
                elif line.startswith('OPENAI_VOICE='):
                    lines[i] = f'OPENAI_VOICE={voice}\n'
                    openai_voice_updated = True
            
            # Add missing settings
            if not voice_updated:
                lines.append(f'VOICE_MODEL={voice}\n')
            if not tts_updated:
                lines.append(f'TTS_MODEL={tts_model}\n')
            if not openai_voice_updated:
                lines.append(f'OPENAI_VOICE={voice}\n')
            
            # Write back to file
            with open(env_file, 'w') as f:
                f.writelines(lines)
            
            print(f"✅ Voice settings updated:")
            print(f"   Voice: {voice}")
            print(f"   TTS Model: {tts_model}")
            return True
        else:
            print("❌ .env file not found")
            return False
    except Exception as e:
        print(f"❌ Failed to update settings: {e}")
        return False

def test_voice(voice: str):
    """Test a specific voice"""
    try:
        # Add src to path for imports
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        
        from voice_assistant.audio.enhanced_tts import speak_text_enhanced
        
        test_message = f"Hello! This is the {voice} voice from NPCL Customer Service. How does this sound for our voice assistant?"
        
        print(f"🔊 Testing {voice} voice...")
        print(f"Message: {test_message}")
        print()
        
        success = speak_text_enhanced(test_message, voice=voice)
        
        if success:
            print(f"✅ {voice} voice test successful!")
            return True
        else:
            print(f"❌ {voice} voice test failed!")
            return False
            
    except Exception as e:
        print(f"❌ Voice test failed: {e}")
        return False

def main():
    """Main configuration interface"""
    print_banner()
    
    # Show current settings
    current_voice, current_tts = get_current_settings()
    if current_voice:
        print(f"📋 Current Settings:")
        print(f"   Voice: {current_voice}")
        print(f"   TTS Model: {current_tts or 'tts-1-hd'}")
        print()
    
    while True:
        print("🎯 Voice Configuration Options:")
        print("1. 🎵 Show available voices")
        print("2. 🔊 Test current voice")
        print("3. 🎤 Test a specific voice")
        print("4. ⚙️  Change voice settings")
        print("5. 🧪 Test all voices")
        print("6. ❌ Exit")
        print()
        
        try:
            choice = input("Enter your choice (1-6): ").strip()
            
            if choice == '1':
                voices = show_voice_options()
                
            elif choice == '2':
                if current_voice:
                    test_voice(current_voice)
                else:
                    print("❌ No current voice configured")
                
            elif choice == '3':
                voices = show_voice_options()
                voice_choice = input("Enter voice name (alloy, echo, fable, onyx, nova, shimmer): ").strip().lower()
                
                if voice_choice in ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer']:
                    test_voice(voice_choice)
                else:
                    print("❌ Invalid voice name")
                
            elif choice == '4':
                voices = show_voice_options()
                voice_choice = input("Enter voice name: ").strip().lower()
                
                if voice_choice in ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer']:
                    print()
                    print("🎛️  TTS Model Options:")
                    print("1. tts-1-hd (High quality, slower)")
                    print("2. tts-1 (Standard quality, faster)")
                    
                    tts_choice = input("Choose TTS model (1-2, default=1): ").strip()
                    tts_model = "tts-1-hd" if tts_choice != "2" else "tts-1"
                    
                    # Test the voice first
                    print(f"\n🔊 Testing {voice_choice} with {tts_model}...")
                    if test_voice(voice_choice):
                        confirm = input(f"\n✅ Save {voice_choice} as default voice? (y/n): ").strip().lower()
                        
                        if confirm in ['y', 'yes']:
                            if update_voice_settings(voice_choice, tts_model):
                                current_voice = voice_choice
                                current_tts = tts_model
                                print("🎉 Voice settings saved successfully!")
                            else:
                                print("❌ Failed to save settings")
                        else:
                            print("ℹ️  Settings not saved")
                    else:
                        print("❌ Voice test failed, settings not saved")
                else:
                    print("❌ Invalid voice name")
                
            elif choice == '5':
                # Run full voice testing
                try:
                    import subprocess
                    subprocess.run([sys.executable, "test_voices.py"])
                except Exception as e:
                    print(f"❌ Failed to run voice testing: {e}")
                
            elif choice == '6':
                print("👋 Voice configuration complete!")
                break
                
            else:
                print("❌ Invalid choice")
            
            print()
            
        except KeyboardInterrupt:
            print("\n👋 Configuration interrupted")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()