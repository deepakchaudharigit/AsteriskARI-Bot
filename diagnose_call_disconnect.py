#!/usr/bin/env python3
"""
Diagnose Call Disconnect Issues for NPCL Asterisk ARI Voice Assistant
This script helps identify why calls disconnect after welcome message
"""

import subprocess
import time
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

def check_asterisk_logs():
    """Check recent Asterisk logs for call disconnect issues"""
    print("🔍 Checking Asterisk logs for call disconnect patterns...")
    
    log_files = [
        "/var/log/asterisk/messages",
        "/var/log/asterisk/full",
        "/var/log/asterisk/debug"
    ]
    
    for log_file in log_files:
        if os.path.exists(log_file):
            print(f"\n📋 Checking {log_file}...")
            stdout, stderr, returncode = run_command(f"sudo tail -50 {log_file} | grep -E '(SIP|RTP|disconnect|hangup|timeout|406|bye)'")
            if returncode == 0 and stdout:
                print(f"Recent entries from {log_file}:")
                print(stdout)
            else:
                print(f"No relevant entries found in {log_file}")
        else:
            print(f"❌ {log_file} not found")

def check_rtp_settings():
    """Check RTP configuration"""
    print("\n🔍 Checking RTP configuration...")
    
    # Check RTP settings
    stdout, stderr, returncode = run_command("sudo asterisk -rx 'rtp show settings'")
    if returncode == 0:
        print("✅ RTP Settings:")
        print(stdout)
    else:
        print(f"❌ Error checking RTP settings: {stderr}")

def check_sip_debug():
    """Enable SIP debugging and check for issues"""
    print("\n🔍 Enabling SIP debugging...")
    
    # Enable SIP debug
    run_command("sudo asterisk -rx 'sip set debug on'")
    run_command("sudo asterisk -rx 'pjsip set logger on'")
    
    print("✅ SIP debugging enabled")
    print("   Make a test call now and check logs")

def check_network_connectivity():
    """Check network connectivity and firewall"""
    print("\n🔍 Checking network connectivity...")
    
    # Check if ports are open
    ports_to_check = [5060, 8088, 8090, 10000, 20000]
    
    for port in ports_to_check:
        stdout, stderr, returncode = run_command(f"ss -tuln | grep :{port}")
        if returncode == 0 and stdout:
            print(f"✅ Port {port} is listening: {stdout}")
        else:
            print(f"❌ Port {port} not listening or accessible")

def check_voice_assistant_status():
    """Check if voice assistant is running"""
    print("\n🔍 Checking voice assistant status...")
    
    # Check if Python voice assistant is running
    stdout, stderr, returncode = run_command("ps aux | grep -E '(ari_bot|voice_assistant|realtime_server)' | grep -v grep")
    if returncode == 0 and stdout:
        print("✅ Voice assistant processes found:")
        print(stdout)
    else:
        print("❌ No voice assistant processes found")
        print("   Your voice assistant might not be running!")

def check_stasis_app():
    """Check Stasis application status"""
    print("\n🔍 Checking Stasis application...")
    
    stdout, stderr, returncode = run_command("sudo asterisk -rx 'stasis show apps'")
    if returncode == 0:
        if "openai-voice-assistant" in stdout:
            print("✅ Stasis app 'openai-voice-assistant' is registered")
        else:
            print("❌ Stasis app 'openai-voice-assistant' NOT registered")
            print("   This is likely why calls disconnect!")
        print(f"Stasis apps: {stdout}")
    else:
        print(f"❌ Error checking Stasis apps: {stderr}")

def analyze_pjsip_config():
    """Analyze PJSIP configuration for common issues"""
    print("\n🔍 Analyzing PJSIP configuration...")
    
    config_file = "asterisk-config/pjsip.conf"
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            content = f.read()
            
        issues = []
        
        # Check for common configuration issues
        if "direct_media=no" not in content:
            issues.append("Missing 'direct_media=no' - may cause RTP issues")
        
        if "rtp_symmetric=yes" not in content:
            issues.append("Missing 'rtp_symmetric=yes' - may cause NAT issues")
        
        if "force_rport=yes" not in content:
            issues.append("Missing 'force_rport=yes' - may cause NAT issues")
        
        if "media_address=127.0.0.1" in content:
            issues.append("Using 127.0.0.1 for media_address - may cause external connectivity issues")
        
        if issues:
            print("⚠️  Potential configuration issues found:")
            for issue in issues:
                print(f"   - {issue}")
        else:
            print("✅ PJSIP configuration looks good")
    else:
        print(f"❌ Configuration file not found: {config_file}")

def provide_solutions():
    """Provide solutions based on common issues"""
    print("\n" + "=" * 60)
    print("🎯 SOLUTIONS FOR CALL DISCONNECT ISSUES")
    print("=" * 60)
    
    print("\n🔧 Most Common Causes & Solutions:")
    
    print("\n1. ❌ Voice Assistant Not Running")
    print("   Solution: Start your voice assistant")
    print("   Command: python3 ari_bot.py")
    print("   Or: python3 src/run_realtime_server.py")
    
    print("\n2. ❌ Stasis App Not Registered")
    print("   Solution: Ensure your ARI application is connected")
    print("   Check: sudo asterisk -rx 'stasis show apps'")
    print("   Should show: openai-voice-assistant")
    
    print("\n3. ❌ RTP/Media Issues")
    print("   Solution: Fix PJSIP configuration")
    print("   Ensure: direct_media=no, rtp_symmetric=yes")
    print("   Check: RTP port range is open (10000-20000)")
    
    print("\n4. ❌ NAT/Firewall Issues")
    print("   Solution: Configure NAT traversal")
    print("   Ports: 5060 (SIP), 8088 (ARI), 8090 (External Media)")
    print("   RTP: 10000-20000 range")
    
    print("\n5. ❌ OpenAI API Issues")
    print("   Solution: Check OpenAI API key and connectivity")
    print("   Verify: OPENAI_API_KEY in .env file")
    print("   Test: OpenAI Realtime API access")
    
    print("\n🚀 Quick Fix Steps:")
    print("1. Start voice assistant: python3 ari_bot.py")
    print("2. Make test call to 1000")
    print("3. Check Asterisk logs: sudo tail -f /var/log/asterisk/messages")
    print("4. Verify Stasis app: sudo asterisk -rx 'stasis show apps'")
    
    print("\n📋 Test Extensions:")
    print("├── 1000 - Main voice assistant (needs ARI app)")
    print("├── 1010 - Simple test (no ARI needed)")
    print("└── 9000 - Echo test (no ARI needed)")
    
    print("\n💡 Pro Tip: Try calling 1010 first")
    print("   If 1010 works but 1000 doesn't, it's an ARI/Stasis issue")
    print("   If both fail, it's a SIP/RTP configuration issue")

def main():
    """Main diagnostic function"""
    print("🔧 NPCL Asterisk Call Disconnect Diagnostic Tool")
    print("=" * 60)
    print("This tool helps diagnose why calls disconnect after welcome message")
    print()
    
    # Run all diagnostic checks
    check_voice_assistant_status()
    check_stasis_app()
    check_network_connectivity()
    analyze_pjsip_config()
    check_rtp_settings()
    check_sip_debug()
    
    # Provide solutions
    provide_solutions()
    
    print("\n" + "=" * 60)
    print("🎯 NEXT STEPS:")
    print("1. Review the diagnostic results above")
    print("2. Start your voice assistant if not running")
    print("3. Make a test call and monitor logs")
    print("4. Try extension 1010 for simple testing")
    print("=" * 60)

if __name__ == "__main__":
    main()