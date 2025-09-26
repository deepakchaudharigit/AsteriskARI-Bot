#!/usr/bin/env python3
import socket
import hashlib
import time

def test_sip_auth():
    """Test SIP authentication with different passwords"""
    passwords = ['1234', 'secret', 'asterisk', '1000', '']
    
    print("🧪 Testing SIP authentication with different passwords...")
    
    for password in passwords:
        print(f"\n🔍 Testing password: '{password}'")
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(3)
            
            # Create SIP REGISTER message
            call_id = f"test-{int(time.time())}"
            
            sip_msg = f"""REGISTER sip:192.168.0.212:5060 SIP/2.0
Via: SIP/2.0/UDP 192.168.0.212:5060;branch=z9hG4bK-{call_id}
From: <sip:1000@192.168.0.212>;tag={call_id}
To: <sip:1000@192.168.0.212>
Call-ID: {call_id}@192.168.0.212
CSeq: 1 REGISTER
Contact: <sip:1000@192.168.0.212:5060>
Authorization: Digest username="1000", realm="asterisk", nonce="test", uri="sip:192.168.0.212", response="test"
Expires: 3600
Content-Length: 0

""".encode()
            
            sock.sendto(sip_msg, ('192.168.0.212', 5060))
            response, addr = sock.recvfrom(1024)
            
            response_str = response.decode('utf-8', errors='ignore')
            
            if '401 Unauthorized' in response_str:
                print(f"   📋 Got authentication challenge (normal)")
            elif '200 OK' in response_str:
                print(f"   ✅ Authentication successful!")
            else:
                print(f"   ❓ Unexpected response: {response_str[:50]}...")
                
        except socket.timeout:
            print(f"   ❌ Timeout - no response")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        finally:
            sock.close()

if __name__ == "__main__":
    test_sip_auth()
