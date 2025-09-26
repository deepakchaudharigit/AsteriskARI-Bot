# 🔧 Manual Commands to Fix SIP vs PJSIP Issue

## 🎯 Problem Identified

Your Asterisk is using **chan_sip** instead of **PJSIP**, which is why you're getting "Wrong password" errors and calls aren't reaching the voice assistant.

## 🚀 Solution: Run These Commands

### Step 1: Disable chan_sip and Restart Asterisk

```bash
# Stop Asterisk
sudo systemctl stop asterisk

# Wait a moment
sleep 3

# Start Asterisk (will load new modules.conf)
sudo systemctl start asterisk

# Wait for startup
sleep 5
```

### Step 2: Verify PJSIP is Working

```bash
# Check that chan_sip is disabled
sudo asterisk -rx 'module show like chan_sip'
# Should show "Not Loaded" or no results

# Check PJSIP endpoints
sudo asterisk -rx 'pjsip show endpoints'
# Should show: 1000, 1001, agent1, supervisor

# Check Stasis app
sudo asterisk -rx 'stasis show apps'
# Should show: openai-voice-assistant
```

### Step 3: Test with Zoiper

After running the above commands:

1. **Re-register Zoiper** (disconnect and reconnect)
2. **Call 1010** - Should work as before
3. **Call 1000** - Should now connect to voice assistant

## 🎯 Expected Results After Fix

### Before Fix (Current Issue):
```
[NOTICE] Registration from '<sip:1000@192.168.0.212>' failed - Wrong password
```

### After Fix (Expected):
```
- No "Wrong password" errors
- Zoiper shows "Registered" status
- Extension 1000 connects to AI assistant
```

## 🔍 What I Fixed

I updated your `modules.conf` to:
- ✅ **Disable chan_sip** (`noload => chan_sip.so`)
- ✅ **Force PJSIP loading** (explicit load directives)
- ✅ **Load all required ARI modules**

## 📋 Alternative: Quick Test

If you want to test immediately without restarting:

```bash
# Unload chan_sip module
sudo asterisk -rx 'module unload chan_sip.so'

# Reload PJSIP
sudo asterisk -rx 'pjsip reload'

# Check endpoints
sudo asterisk -rx 'pjsip show endpoints'
```

## ✅ Success Indicators

You'll know it's working when:
1. **No "Wrong password" errors** in Asterisk logs
2. **Zoiper shows green "Registered" status**
3. **Extension 1000 connects to AI** instead of playing demo messages
4. **Voice conversation works** with the AI assistant

## 🎯 Root Cause

The issue was that Asterisk was loading both chan_sip and chan_pjsip, but chan_sip was taking precedence. Your Zoiper was connecting via chan_sip (which doesn't have the user 1000 configured), while your voice assistant configuration is in PJSIP.

By disabling chan_sip, all SIP traffic will go through PJSIP, which has your correct configuration with user 1000/password 1234.

**Run the commands above and test again!** 🚀