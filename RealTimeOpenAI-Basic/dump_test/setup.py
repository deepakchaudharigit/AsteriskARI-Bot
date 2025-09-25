#!/usr/bin/env python3
"""
Setup script for Real-time Voice Chatbot
This script helps install dependencies and configure the environment.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def install_system_dependencies():
    """Install system-level dependencies based on the operating system."""
    system = platform.system().lower()
    
    if system == "darwin":  # macOS
        print("🍎 Detected macOS")
        # Check if Homebrew is installed
        if subprocess.run("which brew", shell=True, capture_output=True).returncode != 0:
            print("❌ Homebrew not found. Please install Homebrew first:")
            print("   /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
            return False
            
        commands = [
            "brew install portaudio",
            "brew install ffmpeg"
        ]
        
    elif system == "linux":
        print("🐧 Detected Linux")
        # Try to detect the package manager
        if subprocess.run("which apt", shell=True, capture_output=True).returncode == 0:
            commands = [
                "sudo apt update",
                "sudo apt install -y portaudio19-dev python3-pyaudio",
                "sudo apt install -y ffmpeg"
            ]
        elif subprocess.run("which yum", shell=True, capture_output=True).returncode == 0:
            commands = [
                "sudo yum install -y portaudio-devel",
                "sudo yum install -y ffmpeg"
            ]
        elif subprocess.run("which pacman", shell=True, capture_output=True).returncode == 0:
            commands = [
                "sudo pacman -S portaudio",
                "sudo pacman -S ffmpeg"
            ]
        else:
            print("❌ Unsupported Linux distribution. Please install portaudio and ffmpeg manually.")
            return False
            
    elif system == "windows":
        print("🪟 Detected Windows")
        print("ℹ️  For Windows, PyAudio wheels should install automatically.")
        print("ℹ️  If you encounter issues, consider installing:")
        print("   - Microsoft Visual C++ Build Tools")
        print("   - FFmpeg (add to PATH)")
        return True
        
    else:
        print(f"❌ Unsupported operating system: {system}")
        return False
    
    # Run system commands
    for command in commands:
        if not run_command(command, f"Running: {command}"):
            return False
            
    return True

def install_python_dependencies():
    """Install Python dependencies."""
    print("🐍 Installing Python dependencies...")
    
    # Upgrade pip first
    if not run_command(f"{sys.executable} -m pip install --upgrade pip", "Upgrading pip"):
        return False
    
    # Install requirements
    if not run_command(f"{sys.executable} -m pip install -r requirements.txt", "Installing Python packages"):
        return False
        
    return True

def create_env_file():
    """Create .env file if it doesn't exist."""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        print("📝 Creating .env file from template...")
        env_file.write_text(env_example.read_text())
        print("✅ .env file created!")
        print("⚠️  Please edit .env file and add your OpenAI API key!")
        return True
    elif env_file.exists():
        print("ℹ️  .env file already exists.")
        return True
    else:
        print("❌ .env.example not found!")
        return False

def check_microphone():
    """Check if microphone is available."""
    print("🎤 Checking microphone availability...")
    try:
        import pyaudio
        audio = pyaudio.PyAudio()
        
        # Get default input device
        default_input = audio.get_default_input_device_info()
        print(f"✅ Default microphone found: {default_input['name']}")
        
        audio.terminate()
        return True
    except Exception as e:
        print(f"❌ Microphone check failed: {e}")
        return False

def main():
    """Main setup function."""
    print("🚀 Setting up Real-time Voice Chatbot...")
    print("=" * 50)
    
    success = True
    
    # Install system dependencies
    if not install_system_dependencies():
        success = False
        print("⚠️  System dependencies installation failed. You may need to install them manually.")
    
    # Install Python dependencies
    if not install_python_dependencies():
        success = False
        print("❌ Python dependencies installation failed!")
        return
    
    # Create .env file
    if not create_env_file():
        success = False
    
    # Check microphone
    if not check_microphone():
        print("⚠️  Microphone check failed. Please ensure your microphone is connected and working.")
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Edit .env file and add your OpenAI API key")
        print("2. Run: python voice_chatbot.py")
        print("\n🔑 Get your OpenAI API key from: https://platform.openai.com/api-keys")
    else:
        print("⚠️  Setup completed with some issues. Please check the errors above.")

if __name__ == "__main__":
    main()