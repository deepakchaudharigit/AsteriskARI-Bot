#!/bin/bash

# SIP 408 Request Timeout Troubleshooting Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}🔧 SIP 408 Request Timeout Troubleshooting${NC}"
    echo -e "${BLUE}===========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

check_asterisk_status() {
    print_info "Checking Asterisk status..."
    
    if pgrep -f asterisk > /dev/null; then
        ASTERISK_PID=$(pgrep -f asterisk | head -1)
        print_success "Asterisk is running (PID: $ASTERISK_PID)"
        
        # Check how long it's been running
        UPTIME=$(ps -o etime= -p $ASTERISK_PID | tr -d ' ')
        print_info "Asterisk uptime: $UPTIME"
    else
        print_error "Asterisk is not running"
        return 1
    fi
}

check_network_connectivity() {
    print_info "Testing network connectivity..."
    
    LOCAL_IP=$(ip addr show wlp0s20f3 | grep "inet " | awk '{print $2}' | cut -d'/' -f1)
    print_success "Local IP: $LOCAL_IP"
    
    # Test UDP connectivity to SIP port
    print_info "Testing UDP connectivity to SIP port..."
    if timeout 3 nc -u -z localhost 5060 2>/dev/null; then
        print_success "Can connect to SIP port via UDP"
    else
        print_warning "Cannot connect to SIP port via UDP"
    fi
    
    # Test if we can reach our own IP
    print_info "Testing connectivity to own IP..."
    if timeout 3 nc -u -z $LOCAL_IP 5060 2>/dev/null; then
        print_success "Can connect to own IP on SIP port"
    else
        print_warning "Cannot connect to own IP on SIP port"
    fi
}

check_firewall_detailed() {
    print_info "Detailed firewall check..."
    
    # Check UFW status
    if command -v ufw &> /dev/null; then
        UFW_STATUS=$(sudo ufw status 2>/dev/null || echo "inactive")
        echo "UFW Status: $UFW_STATUS"
        
        if [[ "$UFW_STATUS" == *"5060/udp"* ]]; then
            print_success "SIP port 5060/udp is allowed in UFW"
        else
            print_warning "SIP port 5060/udp not explicitly allowed in UFW"
        fi
    fi
    
    # Check if any process is blocking the port
    print_info "Checking for port conflicts..."
    LISTENING_PROCESS=$(ss -tulpn | grep ":5060" | head -1)
    if [ ! -z "$LISTENING_PROCESS" ]; then
        print_success "Port 5060 is being used by: $LISTENING_PROCESS"
    else
        print_error "No process listening on port 5060"
    fi
}

test_sip_response() {
    print_info "Testing SIP server response..."
    
    LOCAL_IP=$(ip addr show wlp0s20f3 | grep "inet " | awk '{print $2}' | cut -d'/' -f1)
    
    # Create a simple SIP OPTIONS request
    cat > /tmp/sip_test.txt << EOF
OPTIONS sip:$LOCAL_IP SIP/2.0
Via: SIP/2.0/UDP $LOCAL_IP:5060;branch=z9hG4bK-test
From: <sip:test@$LOCAL_IP>;tag=test
To: <sip:$LOCAL_IP>
Call-ID: test@$LOCAL_IP
CSeq: 1 OPTIONS
Max-Forwards: 70
Content-Length: 0

EOF

    print_info "Sending SIP OPTIONS request to test server response..."
    
    # Send the SIP request and check for response
    if timeout 5 nc -u $LOCAL_IP 5060 < /tmp/sip_test.txt > /tmp/sip_response.txt 2>&1; then
        if [ -s /tmp/sip_response.txt ]; then
            print_success "Received SIP response from server"
            echo "Response preview:"
            head -3 /tmp/sip_response.txt | sed 's/^/  /'
        else
            print_warning "No response received from SIP server"
        fi
    else
        print_warning "Failed to send SIP request or timeout occurred"
    fi
    
    # Cleanup
    rm -f /tmp/sip_test.txt /tmp/sip_response.txt
}

check_zoiper_config() {
    print_info "Zoiper configuration recommendations for timeout issues..."
    
    LOCAL_IP=$(ip addr show wlp0s20f3 | grep "inet " | awk '{print $2}' | cut -d'/' -f1)
    
    echo "=== Recommended Zoiper Settings ==="
    echo "Account Configuration:"
    echo "  Username: 1000"
    echo "  Password: 1234"
    echo "  Domain: $LOCAL_IP"
    echo "  Port: 5060"
    echo "  Transport: UDP"
    echo ""
    echo "Advanced Settings (to fix timeouts):"
    echo "  Registration Timeout: 60 seconds"
    echo "  Keep-alive: 30 seconds"
    echo "  Retry Interval: 30 seconds"
    echo "  STUN: Disabled"
    echo "  ICE: Disabled"
    echo "  NAT Traversal: Auto"
    echo "  Outbound Proxy: (leave empty)"
    echo ""
    echo "Network Settings:"
    echo "  Local SIP Port: 5060"
    echo "  Local RTP Port Range: 8000-8100"
    echo "  Use Random Ports: No"
    echo ""
    echo "Authentication:"
    echo "  Authentication Username: 1000"
    echo "  Authorization Username: (leave empty)"
    echo "  Display Name: Test User"
}

