#!/usr/bin/env python3
"""
PJSIP Configuration Checker for NPCL Asterisk ARI Voice Assistant
This script checks if your project PJSIP configuration is being used by Asterisk
"""

import subprocess
import sys
import os

def run_asterisk_command(command):
    """Run an Asterisk CLI command"""
    try:
        full_command = f"sudo asterisk -rx '{command}'"
        result = subprocess.run(full_command, shell=True, capture_output=True, text=True, timeout=10)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "", "Command timed out", 1
    except Exception as e:
        return "", str(e), 1

def check_pjsip_status():
    """Check PJSIP configuration and status"""
    print("🔍 PJSIP Configuration Checker")
    print("=" * 50)
    
    # Check if PJSIP module is loaded
    print("\n📋 1. Checking if PJSIP module is loaded...")
    stdout, stderr, returncode = run_asterisk_command("module show like res_pjsip")
    
    if returncode == 0 and "res_pjsip.so" in stdout:
        print("✅ PJSIP module is loaded")
    else:
        print("❌ PJSIP module not loaded or accessible")
        print(f"   Error: {stderr}")
        return
    
    # Check PJSIP endpoints
    print("\n📋 2. Checking PJSIP endpoints...")
    stdout, stderr, returncode = run_asterisk_command("pjsip show endpoints")
    
    if returncode == 0:
        if stdout and "1000" in stdout:
            print("✅ PJSIP endpoints found:")
            print(f"   {stdout}")
        else:
            print("❌ No PJSIP endpoints found or user 1000 not configured")
    else:
        print(f"❌ Error checking endpoints: {stderr}")
    
    # Check PJSIP auths
    print("\n📋 3. Checking PJSIP authentication...")
    stdout, stderr, returncode = run_asterisk_command("pjsip show auths")
    
    if returncode == 0:
        if stdout and "1000" in stdout:
            print("✅ PJSIP authentication found:")
            print(f"   {stdout}")
        else:
            print("❌ No PJSIP authentication found for user 1000")
    else:
        print(f"❌ Error checking auths: {stderr}")
    
    # Check PJSIP AORs
    print("\n📋 4. Checking PJSIP AORs...")
    stdout, stderr, returncode = run_asterisk_command("pjsip show aors")
    
    if returncode == 0:
        if stdout and "1000" in stdout:
            print("✅ PJSIP AORs found:")
            print(f"   {stdout}")
        else:
            print("❌ No PJSIP AORs found for user 1000")
    else:
        print(f"❌ Error checking AORs: {stderr}")
    
    # Check current registrations
    print("\n📋 5. Checking current registrations...")
    stdout, stderr, returncode = run_asterisk_command("pjsip show registrations")
    
    if returncode == 0:
        if stdout:
            print("📋 Current registrations:")
            print(f"   {stdout}")
        else:
            print("ℹ️  No current registrations")
    else:
        print(f"❌ Error checking registrations: {stderr}")
    
    # Check PJSIP settings
    print("\n📋 6. Checking PJSIP settings...")
    stdout, stderr, returncode = run_asterisk_command("pjsip show settings")
    
    if returncode == 0:
        print("✅ PJSIP settings:")
        # Show only relevant lines
        lines = stdout.split('\n')
        for line in lines[:10]:  # Show first 10 lines
            if line.strip():
                print(f"   {line}")
        if len(lines) > 10:
            print("   ... (truncated)")
    else:
        print(f"❌ Error checking settings: {stderr}")

def check_config_files():
    """Check which configuration files exist"""
    print("\n📋 7. Checking configuration files...")
    
    # Check project config
    project_pjsip = "asterisk-config/pjsip.conf"
    if os.path.exists(project_pjsip):
        print(f"✅ Project PJSIP config exists: {project_pjsip}")
    else:
        print(f"❌ Project PJSIP config not found: {project_pjsip}")
    
    # Check system config
    system_pjsip = "/etc/asterisk/pjsip.conf"
    if os.path.exists(system_pjsip):
        print(f"✅ System PJSIP config exists: {system_pjsip}")
    else:
        print(f"❌ System PJSIP config not found: {system_pjsip}")

def provide_solution():
    """Provide solution based on findings"""
    print("\n" + "=" * 50)
    print("🎯 SOLUTION FOR ZOIPER")
    print("=" * 50)
    
    print("\nBased on your pjsip.conf file, use this EXACT configuration in Zoiper:")
    print()
    print("Account Settings:")
    print("├── Account name: NPCL User 1000")
    print("├── Domain: 192.168.0.212")
    print("├── Username: 1000")
    print("├── Password: 1234")
    print("├── Authentication username: 1000")
    print("├── Outbound proxy: 192.168.0.212:5060")
    print("├── Transport: UDP")
    print("└── Enable registration: ✓")
    print()
    
    print("Alternative accounts to try:")
    print("├── Username: 1001, Password: 1234")
    print("├── Username: agent1, Password: agent123")
    print("└── Username: supervisor, Password: super123")
    print()
    
    print("🔧 If still getting 'Wrong password':")
    print("1. Your system might not be using your project pjsip.conf")
    print("2. Copy your config to system: sudo cp asterisk-config/pjsip.conf /etc/asterisk/")
    print("3. Reload PJSIP: sudo asterisk -rx 'pjsip reload'")
    print("4. Check again with this script")

def main():
    """Main function"""
    if os.geteuid() != 0:
        print("⚠️  Note: Some commands require sudo access")
        print("   Run with sudo for complete information")
        print()
    
    check_pjsip_status()
    check_config_files()
    provide_solution()

if __name__ == "__main__":
    main()