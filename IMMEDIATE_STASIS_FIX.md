# 🚀 IMMEDIATE FIX: Stasis Transfer Issue

## 🎯 Problem Identified

Your call flow is:
1. ✅ Zoiper dials 1000 → connects
2. ✅ Plays welcome message for 32 seconds
3. ❌ **Stasis transfer FAILS** → call disconnects
4. ❌ **No Stasis events in ARI bot logs**

## 🔧 IMMEDIATE DIAGNOSTIC COMMANDS

Run these commands to identify the exact issue:

### Check 1: Stasis App Registration
```bash
sudo asterisk -rx 'ari show apps'
```
**Expected:** Should show `openai-voice-assistant`
**If empty:** Stasis app not registered (main issue)

### Check 2: ARI Connection Test
```bash
curl http://localhost:8088/ari/asterisk/info -u asterisk:1234
```
**Expected:** JSON response with Asterisk info
**If fails:** ARI authentication/connectivity issue

### Check 3: Extension Configuration
```bash
sudo asterisk -rx 'dialplan show 1000@demo'
```
**Expected:** Should show the Stasis line
**Check:** Verify Stasis application name is correct

## 🚀 QUICK FIXES (Try in Order)

### Fix 1: Restart ARI Bot (Most Likely Fix)
```bash
# In the terminal running ARI bot, press Ctrl+C to stop
# Wait 5 seconds
# Restart:
python3 ari_bot.py
# Wait for "ready for conversation"
# Test dial 1000
```

### Fix 2: Simplify Stasis Call
```bash
sudo nano /etc/asterisk/extensions.conf
```
**Find the line:**
```
same => n,Stasis(openai-voice-assistant,${CALLERID(num)},${EXTEN})
```
**Change to:**
```
same => n,Stasis(openai-voice-assistant)
```
**Save and reload:**
```bash
sudo asterisk -rx 'dialplan reload'
```

### Fix 3: Test ARI Connection
```bash
# Check if ARI bot can connect to Asterisk
curl http://localhost:8000/ari/status
```

## 🧪 TEST WITH MONITORING

### Monitor Both Logs During Call:

**Terminal 1 - ARI Bot Logs:**
```bash
tail -f logs/ari_bot_final.log
```

**Terminal 2 - Asterisk Logs:**
```bash
sudo tail -f /var/log/asterisk/messages
```

**Terminal 3 - Make Call:**
Dial 1000 in Zoiper and watch both logs

## ✅ Success Indicators

You'll know it's working when:
- **ARI bot logs show:** "Stasis application started"
- **Asterisk logs show:** Successful Stasis transfer
- **Call doesn't disconnect** after welcome message
- **AI conversation begins**

## 🎯 Most Likely Solution

Based on the diagnostic, the **ARI bot is not properly registering the Stasis application**. 

**Try Fix 1 first** (restart ARI bot) - this usually resolves the issue.

## 📞 Expected Flow After Fix

1. ✅ Dial 1000
2. ✅ Welcome message plays
3. ✅ **Stasis transfer succeeds**
4. ✅ **ARI bot receives call**
5. ✅ **AI conversation begins**

**Run the diagnostic commands above to identify the exact issue!** 🚀