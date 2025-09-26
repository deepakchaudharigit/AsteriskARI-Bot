# 🎯 FINAL ZOIPER SOLUTION - Based on Your PJSIP Configuration

## 🔍 Root Cause Analysis

Based on your `pjsip.conf` file and the "Wrong password" errors, here's what's happening:

1. ✅ **Your Asterisk is using PJSIP** (not chan_sip)
2. ✅ **Your project has the correct configuration** in `asterisk-config/pjsip.conf`
3. ❌ **System Asterisk might be using different config** in `/etc/asterisk/pjsip.conf`
4. ✅ **Zoiper is connecting correctly** but password doesn't match

## 🎯 EXACT ZOIPER CONFIGURATION

Based on your `pjsip.conf`, use these **EXACT** settings in Zoiper:

### **Primary Account (User 1000)**

```
Zoiper Account Settings:
├── Account name: NPCL User 1000
├── Domain: 192.168.0.212
├── Username: 1000
├── Password: 1234
├── Authentication username: 1000
├── Outbound proxy: 192.168.0.212:5060
├── Transport: UDP
└── Enable registration: ✓
```

### **Secondary Account (User 1001)**

```
Zoiper Account Settings:
├── Account name: NPCL User 1001
├── Domain: 192.168.0.212
├── Username: 1001
├── Password: 1234
├── Authentication username: 1001
├── Outbound proxy: 192.168.0.212:5060
├── Transport: UDP
└── Enable registration: ✓
```

### **Agent Account**

```
Zoiper Account Settings:
├── Account name: NPCL Agent
├── Domain: 192.168.0.212
├── Username: agent1
├── Password: agent123
├── Authentication username: agent1
├── Outbound proxy: 192.168.0.212:5060
├── Transport: UDP
└── Enable registration: ✓
```

## 🔧 Step-by-Step Zoiper Setup

### Step 1: Open Zoiper Configuration

1. **Open Zoiper**
2. **Settings** → **Accounts** → **Add Account**
3. **Choose "SIP Account"**
4. **Select "Manual Configuration"**

### Step 2: Enter Basic Settings

```
Account Information:
├── Account name: NPCL Voice Assistant
├── Domain: 192.168.0.212
├── Username: 1000
├── Password: 1234
└── Authentication username: 1000
```

### Step 3: Configure Network Settings

```
Network Settings:
├── Outbound proxy: 192.168.0.212:5060
├── Transport: UDP
├── STUN: Disabled
├── ICE: Disabled
└── Enable registration: ✓
```

### Step 4: Audio Codec Settings

```
Audio Codecs (enable in this order):
1. ✓ PCMU (G.711 μ-law)
2. ✓ PCMA (G.711 A-law)
3. ✓ GSM
4. ✗ Disable all others
```

### Step 5: Advanced Settings

```
Advanced Settings:
├── NAT traversal: Enable
├── Force rport: Enable
├── Symmetric RTP: Enable
├── Registration period: 3600
└── Re-registration time: 60
```

## 🚨 If Configuration Still Doesn't Work

The issue might be that your system Asterisk is not using your project configuration. Here's how to fix it:

### Option 1: Copy Your Config to System

```bash
# Backup current system config
sudo cp /etc/asterisk/pjsip.conf /etc/asterisk/pjsip.conf.backup

# Copy your project config to system
sudo cp asterisk-config/pjsip.conf /etc/asterisk/pjsip.conf

# Reload PJSIP configuration
sudo asterisk -rx 'pjsip reload'
```

### Option 2: Start Asterisk with Your Config

```bash
# Stop system Asterisk
sudo systemctl stop asterisk

# Start Asterisk with your project config
cd /home/ameen/AsteriskARI-Bot
sudo asterisk -C asterisk-config/asterisk.conf -f
```

### Option 3: Use Docker Setup

```bash
# Use your Docker setup which uses project configs
docker-compose up -d
```

## 🧪 Testing Your Configuration

### Test 1: Check Registration Status

After configuring Zoiper:
- 🟢 **Green dot** = Successfully registered
- 🔴 **Red dot** = Registration failed
- 🟡 **Yellow dot** = Trying to register

### Test 2: Make Test Calls

Try calling these extensions:

```
Available Extensions:
├── 1000 - Main NPCL Voice Assistant
├── 1010 - Simple codec test (no AI)
├── 9000 - Echo test
└── 1005 - IVR menu
```

### Test 3: Cross-Account Testing

- Register as **1001** and call **1000**
- Register as **agent1** and call **1000**

## 🔍 Verification Commands

To verify your configuration is working:

```bash
# Check PJSIP endpoints
sudo asterisk -rx 'pjsip show endpoints'

# Check PJSIP registrations
sudo asterisk -rx 'pjsip show registrations'

# Check PJSIP authentication
sudo asterisk -rx 'pjsip show auths'
```

## ✅ Success Indicators

You'll know it's working when:

1. ✅ **Zoiper shows "Registered" status** (green dot)
2. ✅ **No "Wrong password" errors** in Asterisk logs
3. ✅ **You can call 1000** and hear the NPCL welcome message
4. ✅ **Audio flows both ways** during the call
5. ✅ **Registration appears** in `pjsip show registrations`

## 🎯 MOST LIKELY SOLUTION

**Try this configuration first:**

```
Domain: 192.168.0.212
Username: 1000
Password: 1234
Outbound proxy: 192.168.0.212:5060
Transport: UDP
```

**If that fails, the issue is that your system Asterisk is not using your project `pjsip.conf` file.** In that case, use Option 1 above to copy your configuration to the system location.

## 🚀 Quick Test

After setting up Zoiper:
1. **Check for green registration status**
2. **Dial: 1000**
3. **Should hear: NPCL welcome message**
4. **Test voice interaction with the AI assistant**

Your configuration is correct - it's just a matter of ensuring Asterisk is using the right config file!