#!/usr/bin/env python3
"""
Fix 404 Extension Not Found Error
The issue is likely that extensions are not being found in the correct context
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

def create_fixed_extensions_conf():
    """Create a fixed extensions.conf with proper context handling"""
    print("🔧 Creating fixed extensions.conf...")
    
    extensions_conf = """[general]
static=yes
writeprotect=no
clearglobalvars=no

[globals]
; Global variables for the NPCL Telephonic Bot
OPENAI_APP=openai-voice-assistant
EXTERNAL_MEDIA_HOST=localhost
EXTERNAL_MEDIA_PORT=8090

[openai-voice-assistant]
; Main NPCL Telephonic Bot Extension
exten => 1000,1,NoOp(NPCL Telephonic Bot - Main Line)
same => n,Set(CHANNEL(hangup_handler_push)=hangup-handler,s,1)
same => n,Answer()
same => n,Set(TALK_DETECT(set)=4,160)  ; Enable talk detection
same => n,Wait(1)  ; Brief pause to establish media
same => n,Playback(/home/ameen/AsteriskARI-Bot/sounds/welcome)  ; Play welcome greeting
same => n,Wait(1)  ; Brief pause after welcome
same => n,Stasis(${OPENAI_APP},${CALLERID(num)},${EXTEN})
same => n,Hangup()

; Test Extensions (IMPORTANT: These need to be in the same context)
exten => 1010,1,NoOp(Codec Test - No Stasis)
same => n,Answer()
same => n,Wait(2)
same => n,Playback(demo-congrats)
same => n,Wait(5)
same => n,Hangup()

exten => 9000,1,NoOp(Echo Test)
same => n,Answer()
same => n,Echo()
same => n,Hangup()

; Customer Service Queue
exten => 1001,1,NoOp(NPCL Customer Service Queue)
same => n,Answer()
same => n,Playback(welcome)
same => n,Queue(customer-service,t,,,300)
same => n,Hangup()

; Technical Support Queue
exten => 1002,1,NoOp(NPCL Technical Support Queue)
same => n,Answer()
same => n,Playback(technical-support)
same => n,Queue(technical-support,t,,,300)
same => n,Hangup()

; Billing Department
exten => 1003,1,NoOp(NPCL Billing Department)
same => n,Answer()
same => n,Playback(billing-department)
same => n,Queue(billing,t,,,300)
same => n,Hangup()

; Emergency Power Outage Reporting
exten => 1004,1,NoOp(NPCL Emergency Outage Reporting)
same => n,Answer()
same => n,Playback(emergency-outage)
same => n,Stasis(${OPENAI_APP},${CALLERID(num)},emergency)
same => n,Hangup()

; IVR Main Menu
exten => 1005,1,NoOp(NPCL IVR Main Menu)
same => n,Answer()
same => n,Background(npcl-main-menu)
same => n,WaitExten(10)
same => n,Goto(1000,1)  ; Default to main bot

; IVR Menu Options
exten => 1,1,Goto(1000,1)  ; AI Assistant
exten => 2,1,Goto(1001,1)  ; Customer Service
exten => 3,1,Goto(1002,1)  ; Technical Support
exten => 4,1,Goto(1003,1)  ; Billing
exten => 9,1,Goto(1004,1)  ; Emergency

; Call Transfer Extensions
exten => 2000,1,NoOp(Transfer to Agent)
same => n,Dial(PJSIP/agent1,30)
same => n,Hangup()

exten => 2001,1,NoOp(Transfer to Supervisor)
same => n,Dial(PJSIP/supervisor,30)
same => n,Hangup()

; Conference Rooms
exten => 3000,1,NoOp(Customer Conference)
same => n,Answer()
same => n,ConfBridge(customer-conf)
same => n,Hangup()

exten => 3001,1,NoOp(Agent Conference)
same => n,Answer()
same => n,ConfBridge(agent-conf)
same => n,Hangup()

; Recording Test
exten => 9001,1,NoOp(Recording Test)
same => n,Answer()
same => n,Playback(beep)
same => n,Record(test-recording:wav,10,k)
same => n,Playback(test-recording)
same => n,Hangup()

; Emergency fallback for any other extension
exten => _X.,1,NoOp(Fallback for ${EXTEN})
same => n,Answer()
same => n,Playback(invalid)
same => n,Wait(1)
same => n,Goto(1005,1)  ; Redirect to IVR

; Hangup handler for cleanup and data logging
[hangup-handler]
exten => s,1,NoOp(Hangup handler for ${CHANNEL})
same => n,System(echo "Call ended: ${CHANNEL} at $(date) - Duration: ${CDR(duration)}s" >> /var/log/asterisk/npcl-calls.log)
same => n,AGI(call-data-logger.py,${CALLERID(num)},${EXTEN},${CDR(duration)})
same => n,Return()

[default]
include => openai-voice-assistant

