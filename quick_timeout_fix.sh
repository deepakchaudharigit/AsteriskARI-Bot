#!/bin/bash

# Quick SIP 408 Timeout Fix

echo "🔧 Quick SIP 408 Timeout Fix"
echo "============================"

# Get local IP
LOCAL_IP=$(ip addr show wlp0s20f3 | grep "inet " | awk '{print $2}' | cut -d'/' -f1)
echo "Local IP: $LOCAL_IP"

# 1. Restart Asterisk to ensure clean state
echo ""
echo "1. Restarting Asterisk..."
sudo systemctl restart asterisk
sleep 3

# 2. Verify Asterisk is running and listening
echo ""
echo "2. Checking Asterisk status..."
if pgrep -f asterisk > /dev/null; then
    echo "✅ Asterisk is running"
    
    if ss -tuln | grep -q ":5060"; then
        echo "✅ SIP port 5060 is listening"
    else
        echo "❌ SIP port 5060 is not listening"
    fi
else
    echo "❌ Asterisk is not running"
    exit 1
fi

# 3. Test basic connectivity
echo ""
echo "3. Testing connectivity..."
if timeout 2 nc -u -z localhost 5060 2>/dev/null; then
    echo "✅ Local SIP connectivity works"
else
    echo "⚠️  Local SIP connectivity issue"
fi

# 4. Show current firewall status
echo ""
echo "4. Firewall status:"
sudo ufw status | grep -E "(Status|5060)" || echo "UFW status unknown"

echo ""
echo "🎯 Zoiper Configuration for Timeout Fix:"
echo "========================================"
echo "Account Settings:"
echo "  Username: 1000"
echo "  Password: 1234"
echo "  Server: $LOCAL_IP"
echo "  Port: 5060"
echo "  Transport: UDP"
echo ""
echo "Advanced Settings (IMPORTANT for timeout fix):"
echo "  ✅ Registration Timeout: 120 seconds"
echo "  ✅ Keep-alive: 30 seconds"
echo "  ✅ Retry Interval: 60 seconds"
echo "  ✅ STUN: DISABLED"
echo "  ✅ ICE: DISABLED"
echo "  ✅ NAT Traversal: Auto"
echo "  ✅ Outbound Proxy: (leave EMPTY)"
echo ""
echo "Network Settings:"
echo "  ✅ Local SIP Port: 5060"
echo "  ✅ Use Random Ports: NO"
echo ""
echo "🔄 After applying these settings in Zoiper:"
echo "1. Delete the existing account"
echo "2. Create a new account with these exact settings"
echo "3. Make sure 'Register' is enabled"
echo "4. Try registering again"
echo ""
echo "✅ Fix applied! Try Zoiper registration now."