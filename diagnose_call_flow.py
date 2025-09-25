#!/usr/bin/env python3
"""
Call Flow Diagnostic Script
Helps diagnose why calls aren't reaching the ARI application
"""

import requests
import json
import time
import subprocess
import sys
from pathlib import Path

def check_ari_server():
    """Check if ARI server is running"""
    try:
        response = requests.get("http://localhost:8000/ari/health", timeout=5)
        if response.status_code == 200:
            print("✅ ARI Server: Running")
            return True
        else:
            print(f"❌ ARI Server: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ ARI Server: Not reachable - {e}")
        return False

def check_asterisk_ari():
    """Check Asterisk ARI interface"""
    try:
        # Try to connect to Asterisk ARI
        response = requests.get(
            "http://localhost:8088/ari/asterisk/info",
            auth=("asterisk", "1234"),
            timeout=5
        )
        if response.status_code == 200:
            print("✅ Asterisk ARI: Connected")
            return True
        else:
            print(f"❌ Asterisk ARI: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Asterisk ARI: Not reachable - {e}")
        return False

def check_stasis_apps():
    """Check registered Stasis applications"""
    try:
        response = requests.get(
            "http://localhost:8088/ari/applications",
            auth=("asterisk", "1234"),
            timeout=5
        )
        if response.status_code == 200:
            apps = response.json()
            print(f"📱 Registered Stasis Apps: {len(apps)}")
            for app in apps:
                print(f"   - {app.get('name', 'Unknown')}")
            
            # Check if our app is registered
            app_names = [app.get('name') for app in apps]
            if 'openai-voice-assistant' in app_names:
                print("✅ openai-voice-assistant: Registered")
                return True
            else:
                print("❌ openai-voice-assistant: NOT REGISTERED")
                return False
        else:
            print(f"❌ Stasis Apps: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Stasis Apps: Error - {e}")
        return False

def check_asterisk_config():
    """Check Asterisk configuration"""
    print("\n🔍 ASTERISK CONFIGURATION CHECK:")
    
    # Check if Asterisk is running
    try:
        result = subprocess.run(
            ["pgrep", "-f", "asterisk"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("✅ Asterisk Process: Running")
        else:
            print("❌ Asterisk Process: Not running")
            return False
    except Exception as e:
        print(f"❌ Asterisk Process: Error checking - {e}")
        return False
    
    # Check configuration files
    config_files = [
        "/etc/asterisk/extensions.conf",
        "/usr/local/etc/asterisk/extensions.conf",
        "asterisk-config/extensions.conf"
    ]
    
    config_found = False
    for config_file in config_files:
        if Path(config_file).exists():
            print(f"✅ Config Found: {config_file}")
            config_found = True
            break
    
    if not config_found:
        print("❌ Asterisk Config: extensions.conf not found")
        return False
    
    return True

def check_sip_endpoints():
    """Check SIP endpoints"""
    try:
        response = requests.get(
            "http://localhost:8088/ari/endpoints",
            auth=("asterisk", "1234"),
            timeout=5
        )
        if response.status_code == 200:
            endpoints = response.json()
            print(f"📞 SIP Endpoints: {len(endpoints)}")
            for endpoint in endpoints:
                name = endpoint.get('resource', 'Unknown')
                state = endpoint.get('state', 'Unknown')
                print(f"   - {name}: {state}")
            return True
        else:
            print(f"❌ SIP Endpoints: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ SIP Endpoints: Error - {e}")
        return False

def suggest_fixes():
    """Suggest fixes based on diagnostic results"""
    print("\n🔧 SUGGESTED FIXES:")
    print("=" * 50)
    
    print("\n1. 📞 ASTERISK CONFIGURATION:")
    print("   Copy the configuration to Asterisk:")
    print("   sudo cp asterisk-config/extensions.conf /etc/asterisk/")
    print("   sudo asterisk -rx 'dialplan reload'")
    
    print("\n2. 🔄 RESTART ASTERISK:")
    print("   sudo systemctl restart asterisk")
    print("   # OR")
    print("   sudo asterisk -rx 'core restart now'")
    
    print("\n3. 📱 CHECK SIP CLIENT CONTEXT:")
    print("   Ensure your SIP client (1001) is configured to use:")
    print("   - Context: openai-voice-assistant")
    print("   - OR Context: from-sip")
    print("   - OR Context: internal")
    
    print("\n4. 🧪 TEST ASTERISK CLI:")
    print("   sudo asterisk -r")
    print("   > dialplan show 1000")
    print("   > stasis show apps")
    print("   > pjsip show endpoints")
    
    print("\n5. 🔍 MONITOR ASTERISK LOGS:")
    print("   sudo tail -f /var/log/asterisk/messages")
    print("   # Make a call and watch for errors")

def main():
    """Main diagnostic function"""
    print("🔍 NPCL VOICE ASSISTANT - CALL FLOW DIAGNOSTICS")
    print("=" * 60)
    
    print("\n📊 SYSTEM STATUS:")
    print("-" * 30)
    
    # Check all components
    ari_ok = check_ari_server()
    asterisk_ari_ok = check_asterisk_ari()
    stasis_ok = check_stasis_apps()
    config_ok = check_asterisk_config()
    sip_ok = check_sip_endpoints()
    
    print("\n📋 DIAGNOSTIC SUMMARY:")
    print("-" * 30)
    print(f"ARI Server:           {'✅' if ari_ok else '❌'}")
    print(f"Asterisk ARI:         {'✅' if asterisk_ari_ok else '❌'}")
    print(f"Stasis App:           {'✅' if stasis_ok else '❌'}")
    print(f"Asterisk Config:      {'✅' if config_ok else '❌'}")
    print(f"SIP Endpoints:        {'✅' if sip_ok else '❌'}")
    
    # Overall status
    all_ok = all([ari_ok, asterisk_ari_ok, stasis_ok, config_ok, sip_ok])
    
    if all_ok:
        print("\n🎉 ALL SYSTEMS OPERATIONAL!")
        print("   If calls still don't work, check:")
        print("   1. SIP client context configuration")
        print("   2. Asterisk logs during call attempts")
    else:
        print("\n⚠️  ISSUES DETECTED!")
        suggest_fixes()
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()