# 🔧 MANUAL RESTART ARI BOT - Fix OpenAI Session Expired

## 🎯 Issue Identified

The OpenAI Real-time API session has expired (60-minute limit):
```
ERROR: Your session hit the maximum duration of 60 minutes.
WARNING: WebSocket connection closed
```

## 🚀 IMMEDIATE FIX

### Step 1: Stop Current ARI Bot
```bash
# Find and stop ARI bot process
pkill -f "ari_bot.py"

# Or find PID and kill manually
ps aux | grep ari_bot.py
# Then: kill [PID]
```

### Step 2: Start Fresh ARI Bot
```bash
# Start with fresh OpenAI session
python3 ari_bot.py > logs/ari_bot_fresh.log 2>&1 &
```

### Step 3: Monitor Startup
```bash
# Watch for successful startup
tail -f logs/ari_bot_fresh.log
```

**Look for:**
- ✅ "OpenAI Real-time session created"
- ✅ "ready for conversation"
- ✅ "Enhanced Real-time ARI Handler started successfully"

### Step 4: Test Voice Assistant
Once you see "ready for conversation":

1. **Dial 1010** - Simple test
2. **Dial 1000** - Voice assistant

## 🎯 QUICK COMMANDS

```bash
# Stop old ARI bot
pkill -f "ari_bot.py"

# Start fresh ARI bot
python3 ari_bot.py

# In another terminal, test
tail -f logs/ari_bot_fresh.log
```

## ✅ Expected Results

After restart:
- ✅ **Fresh OpenAI session** (no expired errors)
- ✅ **Extension 1010 works** (plays demo)
- ✅ **Extension 1000 works** (AI conversation)
- ✅ **Voice assistant responds** to your speech

## 🚨 If Issues Persist

Check OpenAI API key and quota:
- Verify API key is valid
- Check OpenAI usage limits
- Ensure sufficient credits

## 🎉 SUCCESS INDICATORS

You'll know it's working when:
1. **No session expired errors**
2. **Extension 1000 connects to AI**
3. **Voice conversation flows naturally**
4. **AI responds to your questions**

**Run the commands above to restart with a fresh OpenAI session!** 🚀