check_asterisk_sip_config() {
    print_info "Checking Asterisk SIP configuration..."
    
    if [ -f "asterisk-config/sip.conf" ]; then
        echo "Current SIP configuration:"
        echo "========================="
        
        # Check general settings
        echo "General settings:"
        grep -A 10 "^\[general\]" asterisk-config/sip.conf | grep -E "(bindport|bindaddr|nat|transport)" | sed 's/^/  /'
        
        echo ""
        echo "User 1000 settings:"
        grep -A 15 "^\[1000\]" asterisk-config/sip.conf | sed 's/^/  /'
        
        # Check for timeout-related settings
        echo ""
        print_info "Checking for timeout-related settings..."
        
        if grep -q "qualify=yes" asterisk-config/sip.conf; then
            print_success "SIP qualify is enabled (good for detecting timeouts)"
        else
            print_warning "SIP qualify is not enabled"
        fi
        
        if grep -q "nat=" asterisk-config/sip.conf; then
            NAT_SETTING=$(grep "nat=" asterisk-config/sip.conf | head -1)
            print_info "NAT setting: $NAT_SETTING"
        else
            print_warning "No NAT setting found"
        fi
    else
        print_error "SIP configuration file not found"
    fi
}

suggest_timeout_fixes() {
    print_info "🎯 Timeout Fix Suggestions:"
    echo "=========================="
    
    LOCAL_IP=$(ip addr show wlp0s20f3 | grep "inet " | awk '{print $2}' | cut -d'/' -f1)
    
    echo "1. In Zoiper, try these settings:"
    echo "   - Increase Registration Timeout to 120 seconds"
    echo "   - Set Keep-alive to 30 seconds"
    echo "   - Disable STUN and ICE"
    echo "   - Use server IP directly: $LOCAL_IP"
    echo ""
    echo "2. Check Asterisk configuration:"
    echo "   - Ensure qualify=yes is set for user 1000"
    echo "   - Verify NAT settings are appropriate"
    echo "   - Check if bindaddr=0.0.0.0 (not 127.0.0.1)"
    echo ""
    echo "3. Network troubleshooting:"
    echo "   - Restart Asterisk: sudo systemctl restart asterisk"
    echo "   - Check firewall: sudo ufw status"
    echo "   - Test with different SIP client"
    echo ""
    echo "4. Alternative test:"
    echo "   - Try connecting from another device on same network"
    echo "   - Use SIP client on mobile phone with WiFi"
    echo "   - Test with softphone like Linphone or X-Lite"
}

create_timeout_fix_config() {
    print_info "Creating timeout-optimized SIP configuration..."
    
    cat > asterisk-config/sip.conf.timeout-fix << 'EOF'
[general]
context=default
bindport=5060
bindaddr=0.0.0.0
allowoverlap=no
allowguest=no
disallow=all
allow=ulaw
allow=alaw
allow=gsm
language=en
transport=udp
srvlookup=yes
nat=force_rport,comedia
qualify=yes
qualifyfreq=60
defaultexpiry=120
minexpiry=60
maxexpiry=3600
registertimeout=20
registerattempts=10

; Main customer line with timeout optimizations
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
qualifyfreq=30
insecure=port,invite
defaultexpiry=120
registertimeout=20

; Additional customer lines
[1001]
type=friend
username=1001
secret=1234
host=dynamic
context=default
nat=force_rport,comedia
canreinvite=no
dtmfmode=rfc2833
qualify=yes
qualifyfreq=30
insecure=port,invite
defaultexpiry=120

[1002]
type=friend
username=1002
secret=1234
host=dynamic
context=default
nat=force_rport,comedia
canreinvite=no
dtmfmode=rfc2833
qualify=yes
qualifyfreq=30
insecure=port,invite
defaultexpiry=120
EOF

    print_success "Created timeout-optimized configuration: asterisk-config/sip.conf.timeout-fix"
    print_info "Key timeout improvements:"
    echo "  - Added qualify settings for connection monitoring"
    echo "  - Set appropriate expiry times"
    echo "  - Added registration timeout settings"
    echo "  - Optimized NAT handling"
    echo ""
    print_warning "To apply:"
    echo "  cp asterisk-config/sip.conf.timeout-fix asterisk-config/sip.conf"
    echo "  sudo systemctl restart asterisk"
}

# Main execution
print_header

echo "🔍 Diagnosing SIP 408 Request Timeout Error..."
echo

check_asterisk_status
echo

check_network_connectivity
echo

check_firewall_detailed
echo

test_sip_response
echo

check_asterisk_sip_config
echo

check_zoiper_config
echo

suggest_timeout_fixes
echo

create_timeout_fix_config
echo

print_success "Timeout troubleshooting complete!"
print_info "Try the suggested fixes and test Zoiper registration again."