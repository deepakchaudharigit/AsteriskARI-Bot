#!/usr/bin/env python3
"""
Basic audio file creation script for NPCL IVR system
Creates placeholder files when TTS dependencies are not available
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def create_placeholder_file(text, filename):
    """Create a placeholder text file when audio creation fails"""
    try:
        output_path = project_root / "sounds" / "en" / f"{filename}.txt"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"Audio placeholder for: {filename}\n")
            f.write(f"Text: {text}\n")
            f.write("Note: Install gtts and pydub to generate actual audio files\n")
        print(f"Created placeholder: {output_path}")
        return True
    except Exception as e:
        print(f"Error creating placeholder {filename}: {e}")
        return False

def create_audio_file_with_tts(text, filename, language='en'):
    """Create audio file using TTS if available"""
    try:
        from gtts import gTTS
        from pydub import AudioSegment
        import tempfile
        
        # Create TTS object
        tts = gTTS(text=text, lang=language, slow=False)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
            tts.save(temp_file.name)
            
            # Convert to WAV format for Asterisk
            audio = AudioSegment.from_mp3(temp_file.name)
            
            # Convert to format suitable for Asterisk (8kHz, mono, 16-bit)
            audio = audio.set_frame_rate(8000).set_channels(1).set_sample_width(2)
            
            # Save as WAV
            output_path = project_root / "sounds" / "en" / f"{filename}.wav"
            audio.export(output_path, format="wav")
            
            print(f"Created audio: {output_path}")
            
            # Cleanup temp file
            os.unlink(temp_file.name)
            return True
            
    except ImportError:
        print(f"TTS dependencies not available for {filename}, creating placeholder")
        return create_placeholder_file(text, filename)
    except Exception as e:
        print(f"Error creating audio {filename}: {e}, creating placeholder")
        return create_placeholder_file(text, filename)

def main():
    """Create all required audio files"""
    
    # Ensure sounds directory exists
    sounds_dir = project_root / "sounds" / "en"
    sounds_dir.mkdir(parents=True, exist_ok=True)
    
    # Audio files to create
    audio_files = {
        "welcome-to-npcl": "Welcome to NPCL customer service. Your call is important to us.",
        "npcl-main-menu": """Welcome to NPCL customer service. Please select from the following options:
                            Press 1 for AI voice assistant,
                            Press 2 for customer service,
                            Press 3 for technical support,
                            Press 4 for billing department,
                            Press 9 for emergency power outage reporting.""",
        "technical-support": "Connecting you to technical support. Please wait.",
        "billing-department": "Connecting you to billing department. Please wait.",
        "emergency-outage": "Emergency power outage reporting. Please describe your location and the nature of the outage.",
        "queue-periodic-announce": "Thank you for holding. Your call is important to us. Please continue to hold.",
        "queue-technical-announce": "Thank you for calling NPCL technical support. Your call will be answered in the order it was received.",
        "queue-billing-announce": "Thank you for calling NPCL billing department. Your call will be answered shortly.",
        "queue-emergency-announce": "Emergency services. Your call is being prioritized.",
        "hello-world": "Hello World! This is NPCL voice assistant test.",
        "invalid": "Invalid selection. Please try again.",
        "beep": "Please speak after the beep."
    }
    
    print("Creating NPCL IVR audio files...")
    
    success_count = 0
    for filename, text in audio_files.items():
        if create_audio_file_with_tts(text, filename):
            success_count += 1
    
    print(f"\nProcessed {success_count}/{len(audio_files)} audio files in {sounds_dir}")
    
    if success_count == len(audio_files):
        print("✅ All audio files created successfully!")
    else:
        print("⚠️  Some files created as placeholders. Install 'gtts pydub' for actual audio files.")
    
    return success_count > 0

if __name__ == "__main__":
    if main():
        sys.exit(0)
    else:
        sys.exit(1)