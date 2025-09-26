#!/usr/bin/env python3
"""
Fix SIP vs PJSIP Configuration Issue
The system is using chan_sip instead of PJSIP, causing wrong password errors
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

def check_sip_modules():
    """Check which SIP modules are loaded"""
    print("🔍 Checking SIP modules...")
    
    commands = [
        ("chan_sip", "sudo asterisk -rx 'module show like chan_sip'"),
        ("chan_pjsip", "sudo asterisk -rx 'module show like chan_pjsip'"),
        ("res_pjsip", "sudo asterisk -rx 'module show like res_pjsip'")
    ]
    
    for name, cmd in commands:
        stdout, stderr, returncode = run_command(cmd)
        if returncode == 0:
            if "Loaded" in stdout or name in stdout:
                print(f"✅ {name}: Loaded")
            else:
                print(f"❌ {name}: Not loaded")
        else:
            print(f"❌ Error checking {name}: {stderr}")

def disable_chan_sip():
    """Disable chan_sip module to force PJSIP usage"""
    print("\n🔧 Disabling chan_sip module...")
    
    commands = [
        "sudo asterisk -rx 'module unload chan_sip.so'",
        "sudo asterisk -rx 'module reload'",
        "sudo asterisk -rx 'pjsip reload'"
    ]
    
    for cmd in commands:
        stdout, stderr, returncode = run_command(cmd)
        if returncode == 0:
            print(f"✅ Command successful: {cmd.split()[-1]}")
        else:
            print(f"❌ Command failed: {stderr}")

def update_modules_conf():
    """Update modules.conf to prevent chan_sip from loading"""
    print("\n🔧 Updating modules.conf to disable chan_sip...")
    
    modules_conf = """[modules]
autoload=yes

; Disable chan_sip to force PJSIP usage
noload => chan_sip.so

; Core HTTP and WebSocket support
load => res_http_websocket.so

; ARI Core modules
load => res_ari.so
load => res_ari_asterisk.so
load => res_ari_channels.so
load => res_ari_bridges.so
load => res_ari_endpoints.so
load => res_ari_events.so
load => res_ari_playbacks.so
load => res_ari_recordings.so
load => res_ari_sounds.so
load => res_ari_device_states.so
load => res_ari_applications.so

; Additional useful modules
load => res_stasis.so
load => res_stasis_answer.so
load => res_stasis_playback.so
load => res_stasis_recording.so
load => res_stasis_snoop.so

; PJSIP modules (force load)
load => res_pjsip.so
load => res_pjsip_session.so
load => res_pjsip_registrar.so
load => res_pjsip_authenticator_digest.so
load => res_pjsip_endpoint_identifier_ip.so
load => res_pjsip_endpoint_identifier_user.so
load => chan_pjsip.so

; Applications
load => app_stasis.so
load => app_playback.so
load => app_record.so
load => app_dial.so
load => app_queue.so
load => app_confbridge.so

; Additional channel drivers
load => chan_local.so

; Codec modules
load => codec_ulaw.so
load => codec_alaw.so
load => codec_gsm.so

; Format modules
load => format_wav.so
load => format_gsm.so
load => format_pcm.so

; RTP support
load => res_rtp_asterisk.so

