# 📞 Asterisk CLI Commands & Diagnostics

## 🚨 **Issues Identified from Your CLI Output**

From your Asterisk CLI connection, I can see two important issues:

1. **❌ Stasis App Not Registered**: `Stasis app 'openai-voice-assistant' not registered`
2. **⚠️ Missing AGI Script**: `call-data-logger.py: File does not exist`

## 🔍 **Essential Asterisk CLI Commands**

### **Current Status Commands:**
```bash
# Check active calls
core show calls

# Show SIP endpoints
pjsip show endpoints

# Show SIP registrations
pjsip show registrations

# Show channels
core show channels

# Show dialplan
dialplan show

# Show Stasis applications
stasis show apps

# Show system info
core show version
core show uptime
```

### **SIP Diagnostics:**
```bash
# Check if endpoint 1001 is configured
pjsip show endpoint 1001

# Check if endpoint 1000 is configured  
pjsip show endpoint 1000

# Show all AORs (Address of Records)
pjsip show aors

# Show authentication
pjsip show auths

# Show transports
pjsip show transports
```

### **Call Flow Diagnostics:**
```bash
# Show dialplan for extension 1000
dialplan show 1000

# Show dialplan for context openai-voice-assistant
dialplan show openai-voice-assistant

# Check if Stasis app is loaded
module show like stasis

# Show ARI configuration
ari show status
```

## 🔧 **Troubleshooting Commands**

### **Configuration Reload:**
```bash
# Reload dialplan
dialplan reload

# Reload PJSIP configuration
pjsip reload

# Reload ARI configuration
ari reload

# Full configuration reload
core reload
```

### **Module Management:**
```bash
# Check if required modules are loaded
module show like res_stasis
module show like res_ari
module show like app_stasis

# Load missing modules if needed
module load res_stasis.so
module load res_ari.so
module load app_stasis.so
```

## 🎯 **Immediate Diagnostic Steps**

### **Step 1: Check SIP Configuration**
```bash
pjsip show endpoints
```
**Expected Output:** Should show endpoints 1000 and 1001

### **Step 2: Check Dialplan**
```bash
dialplan show 1000
```
**Expected Output:** Should show Stasis application configuration

### **Step 3: Check Stasis Apps**
```bash
stasis show apps
```
**Expected Output:** Should show 'openai-voice-assistant' if voice assistant is connected

### **Step 4: Check ARI Status**
```bash
ari show status
```
**Expected Output:** Should show ARI is enabled and running

## 🚨 **Root Cause Analysis**

The main issue is: **Stasis app 'openai-voice-assistant' not registered**

This means:
- ✅ Asterisk is running
- ✅ Configuration is loaded
- ❌ Voice assistant is not connected to Asterisk ARI
- ❌ Stasis application is not registered

## 🔧 **Solution Steps**

### **1. Exit Asterisk CLI and Check Voice Assistant**
```bash
# In Asterisk CLI, type:
exit

# Then check if voice assistant is running
curl http://localhost:8000/ari/status
```

### **2. Check ARI Connection**
```bash
# Test ARI connectivity
curl http://localhost:8088/ari/asterisk/info -u asterisk:1234

# Check if voice assistant can connect to ARI
curl http://localhost:8000/ari/health
```

### **3. Restart Voice Assistant**
If the voice assistant is not properly connected:
```bash
# Stop current voice assistant (Ctrl+C in the terminal)
# Then restart:
./activate_and_start.sh
```

## 📊 **Expected Healthy Output**

### **When System is Working:**
```bash
# pjsip show endpoints should show:
Endpoint:  1000/1000                                         Not in use    0 of inf
Endpoint:  1001/1001                                         Not in use    0 of inf

# stasis show apps should show:
App: openai-voice-assistant

# core show calls should show:
No active calls

# dialplan show 1000 should show:
[ Context 'openai-voice-assistant' created by 'pbx_config' ]
  '1000' =>           1. Stasis(openai-voice-assistant)
```

## 🎯 **Quick Fix Commands**

### **In Asterisk CLI:**
```bash
# Check current status
pjsip show endpoints
stasis show apps
dialplan show 1000

# If needed, reload configuration
core reload
```

### **Outside Asterisk CLI:**
```bash
# Check voice assistant connection
curl http://localhost:8000/ari/status | jq '.is_running'

# If false, restart voice assistant
./activate_and_start.sh
```

## 📞 **Test Call After Fix**

Once the Stasis app is registered:
1. **Configure SIP client**: 1001@localhost:5060, password: 1234
2. **Call extension 1000**
3. **In Asterisk CLI, monitor**: `core show calls`
4. **Expected**: Call should connect and show Stasis application

## 🔍 **Monitoring During Call**

### **In Asterisk CLI:**
```bash
# Watch active calls
core show calls

# Watch channels
core show channels verbose

# Watch for events
events
```

### **In Another Terminal:**
```bash
# Monitor voice assistant
curl http://localhost:8000/ari/calls

# Watch logs
docker logs -f voice-assistant-asterisk
```

---

**The main issue is that your voice assistant needs to connect to Asterisk ARI to register the Stasis application. Let's fix this first!** 🔧