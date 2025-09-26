#!/usr/bin/env python3
"""
Fix Call Disconnect Issues for NPCL Asterisk ARI Voice Assistant
This script addresses the main causes of call disconnection after welcome message
"""

import subprocess
import os
import sys

def run_command(command, timeout=10):
    """Run a command and return output"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "", "Command timed out", 1
    except Exception as e:
        return "", str(e), 1

def check_stasis_app():
    """Check if Stasis application is registered"""
    print("🔍 Checking Stasis application registration...")
    
    stdout, stderr, returncode = run_command("sudo asterisk -rx 'stasis show apps'")
    if returncode == 0:
        if "openai-voice-assistant" in stdout:
            print("✅ Stasis app 'openai-voice-assistant' is registered")
            return True
        else:
            print("❌ Stasis app 'openai-voice-assistant' NOT registered")
            print("   This is the main cause of call disconnection!")
            return False
    else:
        print(f"❌ Error checking Stasis apps: {stderr}")
        return False

def fix_pjsip_media_config():
    """Fix PJSIP media configuration issues"""
    print("\n🔧 Fixing PJSIP media configuration...")
    
    config_file = "asterisk-config/pjsip.conf"
    if not os.path.exists(config_file):
        print(f"❌ Configuration file not found: {config_file}")
        return False
    
    # Read current config
    with open(config_file, 'r') as f:
        content = f.read()
    
    # Fix media_address issue
    if "media_address=127.0.0.1" in content:
        print("🔧 Fixing media_address from 127.0.0.1 to 192.168.0.212...")
        content = content.replace("media_address=127.0.0.1", "media_address=192.168.0.212")
        
        # Write back the fixed config
        with open(config_file, 'w') as f:
            f.write(content)
        
        print("✅ Fixed media_address in pjsip.conf")
        
        # Copy to system and reload
        run_command("sudo cp asterisk-config/pjsip.conf /etc/asterisk/pjsip.conf")
        run_command("sudo asterisk -rx 'pjsip reload'")
        print("✅ Reloaded PJSIP configuration")
        return True
    else:
        print("✅ media_address configuration looks correct")
        return True

def configure_rtp_settings():
    """Configure RTP settings for better media handling"""
    print("\n🔧 Configuring RTP settings...")
    
    rtp_config = """[general]
