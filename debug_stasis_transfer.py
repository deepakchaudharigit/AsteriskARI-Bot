#!/usr/bin/env python3
"""
Debug Stasis Transfer Issue
Call connects and plays welcome but doesn't transfer to AI conversation
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

def check_stasis_registration():
    """Check if Stasis application is registered"""
    print("🔍 Checking Stasis application registration...")
    
    commands = [
        ("ARI Apps", "sudo asterisk -rx 'ari show apps'"),
        ("Core Applications", "sudo asterisk -rx 'core show applications' | grep -i stasis"),
        ("Module Status", "sudo asterisk -rx 'module show like res_ari'")
    ]
    
    stasis_found = False
    
    for name, cmd in commands:
        print(f"\n📋 {name}:")
        stdout, stderr, returncode = run_command(cmd)
        if returncode == 0:
            if stdout:
                print(f"✅ Output: {stdout}")
                if "openai-voice-assistant" in stdout:
                    stasis_found = True
                    print("✅ Found openai-voice-assistant Stasis app!")
            else:
                print("ℹ️  No output")
        else:
            print(f"❌ Error: {stderr}")
    
    return stasis_found

def check_ari_connectivity():
    """Check ARI connectivity from Asterisk to our bot"""
    print("\n🔍 Checking ARI connectivity...")
    
    # Check if ARI is enabled and accessible
    stdout, stderr, returncode = run_command("sudo asterisk -rx 'http show status'")
    if returncode == 0:
        print("✅ HTTP server status:")
        print(stdout)
    else:
        print(f"❌ HTTP server error: {stderr}")

def analyze_call_flow():
    """Analyze the call flow issue"""
    print("\n🔍 Analyzing call flow issue...")
    
    print("📋 Current Call Flow:")
    print("1. ✅ Zoiper dials 1000")
    print("2. ✅ Call connects to Asterisk")
    print("3. ✅ Extension 1000 in [demo] context executes")
    print("4. ✅ Answer() - call is answered")
    print("5. ✅ Playback(demo-congrats) - welcome message plays")
    print("6. ❌ Stasis(openai-voice-assistant) - FAILS HERE")
    print("7. ❌ Call disconnects instead of transferring to AI")
    
    print("\n🎯 Possible Causes:")
    print("- Stasis application not registered with ARI")
    print("- ARI bot not connected to Asterisk")
    print("- Wrong Stasis application name")
    print("- ARI authentication issues")
    print("- Network connectivity between Asterisk and ARI bot")

def check_ari_bot_logs():
    """Check ARI bot logs for Stasis events"""
    print("\n🔍 Checking ARI bot logs for Stasis events...")
    
    # Check recent logs for Stasis-related messages
    stdout, stderr, returncode = run_command("grep -i stasis logs/ari_bot_final.log | tail -10")
    if returncode == 0 and stdout:
        print("✅ Recent Stasis events in ARI bot logs:")
        print(stdout)
    else:
        print("❌ No Stasis events found in ARI bot logs")
    
    # Check for ARI connection messages
    stdout, stderr, returncode = run_command("grep -i 'ari' logs/ari_bot_final.log | tail -5")
    if returncode == 0 and stdout:
        print("\n✅ Recent ARI messages:")
        print(stdout)
    else:
        print("\n❌ No ARI messages found")

def create_test_stasis_extension():
    """Create a simple test Stasis extension"""
    print("\n🔧 Creating test Stasis extension...")
    
    test_extension = """
