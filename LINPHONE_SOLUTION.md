# 🎯 DEFINITIVE SOLUTION: Linphone "Wrong Password" Fix

## 🔍 Problem Analysis

Based on your Asterisk logs, the issue is clear:
```
Registration from '<sip:1000@192.168.0.212:5060;transport=UDP>' failed for '192.168.0.212:38720' - Wrong password
```

**Good News:** 
- ✅ Asterisk is running and receiving SIP requests
- ✅ Linphone is connecting to the correct server
- ✅ Network connectivity is working
- ❌ Only the password is wrong

## 🎯 IMMEDIATE SOLUTIONS (Try in Order)

### Solution 1: Try Common Asterisk Passwords

Keep your current Linphone settings but try these passwords **one by one**:

```
Configuration: Keep everything the same, just change password
Domain: 192.168.0.212
Username: 1000
Password: Try these in order:
  1. secret
  2. asterisk  
  3. 1234
  4. 1000
  5. (empty/blank)
```

### Solution 2: Use Default Asterisk Account

Many Asterisk installations have a default demo account:

```
Username: demo
Password: demo
Domain: 192.168.0.212
```

### Solution 3: Try Guest Access (No Registration)

```
In Linphone:
- Disable "Register" option
- Just dial directly: 1000@192.168.0.212
```

## 🔧 Advanced Solutions

### Solution 4: Check What Asterisk Actually Expects

Run these commands to see the real configuration:

```bash
# Check SIP peers (shows configured users)
sudo asterisk -rx 'sip show peers'

# Check specific user 1000
sudo asterisk -rx 'sip show peer 1000'

# Check if user exists
sudo asterisk -rx 'sip show users'
```

### Solution 5: Use PJSIP Instead

Your system might be configured for PJSIP instead of chan_sip:

```bash
# Check PJSIP endpoints
sudo asterisk -rx 'pjsip show endpoints'

# Check PJSIP auths
sudo asterisk -rx 'pjsip show auths'
```

## 🎯 Most Likely Working Configuration

Based on standard Asterisk setups, try this **EXACT** configuration:

```
Linphone Account Settings:
├── Display Name: Asterisk User
├── SIP Address: sip:demo@192.168.0.212
├── Username: demo
├── Password: demo
├── Domain: 192.168.0.212
├── Proxy: sip:192.168.0.212:5060
├── Transport: UDP
└── Register: Yes
```

## 🚀 Alternative: Use Your Project Configuration

Since Asterisk is using system files, let's make it use your project files:

### Option A: Copy Your Config to System

```bash
# Backup current config
sudo cp /etc/asterisk/sip.conf /etc/asterisk/sip.conf.backup

# Copy your project config
sudo cp asterisk-config/sip.conf /etc/asterisk/sip.conf

# Reload Asterisk
sudo asterisk -rx 'sip reload'
```

### Option B: Start Asterisk with Your Config

```bash
# Stop system Asterisk
sudo systemctl stop asterisk

# Start Asterisk with your config directory
sudo asterisk -C asterisk-config/asterisk.conf -f
```

## 🧪 Quick Test Methods

### Method 1: Try Without Registration

```
In Linphone:
1. Go to Account Settings
2. Uncheck "Register"
3. Save
4. Try calling: 1000@192.168.0.212
```

### Method 2: Use SIP URI Dialing

```
In Linphone dialer, enter:
sip:1000@192.168.0.212:5060
```

### Method 3: Test with Command Line

```bash
# Install SIP testing tool
sudo apt install sipgrep

# Monitor SIP traffic
sudo sipgrep -i any port 5060
```

## 🎯 FINAL RECOMMENDATION

**Try this configuration first (most likely to work):**

```
Account Settings:
├── Username: demo
├── Password: demo
├── Domain: 192.168.0.212
├── Proxy: sip:192.168.0.212:5060
├── Transport: UDP
└── Register: Yes
```

**If that fails, try:**

```
Account Settings:
├── Username: 1000
├── Password: secret
├── Domain: 192.168.0.212
├── Proxy: sip:192.168.0.212:5060
├── Transport: UDP
└── Register: Yes
```

**If still failing:**

```
Account Settings:
├── Username: 1000
├── Password: (empty)
├── Domain: 192.168.0.212
├── Register: No
└── Just dial: 1000@192.168.0.212
```

## 🔍 Debugging Commands

If none of the above work, run these to diagnose:

```bash
# Check what SIP users exist
sudo asterisk -rx 'sip show users'

# Check SIP configuration
sudo asterisk -rx 'sip show settings'

# Check if modules are loaded
sudo asterisk -rx 'module show like chan_sip'

# Reload everything
sudo asterisk -rx 'core reload'
```

## ✅ Success Indicators

You'll know it's working when:
1. ✅ Linphone shows "Registered" status (green)
2. ✅ No more "Wrong password" errors in Asterisk logs
3. ✅ You can dial 1000 and hear audio

The key is that **Asterisk is working perfectly** - it's just a password/user configuration mismatch that's easy to fix!