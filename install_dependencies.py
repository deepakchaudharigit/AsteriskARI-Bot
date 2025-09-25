#!/usr/bin/env python3
"""
Install required dependencies for NPCL Voice Assistant
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a package using pip"""
    try:
        # Try different pip commands
        commands = [
            [sys.executable, "-m", "pip", "install", package],
            ["pip3", "install", package],
            ["pip", "install", package]
        ]
        
        for cmd in commands:
            try:
                result = subprocess.run(cmd, check=True, capture_output=True, text=True)
                print(f"✅ Successfully installed {package}")
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue
        
        print(f"❌ Failed to install {package}")
        return False
        
    except Exception as e:
        print(f"❌ Error installing {package}: {e}")
        return False

def main():
    """Install all required dependencies"""
    print("🔧 Installing NPCL Voice Assistant Dependencies")
    print("=" * 50)
    
    # Check if in virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment detected")
    else:
        print("⚠️  Not in virtual environment")
    
    # Required packages
    packages = [
        "openai",
        "uvicorn", 
        "fastapi",
        "pyttsx3",
        "websockets",
        "pygame",
        "requests"
    ]
    
    print(f"\n📦 Installing {len(packages)} packages...")
    
    success_count = 0
    for package in packages:
        print(f"\n📥 Installing {package}...")
        if install_package(package):
            success_count += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Installation Summary:")
    print(f"✅ Successful: {success_count}/{len(packages)}")
    print(f"❌ Failed: {len(packages) - success_count}/{len(packages)}")
    
    if success_count == len(packages):
        print("\n🎉 All dependencies installed successfully!")
        print("🚀 You can now run: python3 src/main.py --ari-bot")
    else:
        print("\n⚠️  Some dependencies failed to install")
        print("💡 Try running manually:")
        for package in packages:
            print(f"   pip install {package}")

if __name__ == "__main__":
    main()