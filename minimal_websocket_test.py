#!/usr/bin/env python3
"""
Minimal WebSocket test for Stasis registration
Uses only standard library and requests
"""

import requests
import time
import threading
import socket
import base64
import json

def test_websocket_with_socket():
    """Test WebSocket connection using raw socket"""
    try:
        print("🔌 Testing WebSocket connection with raw socket...")
        
        # Create socket connection
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect(("localhost", 8088))
        
        # Create WebSocket handshake
        auth_string = base64.b64encode(b"asterisk:1234").decode()
        
        handshake = (
            "GET /ari/events?app=openai-voice-assistant HTTP/1.1\\r\\n"
            "Host: localhost:8088\\r\\n"
            "Upgrade: websocket\\r\\n"
            "Connection: Upgrade\\r\\n"
            "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\\r\\n"
            "Sec-WebSocket-Version: 13\\r\\n"
            f"Authorization: Basic {auth_string}\\r\\n"
            "\\r\\n"
        )
        
        print("📤 Sending WebSocket handshake...")
        sock.send(handshake.encode())
        
        # Receive response
        response = sock.recv(1024).decode()
        print(f"📥 Response: {response[:200]}...")
        
        if "101 Switching Protocols" in response:
            print("✅ WebSocket handshake successful!")
            print("🎯 Stasis app should now be registered")
            
            # Keep connection alive for a moment
            print("⏳ Keeping connection alive for 5 seconds...")
            time.sleep(5)
            
            sock.close()
            return True
        else:
            print("❌ WebSocket handshake failed")
            sock.close()
            return False
            
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")
        return False

def check_stasis_with_requests():
    """Check Stasis registration using requests"""
    try:
        print("\\n🔍 Checking Stasis registration...")
        
        # Get applications
        response = requests.get(
            "http://localhost:8088/ari/applications",
            auth=("asterisk", "1234"),
            timeout=5
        )
        
        if response.status_code == 200:
            apps = response.json()
            print(f"📋 Applications found: {len(apps)}")
            
            for app in apps:
                name = app.get('name', 'Unknown')
                print(f"   - {name}")
                
            app_names = [app.get('name', '') for app in apps]
            if 'openai-voice-assistant' in app_names:
                print("✅ Stasis app 'openai-voice-assistant' is registered!")
                return True
            else:
                print("❌ Stasis app 'openai-voice-assistant' NOT found")
                return False
        else:
            print(f"❌ Failed to get applications: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking applications: {e}")
        return False

def create_persistent_connection():
    """Create a persistent WebSocket-like connection"""
    try:
        print("\\n🔗 Creating persistent connection for Stasis registration...")
        
        # Use requests session for persistent connection
        session = requests.Session()
        session.auth = ("asterisk", "1234")
        
        # Try to establish a long-polling connection
        url = "http://localhost:8088/ari/events"
        params = {"app": "openai-voice-assistant"}
        
        print(f"📡 Connecting to: {url}")
        print(f"📱 App: openai-voice-assistant")
        
        # Make a long-running request
        response = session.get(url, params=params, stream=True, timeout=30)
        
        if response.status_code == 200:
            print("✅ Connected to ARI events stream")
            print("🎯 Stasis app should now be registered")
            
            # Read a few events
            print("📥 Listening for events (10 seconds)...")
            start_time = time.time()
            
            for line in response.iter_lines():
                if time.time() - start_time > 10:
                    break
                    
                if line:
                    try:
                        event = json.loads(line.decode())
                        event_type = event.get('type', 'Unknown')
                        print(f"📨 Event: {event_type}")
                    except:
                        print(f"📨 Raw: {line.decode()[:100]}")
            
            return True
        else:
            print(f"❌ Connection failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Persistent connection failed: {e}")
        return False

def main():
    """Main test function"""
    print("🔧 MINIMAL WEBSOCKET STASIS REGISTRATION TEST")
    print("=" * 60)
    
    # Test 1: Check current status
    print("🧪 Step 1: Check current Stasis registration")
    initial_status = check_stasis_with_requests()
    
    if initial_status:
        print("\\n✅ Stasis app already registered!")
        print("📞 Try dialing 1000 in Zoiper")
        return
    
    # Test 2: Try WebSocket handshake
    print("\\n🧪 Step 2: Test WebSocket handshake")
    websocket_success = test_websocket_with_socket()
    
    if websocket_success:
        # Check if registration worked
        time.sleep(2)
        if check_stasis_with_requests():
            print("\\n🎉 SUCCESS! Stasis app registered via WebSocket")
            print("📞 Try dialing 1000 in Zoiper")
            return
    
    # Test 3: Try persistent HTTP connection
    print("\\n🧪 Step 3: Test persistent HTTP connection")
    persistent_success = create_persistent_connection()
    
    if persistent_success:
        # Check if registration worked
        time.sleep(2)
        if check_stasis_with_requests():
            print("\\n🎉 SUCCESS! Stasis app registered via persistent connection")
            print("📞 Try dialing 1000 in Zoiper")
            return
    
    # Final status
    print("\\n" + "=" * 60)
    print("🎯 FINAL RESULT")
    print("=" * 60)
    print("❌ Could not register Stasis app with available methods")
    print("\\n💡 Solutions:")
    print("1. Install websockets library: pip install websockets")
    print("2. Modify ARI bot to include WebSocket subscription")
    print("3. Use external WebSocket client (wscat, websocat)")
    print("\\n🔍 Manual check:")
    print("sudo asterisk -rx 'ari show apps'")

if __name__ == "__main__":
    main()