#!/usr/bin/env python3
"""
Fix Working Extensions - Add our extensions to the default context
"""

import subprocess
import os

def run_command(command, timeout=10):
    """Run a command and return output"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "", "Command timed out", 1
    except Exception as e:
        return "", str(e), 1

def create_working_extensions():
    """Create working extensions that will be added to the default context"""
    print("🔧 Creating working extensions for default context...")
    
    # Read the current system extensions.conf
    try:
        with open("/etc/asterisk/extensions.conf", 'r') as f:
            current_config = f.read()
    except:
        print("❌ Could not read current extensions.conf")
        return False
    
    # Add our extensions to the end of the file
    our_extensions = """

; NPCL Voice Assistant Extensions - Added by fix script
[npcl-extensions]
; Test Extension - Simple demo
exten => 1010,1,NoOp(NPCL Test Extension)
same => n,Answer()
same => n,Wait(1)
same => n,Playback(demo-congrats)
same => n,Wait(3)
same => n,Hangup()

; Voice Assistant Extension
exten => 1000,1,NoOp(NPCL Voice Assistant)
same => n,Answer()
same => n,Wait(1)
same => n,Playback(demo-congrats)
same => n,Wait(2)
same => n,Stasis(openai-voice-assistant,${CALLERID(num)},${EXTEN})
same => n,Hangup()

; Echo Test
exten => 9000,1,NoOp(Echo Test)
same => n,Answer()
same => n,Echo()
same => n,Hangup()

; Override the existing 1000 extension to use our voice assistant
[demo]
exten => 1000,1,NoOp(NPCL Voice Assistant Override)
same => n,Answer()
same => n,Wait(1)
same => n,Playback(demo-congrats)
same => n,Wait(2)
same => n,Stasis(openai-voice-assistant,${CALLERID(num)},${EXTEN})
same => n,Hangup()

; Add test extension to demo context
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
    
    # Write the updated config
    updated_config = current_config + our_extensions
    
    with open("updated_extensions.conf", 'w') as f:
        f.write(updated_config)
    
    print("✅ Created updated extensions.conf with our extensions")
    return True

def apply_extensions_config():
    """Apply the updated extensions configuration"""
    print("\n🔄 Applying updated extensions configuration...")
    
    # Copy the updated config
    stdout, stderr, returncode = run_command("sudo cp updated_extensions.conf /etc/asterisk/extensions.conf")
    if returncode == 0:
        print("✅ Copied updated extensions.conf to system")
    else:
        print(f"❌ Failed to copy: {stderr}")
        return False
    
    # Reload dialplan
    stdout, stderr, returncode = run_command("sudo asterisk -rx 'dialplan reload'")
    if returncode == 0:
        print("✅ Reloaded dialplan")
    else:
        print(f"❌ Failed to reload: {stderr}")
        return False
    
    return True

def verify_extensions():
    """Verify that our extensions are now available"""
    print("\n🔍 Verifying extensions...")
    
    extensions_to_check = [
        ("1000", "demo"),
        ("1010", "demo"), 
        ("9000", "demo")
    ]
    
    for ext, context in extensions_to_check:
        stdout, stderr, returncode = run_command(f"sudo asterisk -rx 'dialplan show {ext}@{context}'")
        if returncode == 0 and ext in stdout:
            print(f"✅ Extension {ext} found in {context} context")
        else:
            print(f"❌ Extension {ext} not found in {context} context")

def update_pjsip_context():
    """Update PJSIP to use the correct context"""
    print("\n🔧 Updating PJSIP context...")
    
    # Read current PJSIP config
    try:
        with open("asterisk-config/pjsip.conf", 'r') as f:
            pjsip_config = f.read()
    except:
        print("❌ Could not read pjsip.conf")
        return False
    
    # Change context from openai-voice-assistant to demo
    updated_pjsip = pjsip_config.replace("context=openai-voice-assistant", "context=demo")
    
    # Write updated config
    with open("updated_pjsip.conf", 'w') as f:
        f.write(updated_pjsip)
    
    # Copy to system
    stdout, stderr, returncode = run_command("sudo cp updated_pjsip.conf /etc/asterisk/pjsip.conf")
    if returncode == 0:
        print("✅ Updated PJSIP configuration")
    else:
        print(f"❌ Failed to update PJSIP: {stderr}")
        return False
    
    # Reload PJSIP
    stdout, stderr, returncode = run_command("sudo asterisk -rx 'pjsip reload'")
    if returncode == 0:
        print("✅ Reloaded PJSIP")
    else:
        print(f"❌ Failed to reload PJSIP: {stderr}")
        return False
    
    return True

def provide_testing_instructions():
    """Provide testing instructions"""
    print("\n" + "=" * 60)
    print("🎯 TESTING INSTRUCTIONS")
    print("=" * 60)
    
    print("\n📞 Your extensions are now configured in the 'demo' context")
    print("which is included in the 'default' context that your PJSIP endpoint uses.")
    
    print("\n🧪 Test with Zoiper:")
    print("1. 📞 Dial 1010 - Should play demo message and stay connected")
    print("2. 📞 Dial 1000 - Should play demo message then connect to voice assistant")
    print("3. 📞 Dial 9000 - Should start echo test")
    
    print("\n✅ Expected Results:")
    print("- No 404 errors")
    print("- Calls connect successfully")
    print("- Extension 1000 connects to voice assistant")
    print("- You can have voice conversations with the AI")
    
    print("\n🔍 Monitor Commands:")
    print("# Watch ARI bot logs")
    print("tail -f logs/ari_bot_final.log")
    print()
    print("# Watch Asterisk logs")
    print("sudo tail -f /var/log/asterisk/messages")
    print()
    print("# Check if extensions exist")
    print("sudo asterisk -rx 'dialplan show 1000@demo'")
    print("sudo asterisk -rx 'dialplan show 1010@demo'")

def main():
    """Main function"""
    print("🔧 Fix Working Extensions")
    print("=" * 50)
    print("Adding NPCL voice assistant extensions to existing dialplan")
    print()
    
    # Step 1: Create working extensions
    if not create_working_extensions():
        return 1
    
    # Step 2: Apply extensions config
    if not apply_extensions_config():
        return 1
    
    # Step 3: Update PJSIP context
    if not update_pjsip_context():
        return 1
    
    # Step 4: Verify extensions
    verify_extensions()
    
    # Step 5: Provide testing instructions
    provide_testing_instructions()
    
    print("\n" + "=" * 60)
    print("🎯 SUMMARY")
    print("=" * 60)
    print("✅ Added NPCL extensions to demo context")
    print("✅ Updated PJSIP to use demo context")
    print("✅ Reloaded dialplan and PJSIP")
    print("📞 Ready for testing with Zoiper!")
    print("=" * 60)
    
    return 0

if __name__ == "__main__":
    exit(main())