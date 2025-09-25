# 📞 Call Testing & History Monitoring Guide

## 🎯 **Current Setup Status**

Your current setup:
- ✅ **Asterisk Container**: Running and healthy (`voice-assistant-asterisk`)
- ✅ **Local Voice Assistant**: Running with OpenAI Real-time API
- ✅ **SIP Configuration**: Ready for testing

## 📞 **How to Test Voice Calls**

### **Step 1: Configure Your SIP Client**
```
Server: localhost:5060
Username: 1001
Password: 1234
Protocol: UDP
```

### **Step 2: Make Test Calls**
- **Call Extension 1000**: AI Voice Assistant
- **Expected**: AI should answer with NPCL greeting
- **Test Voice Interruption**: Interrupt AI while speaking

### **Step 3: Monitor in Real-Time**
Open multiple terminals to monitor different aspects:

## 🔍 **Docker Log Commands**

### **1. Asterisk Container Logs**
```bash
# Real-time Asterisk logs (shows all call activity)
docker logs -f voice-assistant-asterisk

# Last 50 lines of Asterisk logs
docker logs --tail 50 voice-assistant-asterisk

# Asterisk logs with timestamps
docker logs -t voice-assistant-asterisk

# Filter for specific call events
docker logs voice-assistant-asterisk | grep -E "(INVITE|BYE|ANSWER|HANGUP)"
```

### **2. Voice Assistant Logs (if using Docker)**
```bash
# If you start voice assistant in Docker later
docker logs -f voice-assistant-app

# Voice assistant logs with timestamps
docker logs -t voice-assistant-app
```

### **3. Combined Monitoring**
```bash
# Monitor both containers simultaneously
docker logs -f voice-assistant-asterisk &
docker logs -f voice-assistant-app &

# Or use docker-compose logs
docker-compose logs -f
```

## 📊 **Call History Analysis**

### **Asterisk Call Events to Look For:**
```bash
# Incoming call
grep "INVITE" /var/log/asterisk/messages

# Call answered
grep "ANSWER" /var/log/asterisk/messages

# Call ended
grep "HANGUP" /var/log/asterisk/messages

# SIP registration
grep "REGISTER" /var/log/asterisk/messages
```

### **Real-Time Call Monitoring:**
```bash
# Monitor active calls
docker exec voice-assistant-asterisk asterisk -rx "core show calls"

# Monitor SIP peers
docker exec voice-assistant-asterisk asterisk -rx "pjsip show endpoints"

# Monitor channels
docker exec voice-assistant-asterisk asterisk -rx "core show channels"
```

## 🎤 **Voice Assistant Monitoring**

### **API Endpoints for Call History:**
```bash
# Check active calls
curl http://localhost:8000/ari/calls

# Check system status
curl http://localhost:8000/ari/status

# Check session statistics
curl http://localhost:8000/ari/status | jq '.session_stats'

# Check AI client status
curl http://localhost:8000/ai/provider/current
```

### **Local Server Logs:**
If running voice assistant locally, monitor the terminal output for:
- Call connection events
- Audio processing status
- AI response generation
- Error messages

## 📋 **Complete Testing Workflow**

### **Terminal 1: Start Voice Assistant (if not running)**
```bash
./activate_and_start.sh
```

### **Terminal 2: Monitor Asterisk Logs**
```bash
docker logs -f voice-assistant-asterisk
```

### **Terminal 3: Monitor Voice Assistant API**
```bash
# Watch for call events
watch -n 2 'curl -s http://localhost:8000/ari/calls | jq .'
```

### **Terminal 4: Real-Time Asterisk Commands**
```bash
# Interactive Asterisk CLI
docker exec -it voice-assistant-asterisk asterisk -r

# Then use commands like:
# core show calls
# pjsip show endpoints
# core show channels verbose
```

## 🔍 **Call History Examples**

