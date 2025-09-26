#!/usr/bin/env python3
"""
Check Dialplan Status and Available Contexts
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

def check_dialplan_commands():
    """Check various dialplan commands to see what works"""
    print("🔍 Checking dialplan status...")
    
    commands = [
        ("Show all dialplan", "sudo asterisk -rx 'dialplan show'"),
        ("Core show help dialplan", "sudo asterisk -rx 'core show help dialplan'"),
        ("Show default context", "sudo asterisk -rx 'dialplan show default'"),
        ("Show any context", "sudo asterisk -rx 'dialplan show'"),
    ]
    
    for name, cmd in commands:
        print(f"\n📋 {name}:")
        stdout, stderr, returncode = run_command(cmd)
        if returncode == 0:
            if stdout:
                print("✅ Success:")
                # Show first 20 lines to avoid too much output
                lines = stdout.split('\n')[:20]
                for line in lines:
                    print(f"   {line}")
                if len(stdout.split('\n')) > 20:
                    print("   ... (truncated)")
            else:
                print("✅ Command succeeded but no output")
        else:
            print(f"❌ Error: {stderr}")

def create_minimal_extensions_conf():
    """Create a minimal working extensions.conf"""
    print("\n🔧 Creating minimal extensions.conf...")
    
    minimal_config = """[general]
static=yes
writeprotect=no

[default]
exten => s,1,Answer()
same => n,Playback(demo-congrats)
same => n,Hangup()

exten => 1010,1,Answer()
same => n,Playback(demo-congrats)
same => n,Wait(3)
same => n,Hangup()

exten => 1000,1,Answer()
same => n,Playback(demo-congrats)
same => n,Wait(2)
same => n,Stasis(openai-voice-assistant)
same => n,Hangup()

exten => _X.,1,Answer()
same => n,Playback(demo-congrats)
same => n,Hangup()
"""
    
    # Write to file
    with open("minimal_extensions.conf", 'w') as f:
        f.write(minimal_config)
    
    print("✅ Created minimal_extensions.conf")
    return minimal_config

def provide_step_by_step_fix():
    """Provide step by step fix"""
    print("\n" + "=" * 60)
    print("🔧 STEP-BY-STEP FIX")
    print("=" * 60)
    
    print("\n📋 The issue is that there's no working dialplan loaded.")
    print("Let's fix this step by step:")
    
    print("\n🚀 STEP 1: Check what dialplan exists")
    print("sudo asterisk -rx 'dialplan show'")
    print("(This will show ALL contexts and extensions)")
    
    print("\n🚀 STEP 2: Replace extensions.conf with minimal working version")
    print("sudo cp minimal_extensions.conf /etc/asterisk/extensions.conf")
    
    print("\n🚀 STEP 3: Reload dialplan")
    print("sudo asterisk -rx 'dialplan reload'")
    
    print("\n🚀 STEP 4: Verify it worked")
    print("sudo asterisk -rx 'dialplan show default'")
    
    print("\n🚀 STEP 5: Change PJSIP to use default context")
    print("sudo nano /etc/asterisk/pjsip.conf")
    print("(Change context=openai-voice-assistant to context=default)")
    
    print("\n🚀 STEP 6: Reload PJSIP")
    print("sudo asterisk -rx 'pjsip reload'")
    
    print("\n🚀 STEP 7: Test with Zoiper")
    print("Dial 1010 - should play demo message")
    print("Dial 1000 - should connect to voice assistant")
    
    print("\n✅ Expected Results:")
    print("- No 404 errors")
    print("- Calls connect and play audio")
    print("- Extension 1000 connects to voice assistant")

def main():
    """Main function"""
    print("🔍 DIALPLAN STATUS CHECK")
    print("=" * 50)
    print("Checking what dialplan contexts and extensions exist")
    print()
    
    # Check dialplan commands
    check_dialplan_commands()
    
    # Create minimal config
    create_minimal_extensions_conf()
    
    # Provide fix steps
    provide_step_by_step_fix()
    
    print("\n" + "=" * 60)
    print("🎯 SUMMARY")
    print("=" * 60)
    print("The dialplan is either empty or has syntax errors.")
    print("Follow the steps above to create a working dialplan.")
    print("=" * 60)

if __name__ == "__main__":
    main()