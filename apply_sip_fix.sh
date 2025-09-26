#!/bin/bash

# Quick SIP 403 Forbidden Fix Script

echo "🔧 Applying SIP Authentication Fix..."
echo "===================================="

# Step 1: Allow SIP port through firewall
echo "1. Opening SIP port 5060 in firewall..."
sudo ufw allow 5060/udp
echo "✅ SIP port allowed through UFW firewall"

# Step 2: Apply improved SIP configuration
echo ""
echo "2. Applying improved SIP configuration..."
cp asterisk-config/sip.conf.fixed asterisk-config/sip.conf
echo "✅ Updated SIP configuration applied"

# Step 3: Restart Asterisk
echo ""
echo "3. Restarting Asterisk service..."
sudo systemctl restart asterisk
sleep 3

# Step 4: Verify Asterisk is running
echo ""
echo "4. Verifying Asterisk status..."
if pgrep -f asterisk > /dev/null; then
    echo "✅ Asterisk is running"
    
    # Check if SIP port is listening
    if ss -tuln | grep -q ":5060"; then
        echo "✅ SIP port 5060 is listening"
    else
        echo "❌ SIP port 5060 is not listening"
    fi
else
    echo "❌ Asterisk is not running"
    echo "Try: sudo systemctl start asterisk"
fi

echo ""
echo "🎯 Zoiper Configuration:"
echo "========================"
echo "Username: 1000"
echo "Password: 1234"
echo "Server: 192.168.0.212"
echo "Port: 5060"
echo "Transport: UDP"
echo "Register: Yes"
echo ""
echo "✅ Fix applied! Try registering Zoiper again."