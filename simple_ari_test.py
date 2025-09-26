#!/usr/bin/env python3
"""
Simple ARI WebSocket Test using requests and basic websocket
"""

import requests
import time
import json

def test_ari_http():
    """Test ARI HTTP connection"""
    try:
        print("🧪 Testing ARI HTTP connection...")
        
        response = requests.get(
            "http://localhost:8088/ari/asterisk/info",
            auth=("asterisk", "1234"),
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ ARI HTTP connection working")
            print(f"   Asterisk version: {data.get('system', {}).get('version', 'Unknown')}")
            return True
        else:
            print(f"❌ ARI HTTP failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ ARI HTTP test failed: {e}")
        return False

def register_stasis_app():
    """Register Stasis application using HTTP requests"""
    try:
        print("\n🔌 Attempting to register Stasis app via HTTP...")
        
        # Try to get applications list
        response = requests.get(
            "http://localhost:8088/ari/applications",
            auth=("asterisk", "1234"),
            timeout=5
        )
        
        if response.status_code == 200:
            apps = response.json()
            print(f"✅ Current applications: {apps}")
            
            # Check if our app is listed
            app_names = [app.get('name', '') for app in apps]
            if 'openai-voice-assistant' in app_names:
                print("✅ Stasis app 'openai-voice-assistant' is registered!")
                return True
            else:
                print("⚠️ Stasis app not found in applications list")
                return False
        else:
            print(f"❌ Failed to get applications: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking applications: {e}")
        return False

def create_websocket_connection():
    """Create WebSocket connection using simple approach"""
    try:
        print("\n🔌 Creating WebSocket connection...")
        
        # Use curl to test WebSocket connection
        import subprocess
        
        # Test WebSocket connection with curl
        cmd = [
            "curl", "-v",
            "-H", "Authorization: Basic YXN0ZXJpc2s6MTIzNA==",  # asterisk:1234 in base64
            "-H", "Connection: Upgrade",
            "-H", "Upgrade: websocket",
            "-H", "Sec-WebSocket-Version: 13",
            "-H", "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==",
            "http://localhost:8088/ari/events?app=openai-voice-assistant"
        ]
        
        print("🧪 Testing WebSocket upgrade...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if "101 Switching Protocols" in result.stderr:
            print("✅ WebSocket upgrade successful!")
            return True
        else:
            print("❌ WebSocket upgrade failed")
            print(f"Output: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")
        return False

def check_stasis_registration():
    """Check if Stasis app is registered in Asterisk"""
    try:
        print("\n🔍 Checking Stasis registration in Asterisk...")
        
        import subprocess
        
        # Run asterisk command to check apps
        result = subprocess.run(
            ["sudo", "asterisk", "-rx", "ari show apps"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            output = result.stdout.strip()
            print(f"📋 ARI apps output:\n{output}")
            
            if "openai-voice-assistant" in output:
                print("✅ Stasis app 'openai-voice-assistant' is registered!")
                return True
            else:
                print("❌ Stasis app 'openai-voice-assistant' NOT registered")
                return False
        else:
            print(f"❌ Error running asterisk command: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking Stasis registration: {e}")
        return False

def main():
    """Main test function"""
    print("🔧 SIMPLE ARI STASIS REGISTRATION TEST")
    print("=" * 50)
    
    # Step 1: Test basic ARI HTTP
    if not test_ari_http():
        print("\n❌ Basic ARI connection failed")
        return
    
    # Step 2: Check current Stasis registration
    stasis_registered = check_stasis_registration()
    
    # Step 3: Test applications endpoint
    register_stasis_app()
    
    # Step 4: Test WebSocket connection
    create_websocket_connection()
    
    # Step 5: Final check
    print("\n" + "=" * 50)
    print("🎯 FINAL STATUS")
    print("=" * 50)
    
    if stasis_registered:
        print("✅ Stasis app is already registered!")
        print("📞 Try dialing 1000 in Zoiper - should work now")
    else:
        print("❌ Stasis app still not registered")
        print("💡 The ARI bot needs to maintain a WebSocket connection")
        print("💡 Try restarting the ARI bot: python3 ari_bot.py")
    
    print("\n🔍 Manual check:")
    print("sudo asterisk -rx 'ari show apps'")

if __name__ == "__main__":
    main()