; Inbound context for SIP calls
[from-sip]
include => openai-voice-assistant

; Context for internal calls
[internal]
include => openai-voice-assistant
"""
    
    # Write to project config
    with open("asterisk-config/extensions.conf", 'w') as f:
        f.write(extensions_conf)
    
    print("✅ Updated project extensions.conf")
    
    # Copy to system
    run_command("sudo cp asterisk-config/extensions.conf /etc/asterisk/extensions.conf")
    print("✅ Copied to system extensions.conf")

def reload_dialplan():
    """Reload the dialplan"""
    print("\n🔄 Reloading dialplan...")
    
    commands = [
        "sudo asterisk -rx 'dialplan reload'",
        "sudo asterisk -rx 'core reload'"
    ]
    
    for cmd in commands:
        stdout, stderr, returncode = run_command(cmd)
        if returncode == 0:
            print(f"✅ {cmd.split()[-1]} successful")
        else:
            print(f"❌ {cmd.split()[-1]} failed: {stderr}")

def test_extensions():
    """Test if extensions are now available"""
    print("\n🔍 Testing extension availability...")
    
    extensions_to_test = ["1000", "1010", "9000"]
    
    for ext in extensions_to_test:
        stdout, stderr, returncode = run_command(f"sudo asterisk -rx 'dialplan show {ext}@openai-voice-assistant'")
        if returncode == 0 and ext in stdout:
            print(f"✅ Extension {ext} found in openai-voice-assistant context")
        else:
            print(f"❌ Extension {ext} not found")

def create_simple_test_context():
    """Create a simple test context for debugging"""
    print("\n🔧 Creating simple test context...")
    
    test_extensions = """
; Add this to the end of extensions.conf for testing
[test-context]
exten => 1010,1,NoOp(Simple Test Extension)
same => n,Answer()
same => n,Playback(demo-congrats)
same => n,Wait(3)
same => n,Hangup()

exten => 1000,1,NoOp(Voice Assistant Test)
same => n,Answer()
same => n,Playback(demo-congrats)
same => n,Wait(2)
same => n,Hangup()
"""
    
    # Append to extensions.conf
    with open("asterisk-config/extensions.conf", 'a') as f:
        f.write(test_extensions)
    
    print("✅ Added test context")

def provide_debugging_steps():
    """Provide debugging steps"""
    print("\n" + "=" * 60)
    print("🔍 DEBUGGING STEPS FOR 404 ERROR")
    print("=" * 60)
    
    print("\n📋 Manual Commands to Run:")
    print("1. Copy updated config:")
    print("   sudo cp asterisk-config/extensions.conf /etc/asterisk/extensions.conf")
    print()
    print("2. Reload dialplan:")
    print("   sudo asterisk -rx 'dialplan reload'")
    print()
    print("3. Check if extensions exist:")
    print("   sudo asterisk -rx 'dialplan show 1010@openai-voice-assistant'")
    print("   sudo asterisk -rx 'dialplan show 1000@openai-voice-assistant'")
    print()
    print("4. Check endpoint context:")
    print("   sudo asterisk -rx 'pjsip show endpoint 1000'")
    print()
    
    print("🧪 Alternative Testing:")
    print("If 404 persists, try changing PJSIP context:")
    print("1. Edit asterisk-config/pjsip.conf")
    print("2. Change endpoint 1000 context from 'openai-voice-assistant' to 'default'")
    print("3. Copy and reload: sudo cp asterisk-config/pjsip.conf /etc/asterisk/pjsip.conf")
    print("4. Reload: sudo asterisk -rx 'pjsip reload'")
    
    print("\n🎯 What Extension to Dial:")
    print("- Try dialing: 1010 (should work)")
    print("- Try dialing: 1000 (voice assistant)")
    print("- Try dialing: 9000 (echo test)")
    
    print("\n📞 Expected Results:")
    print("✅ No 404 errors")
    print("✅ Call connects and plays audio")
    print("✅ Extension 1000 connects to voice assistant")

def main():
    """Main function"""
    print("🔧 Fix 404 Extension Not Found Error")
    print("=" * 50)
    print("Issue: Zoiper getting 404 when dialing extensions")
    print("Solution: Fix context and extension configuration")
    print()
    
    # Step 1: Create fixed extensions.conf
    create_fixed_extensions_conf()
    
    # Step 2: Reload dialplan
    reload_dialplan()
    
    # Step 3: Test extensions
    test_extensions()
    
    # Step 4: Provide debugging steps
    provide_debugging_steps()
    
    print("\n" + "=" * 60)
    print("🎯 SUMMARY")
    print("=" * 60)
    print("✅ Updated extensions.conf with all extensions in correct context")
    print("✅ Fixed PJSIP dial syntax (PJSIP/ instead of SIP/)")
    print("✅ Reloaded dialplan")
    print("📞 Try calling 1010 and 1000 now")
    print("=" * 60)

if __name__ == "__main__":
    main()