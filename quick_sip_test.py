#!/usr/bin/env python3
import socket
import time

def test_sip():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(3)
        
        # Simple SIP OPTIONS request
        sip_msg = f"""OPTIONS sip:192.168.0.212:5060 SIP/2.0
Via: SIP/2.0/UDP 192.168.0.212:5060;branch=z9hG4bK-test-{int(time.time())}
From: <sip:test@192.168.0.212>;tag=test-{int(time.time())}
To: <sip:192.168.0.212>
Call-ID: test-{int(time.time())}@192.168.0.212
CSeq: 1 OPTIONS
Max-Forwards: 70
User-Agent: NPCL-Test
Content-Length: 0

""".encode()
        
        sock.sendto(sip_msg, ('192.168.0.212', 5060))
        response, addr = sock.recvfrom(1024)
        
        if b'SIP/2.0' in response:
            print("✅ SIP server is responding!")
            print(f"Response: {response.decode('utf-8', errors='ignore')[:100]}...")
        else:
            print("❌ Invalid SIP response")
            
    except socket.timeout:
        print("❌ SIP server not responding (timeout)")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    print("🧪 Quick SIP Test...")
    test_sip()
