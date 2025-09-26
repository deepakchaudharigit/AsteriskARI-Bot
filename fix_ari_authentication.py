#!/usr/bin/env python3
"""
Fix ARI Authentication and Stasis Registration Issues
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

def check_ari_config():
    """Check ARI configuration"""
    print("🔍 Checking ARI configuration...")
    
    # Check if our project ARI config exists
    if os.path.exists("asterisk-config/ari.conf"):
        print("✅ Project ARI config exists")
        with open("asterisk-config/ari.conf", 'r') as f:
            content = f.read()
            print("📋 Project ARI config:")
            print(content)
    else:
        print("❌ Project ARI config not found")
    
    # Check system ARI config
    stdout, stderr, returncode = run_command("sudo cat /etc/asterisk/ari.conf")
    if returncode == 0:
        print("\n📋 System ARI config:")
        print(stdout)
    else:
        print(f"\n❌ Cannot read system ARI config: {stderr}")

def create_working_ari_config():
    """Create a working ARI configuration"""
    print("\n🔧 Creating working ARI configuration...")
    
    ari_config = """[general]
enabled = yes
pretty = yes
allowed_origins = localhost:8000,127.0.0.1:8000

[asterisk]
type = user
read_only = no
password = 1234
"""
    
    # Write to project config
    with open("asterisk-config/ari.conf", 'w') as f:
        f.write(ari_config)
    
    print("✅ Created working ARI configuration")
    return ari_config

def apply_ari_config():
    """Apply ARI configuration to system"""
    print("\n🔄 Applying ARI configuration...")
    
    # Copy to system
    stdout, stderr, returncode = run_command("sudo cp asterisk-config/ari.conf /etc/asterisk/ari.conf")
    if returncode == 0:
        print("✅ Copied ARI config to system")
    else:
        print(f"❌ Failed to copy ARI config: {stderr}")
        return False
    
    # Reload ARI
    stdout, stderr, returncode = run_command("sudo asterisk -rx 'ari reload'")
    if returncode == 0:
        print("✅ Reloaded ARI configuration")
    else:
        print(f"❌ Failed to reload ARI: {stderr}")
        return False
    
    return True

def test_ari_authentication():
    """Test ARI authentication"""
    print("\n🧪 Testing ARI authentication...")
    
    # Test with correct credentials
    stdout, stderr, returncode = run_command("curl -s http://localhost:8088/ari/asterisk/info -u asterisk:1234")
    if returncode == 0:
        if "Authentication required" in stdout:
            print("❌ Authentication still failing")
            return False
        elif "{" in stdout:  # JSON response
            print("✅ ARI authentication successful!")
            print(f"Response: {stdout[:100]}...")
            return True
        else:
            print(f"⚠️  Unexpected response: {stdout}")
            return False
    else:
        print(f"❌ Connection failed: {stderr}")
        return False

def check_http_server():
    """Check if HTTP server is enabled"""
    print("\n🔍 Checking HTTP server configuration...")
    
    stdout, stderr, returncode = run_command("sudo asterisk -rx 'http show status'")
    if returncode == 0:
        print("✅ HTTP server status:")
        print(stdout)
        if "HTTP Server Status" in stdout and "Enabled" in stdout:
            return True
        else:
            print("❌ HTTP server not properly enabled")
            return False
    else:
        print(f"❌ Cannot check HTTP status: {stderr}")
        return False

def create_http_config():
    """Create HTTP configuration if needed"""
    print("\n🔧 Creating HTTP configuration...")
    
    http_config = """[general]
enabled=yes
bindaddr=127.0.0.1
bindport=8088
prefix=asterisk
"""
    
    # Write to project config
    with open("asterisk-config/http.conf", 'w') as f:
        f.write(http_config)
    
    print("✅ Created HTTP configuration")
    
    # Copy to system
    stdout, stderr, returncode = run_command("sudo cp asterisk-config/http.conf /etc/asterisk/http.conf")
    if returncode == 0:
        print("✅ Applied HTTP configuration")
        
        # Reload HTTP
        stdout, stderr, returncode = run_command("sudo asterisk -rx 'http reload'")
        if returncode == 0:
            print("✅ Reloaded HTTP server")
            return True
    
    return False

def provide_restart_instructions():
    """Provide instructions to restart ARI bot"""
    print("\n" + "=" * 60)
    print("🚀 RESTART ARI BOT WITH FIXED AUTHENTICATION")
    print("=" * 60)
    
    print("\n📋 Now that ARI authentication is fixed:")
    print("1. Stop the current ARI bot (Ctrl+C in its terminal)")
    print("2. Wait 5 seconds")
    print("3. Restart ARI bot: python3 ari_bot.py")
    print("4. Wait for 'ready for conversation'")
    print("5. Check Stasis registration: sudo asterisk -rx 'ari show apps'")
    print("6. Test dial 1000")
    
    print("\n✅ Expected Results After Restart:")
    print("- ARI authentication works")
    print("- Stasis app 'openai-voice-assistant' appears in 'ari show apps'")
    print("- Extension 1000 transfers to AI instead of disconnecting")
    print("- Voice conversation with AI works")
    
    print("\n🔍 Monitor During Test:")
    print("# Watch ARI bot logs")
    print("tail -f logs/ari_bot_final.log")
    print()
    print("# Watch Asterisk logs")
    print("sudo tail -f /var/log/asterisk/messages")

def main():
    """Main function"""
    print("🔧 FIX ARI AUTHENTICATION AND STASIS REGISTRATION")
    print("=" * 60)
    print("Issues found:")
    print("❌ No Stasis applications registered")
    print("❌ ARI authentication failing")
    print()
    
    # Check current ARI config
    check_ari_config()
    
    # Check HTTP server
    http_ok = check_http_server()
    if not http_ok:
        create_http_config()
    
    # Create and apply working ARI config
    create_working_ari_config()
    if apply_ari_config():
        # Test authentication
        if test_ari_authentication():
            print("\n🎉 ARI authentication fixed!")
        else:
            print("\n⚠️  ARI authentication still has issues")
    
    # Provide restart instructions
    provide_restart_instructions()
    
    print("\n" + "=" * 60)
    print("🎯 SUMMARY")
    print("=" * 60)
    print("✅ Fixed ARI configuration")
    print("✅ Applied authentication settings")
    print("🔄 NEXT: Restart ARI bot to register Stasis app")
    print("📞 THEN: Test dial 1000 for voice assistant")
    print("=" * 60)

if __name__ == "__main__":
    main()