; Test Stasis Extension - Add to [demo] context
exten => 1011,1,NoOp(Test Stasis Extension)
same => n,Answer()
same => n,Wait(1)
same => n,Playback(demo-congrats)
same => n,Wait(1)
same => n,NoOp(About to call Stasis)
same => n,Stasis(openai-voice-assistant,test-call)
same => n,NoOp(Stasis returned - this should not execute)
same => n,Hangup()
"""
    
    with open("test_stasis_extension.txt", 'w') as f:
        f.write(test_extension)
    
    print("✅ Created test_stasis_extension.txt")
    print("📋 Add this to your [demo] context to test Stasis transfer")

def provide_debugging_steps():
    """Provide step-by-step debugging"""
    print("\n" + "=" * 60)
    print("🔧 DEBUGGING STEPS")
    print("=" * 60)
    
    print("\n🚀 STEP 1: Check Stasis Registration")
    print("sudo asterisk -rx 'ari show apps'")
    print("Expected: Should show 'openai-voice-assistant'")
    
    print("\n🚀 STEP 2: Test ARI Connection")
    print("curl http://localhost:8088/ari/asterisk/info -u asterisk:1234")
    print("Expected: Should return Asterisk info JSON")
    
    print("\n🚀 STEP 3: Monitor Asterisk Logs During Call")
    print("sudo tail -f /var/log/asterisk/messages")
    print("Then dial 1000 and watch for Stasis errors")
    
    print("\n🚀 STEP 4: Monitor ARI Bot Logs During Call")
    print("tail -f logs/ari_bot_final.log")
    print("Then dial 1000 and watch for incoming Stasis events")
    
    print("\n🚀 STEP 5: Add Test Extension")
    print("Add extension 1011 from test_stasis_extension.txt")
    print("Then test: dial 1011 instead of 1000")
    
    print("\n🚀 STEP 6: Check Extension Configuration")
    print("sudo asterisk -rx 'dialplan show 1000@demo'")
    print("Verify the Stasis line is correct")

def provide_quick_fixes():
    """Provide quick fixes to try"""
    print("\n" + "=" * 60)
    print("🎯 QUICK FIXES TO TRY")
    print("=" * 60)
    
    print("\n🔧 FIX 1: Restart ARI Connection")
    print("# Stop ARI bot (Ctrl+C)")
    print("# Wait 5 seconds")
    print("# Start ARI bot: python3 ari_bot.py")
    print("# Wait for 'ready for conversation'")
    print("# Test dial 1000")
    
    print("\n🔧 FIX 2: Check ARI Authentication")
    print("# Verify ARI credentials in your bot match asterisk-config/ari.conf")
    print("# Default: username=asterisk, password=1234")
    
    print("\n🔧 FIX 3: Simplify Stasis Call")
    print("# Edit extensions.conf, change:")
    print("# FROM: Stasis(openai-voice-assistant,${CALLERID(num)},${EXTEN})")
    print("# TO:   Stasis(openai-voice-assistant)")
    print("# Reload: sudo asterisk -rx 'dialplan reload'")
    
    print("\n🔧 FIX 4: Test with Simple Stasis")
    print("# Add test extension 1011 (from test file)")
    print("# Test dial 1011 instead of 1000")
    
    print("\n✅ Success Indicators:")
    print("- ARI bot logs show: 'Stasis application started'")
    print("- Call doesn't disconnect after welcome")
    print("- AI conversation begins")

def main():
    """Main debugging function"""
    print("🔧 DEBUG: Stasis Transfer Issue")
    print("=" * 50)
    print("Issue: Call plays welcome but disconnects instead of transferring to AI")
    print()
    
    # Check Stasis registration
    stasis_registered = check_stasis_registration()
    
    # Check ARI connectivity
    check_ari_connectivity()
    
    # Analyze call flow
    analyze_call_flow()
    
    # Check ARI bot logs
    check_ari_bot_logs()
    
    # Create test extension
    create_test_stasis_extension()
    
    # Provide debugging steps
    provide_debugging_steps()
    
    # Provide quick fixes
    provide_quick_fixes()
    
    print("\n" + "=" * 60)
    print("🎯 SUMMARY")
    print("=" * 60)
    
    if stasis_registered:
        print("✅ Stasis app appears to be registered")
        print("🔧 Focus on ARI connectivity and authentication")
    else:
        print("❌ Stasis app NOT registered")
        print("🔧 This is likely the main issue")
    
    print("\n📞 Next Steps:")
    print("1. Check if 'openai-voice-assistant' appears in 'ari show apps'")
    print("2. Monitor both Asterisk and ARI bot logs during call")
    print("3. Try the quick fixes above")
    print("4. Test with extension 1011 (simpler Stasis call)")

if __name__ == "__main__":
    main()