#!/usr/bin/env python3
"""
SIP Connectivity Test Script for NPCL Asterisk ARI Voice Assistant
This script tests SIP registration and basic connectivity
"""

import socket
import time
import sys

def test_sip_port():
    """Test if SIP port 5060 is accessible"""
    print("🔍 Testing SIP port accessibility...")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(5)
        
        # Try to connect to SIP port
        result = sock.connect_ex(('192.168.0.212', 5060))
        sock.close()
        
        if result == 0:
            print("✅ SIP port 5060 is accessible")
            return True
        else:
            print("❌ SIP port 5060 is not accessible")
            return False
            
    except Exception as e:
        print(f"❌ Error testing SIP port: {e}")
        return False

def test_ari_connectivity():
    """Test ARI connectivity"""
    print("🔍 Testing ARI connectivity...")
    
    try:
        import requests
        
        # Test ARI endpoint
        response = requests.get(
            'http://localhost:8088/ari/asterisk/info',
            auth=('asterisk', '1234'),
            timeout=5
        )
        
        if response.status_code == 200:
            print("✅ ARI is accessible and responding")
            return True
        else:
            print(f"❌ ARI returned status code: {response.status_code}")
            return False
            
    except ImportError:
        print("⚠️  requests module not available, skipping ARI test")
        return None
    except Exception as e:
        print(f"❌ Error testing ARI: {e}")
        return False

def generate_sip_test_message():
    """Generate a simple SIP OPTIONS message for testing"""
    sip_message = f"""OPTIONS sip:192.168.0.212:5060 SIP/2.0
Via: SIP/2.0/UDP 192.168.0.212:5060;branch=z9hG4bK-test-{int(time.time())}
From: <sip:test@192.168.0.212>;tag=test-{int(time.time())}
To: <sip:192.168.0.212>
Call-ID: test-{int(time.time())}@192.168.0.212
CSeq: 1 OPTIONS
Max-Forwards: 70
User-Agent: NPCL-SIP-Test
Content-Length: 0

"""
    return sip_message.encode()

def test_sip_response():
    """Test if Asterisk responds to SIP messages"""
    print("🔍 Testing SIP server response...")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(5)
        
        # Send SIP OPTIONS message
        message = generate_sip_test_message()
        sock.sendto(message, ('192.168.0.212', 5060))
        
        # Wait for response
        response, addr = sock.recvfrom(1024)
        sock.close()
        
        response_str = response.decode('utf-8', errors='ignore')
        
        if 'SIP/2.0' in response_str:
            print("✅ Asterisk is responding to SIP messages")
            print(f"   Response: {response_str.split()[1]} {response_str.split()[2]}")
            return True
        else:
            print("❌ Invalid SIP response received")
            return False
            
    except socket.timeout:
        print("❌ No response from SIP server (timeout)")
        return False
    except Exception as e:
        print(f"❌ Error testing SIP response: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 NPCL Asterisk SIP Connectivity Test")
    print("=" * 50)
    
    tests = [
        ("SIP Port", test_sip_port),
        ("ARI Connectivity", test_ari_connectivity),
        ("SIP Response", test_sip_response)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} test...")
        result = test_func()
        results.append((test_name, result))
        time.sleep(1)
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    all_passed = True
    for test_name, result in results:
        if result is True:
            status = "✅ PASS"
        elif result is False:
            status = "❌ FAIL"
            all_passed = False
        else:
            status = "⚠️  SKIP"
        
        print(f"{test_name:20} {status}")
    
    print("\n" + "=" * 50)
    
    if all_passed:
        print("🎉 All tests passed! Your SIP configuration should work.")
        print("\n📋 Linphone Configuration:")
        print("   Domain: 192.168.0.212")
        print("   Username: 1000")
        print("   Password: 1234")
        print("   Proxy: sip:192.168.0.212:5060")
        print("   Transport: UDP")
    else:
        print("⚠️  Some tests failed. Check Asterisk configuration.")
        print("\n🔧 Troubleshooting steps:")
        print("1. Restart Asterisk: sudo systemctl restart asterisk")
        print("2. Check Asterisk logs: sudo tail -f /var/log/asterisk/messages")
        print("3. Verify modules are loaded: asterisk -rx 'module show like chan_pjsip'")

if __name__ == "__main__":
    main()