### **Successful Call Log Pattern:**
```
# Asterisk logs will show:
[timestamp] NOTICE[xxx]: chan_pjsip.c: Call from '1001' to extension '1000'
[timestamp] NOTICE[xxx]: app_stasis.c: Starting Stasis application 'openai-voice-assistant'
[timestamp] NOTICE[xxx]: res_pjsip_session.c: Call answered

# Voice Assistant logs will show:
[timestamp] INFO - New call received: channel_id=xxx
[timestamp] INFO - Starting voice conversation
[timestamp] INFO - AI response generated
[timestamp] INFO - Call ended successfully
```

### **Failed Call Log Pattern:**
```
# Asterisk logs might show:
[timestamp] WARNING[xxx]: chan_pjsip.c: No matching endpoint found
[timestamp] ERROR[xxx]: app_stasis.c: Failed to start Stasis application

# Voice Assistant logs might show:
[timestamp] ERROR - Failed to connect to OpenAI
[timestamp] WARNING - No response from AI service
```

## 📊 **Advanced Monitoring**

### **Call Statistics:**
```bash
# Get detailed call statistics
curl http://localhost:8000/ari/status | jq '{
  active_calls: .active_calls,
  total_sessions: .session_stats.total_sessions,
  total_duration: .session_stats.total_duration,
  average_duration: .session_stats.average_session_duration
}'
```

### **Audio Quality Monitoring:**
```bash
# Check audio processing stats
curl http://localhost:8000/ari/status | jq '.external_media_stats'

# Monitor AI client connection
curl http://localhost:8000/ari/status | jq '.ai_client_status'
```

### **Export Call History:**
```bash
# Export Asterisk logs
docker logs voice-assistant-asterisk > asterisk_call_history.log

# Export with timestamps
docker logs -t voice-assistant-asterisk > asterisk_call_history_timestamped.log

# Filter for call events only
docker logs voice-assistant-asterisk | grep -E "(INVITE|ANSWER|HANGUP|BYE)" > call_events.log
```

## 🚨 **Troubleshooting Commands**

### **If Calls Don't Connect:**
```bash
# Check SIP registration
docker exec voice-assistant-asterisk asterisk -rx "pjsip show registrations"

# Check endpoints
docker exec voice-assistant-asterisk asterisk -rx "pjsip show endpoints"

# Check dialplan
docker exec voice-assistant-asterisk asterisk -rx "dialplan show"
```

### **If Voice Assistant Doesn't Respond:**
```bash
# Check voice assistant health
curl http://localhost:8000/ari/health

# Check AI provider status
curl http://localhost:8000/ai/provider/current

# Check if ARI handler is running
curl http://localhost:8000/ari/status | jq '.is_running'
```

## 📱 **Quick Test Commands**

### **One-Line Status Check:**
```bash
echo "=== Container Status ===" && docker ps && echo -e "\n=== Voice Assistant Health ===" && curl -s http://localhost:8000/ari/health | jq . && echo -e "\n=== Active Calls ===" && curl -s http://localhost:8000/ari/calls | jq .
```

### **Call History Summary:**
```bash
echo "=== Recent Call Events ===" && docker logs --tail 20 voice-assistant-asterisk | grep -E "(INVITE|ANSWER|HANGUP)" && echo -e "\n=== Session Statistics ===" && curl -s http://localhost:8000/ari/status | jq '.session_stats'
```

## 🎯 **Testing Checklist**

### **Before Making Calls:**
- [ ] Asterisk container is healthy
- [ ] Voice assistant server is running
- [ ] SIP client is configured (1001@localhost:5060)
- [ ] Monitoring terminals are open

### **During Call Testing:**
- [ ] Watch Asterisk logs for INVITE/ANSWER events
- [ ] Monitor voice assistant API for call status
- [ ] Test voice interruption functionality
- [ ] Check audio quality

### **After Call Testing:**
- [ ] Review call logs for errors
- [ ] Check session statistics
- [ ] Export logs if needed
- [ ] Verify call cleanup

**Ready to test your voice assistant with comprehensive monitoring!** 📞🎤

---

*Use these commands to monitor every aspect of your voice calls and troubleshoot any issues!*