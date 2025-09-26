# 🎯 ZOIPER PJSIP SOLUTION - Based on Your Actual Configuration

## 🔍 Analysis of Your PJSIP Configuration

Based on your `pjsip.conf` file, I can see the exact accounts configured:

```
Available Accounts:
├── Username: 1000, Password: 1234, Context: openai-voice-assistant
├── Username: 1001, Password: 1234, Context: openai-voice-assistant  
├── Username: agent1, Password: agent123, Context: default
└── Username: supervisor, Password: super123, Context: default
```

## 🎯 CORRECT ZOIPER CONFIGURATION

### **Configuration 1: User 1000 (Main Account)**

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

### **Configuration 2: User 1001 (Test Account)**

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

### **Configuration 3: Agent Account**

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

## 🔧 Why You Were Getting "Wrong Password"

The issue was that your Asterisk is using **PJSIP** (not chan_sip), and the password for user `1000` is `1234`, not the common defaults like "secret" or "demo".

## 🎯 EXACT ZOIPER SETUP STEPS

### Step 1: Configure Account in Zoiper

1. **Open Zoiper**
2. **Settings** → **Accounts** → **Add Account**
3. **Choose "SIP Account"**
4. **Manual Configuration**

### Step 2: Enter These EXACT Settings

```
Basic Settings:
├── Account name: NPCL Voice Assistant
├── Domain: 192.168.0.212
├── Username: 1000
├── Password: 1234
└── Authentication username: 1000

Network Settings:
├── Outbound proxy: 192.168.0.212:5060
├── Transport: UDP
├── STUN: Disabled
└── ICE: Disabled

Advanced Settings:
├── Enable registration: ✓
├── Registration period: 3600
└── Re-registration time: 60
```

### Step 3: Audio Codec Settings

```
Preferred Codecs (in order):
1. PCMU (G.711 μ-law) ✓
2. PCMA (G.711 A-law) ✓
3. GSM ✓
```

## 🧪 Testing Your Configuration

### Test 1: Registration Status

After saving the account, check:
- 🟢 **Green dot** = Successfully registered with PJSIP
- 🔴 **Red dot** = Still having issues

### Test 2: Make Test Calls

Try calling these extensions:

```
Test Extensions:
├── 1000 - Main NPCL Voice Assistant (openai-voice-assistant context)
├── 1001 - Secondary test line
├── agent1 - Agent extension
└── supervisor - Supervisor extension
```

### Test 3: Cross-Account Calling

- Register as **1001** and call **1000**
- Register as **agent1** and call **1000**

## 🔧 PJSIP-Specific Zoiper Settings

### NAT Traversal Settings

```
In Zoiper Advanced Settings:
├── NAT traversal: Enable
├── STUN server: (leave empty for local testing)
├── ICE support: Disable
├── Force rport: Enable
└── Symmetric RTP: Enable
```

### Media Settings

```
Audio Settings:
├── Audio device: Default
├── Echo cancellation: Enable
├── Noise suppression: Enable
└── Automatic gain control: Enable
```

## 🎯 TROUBLESHOOTING PJSIP

### Check PJSIP Status

Run these commands to verify PJSIP configuration:

```bash
# Check PJSIP endpoints
sudo asterisk -rx 'pjsip show endpoints'

# Check PJSIP auths
sudo asterisk -rx 'pjsip show auths'

# Check PJSIP AORs
sudo asterisk -rx 'pjsip show aors'

# Check PJSIP registrations
sudo asterisk -rx 'pjsip show registrations'
```

### Reload PJSIP Configuration

```bash
# Reload PJSIP
sudo asterisk -rx 'pjsip reload'

# Or reload everything
sudo asterisk -rx 'core reload'
```

## 🚨 If Still Having Issues

### Issue 1: Configuration File Not Loaded

Your project `pjsip.conf` might not be loaded by the system Asterisk. Check:

```bash
# See which config file Asterisk is using
sudo asterisk -rx 'pjsip show settings'
```

### Issue 2: Copy Project Config to System

```bash
# Backup current system config
sudo cp /etc/asterisk/pjsip.conf /etc/asterisk/pjsip.conf.backup

# Copy your project config
sudo cp asterisk-config/pjsip.conf /etc/asterisk/pjsip.conf

# Reload PJSIP
sudo asterisk -rx 'pjsip reload'
```

## ✅ SUCCESS INDICATORS

You'll know it's working when:

1. ✅ Zoiper shows **"Registered"** status (green dot)
2. ✅ No more "Wrong password" errors in Asterisk logs
3. ✅ You can call **1000** and hear the NPCL welcome message
4. ✅ Audio flows both ways during the call
5. ✅ You can see the registration in: `sudo asterisk -rx 'pjsip show registrations'`

## 🎯 RECOMMENDED FIRST TRY

**Use this EXACT configuration in Zoiper:**

```
Account name: NPCL Main
Domain: 192.168.0.212
Username: 1000
Password: 1234
Authentication username: 1000
Outbound proxy: 192.168.0.212:5060
Transport: UDP
Enable registration: ✓
```

This should work immediately since it matches your PJSIP configuration exactly!