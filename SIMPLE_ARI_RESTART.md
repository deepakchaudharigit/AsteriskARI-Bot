# 🚀 SIMPLE ARI BOT RESTART

## 🎯 Issue
Stasis application not registered even though ARI authentication works.

## 🔧 SIMPLE RESTART STEPS

### Step 1: Stop Current ARI Bot
```bash
# Find and stop ARI bot process
pkill -f "ari_bot.py"

# Or find PID manually:
ps aux | grep ari_bot.py
# Then: kill [PID]
```

### Step 2: Clean Start
```bash
# Wait 5 seconds for cleanup
sleep 5

# Start ARI bot fresh
python3 ari_bot.py
```

### Step 3: Monitor Startup
**Watch for these messages:**
- ✅ "Connected to OpenAI Real-time API successfully"
- ✅ "Enhanced Real-time ARI Handler started successfully"
- ✅ "ready for conversation"

### Step 4: Check Stasis Registration
**After seeing "ready for conversation":**
```bash
# In another terminal
sudo asterisk -rx 'ari show apps'
```
**Should show:** `openai-voice-assistant`

### Step 5: Test Voice Assistant
**Dial 1000 in Zoiper**

## 🔍 TROUBLESHOOTING

### If Stasis Still Not Registered:
1. **Check ARI bot logs for errors:**
   ```bash
   tail -20 logs/ari_bot_final.log
   ```

2. **Check if ARI bot is connecting to Asterisk:**
   Look for connection messages in startup

3. **Verify ARI configuration:**
   ```bash
   sudo cat /etc/asterisk/ari.conf | grep -A5 "\[asterisk\]"
   ```

### If ARI Bot Won't Start:
1. **Check for port conflicts:**
   ```bash
   lsof -ti:8000
   lsof -ti:8090
   ```

2. **Check OpenAI API key:**
   Verify .env file has valid OPENAI_API_KEY

## 🎯 SUCCESS INDICATORS

You'll know it's working when:
1. ✅ **ARI bot starts without errors**
2. ✅ **"ready for conversation" appears**
3. ✅ **`ari show apps` shows openai-voice-assistant**
4. ✅ **Extension 1000 transfers to AI**

## 🚀 QUICK COMMANDS

```bash
# Stop ARI bot
pkill -f "ari_bot.py"

# Wait and restart
sleep 5
python3 ari_bot.py

# In another terminal, after "ready for conversation":
sudo asterisk -rx 'ari show apps'

# Test: dial 1000 in Zoiper
```

**Try the simple restart commands above!** 🚀