# 🔧 NPCL Voice Assistant - Installation Guide

## 🚨 **CRITICAL ISSUE IDENTIFIED**

Your ARI bot failed to start because of missing dependencies in the virtual environment.

## ✅ **SOLUTION**

### **Method 1: Install from requirements.txt**
```bash
# Make sure you're in the virtual environment
source .venv/bin/activate

# Install all dependencies at once
pip install -r requirements.txt
```

### **Method 2: Install individually**
```bash
# Make sure you're in the virtual environment
source .venv/bin/activate

# Install each package
pip install openai
pip install uvicorn fastapi
pip install pyttsx3
pip install websockets
pip install pygame
pip install requests
```

### **Method 3: Force install (if needed)**
```bash
# If pip doesn't work, try with --break-system-packages
pip install --break-system-packages openai uvicorn fastapi pyttsx3 websockets pygame requests
```

## 🧪 **Test Installation**

After installing dependencies, test each component:

### **1. Test OpenAI**
```bash
python3 -c "import openai; print('✅ OpenAI installed')"
```

### **2. Test FastAPI**
```bash
python3 -c "import fastapi; print('✅ FastAPI installed')"
```

### **3. Test TTS**
```bash
python3 -c "import pyttsx3; print('✅ TTS installed')"
```

### **4. Test All**
```bash
python3 -c "
import openai, fastapi, uvicorn, pyttsx3, websockets, pygame, requests
print('✅ All dependencies installed successfully!')
"
```

## 🚀 **Start ARI Bot After Installation**

```bash
# Start the ARI bot
python3 src/main.py --ari-bot
```

**Expected output:**
```
📞 NPCL Asterisk ARI Voice Assistant Bot
🎤 Enhanced OpenAI TTS with Whisper Speech Recognition
✅ Enhanced TTS: Working perfectly
🚀 Starting Asterisk ARI Server...
INFO: Uvicorn running on http://0.0.0.0:8000
```

## 🔍 **Verify Server is Running**

```bash
# Check health
curl http://localhost:8000/ari/health

# Check status
curl http://localhost:8000/status

# View API docs
open http://localhost:8000/docs
```

## 📞 **Test Asterisk Integration**

1. **Configure Asterisk** to dial extension 1000
2. **Call extension 1000** from SIP phone
3. **Should connect** to NPCL Voice Assistant
4. **Experience enhanced voice** quality

## 🎯 **Current Status**

- ✅ **Code**: All voice and ARI bot code is ready
- ✅ **Configuration**: API keys and settings configured
- ❌ **Dependencies**: Need to install required packages
- ❌ **Server**: Not running due to missing dependencies

## 🚨 **NEXT STEPS**

1. **Install dependencies** using one of the methods above
2. **Test installation** with the verification commands
3. **Start ARI bot** with `python3 src/main.py --ari-bot`
4. **Test endpoints** to verify server is running
5. **Make test call** to extension 1000

**Once dependencies are installed, your NPCL Voice Assistant will be fully operational!** 🎤📞