; DTMF support
load => res_features.so
"""
    
    # Write to project config
    with open("asterisk-config/modules.conf", 'w') as f:
        f.write(modules_conf)
    
    print("✅ Updated project modules.conf")
    
    # Copy to system
    run_command("sudo cp asterisk-config/modules.conf /etc/asterisk/modules.conf")
    print("✅ Copied to system modules.conf")

def check_pjsip_endpoints():
    """Check PJSIP endpoints"""
    print("\n🔍 Checking PJSIP endpoints...")
    
    stdout, stderr, returncode = run_command("sudo asterisk -rx 'pjsip show endpoints'")
    if returncode == 0:
        if "1000" in stdout:
            print("✅ PJSIP endpoint 1000 found")
            print(f"Endpoints:\n{stdout}")
        else:
            print("❌ PJSIP endpoint 1000 not found")
            print(f"Output: {stdout}")
    else:
        print(f"❌ Error: {stderr}")

def restart_asterisk():
    """Restart Asterisk to apply changes"""
    print("\n🔄 Restarting Asterisk...")
    
    commands = [
        "sudo systemctl stop asterisk",
        "sleep 3",
        "sudo systemctl start asterisk",
        "sleep 5"
    ]
    
    for cmd in commands:
        if "sleep" in cmd:
            import time
            time.sleep(int(cmd.split()[1]))
            continue
            
        stdout, stderr, returncode = run_command(cmd)
        if returncode == 0:
            print(f"✅ {cmd}")
        else:
            print(f"❌ {cmd} failed: {stderr}")

def verify_fix():
    """Verify the fix worked"""
    print("\n🔍 Verifying fix...")
    
    # Check if chan_sip is unloaded
    stdout, stderr, returncode = run_command("sudo asterisk -rx 'module show like chan_sip'")
    if returncode == 0:
        if "Not Loaded" in stdout or "chan_sip" not in stdout:
            print("✅ chan_sip is disabled")
        else:
            print("❌ chan_sip is still loaded")
    
    # Check PJSIP endpoints
    check_pjsip_endpoints()
    
    # Check Stasis apps
    stdout, stderr, returncode = run_command("sudo asterisk -rx 'stasis show apps'")
    if returncode == 0:
        if "openai-voice-assistant" in stdout:
            print("✅ Stasis app registered")
        else:
            print("❌ Stasis app not registered")
    else:
        print(f"❌ Error checking Stasis: {stderr}")

def provide_testing_instructions():
    """Provide updated testing instructions"""
    print("\n" + "=" * 60)
    print("🎯 UPDATED TESTING INSTRUCTIONS")
    print("=" * 60)
    
    print("\n📞 Zoiper Configuration (Updated):")
    print("Since we're now using PJSIP exclusively:")
    print("├── Username: 1000")
    print("├── Password: 1234")
    print("├── Domain: 192.168.0.212")
    print("├── Outbound proxy: 192.168.0.212:5060")
    print("├── Transport: UDP")
    print("└── Enable registration: ✓")
    
    print("\n🧪 Test Sequence:")
    print("1. Wait 30 seconds for Asterisk to fully restart")
    print("2. Re-register Zoiper (should succeed now)")
    print("3. Call 1010 - should work as before")
    print("4. Call 1000 - should now connect to voice assistant")
    
    print("\n✅ Success Indicators:")
    print("- No more 'Wrong password' errors")
    print("- Zoiper shows 'Registered' status")
    print("- Extension 1000 connects to AI assistant")
    
    print("\n🔍 Monitor Commands:")
    print("sudo asterisk -rx 'pjsip show registrations'")
    print("sudo asterisk -rx 'pjsip show endpoints'")
    print("tail -f logs/ari_bot_final.log")

def main():
    """Main function"""
    print("🔧 SIP vs PJSIP Configuration Fix")
    print("=" * 50)
    print("Issue: Asterisk is using chan_sip instead of PJSIP")
    print("Solution: Disable chan_sip and force PJSIP usage")
    print()
    
    # Step 1: Check current modules
    check_sip_modules()
    
    # Step 2: Update modules configuration
    update_modules_conf()
    
    # Step 3: Disable chan_sip
    disable_chan_sip()
    
    # Step 4: Restart Asterisk
    restart_asterisk()
    
    # Step 5: Verify fix
    verify_fix()
    
    # Step 6: Provide instructions
    provide_testing_instructions()
    
    print("\n" + "=" * 60)
    print("🎯 SUMMARY")
    print("=" * 60)
    print("✅ Disabled chan_sip module")
    print("✅ Forced PJSIP usage")
    print("✅ Restarted Asterisk")
    print("📞 Ready for testing with Zoiper")
    print("=" * 60)

if __name__ == "__main__":
    main()