rtpstart=10000
rtpend=20000
rtpchecksums=no
rtptimeout=60
rtpholdtimeout=300
rtpkeepalive=5
icesupport=yes
stunaddr=stun.l.google.com:19302
"""
    
    # Write RTP configuration
    with open("asterisk-config/rtp.conf", 'w') as f:
        f.write(rtp_config)
    
    print("✅ Created RTP configuration")
    
    # Copy to system
    run_command("sudo cp asterisk-config/rtp.conf /etc/asterisk/rtp.conf")
    run_command("sudo asterisk -rx 'rtp reload'")
    print("✅ Applied RTP configuration")

def start_proper_voice_assistant():
    """Start the proper voice assistant that registers Stasis app"""
    print("\n🚀 Starting proper voice assistant...")
    
    # Check if already running
    stdout, stderr, returncode = run_command("ps aux | grep -E '(ari_bot|run_realtime_server)' | grep -v grep")
    if returncode == 0 and stdout:
        print("ℹ️  Voice assistant process already running:")
        print(stdout)
        return True
    
    print("🔄 Starting ARI bot (this registers the Stasis app)...")
    print("   This will run in the background...")
    
    # Start the ARI bot in background
    command = "nohup python3 ari_bot.py > logs/ari_bot.log 2>&1 &"
    run_command(command)
    
    print("✅ Started ARI bot")
    print("   Check logs: tail -f logs/ari_bot.log")
    
    return True

def test_extensions():
    """Test different extensions to isolate the issue"""
    print("\n🧪 Extension Testing Guide:")
    print("=" * 50)
    
    print("\n📞 Test these extensions in order:")
    print("1. Extension 1010 - Simple test (no ARI needed)")
    print("   - Should play demo-congrats and stay connected")
    print("   - If this fails: SIP/RTP configuration issue")
    print("   - If this works: Continue to step 2")
    
    print("\n2. Extension 9000 - Echo test")
    print("   - Should echo back your voice")
    print("   - Tests bidirectional audio")
    print("   - If this fails: Audio/codec issue")
    
    print("\n3. Extension 1000 - Voice assistant")
    print("   - Should play welcome message then connect to AI")
    print("   - If disconnects after welcome: Stasis app issue")
    print("   - If works: Success!")
    
    print("\n📋 Zoiper Test Settings:")
    print("├── Username: 1000")
    print("├── Password: 1234") 
    print("├── Domain: 192.168.0.212")
    print("├── Codecs: PCMU, PCMA, GSM only")
    print("└── NAT: Enable")

def provide_immediate_fixes():
    """Provide immediate fixes for common issues"""
    print("\n" + "=" * 60)
    print("🎯 IMMEDIATE FIXES FOR CALL DISCONNECT")
    print("=" * 60)
    
    print("\n🔧 Fix 1: Start Proper Voice Assistant")
    print("Command: python3 ari_bot.py")
    print("This registers the Stasis application that handles calls")
    
    print("\n🔧 Fix 2: Test Simple Extension First")
    print("Call: 1010 (simple test without ARI)")
    print("Should stay connected and play demo message")
    
    print("\n🔧 Fix 3: Check Asterisk Logs")
    print("Command: sudo tail -f /var/log/asterisk/messages")
    print("Look for: Stasis app registration, SIP errors, RTP issues")
    
    print("\n🔧 Fix 4: Verify Stasis App")
    print("Command: sudo asterisk -rx 'stasis show apps'")
    print("Should show: openai-voice-assistant")
    
    print("\n🔧 Fix 5: Enable SIP Debug")
    print("Command: sudo asterisk -rx 'sip set debug on'")
    print("Command: sudo asterisk -rx 'pjsip set logger on'")
    print("Then make call and check logs")

def main():
    """Main function to fix call disconnect issues"""
    print("🔧 NPCL Call Disconnect Fix Tool")
    print("=" * 50)
    print("Fixing common causes of call disconnection after welcome message")
    print()
    
    # Check current status
    print("📋 Current Status Check:")
    
    # Check if voice assistant is running
    stdout, stderr, returncode = run_command("ps aux | grep start_voice_assistant | grep -v grep")
    if returncode == 0 and stdout:
        print("✅ Voice assistant process found")
        print("   But it might not be the right one for Stasis registration")
    else:
        print("❌ No voice assistant process found")
    
    # Check Stasis app registration
    stasis_ok = check_stasis_app()
    
    # Apply fixes
    print("\n🔧 Applying Fixes:")
    
    # Fix 1: PJSIP media configuration
    fix_pjsip_media_config()
    
    # Fix 2: RTP settings
    configure_rtp_settings()
    
    # Fix 3: Start proper voice assistant if Stasis not registered
    if not stasis_ok:
        print("\n❌ Stasis app not registered - this is the main issue!")
        print("🔧 Starting proper ARI bot to register Stasis app...")
        start_proper_voice_assistant()
        
        print("\n⏳ Waiting 5 seconds for registration...")
        import time
        time.sleep(5)
        
        # Check again
        stasis_ok = check_stasis_app()
        if stasis_ok:
            print("✅ Stasis app now registered!")
        else:
            print("❌ Stasis app still not registered")
            print("   Manual start required: python3 ari_bot.py")
    
    # Provide testing guide
    test_extensions()
    
    # Provide immediate fixes
    provide_immediate_fixes()
    
    print("\n" + "=" * 60)
    print("🎯 SUMMARY")
    print("=" * 60)
    
    if stasis_ok:
        print("✅ Stasis app is registered - calls should work")
        print("📞 Test: Call 1000 from Zoiper")
        print("🎯 Expected: Welcome message → AI conversation")
    else:
        print("❌ Stasis app NOT registered - calls will disconnect")
        print("🔧 Fix: Run 'python3 ari_bot.py' to register Stasis app")
        print("📞 Test: Call 1010 first (simple test)")
    
    print("\n💡 Pro Tip: Always test extension 1010 first")
    print("   If 1010 works but 1000 doesn't = Stasis issue")
    print("   If both fail = SIP/RTP configuration issue")

if __name__ == "__main__":
    main()