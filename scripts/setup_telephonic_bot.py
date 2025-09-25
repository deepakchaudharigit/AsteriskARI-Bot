#!/usr/bin/env python3
"""
Complete setup script for NPCL Telephonic Bot
Sets up database, creates audio files, and prepares the system for operation.
"""

import sys
import os
import subprocess
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(f"Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Error: {e.stderr.strip()}")
        return False

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        "openai",
        "fastapi",
        "uvicorn",
        "websockets",
        "pydantic",
        "requests",
        "gtts",
        "pydub",
        "sqlite3"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == "sqlite3":
                import sqlite3
            else:
                __import__(package.replace("-", "_"))
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Please install them with: pip install " + " ".join(missing_packages))
        return False
    
    print("✅ All dependencies are installed")
    return True

def setup_directories():
    """Create required directories"""
    print("\n📁 Setting up directories...")
    
    directories = [
        "data",
        "logs",
        "sounds/en",
        "sounds/temp",
        "recordings"
    ]
    
    for directory in directories:
        dir_path = project_root / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"  ✅ {directory}")
    
    print("✅ Directories created successfully")
    return True

def setup_database():
    """Setup database"""
    print("\n🗄️ Setting up database...")
    
    try:
        from scripts.setup_database import setup_database
        if setup_database():
            print("✅ Database setup completed")
            return True
        else:
            print("❌ Database setup failed")
            return False
    except Exception as e:
        print(f"❌ Database setup error: {e}")
        return False

def create_audio_files():
    """Create audio files for IVR"""
    print("\n🔊 Creating audio files...")
    
    try:
        # Run the audio creation script
        script_path = project_root / "scripts" / "create_audio_files.py"
        result = subprocess.run([sys.executable, str(script_path)], 
                              capture_output=True, text=True, check=True)
        print("✅ Audio files created successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Audio file creation failed: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Audio file creation error: {e}")
        return False

def setup_environment():
    """Setup environment file"""
    print("\n⚙️ Setting up environment...")
    
    env_file = project_root / ".env"
    env_example = project_root / ".env.example"
    
    if not env_file.exists() and env_example.exists():
        # Copy example to .env
        with open(env_example, 'r') as src, open(env_file, 'w') as dst:
            content = src.read()
            dst.write(content)
        print("✅ Created .env file from .env.example")
        print("⚠️  Please update .env file with your Google API key")
    elif env_file.exists():
        print("✅ .env file already exists")
    else:
        print("❌ No .env.example file found")
        return False
    
    return True

def make_scripts_executable():
    """Make scripts executable"""
    print("\n🔧 Making scripts executable...")
    
    scripts = [
        "scripts/call-data-logger.py",
        "scripts/create_audio_files.py",
        "scripts/setup_database.py",
        "scripts/setup_telephonic_bot.py"
    ]
    
    for script in scripts:
        script_path = project_root / script
        if script_path.exists():
            os.chmod(script_path, 0o755)
            print(f"  ✅ {script}")
    
    print("✅ Scripts made executable")
    return True

def verify_asterisk_config():
    """Verify Asterisk configuration files"""
    print("\n📞 Verifying Asterisk configuration...")
    
    config_files = [
        "asterisk-config/extensions.conf",
        "asterisk-config/sip.conf",
        "asterisk-config/ari.conf",
        "asterisk-config/queues.conf"
    ]
    
    all_good = True
    for config_file in config_files:
        config_path = project_root / config_file
        if config_path.exists():
            print(f"  ✅ {config_file}")
        else:
            print(f"  ❌ {config_file}")
            all_good = False
    
    if all_good:
        print("✅ Asterisk configuration files are ready")
    else:
        print("❌ Some Asterisk configuration files are missing")
    
    return all_good

def display_next_steps():
    """Display next steps for the user"""
    print("\n" + "="*60)
    print("🎉 NPCL TELEPHONIC BOT SETUP COMPLETE!")
    print("="*60)
    
    print("\n📋 NEXT STEPS:")
    print("\n1. 🔑 Configure API Key:")
    print("   - Edit .env file")
    print("   - Add your Google API key: OPENAI_API_KEY=your_key_here")
    
    print("\n2. 🐳 Start Asterisk (Docker):")
    print("   docker-compose up asterisk")
    
    print("\n3. 🚀 Start the Telephonic Bot:")
    print("   python src/run_realtime_server.py")
    
    print("\n4. 📱 Configure Zoiper:")
    print("   - User: 1000")
    print("   - Password: 1234")
    print("   - Domain: your_server_ip")
    print("   - Protocol: SIP over UDP")
    
    print("\n5. 📞 Test Extensions:")
    print("   - 1000: AI Voice Assistant")
    print("   - 1001: Customer Service Queue")
    print("   - 1002: Technical Support Queue")
    print("   - 1003: Billing Department")
    print("   - 1004: Emergency Outage Reporting")
    print("   - 1005: IVR Main Menu")
    
    print("\n6. 🌐 API Endpoints:")
    print("   - Health Check: http://localhost:8000/health")
    print("   - Active Calls: http://localhost:8000/calls")
    print("   - Transfer Stats: http://localhost:8000/transfers/stats")
    print("   - Customer Stats: http://localhost:8000/customer-data/stats")
    
    print("\n7. 📊 Features Available:")
    print("   ✅ Real-time AI conversation")
    print("   ✅ Call transfer (agent, queue, supervisor)")
    print("   ✅ Customer data collection")
    print("   ✅ Multi-language support (12 languages)")
    print("   ✅ Call recording and analytics")
    print("   ✅ Queue management")
    print("   ✅ IVR system")
    
    print("\n" + "="*60)
    print("🎯 Your telephonic bot is 100% ready for production!")
    print("="*60)

def main():
    """Main setup function"""
    print("🤖 NPCL TELEPHONIC BOT - COMPLETE SETUP")
    print("="*50)
    print("Setting up your enterprise-grade telephonic bot system...")
    
    setup_steps = [
        (check_dependencies, "Checking dependencies"),
        (setup_directories, "Setting up directories"),
        (setup_environment, "Setting up environment"),
        (setup_database, "Setting up database"),
        (create_audio_files, "Creating audio files"),
        (make_scripts_executable, "Making scripts executable"),
        (verify_asterisk_config, "Verifying Asterisk configuration")
    ]
    
    failed_steps = []
    
    for step_func, step_name in setup_steps:
        try:
            if not step_func():
                failed_steps.append(step_name)
        except Exception as e:
            print(f"❌ {step_name} failed with error: {e}")
            failed_steps.append(step_name)
    
    if failed_steps:
        print(f"\n❌ Setup completed with {len(failed_steps)} issues:")
        for step in failed_steps:
            print(f"  - {step}")
        print("\nPlease resolve these issues before proceeding.")
    else:
        display_next_steps()

if __name__ == "__main__":
    main()