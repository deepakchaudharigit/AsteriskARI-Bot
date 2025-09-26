#!/bin/bash

# NPCL Asterisk SIP Account Fix Script
# This script fixes the "unable to use this account" error in Linphone

echo "🚀 NPCL Asterisk SIP Account Fix Script"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root for security reasons"
   exit 1
fi

echo "🔍 Step 1: Checking current Asterisk status..."

# Check if Asterisk is running
if pgrep -x "asterisk" > /dev/null; then
    print_status "Asterisk is running"
else
    print_error "Asterisk is not running. Please start it first."
    echo "   Try: sudo systemctl start asterisk"
    exit 1
fi

echo ""
echo "🔍 Step 2: Testing SIP connectivity..."

# Test SIP port
if nc -z -u 192.168.0.212 5060 2>/dev/null; then
    print_status "SIP port 5060 is accessible"
else
    print_warning "SIP port 5060 may not be accessible"
fi

echo ""
echo "🔍 Step 3: Checking configuration files..."

# Check if our project config files exist
if [ -f "asterisk-config/pjsip.conf" ]; then
    print_status "Project PJSIP configuration found"
else
    print_error "Project PJSIP configuration not found"
    exit 1
fi

echo ""
echo "🔧 Step 4: Creating simplified SIP configuration..."

# Create a simple working SIP configuration
cat > simple_sip_test.conf << 'EOF'
[general]
context=default
bindport=5060
bindaddr=0.0.0.0
allowguest=no
disallow=all
allow=ulaw
allow=alaw
nat=force_rport,comedia
qualify=yes

[1000]
type=friend
username=1000
secret=1234
host=dynamic
context=default
nat=force_rport,comedia
canreinvite=no
dtmfmode=rfc2833
qualify=yes
insecure=port,invite
EOF

print_status "Created simplified SIP configuration"

echo ""
echo "📋 Step 5: Linphone Configuration Instructions"
echo "=============================================="

echo ""
echo "🎯 Use these EXACT settings in Linphone:"
echo ""
echo "Account Settings:"
echo "  Display Name: NPCL Test User"
echo "  SIP Address: sip:1000@192.168.0.212"
echo "  Username: 1000"
echo "  Password: 1234"
echo "  Domain: 192.168.0.212"
echo "  Proxy: sip:192.168.0.212:5060"
echo "  Transport: UDP"
echo "  Register: Yes"
echo ""

echo "Advanced Settings:"
echo "  NAT Traversal: Enable"
echo "  STUN Server: (leave empty)"
echo "  ICE: Disable"
echo "  Audio Codecs: PCMU (ulaw), PCMA (alaw)"
echo "  DTMF: RFC2833"
echo ""

echo "🔍 Step 6: Testing alternative configurations..."

echo ""
echo "Alternative 1 - Using localhost:"
echo "  Domain: localhost"
echo "  Proxy: sip:localhost:5060"
echo ""

echo "Alternative 2 - Using hostname:"
hostname_val=$(hostname)
echo "  Domain: $hostname_val"
echo "  Proxy: sip:$hostname_val:5060"
echo ""

echo "🧪 Step 7: Test Extensions Available:"
echo "====================================="
echo "  1000 - Main NPCL Voice Assistant"
echo "  1010 - Simple codec test (no AI)"
echo "  9000 - Echo test"
echo "  1005 - IVR menu"
echo ""

echo "🔧 Step 8: Troubleshooting Commands:"
echo "===================================="
echo ""
echo "If still having issues, try these commands:"
echo ""
echo "1. Check Asterisk SIP status:"
echo "   sudo asterisk -rx 'sip show peers'"
echo "   sudo asterisk -rx 'pjsip show endpoints'"
echo ""
echo "2. Check if modules are loaded:"
echo "   sudo asterisk -rx 'module show like chan_sip'"
echo "   sudo asterisk -rx 'module show like chan_pjsip'"
echo ""
echo "3. Reload SIP configuration:"
echo "   sudo asterisk -rx 'sip reload'"
echo "   sudo asterisk -rx 'pjsip reload'"
echo ""
echo "4. Check Asterisk logs:"
echo "   sudo tail -f /var/log/asterisk/messages"
echo "   sudo tail -f /var/log/asterisk/full"
echo ""
echo "5. Test with simple SIP client:"
echo "   sudo apt install sipgrep"
echo "   sipgrep -i any port 5060"
echo ""

echo "🎯 Step 9: Quick Linphone Setup:"
echo "================================"
echo ""
echo "1. Install Linphone:"
echo "   sudo apt update && sudo apt install linphone-desktop"
echo ""
echo "2. Launch Linphone:"
echo "   linphone"
echo ""
echo "3. Add Account:"
echo "   - Go to Settings → Accounts → Add Account"
echo "   - Choose 'Use SIP Account'"
echo "   - Enter the configuration above"
echo ""
echo "4. Test Call:"
echo "   - Dial 1010 for simple test"
echo "   - Dial 1000 for voice assistant"
echo ""

echo "✅ Setup complete!"
echo ""
print_status "If you're still having issues, the problem might be:"
echo "   1. Asterisk using different config files"
echo "   2. Firewall blocking SIP traffic"
echo "   3. Network configuration issues"
echo "   4. SIP modules not properly loaded"
echo ""
print_warning "Try the troubleshooting commands above to diagnose further."

# Create a quick test script
cat > quick_sip_test.py << 'EOF'
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
EOF

chmod +x quick_sip_test.py
print_status "Created quick SIP test script: quick_sip_test.py"

echo ""
echo "🚀 Run 'python3 quick_sip_test.py' to test SIP connectivity"
echo ""