# 🎯 ZOIPER SOLUTION: Fix "Wrong Password" Error

## 🔍 Problem Analysis

Your Asterisk logs show:
```
Registration from '<sip:1000@192.168.0.212:5060;transport=UDP>' failed for '192.168.0.212:38720' - Wrong password
```

**Good News:** 
- ✅ Asterisk is running and receiving SIP requests from Zoiper
- ✅ Zoiper is connecting to the correct server (192.168.0.212:5060)
- ✅ Network connectivity is working perfectly
- ❌ Only the password is wrong

## 🎯 IMMEDIATE ZOIPER FIXES (Try in Order)

### Solution 1: Try Common Asterisk Passwords

Keep your current Zoiper settings but try these passwords **one by one**:

```
Zoiper Account Settings:
├── Account name: NPCL Test
├── Domain: 192.168.0.212
├── Username: 1000
└── Password: Try these in order:
    1. secret
    2. asterisk  
    3. demo
    4. 1234
    5. 1000
    6. (leave empty)
```

### Solution 2: Try Default Demo Account

Many Asterisk installations have a default demo account:

```
Zoiper Configuration:
├── Account name: Asterisk Demo
├── Domain: 192.168.0.212
├── Username: demo
├── Password: demo
├── Outbound proxy: 192.168.0.212:5060
└── Transport: UDP
```

### Solution 3: Disable Registration (Guest Mode)

```
In Zoiper:
1. Go to Settings → Accounts → [Your Account]
2. Advanced → Registration
3. Uncheck "Enable registration"
4. Save
5. Then dial: 1000@192.168.0.212
```

## 🔧 Zoiper-Specific Configuration Steps

### Step 1: Check Current Zoiper Settings

In Zoiper:
1. Go to **Settings** → **Accounts**
2. Select your current account
3. Verify these settings:

```
Basic Settings:
├── Account name: [Any name]
├── Domain: 192.168.0.212
├── Username: 1000
├── Password: [Try the passwords above]
└── Authentication username: 1000
```

### Step 2: Advanced Settings

```
Network Settings:
├── Outbound proxy: 192.168.0.212:5060
├── Transport: UDP
├── STUN: Disabled
└── ICE: Disabled

Registration:
├── Enable registration: ✓ (checked)
├── Registration period: 3600
└── Re-registration time: 60
```

### Step 3: Audio Settings

```
Codecs (in order of preference):
1. PCMU (G.711 μ-law)
2. PCMA (G.711 A-law)
3. GSM
```

## 🎯 Most Likely Working Configurations

### Configuration 1: Demo Account (Try First)

```
Zoiper Settings:
├── Account name: Asterisk Demo
├── Domain: 192.168.0.212
├── Username: demo
├── Password: demo
├── Outbound proxy: 192.168.0.212:5060
├── Transport: UDP
└── Enable registration: ✓
```

### Configuration 2: User 1000 with Secret

```
Zoiper Settings:
├── Account name: NPCL User 1000
├── Domain: 192.168.0.212
├── Username: 1000
├── Password: secret
├── Outbound proxy: 192.168.0.212:5060
├── Transport: UDP
└── Enable registration: ✓
```

### Configuration 3: Guest Mode (No Registration)

```
Zoiper Settings:
├── Account name: NPCL Guest
├── Domain: 192.168.0.212
├── Username: 1000
├── Password: (empty)
├── Outbound proxy: 192.168.0.212:5060
├── Transport: UDP
└── Enable registration: ✗ (unchecked)
```

## 🧪 Zoiper Testing Steps

### Test 1: Registration Status

1. Open Zoiper
2. Check the account status indicator
3. Look for:
   - 🟢 Green = Registered successfully
   - 🔴 Red = Registration failed
   - 🟡 Yellow = Trying to register

### Test 2: Make Test Calls

Once registered (or in guest mode), try calling:

```
Test Extensions:
├── 1000 - Main NPCL Voice Assistant
├── 1010 - Simple codec test (no AI)
├── 9000 - Echo test
└── demo - Demo extension (if available)
```

### Test 3: Direct SIP URI Dialing

In Zoiper dialer, try:
```
sip:1000@192.168.0.212
sip:demo@192.168.0.212
sip:echo@192.168.0.212
```

## 🔧 Zoiper Troubleshooting

### Check Zoiper Logs

1. In Zoiper: **Settings** → **Advanced** → **Logs**
2. Enable **SIP logs**
3. Try to register
4. Check logs for authentication details

### Common Zoiper Issues

1. **Firewall**: Ensure UDP port 5060 is open
2. **NAT**: Enable NAT traversal in Zoiper
3. **Codecs**: Ensure ulaw/alaw are enabled
4. **Transport**: Use UDP (not TCP/TLS for basic setup)

## 🎯 QUICK ZOIPER SETUP GUIDE

### Method 1: Auto-Configuration

1. Open Zoiper
2. **Add Account** → **SIP Account**
3. Enter:
   ```
   Username: demo
   Password: demo
   Domain: 192.168.0.212
   ```
4. Let Zoiper auto-configure
5. Test call to: **1000**

### Method 2: Manual Configuration

1. **Settings** → **Accounts** → **Add Account**
2. **Manual Configuration**
3. Enter the settings from Configuration 1 above
4. **Save** and test

## ✅ Success Indicators

You'll know it's working when:

1. ✅ Zoiper shows **"Registered"** status
2. ✅ No more "Wrong password" errors in Asterisk logs  
3. ✅ You can dial **1000** and hear the welcome message
4. ✅ Audio flows both ways during the call

## 🚨 If Still Not Working

Run these commands to check what Asterisk expects:

```bash
# Check SIP users
sudo asterisk -rx 'sip show users'

# Check SIP peers  
sudo asterisk -rx 'sip show peers'

# Check specific user
sudo asterisk -rx 'sip show peer 1000'
```

## 🎯 RECOMMENDED FIRST TRY

**Use this exact configuration in Zoiper:**

```
Account name: Asterisk Demo
Domain: 192.168.0.212  
Username: demo
Password: demo
Outbound proxy: 192.168.0.212:5060
Transport: UDP
Enable registration: ✓
```

This is the most likely to work since most Asterisk installations have a default demo account configured!