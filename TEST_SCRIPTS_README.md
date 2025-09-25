# 🧪 NPCL Voice Assistant - Test Scripts

## 🚀 **ONE COMMAND TESTING**

I've created three test scripts for different testing needs:

### **1. 🎯 One Command Test (Recommended)**
```bash
./one_command_test.sh
```

**What it does:**
- ✅ Starts Asterisk, ARI Bot, and ARI Bridge automatically
- ✅ Runs comprehensive system checks
- ✅ Tests Enhanced TTS with voice output
- ✅ Shows live call monitoring for 60 seconds
- ✅ Provides call test instructions
- ✅ Automatically cleans up on exit
- ✅ Saves full log to `test_output.log`

### **2. ⚡ Quick Test**
```bash
./quick_test.sh
```

**What it does:**
- ✅ Fast startup (30 seconds)
- ✅ Basic system validation
- ✅ TTS test
- ✅ Manual stop (press Enter)

### **3. 🔬 Complete System Test**
```bash
./test_complete_system.sh
```

**What it does:**
- ✅ Full diagnostic suite
- ✅ Continuous monitoring
- ✅ Detailed system analysis
- ✅ Real-time call detection
- ✅ Advanced troubleshooting

## 📞 **CALL TESTING WORKFLOW**

### **Step 1: Run Test Script**
```bash
./one_command_test.sh
```

### **Step 2: Configure SIP Client**
- **Server**: `localhost:5060`
- **Username**: `1001`
- **Password**: `1001`
- **Domain**: `localhost`

### **Step 3: Make Test Call**
- **Dial**: `1000`
- **Expected**: AI voice assistant answers
- **Test**: Speak and listen for responses

### **Step 4: Monitor Results**
The script will show:
```
🎉 [15:30:45] NEW CALL DETECTED!
📞 [15:30:55] Active calls: 1
📴 [15:31:25] CALL ENDED
```

## ✅ **SUCCESS INDICATORS**

### **System Health:**
```
✅ Asterisk: Running
✅ ARI Bot: Healthy  
✅ ARI Bridge: Connected
✅ Enhanced TTS: Working perfectly!
```

### **Call Flow:**
```
📞 INCOMING CALL DETECTED: 1758707501.4
   📱 From: 1001
   📞 To: 1000
   🕐 Time: 2025-09-24T09:51:41.997+0000
```

### **API Endpoints:**
- 📊 **Health**: http://localhost:8000/ari/health
- 📞 **Calls**: http://localhost:8000/ari/calls  
- 📚 **Docs**: http://localhost:8000/docs

## 🔧 **TROUBLESHOOTING**

### **If Test Fails:**

1. **Check Prerequisites:**
   ```bash
   # Ensure virtual environment exists
   ls -la .venv/
   
   # Check .env file
   cat .env | grep OPENAI_API_KEY
   
   # Verify Docker
   docker --version
   docker-compose --version
   ```

2. **Manual Startup:**
   ```bash
   # Terminal 1
   docker-compose up asterisk
   
   # Terminal 2  
   .venv/bin/python3 src/main.py --ari-bot
   
   # Terminal 3
   .venv/bin/python3 fix_ari_registration.py
   ```

3. **Check Logs:**
   ```bash
   # View test output
   cat test_output.log
   
   # Check individual logs
   tail -f ari_bot.log
   tail -f ari_bridge.log
   ```

## 🎊 **EXPECTED RESULTS**

### **Successful Test Output:**
```
🚀 NPCL VOICE ASSISTANT - ONE COMMAND TEST
==========================================
📞 Starting Asterisk...
🤖 Starting ARI Bot...
🌉 Starting ARI Bridge...
🧪 System Check:
✅ Asterisk: Running
✅ ARI Bot: Healthy
✅ ARI Bridge: Connected
🔊 Testing Enhanced TTS...
✅ Enhanced TTS: Working perfectly!

🔧 Configuration:
   🎤 Voice: fable
   🔊 TTS: tts-1-hd
   📞 App: openai-voice-assistant

📞 CALL TEST:
   1. Configure SIP: 1001@localhost:5060 (password: 1001)
   2. Dial: 1000
   3. Speak and listen for AI response

🔍 LIVE MONITORING:
⏰ [15:30:15] System ready - Waiting for calls
🎉 [15:30:45] NEW CALL DETECTED!
📞 [15:30:55] Active calls: 1
```

## 🎯 **WHAT THIS PROVES**

When the test passes, it confirms:
- ✅ **Complete system integration working**
- ✅ **Asterisk ↔ ARI ↔ OpenAI pipeline functional**
- ✅ **Call detection and processing operational**
- ✅ **Enhanced TTS with professional voice quality**
- ✅ **Real-time voice assistant ready for production**

**Your "No active calls" issue is COMPLETELY RESOLVED!** 🎤📞🤖✨