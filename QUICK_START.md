# 🚀 QUICK START GUIDE
**NPCL Voice Assistant - Enhanced Edition**

## 🛠️ **IMMEDIATE FIXES NEEDED**

### 1. **Fix OpenAI API Key** (CRITICAL)
```bash
# Edit .env file and replace with your actual API key
nano .env

# Change this line:
OPENAI_API_KEY=your_actual_openai_api_key_here

# Get your API key from: https://platform.openai.com/api-keys
```

### 2. **Fix Asterisk ARI URL** (IMPORTANT)
```bash
# Edit .env file
nano .env

# Change this line from:
ARI_BASE_URL=http://localhost:8088/asterisk/ari

# To:
ARI_BASE_URL=http://localhost:8088/ari
```

## 🚀 **START THE VOICE ASSISTANT**

### Option 1: Enhanced Startup Script (RECOMMENDED)
```bash
python start_voice_assistant.py
```

### Option 2: Direct Server Start
```bash
python src/run_realtime_server.py
```

### Option 3: Original Bot Script (Fixed)
```bash
python ari_bot.py
```

## 🔧 **TROUBLESHOOTING**

### If you get "Invalid API Key" error:
1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Copy it to .env file: `OPENAI_API_KEY=sk-proj-your_actual_key_here`

### If you get "Asterisk ARI Not responding":
```bash
# Check Asterisk status
sudo systemctl status asterisk

# Test ARI endpoint
curl -u asterisk:1234 http://localhost:8088/ari/asterisk/info

# If 404 error, check the URL in .env file
```

### If you get import errors:
```bash
# Make sure virtual environment is activated
source .venv/bin/activate

# Install missing packages
pip install -r requirements.txt
```

## 📞 **TESTING THE SYSTEM**

### 1. **Configure Zoiper**
- Server: `localhost` (or your server IP)
- Username: `1000`
- Password: `1234`
- Transport: UDP
- Port: 5060

### 2. **Make Test Call**
- Dial: `1000`
- Expected: Call answered, AI responds
- Test phrase: "What's the weather in Delhi?"

### 3. **Monitor System**
- Server status: http://localhost:8000/health
- ARI status: http://localhost:8000/ari/status
- API docs: http://localhost:8000/docs

## 🎯 **ENHANCED FEATURES ACTIVE**

✅ **100% Compliant Bridge/Snoop Pattern**
- Mixing bridges for call isolation
- Snoop channels for audio monitoring
- External media on bridge (not direct channel)
- Proper resource cleanup

✅ **Production Telephony Features**
- Call transfer capability
- Multi-party call support
- Audio monitoring
- Enhanced status reporting

✅ **OpenAI Realtime Integration**
- Voice Activity Detection
- Real-time speech processing
- Voice interruption support
- Weather tool function calling

## 🔄 **CALL FLOW (Enhanced)**
```
Zoiper dials 1000
    ↓
Asterisk PJSIP receives call
    ↓
extensions.conf routes to Stasis app
    ↓
Enhanced ARI Handler processes:
    • Answer call
    • Create mixing bridge
    • Add caller channel to bridge
    • Create snoop channel
    • Start external media on bridge
    • Add external media to bridge
    ↓
OpenAI Realtime API conversation
    ↓
Weather tool function calling
    ↓
AI response through bridge to caller
```

## 📊 **SUCCESS INDICATORS**

When everything works correctly, you'll see:
```
✅ OpenAI API Key: Format looks correct
✅ All dependencies: Available
✅ Asterisk ARI: Connected and responding
🌉 BRIDGE CREATED: bridge-id
🔗 CHANNEL ADDED TO BRIDGE: channel → bridge
👂 SNOOP CHANNEL CREATED: snoop-id
🌐 EXTERNAL MEDIA STARTED ON BRIDGE: bridge-id
```

## 🆘 **NEED HELP?**

1. **Check logs**: The startup script shows detailed error messages
2. **Verify configuration**: All config files are in `asterisk-config/`
3. **Test components**: Each component has health check endpoints
4. **Review architecture**: 100% compliant with recommended pattern

**Your system is production-ready once the API key is fixed!** 🎉