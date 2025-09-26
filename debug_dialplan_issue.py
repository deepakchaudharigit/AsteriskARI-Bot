#!/usr/bin/env python3
"""
Debug Dialplan Issue - Context Not Found
"""

import subprocess

def run_command(command, timeout=10):
    """Run a command and return output"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "", "Command timed out", 1
    except Exception as e:
        return "", str(e), 1

def check_available_contexts():
    """Check what contexts are available"""
    print("🔍 Checking available contexts...")
    
    stdout, stderr, returncode = run_command("sudo asterisk -rx 'dialplan show contexts'")
    if returncode == 0:
        print("✅ Available contexts:")
        print(stdout)
        return stdout
    else:
        print(f"❌ Error: {stderr}")
        return ""

def check_extensions_in_default():
    """Check if extensions exist in default context"""
    print("\n🔍 Checking extensions in 'default' context...")
    
    extensions = ["1000", "1010", "9000"]
    
    for ext in extensions:
        stdout, stderr, returncode = run_command(f"sudo asterisk -rx 'dialplan show {ext}@default'")
        if returncode == 0 and ext in stdout:
            print(f"✅ Extension {ext} found in default context")
        else:
            print(f"❌ Extension {ext} not found in default context")

def check_config_file_location():
    """Check which extensions.conf file Asterisk is using"""
    print("\n🔍 Checking extensions.conf file location...")
    
    # Check if our file was copied correctly
    stdout, stderr, returncode = run_command("sudo head -10 /etc/asterisk/extensions.conf")
    if returncode == 0:
        print("✅ System extensions.conf content:")
        print(stdout)
        
        if "openai-voice-assistant" in stdout:
            print("✅ Our configuration is in the system file")
        else:
            print("❌ Our configuration is NOT in the system file")
    else:
        print(f"❌ Error reading system extensions.conf: {stderr}")

def create_simple_working_config():
    """Create a simple working extensions.conf"""
    print("\n🔧 Creating simple working extensions.conf...")
    
    simple_config = """[general]
static=yes
writeprotect=no

[default]
; Test Extensions
exten => 1010,1,NoOp(Simple Test Extension)
same => n,Answer()
same => n,Wait(1)
same => n,Playbook(demo-congrats)
same => n,Wait(3)
same => n,Hangup()

exten => 9000,1,NoOp(Echo Test)
same => n,Answer()
same => n,Echo()
same => n,Hangup()

; Voice Assistant Extension
exten => 1000,1,NoOp(NPCL Voice Assistant)
same => n,Answer()
same => n,Wait(1)
same => n,Playback(demo-congrats)
same => n,Wait(2)
same => n,Stasis(openai-voice-assistant,${CALLERID(num)},${EXTEN})
same => n,Hangup()

; Fallback
exten => _X.,1,NoOp(Fallback for ${EXTEN})
same => n,Answer()
same => n,Playback(demo-congrats)
same => n,Wait(2)
same => n,Hangup()

[openai-voice-assistant]
include => default
"""
    
    # Write to project
    with open("asterisk-config/extensions_simple.conf", 'w') as f:
        f.write(simple_config)
    
    print("✅ Created simple extensions configuration")
    return simple_config

def provide_manual_fix():
    """Provide manual fix instructions"""
    print("\n" + "=" * 60)
    print("🔧 MANUAL FIX INSTRUCTIONS")
    print("=" * 60)
    
    print("\n📋 The issue is that the 'openai-voice-assistant' context doesn't exist.")
    print("This means the extensions.conf file has a syntax error or wasn't loaded.")
    
    print("\n🚀 SOLUTION 1: Use Default Context")
    print("Change PJSIP endpoint to use 'default' context:")
    print()
    print("1. Edit PJSIP config:")
    print("   sudo nano /etc/asterisk/pjsip.conf")
    print()
    print("2. Find the [1000] endpoint section and change:")
    print("   FROM: context=openai-voice-assistant")
    print("   TO:   context=default")
    print()
    print("3. Reload PJSIP:")
    print("   sudo asterisk -rx 'pjsip reload'")
    print()
    
    print("🚀 SOLUTION 2: Fix Extensions.conf")
    print("Create a working extensions.conf:")
    print()
    print("1. Copy simple config:")
    print("   sudo cp asterisk-config/extensions_simple.conf /etc/asterisk/extensions.conf")
    print()
    print("2. Reload dialplan:")
    print("   sudo asterisk -rx 'dialplan reload'")
    print()
    print("3. Check contexts:")
    print("   sudo asterisk -rx 'dialplan show contexts'")
    print()
    
    print("🧪 SOLUTION 3: Quick Test")
    print("Test with extensions in default context:")
    print()
    print("1. Check what's in default:")
    print("   sudo asterisk -rx 'dialplan show default'")
    print()
    print("2. Try dialing extensions that exist")
    print()
    
    print("✅ Expected Results:")
    print("- Extension 1010: Should play demo message")
    print("- Extension 1000: Should connect to voice assistant")
    print("- No 404 errors")

def main():
    """Main debugging function"""
    print("🔍 DEBUG: Dialplan Context Issue")
    print("=" * 50)
    print("Issue: 'openai-voice-assistant' context doesn't exist")
    print()
    
    # Check available contexts
    contexts = check_available_contexts()
    
    # Check extensions in default
    check_extensions_in_default()
    
    # Check config file
    check_config_file_location()
    
    # Create simple config
    create_simple_working_config()
    
    # Provide manual fix
    provide_manual_fix()
    
    print("\n" + "=" * 60)
    print("🎯 QUICK FIX RECOMMENDATION")
    print("=" * 60)
    
    if "default" in contexts:
        print("✅ 'default' context exists")
        print("🔧 RECOMMENDED: Change PJSIP endpoint context to 'default'")
        print()
        print("Run this command:")
        print("sudo asterisk -rx 'pjsip set endpoint 1000 context default'")
        print("OR manually edit /etc/asterisk/pjsip.conf")
    else:
        print("❌ No standard contexts found")
        print("🔧 RECOMMENDED: Fix extensions.conf file")
    
    print("\n📞 Then test with Zoiper by dialing 1010 and 1000")

if __name__ == "__main__":
    main()