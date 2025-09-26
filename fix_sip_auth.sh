#!/bin/bash

# SIP Authentication Troubleshooting Script
# This script helps diagnose and fix SIP 403 Forbidden errors

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}🔧 SIP Authentication Troubleshooting${NC}"
    echo -e "${BLUE}=====================================${NC}"
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
        ASTERISK_PID=$(pgrep -f asterisk)
        print_success "Asterisk is running (PID: $ASTERISK_PID)"
    else
        print_error "Asterisk is not running"
        return 1
    fi
}

check_sip_port() {
    print_info "Checking SIP port 5060..."
    
    if ss -tuln | grep -q ":5060"; then
        print_success "SIP port 5060 is listening"
        ss -tuln | grep ":5060"
    else
        print_error "SIP port 5060 is not listening"
        return 1
    fi
}

check_network() {
    print_info "Checking network configuration..."
    
    LOCAL_IP=$(ip addr show wlp0s20f3 | grep "inet " | awk '{print $2}' | cut -d'/' -f1)
    print_success "Local IP: $LOCAL_IP"
    
    # Test connectivity to localhost
    if nc -z -u localhost 5060 2>/dev/null; then
        print_success "Can connect to SIP port locally"
    else
        print_warning "Cannot connect to SIP port locally"
    fi
}

show_sip_config() {
    print_info "Current SIP configuration for user 1000:"
    echo "----------------------------------------"
    if [ -f "asterisk-config/sip.conf" ]; then
        grep -A 10 "\[1000\]" asterisk-config/sip.conf
    else
        print_error "SIP configuration file not found"
    fi
    echo "----------------------------------------"
}

suggest_zoiper_config() {
    print_info "Recommended Zoiper 5 Configuration:"
    echo "===================================="
    
    LOCAL_IP=$(ip addr show wlp0s20f3 | grep "inet " | awk '{print $2}' | cut -d'/' -f1)
    
    echo "Account Settings:"
    echo "  Account Name: Asterisk Test"
    echo "  Username: 1000"
    echo "  Password: 1234"
    echo "  Domain/Server: $LOCAL_IP"
    echo "  Port: 5060"
    echo "  Transport: UDP"
    echo ""
    echo "Advanced Settings:"
    echo "  Authentication Username: 1000"
    echo "  Outbound Proxy: (leave empty)"
    echo "  STUN Server: (disable)"
    echo "  NAT Traversal: Auto"
    echo "  Register: Yes"
    echo ""
    echo "Codec Settings:"
    echo "  Preferred: ulaw, alaw, gsm"
    echo "  DTMF: RFC2833"
}

test_sip_registration() {
    print_info "Testing SIP registration with sipsak (if available)..."
    
    if command -v sipsak &> /dev/null; then
        LOCAL_IP=$(ip addr show wlp0s20f3 | grep "inet " | awk '{print $2}' | cut -d'/' -f1)
        echo "Testing registration to sip:1000@$LOCAL_IP..."
        # Note: This is just a basic test, actual registration requires proper SIP client
        print_info "Use Zoiper for actual registration testing"
    else
        print_warning "sipsak not available for testing"
        print_info "Install with: sudo apt install sipsak"
    fi
}

check_firewall() {
    print_info "Checking firewall status..."
    
    if command -v ufw &> /dev/null; then
        UFW_STATUS=$(sudo ufw status 2>/dev/null || echo "inactive")
        if [[ "$UFW_STATUS" == *"active"* ]]; then
            print_warning "UFW firewall is active"
            print_info "You may need to allow SIP port: sudo ufw allow 5060/udp"
        else
            print_success "UFW firewall is inactive"
        fi
    fi
    
    if command -v iptables &> /dev/null; then
        IPTABLES_RULES=$(sudo iptables -L INPUT 2>/dev/null | wc -l)
        if [ "$IPTABLES_RULES" -gt 3 ]; then
            print_warning "iptables rules detected"
            print_info "Check if port 5060/udp is allowed"
        else
            print_success "No restrictive iptables rules found"
        fi
    fi
}

show_asterisk_logs() {
    print_info "Recent Asterisk logs (last 20 lines):"
    echo "======================================"
    
    if [ -f "/var/log/asterisk/messages" ]; then
        sudo tail -20 /var/log/asterisk/messages 2>/dev/null || print_warning "Cannot read Asterisk logs"
    elif [ -f "/var/log/asterisk/full" ]; then
        sudo tail -20 /var/log/asterisk/full 2>/dev/null || print_warning "Cannot read Asterisk logs"
    else
        print_warning "Asterisk log files not found in standard locations"
    fi
}

create_fixed_sip_config() {
    print_info "Creating updated SIP configuration..."
    
    cat > asterisk-config/sip.conf.new << 'EOF'
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

; Main customer line
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
insecure=port,invite

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
insecure=port,invite

; Agent endpoints
[agent1]
type=friend
username=agent1
secret=agent123
host=dynamic
context=default
nat=force_rport,comedia
canreinvite=no
dtmfmode=rfc2833
qualify=yes
insecure=port,invite

[supervisor]
type=friend
username=supervisor
secret=super123
host=dynamic
context=default
nat=force_rport,comedia
canreinvite=no
dtmfmode=rfc2833
qualify=yes
insecure=port,invite
EOF

    print_success "Created updated SIP configuration: asterisk-config/sip.conf.new"
    print_info "Key changes made:"
    echo "  - Added nat=force_rport,comedia for better NAT handling"
    echo "  - Added insecure=port,invite to allow authentication flexibility"
    echo "  - Updated general NAT settings"
    echo ""
    print_warning "To apply changes:"
    echo "  1. cp asterisk-config/sip.conf.new asterisk-config/sip.conf"
    echo "  2. sudo systemctl reload asterisk"
    echo "  3. Or restart Asterisk: sudo systemctl restart asterisk"
}

# Main execution
print_header

echo "🔍 Diagnosing SIP 403 Forbidden Error..."
echo

check_asterisk_status
echo

check_sip_port
echo

check_network
echo

show_sip_config
echo

suggest_zoiper_config
echo

check_firewall
echo

test_sip_registration
echo

create_fixed_sip_config
echo

print_info "🎯 Quick Fix Steps:"
echo "1. Apply the new SIP configuration:"
echo "   cp asterisk-config/sip.conf.new asterisk-config/sip.conf"
echo ""
echo "2. Restart Asterisk:"
echo "   sudo systemctl restart asterisk"
echo ""
echo "3. In Zoiper, configure:"
echo "   - Username: 1000"
echo "   - Password: 1234"
echo "   - Server: $(ip addr show wlp0s20f3 | grep "inet " | awk '{print $2}' | cut -d'/' -f1')"
echo "   - Port: 5060"
echo "   - Transport: UDP"
echo ""
echo "4. Enable 'Register' in Zoiper account settings"
echo ""
print_success "Run this script again after applying changes to verify the fix!"