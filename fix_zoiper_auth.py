#!/usr/bin/env python3
"""
Quick fix script for Zoiper authentication issues
"""

import subprocess
import time
import requests

def print_banner():
    print("\n" + "=" * 60)
    print("🔧 ZOIPER AUTHENTICATION FIX")
    print("=" * 60)

def check_asterisk_status():
    print("\n🔍 CHECKING ASTERISK STATUS...")
    
    try:
        # Check endpoints
        result = subprocess.run([
            "docker", "exec", "npcl-asterisk-20", 
            "asterisk", "-rx", "pjsip show endpoints"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Asterisk is running")
            print("\n📋 Configured Endpoints:")
            lines = result.stdout.split('\n')
            for line in lines:
                if 'Endpoint:' in line and ('1000' in line or '1001' in line):
                    print(f"   {line.strip()}")
        else:
            print("❌ Asterisk not responding")
            return False
            
    except Exception as e:
        print(f"❌ Error checking Asterisk: {e}")
        return False
    
    return True

def check_auth_config():
    print("\n🔐 CHECKING AUTHENTICATION CONFIG...")
    
    try:
        result = subprocess.run([
            "docker", "exec", "npcl-asterisk-20",
            "asterisk", "-rx", "pjsip show auths"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Authentication configured")
            lines = result.stdout.split('\n')
            for line in lines:
                if 'Auth:' in line and ('1000' in line or '1001' in line):
                    print(f"   {line.strip()}")
        else:
            print("❌ Cannot check authentication")
            
    except Exception as e:
        print(f"❌ Error checking auth: {e}")

def show_correct_config():
    print("\n📱 CORRECT ZOIPER CONFIGURATION:")
    print("=" * 40)
    print("Account Type: SIP")
    print("Domain: localhost")
    print("Username: 1001")
    print("Password: 1234")
    print("Port: 5060")
    print("Transport: UDP")
    print("Register: YES")
    print("=" * 40)

def test_sip_connectivity():
    print("\n🌐 TESTING SIP CONNECTIVITY...")
    
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(5)
        
        # Try to connect to SIP port
        result = sock.connect_ex(('localhost', 5060))
        sock.close()
        
        if result == 0:
            print("✅ SIP port 5060 is accessible")
        else:
            print("❌ Cannot connect to SIP port 5060")
            
    except Exception as e:
        print(f"❌ Network test failed: {e}")

def restart_asterisk():
    print("\n🔄 RESTARTING ASTERISK...")
    
    try:
        result = subprocess.run([
            "docker", "restart", "npcl-asterisk-20"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Asterisk restarted successfully")
            print("⏳ Waiting for startup...")
            time.sleep(10)
            return True
        else:
            print("❌ Failed to restart Asterisk")
            return False
            
    except Exception as e:
        print(f"❌ Error restarting Asterisk: {e}")
        return False

def enable_debug_logging():
    print("\n🔍 ENABLING DEBUG LOGGING...")
    
    try:
        # Enable verbose logging
        subprocess.run([
            "docker", "exec", "npcl-asterisk-20",
            "asterisk", "-rx", "core set verbose 5"
        ], capture_output=True)
        
        subprocess.run([
            "docker", "exec", "npcl-asterisk-20",
            "asterisk", "-rx", "core set debug 5"
        ], capture_output=True)
        
        print("✅ Debug logging enabled")
        print("💡 Watch logs with: docker logs -f npcl-asterisk-20")
        
    except Exception as e:
        print(f"❌ Error enabling debug: {e}")

def show_troubleshooting_steps():
    print("\n🛠️ TROUBLESHOOTING STEPS:")
    print("=" * 50)
    print("1. 📱 Check Zoiper configuration matches above")
    print("2. 🔄 Try restarting Zoiper application")
    print("3. 🌐 Ensure you're on the same network as Docker")
    print("4. 🔍 Watch Asterisk logs for auth attempts")
    print("5. 📞 Try calling 1000 after successful registration")
    print("=" * 50)
    
    print("\n🔍 REAL-TIME MONITORING:")
    print("Terminal 1: docker logs -f npcl-asterisk-20")
    print("Terminal 2: python3 src/main.py --ari-bot")
    print("Terminal 3: python3 test_call_monitoring.py")

def main():
    print_banner()
    
    if not check_asterisk_status():
        print("\n❌ Asterisk is not running properly!")
        return
    
    check_auth_config()
    show_correct_config()
    test_sip_connectivity()
    
    print("\n🤔 What would you like to do?")
    print("1. 🔄 Restart Asterisk")
    print("2. 🔍 Enable debug logging")
    print("3. 📋 Show troubleshooting steps")
    print("4. ❌ Exit")
    
    try:
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            if restart_asterisk():
                check_asterisk_status()
        elif choice == "2":
            enable_debug_logging()
        elif choice == "3":
            show_troubleshooting_steps()
        elif choice == "4":
            print("👋 Good luck with your configuration!")
        else:
            print("❌ Invalid choice")
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()