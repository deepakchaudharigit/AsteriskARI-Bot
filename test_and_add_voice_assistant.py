#!/usr/bin/env python3
"""
Test Current Setup and Add Voice Assistant Extensions
"""

import subprocess
import time

def run_command(command, timeout=10):
    """Run a command and return output"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "", "Command timed out", 1
    except Exception as e:
        return "", str(e), 1

def check_pjsip_endpoint():
    """Check if PJSIP endpoint is properly configured"""
    print("🔍 Checking PJSIP endpoint configuration...")
    
    stdout, stderr, returncode = run_command("sudo asterisk -rx 'pjsip show endpoint 1000'")
    if returncode == 0:
        if "demo" in stdout:
            print("✅ Endpoint 1000 is using 'demo' context")
            return True
        else:
            print("❌ Endpoint 1000 context not set to demo")
            print(f"Output: {stdout}")
            return False
    else:
        print(f"❌ Error: {stderr}")
        return False

def create_voice_assistant_extensions():
    """Create voice assistant extensions for the demo context"""
    print("\n🔧 Creating voice assistant extensions...")
    
    extensions_to_add = """
; NPCL Voice Assistant Extensions - Add to demo context
exten => 1000,1,NoOp(NPCL Voice Assistant Override)
same => n,Answer()
same => n,Wait(1)
same => n,Playback(demo-congrats)
same => n,Wait(2)
same => n,Stasis(openai-voice-assistant,${CALLERID(num)},${EXTEN})
same => n,Hangup()

exten => 1010,1,NoOp(NPCL Test Extension)
same => n,Answer()
same => n,Wait(1)
same => n,Playback(demo-congrats)
same => n,Wait(3)
same => n,Hangup()

exten => 9000,1,NoOp(Echo Test)
same => n,Answer()
same => n,Echo()
same => n,Hangup()
"""
    
    # Write to a file that can be appended to extensions.conf
    with open("voice_assistant_extensions.txt", 'w') as f:
        f.write(extensions_to_add)
    
    print("✅ Created voice assistant extensions file")
    return extensions_to_add

def provide_testing_and_next_steps():
    """Provide testing instructions and next steps"""
    print("\n" + "=" * 60)
    print("🎯 TESTING AND NEXT STEPS")
    print("=" * 60)
    
    print("\n📞 STEP 1: Test Current Setup")
    print("Try dialing 1000 in Zoiper right now:")
    print("✅ Expected: Call connects, you hear demo menu")
    print("❌ If 404 error: PJSIP config issue")
    print("❌ If no audio: RTP/media issue")
    
    print("\n🔧 STEP 2: Add Voice Assistant Extensions (If Step 1 Works)")
    print("If dialing 1000 works, add voice assistant extensions:")
    print()
    print("1. Edit extensions.conf:")
    print("   sudo nano /etc/asterisk/extensions.conf")
    print()
    print("2. Find the [demo] section and add these extensions:")
    print("   (Copy from voice_assistant_extensions.txt)")
    print()
    print("3. Reload dialplan:")
    print("   sudo asterisk -rx 'dialplan reload'")
    print()
    print("4. Test voice assistant:")
    print("   Dial 1000 - should connect to AI")
    print("   Dial 1010 - should play demo and stay connected")
    
    print("\n🎯 STEP 3: Monitor Voice Assistant")
    print("When testing extension 1000:")
    print("# Watch ARI bot logs")
    print("tail -f logs/ari_bot_final.log")
    print()
    print("# Watch Asterisk logs")
    print("sudo tail -f /var/log/asterisk/messages")
    
    print("\n✅ Success Indicators:")
    print("- Extension 1000: Connects to AI, voice conversation works")
    print("- Extension 1010: Plays demo, stays connected")
    print("- No 404 or connection errors")
    print("- ARI bot receives calls in logs")
    
    print("\n🚨 Troubleshooting:")
    print("- If 1000 still goes to demo menu: Extensions not added correctly")
    print("- If 1000 disconnects after demo: Stasis app issue")
    print("- If no AI response: Check ARI bot logs")

def check_ari_bot_status():
    """Check if ARI bot is still running"""
    print("\n🔍 Checking ARI bot status...")
    
    stdout, stderr, returncode = run_command("ps aux | grep 'ari_bot.py' | grep -v grep")
    if returncode == 0 and stdout:
        print("✅ ARI bot is running")
        
        # Check recent logs
        stdout, stderr, returncode = run_command("tail -3 logs/ari_bot_final.log")
        if "ready for conversation" in stdout or "OpenAI" in stdout:
            print("✅ ARI bot is connected to OpenAI")
        else:
            print("⚠️  Check ARI bot connection")
        
        return True
    else:
        print("❌ ARI bot is not running")
        print("🔧 Start it with: python3 ari_bot.py")
        return False

def main():
    """Main function"""
    print("🎉 PJSIP RELOADED SUCCESSFULLY!")
    print("=" * 50)
    print("Now let's test and add voice assistant extensions")
    print()
    
    # Check PJSIP endpoint
    pjsip_ok = check_pjsip_endpoint()
    
    # Check ARI bot
    ari_ok = check_ari_bot_status()
    
    # Create voice assistant extensions
    create_voice_assistant_extensions()
    
    # Provide testing instructions
    provide_testing_and_next_steps()
    
    print("\n" + "=" * 60)
    print("🎯 IMMEDIATE ACTION REQUIRED")
    print("=" * 60)
    
    if pjsip_ok:
        print("✅ PJSIP configuration looks good")
        print("📞 TEST NOW: Dial 1000 in Zoiper")
        print("   Expected: Call connects, demo menu plays")
        print("   If this works: Add voice assistant extensions")
    else:
        print("❌ PJSIP configuration issue")
        print("🔧 Check endpoint context with:")
        print("   sudo asterisk -rx 'pjsip show endpoint 1000'")
    
    if not ari_ok:
        print("⚠️  ARI bot not running - start it for voice assistant")
    
    print("\n🚀 Next: Test dialing 1000 in Zoiper!")

if __name__ == "__main__":
    main()