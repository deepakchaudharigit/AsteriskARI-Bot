#!/usr/bin/env python3
"""
Quick status check to see if the system is working despite the event loop warnings
"""

import requests
import time

def check_system_status():
    """Check if the system is actually working"""
    print("🔍 Checking System Status...")
    
    try:
        # Check FastAPI health - try multiple endpoints
        endpoints_to_try = [
            "http://localhost:8000/ari/health",
            "http://localhost:8000/health", 
            "http://localhost:8000/"
        ]
        
        response = None
        for endpoint in endpoints_to_try:
            try:
                response = requests.get(endpoint, timeout=5)
                if response.status_code == 200:
                    break
            except:
                continue
        
        if response and response.status_code == 200:
            health = response.json()
            print("✅ FastAPI Health Check:")
            print(f"   Status: {health.get('status', 'Unknown')}")
            print(f"   WebSocket: {health.get('websocket_connected', False)}")
            print(f"   Stasis Registered: {health.get('stasis_registered', False)}")
            
            components = health.get('components', {})
            print("📊 Components:")
            print(f"   WebSocket: {'✅' if components.get('websocket') else '❌'}")
            print(f"   ARI Handler: {'✅' if components.get('ari_handler') else '❌'}")
            print(f"   OpenAI: {'✅' if components.get('openai', True) else '❌'}")
            print(f"   External Media: {'✅' if components.get('external_media') else '❌'}")
            
            return all([
                components.get('websocket', False),
                components.get('ari_handler', False),
                components.get('openai', True),
                components.get('external_media', False)
            ])
        else:
            print(f"❌ Health check failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking health: {e}")
        return False

def check_asterisk_registration():
    """Check if MicroSIP can register with Asterisk"""
    print("\n📡 Checking Asterisk SIP Status...")
    
    try:
        import subprocess
        result = subprocess.run([
            "docker", "exec", "asterisk-fresh", 
            "asterisk", "-rx", "sip show peers"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("SIP Peers Status:")
            lines = result.stdout.split('\n')
            for line in lines:
                if '1000' in line:
                    print(f"   📞 {line}")
                    if 'OK' in line:
                        print("   ✅ User 1000 is registered!")
                        return True
                    else:
                        print("   ⚠️ User 1000 is not registered yet")
            
            print("\n💡 To register with MicroSIP:")
            print("   1. Add account with settings provided")
            print("   2. Wait for 'Registered' status")
            print("   3. Then dial 1000")
            
        return False
        
    except Exception as e:
        print(f"❌ Error checking SIP: {e}")
        return False

def monitor_for_calls():
    """Monitor for incoming calls"""
    print("\n📞 Monitoring for calls...")
    print("Make a call to 1000 now and watch for activity...")
    
    last_count = 0
    
    for i in range(30):  # Monitor for 30 seconds
        try:
            response = requests.get("http://localhost:8088/ari/channels", 
                                  auth=("asterisk", "1234"), timeout=3)
            if response.status_code == 200:
                channels = response.json()
                current_count = len(channels)
                
                if current_count != last_count:
                    if current_count > last_count:
                        print(f"🔔 CALL DETECTED! Active channels: {current_count}")
                        for channel in channels:
                            channel_id = channel.get('id', 'Unknown')
                            state = channel.get('state', 'Unknown')
                            print(f"   📞 Channel: {channel_id} - State: {state}")
                    else:
                        print(f"📴 Call ended. Active channels: {current_count}")
                
                last_count = current_count
            
            time.sleep(1)
            
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped")
            break
        except Exception as e:
            print(f"❌ Monitoring error: {e}")
            time.sleep(2)

def main():
    print("========================================")
    print("🔍 Quick System Status Check")
    print("========================================")
    
    # Check if system is working despite warnings
    system_ok = check_system_status()
    
    # Check SIP registration
    sip_ok = check_asterisk_registration()
    
    print("\n========================================")
    print("📊 Status Summary")
    print("========================================")
    print(f"System Components: {'✅ OK' if system_ok else '❌ FAILED'}")
    print(f"SIP Registration: {'✅ OK' if sip_ok else '⚠️ PENDING'}")
    
    if system_ok:
        print("\n🎉 GOOD NEWS: Despite the event loop warnings,")
        print("your system appears to be working!")
        print("\nThe warnings are non-critical - the core functionality")
        print("should still work for voice calls.")
        
        if not sip_ok:
            print("\n📱 Next step: Register MicroSIP and test a call")
        
        print("\n🔍 Starting call monitoring...")
        monitor_for_calls()
    else:
        print("\n❌ System has issues that need to be resolved")

if __name__ == "__main__":
    main()