#!/bin/bash

# ZOIPER Quick Fix Script for NPCL Asterisk ARI Voice Assistant
# Fixes "Wrong password" error in Zoiper SIP registration

echo "🎯 ZOIPER QUICK FIX - Wrong Password Error"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

echo ""
print_info "Your Asterisk logs show: 'Wrong password' for user 1000"
print_success "Good news: Zoiper is connecting correctly, just wrong password!"
echo ""

echo "🎯 SOLUTION 1: Try These Passwords in Zoiper (Keep everything else same)"
echo "======================================================================="
echo ""
echo "In Zoiper, go to Settings → Accounts → [Your Account]"
echo "Keep Domain: 192.168.0.212 and Username: 1000"
echo "But try these passwords ONE BY ONE:"
echo ""
echo "1. Password: secret"
echo "2. Password: demo" 
echo "3. Password: asterisk"
echo "4. Password: 1234"
echo "5. Password: 1000"
echo "6. Password: (leave empty)"
echo ""

echo "🎯 SOLUTION 2: Try Demo Account (Most Likely to Work)"
echo "===================================================="
echo ""
echo "Create NEW account in Zoiper with these settings:"
echo ""
echo "Account name: Asterisk Demo"
echo "Domain: 192.168.0.212"
echo "Username: demo"
echo "Password: demo"
echo "Outbound proxy: 192.168.0.212:5060"
echo "Transport: UDP"
echo "Enable registration: ✓"
echo ""

echo "🎯 SOLUTION 3: Disable Registration (Guest Mode)"
echo "==============================================="
echo ""
echo "In Zoiper:"
echo "1. Settings → Accounts → [Your Account]"
echo "2. Advanced → Registration"
echo "3. UNCHECK 'Enable registration'"
echo "4. Save"
echo "5. Then dial: 1000@192.168.0.212"
echo ""

echo "🧪 TEST EXTENSIONS TO TRY:"
echo "=========================="
echo ""
echo "Once connected, try calling:"
echo "• 1000 - Main NPCL Voice Assistant"
echo "• 1010 - Simple test (no AI)"
echo "• 9000 - Echo test"
echo "• demo - Demo extension"
echo ""

echo "🔍 ZOIPER STATUS INDICATORS:"
echo "============================"
echo ""
echo "Look for these in Zoiper:"
echo "🟢 Green dot = Successfully registered"
echo "🔴 Red dot = Registration failed"
echo "🟡 Yellow dot = Trying to register"
echo ""

echo "🎯 STEP-BY-STEP ZOIPER CONFIGURATION:"
echo "====================================="
echo ""
echo "Method 1 - Quick Setup:"
echo "1. Open Zoiper"
echo "2. Settings → Accounts → Add Account"
echo "3. Choose 'SIP Account'"
echo "4. Enter:"
echo "   Username: demo"
echo "   Password: demo"
echo "   Domain: 192.168.0.212"
echo "5. Let Zoiper auto-configure"
echo "6. Test call to: 1000"
echo ""

echo "Method 2 - Manual Setup:"
echo "1. Settings → Accounts → Manual Configuration"
echo "2. Enter all settings from Solution 2 above"
echo "3. Save and test"
echo ""

echo "🔧 IF STILL NOT WORKING:"
echo "========================"
echo ""
echo "Check what Asterisk actually expects:"
echo ""
echo "sudo asterisk -rx 'sip show users'"
echo "sudo asterisk -rx 'sip show peers'"
echo "sudo asterisk -rx 'sip show peer 1000'"
echo ""

echo "🎯 MOST LIKELY SOLUTION:"
echo "========================"
echo ""
print_success "Try the DEMO account first (Solution 2)"
print_info "Most Asterisk systems have demo/demo configured by default"
echo ""
print_warning "If demo doesn't work, try password 'secret' with username 1000"
echo ""

# Create a quick test to check what users exist
cat > check_asterisk_users.py << 'EOF'
#!/usr/bin/env python3
import subprocess
import sys

def check_asterisk_users():
    """Check what SIP users are configured in Asterisk"""
    print("🔍 Checking Asterisk SIP configuration...")
    
    commands = [
        ("SIP Users", "sudo asterisk -rx 'sip show users'"),
        ("SIP Peers", "sudo asterisk -rx 'sip show peers'"),
        ("PJSIP Endpoints", "sudo asterisk -rx 'pjsip show endpoints'")
    ]
    
    for name, cmd in commands:
        print(f"\n📋 {name}:")
        print("-" * 40)
        try:
            result = subprocess.run(cmd.split(), capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                output = result.stdout.strip()
                if output:
                    print(output)
                else:
                    print("No output")
            else:
                print(f"Error: {result.stderr}")
        except subprocess.TimeoutExpired:
            print("Command timed out")
        except Exception as e:
            print(f"Error running command: {e}")

if __name__ == "__main__":
    check_asterisk_users()
EOF

chmod +x check_asterisk_users.py

print_success "Created user check script: check_asterisk_users.py"
echo ""
echo "Run: python3 check_asterisk_users.py (to see what users exist)"
echo ""
print_success "SUMMARY: Try demo/demo account in Zoiper first!"
echo ""