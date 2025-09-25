# 🐳 NPCL Voice Assistant - Docker Deployment Guide

## 📋 **Overview**

This guide covers the complete Docker deployment of the NPCL Voice Assistant with custom Asterisk 18 integration.

## 🏗️ **Architecture**

### **Services:**
- **NPCL Voice Assistant** - Main application with OpenAI integration
- **Asterisk 18** - Custom-built PBX with ARI support
- **Redis** - Session management and caching
- **Portainer** - Container management UI (optional)

### **Network Architecture:**
```
┌─────────────────────────────────────────────────────────────┐
│                Docker Network (npcl-network)                │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │ NPCL Voice      │  │ Asterisk 18     │  │ Redis       │  │
│  │ Assistant       │  │ Custom Build    │  │ Session     │  │
│  │ :8000, :8090    │  │ :5060, :8088    │  │ Store :6379 │  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
│           │                     │                   │       │
│           └─────────────────────┼───────────────────┘       │
│                                 │                           │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              Portainer (Management) :9000              │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 **Quick Start**

### **1. Prepare Project**
```bash
# Run preparation script
./prepare-docker.sh
```

### **2. Configure Environment**
```bash
# Edit .env file with your OpenAI API key
nano .env
```

### **3. Build and Start**
```bash
# Build all images
./docker/docker-commands.sh build

# Start all services
./docker/docker-commands.sh start
```

### **4. Verify Deployment**
```bash
# Check status
./docker/docker-commands.sh status

# View logs
./docker/docker-commands.sh logs
```

## 🔧 **Detailed Setup**

### **Prerequisites**
- Docker Engine 20.10+
- Docker Compose 2.0+
- 4GB+ RAM available
- OpenAI API key

### **Environment Configuration**

Create `.env` file with required settings:
```bash
# OpenAI Configuration (REQUIRED)
OPENAI_API_KEY=sk-proj-your-api-key-here

# Voice Configuration
VOICE_MODEL=fable
TTS_MODEL=tts-1-hd
SPEECH_MODEL=whisper-1

# Audio Configuration
SAMPLE_RATE=16000
CHUNK_SIZE=1024
CHANNELS=1
AUDIO_FORMAT=slin16

# Asterisk Configuration
ARI_BASE_URL=http://asterisk:8088/ari
ARI_USERNAME=asterisk
ARI_PASSWORD=1234
STASIS_APP=openai-voice-assistant

# External Media
EXTERNAL_MEDIA_HOST=0.0.0.0
EXTERNAL_MEDIA_PORT=8090

# Assistant Settings
ASSISTANT_NAME=NPCL Assistant
VOICE_LANGUAGE=en
LOG_LEVEL=INFO
```

## 📞 **Asterisk 18 Configuration**

### **Custom Build Features:**
- **Asterisk 18.20.0** - Latest stable version
- **ARI Support** - Full REST interface enabled
- **Stasis Application** - Real-time call control
- **Audio Codecs** - G.711, G.722, GSM support
- **Security** - Runs as non-root user

### **Key Configuration Files:**
- `asterisk-config/asterisk.conf` - Main configuration
- `asterisk-config/ari.conf` - ARI settings
- `asterisk-config/http.conf` - HTTP server for ARI
- `asterisk-config/extensions.conf` - Dialplan

### **Default Dialplan:**
```
[default]
exten => 1000,1,NoOp(NPCL Voice Assistant Call)
 same => n,Stasis(openai-voice-assistant)
 same => n,Hangup()
```

## 🐳 **Docker Images**

### **Main Application Image**
- **Base**: Python 3.11-slim
- **Features**: Audio support, OpenAI integration, FastAPI
- **Size**: ~500MB
- **User**: app (non-root)

### **Asterisk 18 Image**
- **Base**: Debian Bullseye
- **Asterisk**: 18.20.0 (compiled from source)
- **Features**: ARI, Stasis, audio codecs
- **Size**: ~300MB
- **User**: asterisk (non-root)

## 🌐 **Service Endpoints**

After deployment, services are available at:

| Service | URL | Description |
|---------|-----|-------------|
| Voice Assistant | http://localhost:8000 | Main API |
| API Documentation | http://localhost:8000/docs | Swagger UI |
| Health Check | http://localhost:8000/ari/health | Service health |
| Asterisk ARI | http://localhost:8088/ari | Asterisk REST API |
| Portainer | http://localhost:9000 | Container management |
| Redis | localhost:6379 | Session store |

## 📊 **Monitoring & Logging**

### **Health Checks**
All services include health checks:
- **Voice Assistant**: HTTP endpoint check
- **Asterisk**: CLI version check
- **Redis**: Ping command

### **Log Access**
```bash
# View all logs
./docker/docker-commands.sh logs

# View specific service
./docker/docker-commands.sh logs npcl-voice-assistant
./docker/docker-commands.sh logs asterisk
./docker/docker-commands.sh logs redis

# Follow logs in real-time
docker-compose logs -f npcl-voice-assistant
```

### **Log Locations**
- **Application logs**: `./logs/`
- **Asterisk logs**: Docker volume `asterisk-logs`
- **Container logs**: Docker logging driver

## 🔒 **Security Considerations**

### **Network Security**
- Services isolated in Docker network
- Only necessary ports exposed
- Internal communication via service names

### **User Security**
- All services run as non-root users
- Minimal privilege containers
- Read-only configuration mounts

### **Data Security**
- Environment variables for secrets
- No hardcoded credentials
- Secure volume mounts

## 🚀 **Production Deployment**

### **Resource Requirements**
- **CPU**: 2+ cores recommended
- **RAM**: 4GB+ recommended
- **Storage**: 10GB+ for logs and recordings
- **Network**: 1Mbps+ for voice quality

### **Environment Variables for Production**
```bash
# Production settings
LOG_LEVEL=INFO
ENABLE_PERFORMANCE_LOGGING=false
MAX_CALL_DURATION=3600
AUTO_ANSWER_CALLS=true

# External access
EXTERNAL_MEDIA_HOST=your-server-ip
ARI_BASE_URL=http://your-server:8088/ari
```

### **Docker Swarm Deployment**
```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml npcl-stack

# Scale services
docker service scale npcl-stack_npcl-voice-assistant=3
```

### **Load Balancing**
For high availability, use a load balancer:
```yaml
# nginx.conf example
upstream npcl_backend {
    server localhost:8000;
    server localhost:8001;
    server localhost:8002;
}

server {
    listen 80;
    location / {
        proxy_pass http://npcl_backend;
    }
}
```

## 🧹 **Maintenance**

### **Regular Tasks**
```bash
# Update images
./docker/docker-commands.sh build

# Clean up resources
./docker/docker-commands.sh clean

# Reset everything
./docker/docker-commands.sh reset

# Backup volumes
docker run --rm -v npcl_asterisk-logs:/data -v $(pwd):/backup alpine tar czf /backup/asterisk-logs.tar.gz -C /data .
```

### **Troubleshooting**

#### **Common Issues**

1. **Container won't start**
   ```bash
   # Check logs
   ./docker/docker-commands.sh logs
   
   # Check resources
   docker system df
   docker system prune
   ```

2. **Audio issues**
   ```bash
   # Check audio devices
   docker run --rm --device /dev/snd npcl-voice-assistant:latest aplay -l
   ```

3. **Network connectivity**
   ```bash
   # Test internal connectivity
   docker exec npcl-voice-assistant curl http://asterisk:8088/ari/asterisk/info
   ```

4. **Asterisk not responding**
   ```bash
   # Check Asterisk status
   docker exec npcl-asterisk-18 asterisk -rx "core show version"
   
   # Restart Asterisk
   docker-compose restart asterisk
   ```

## 📈 **Performance Tuning**

### **Container Resources**
```yaml
# docker-compose.yml
services:
  npcl-voice-assistant:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
```

### **Audio Optimization**
- Use `SAMPLE_RATE=16000` for optimal Asterisk compatibility
- Set `CHUNK_SIZE=1024` for balanced latency/quality
- Enable `ENABLE_INTERRUPTION_HANDLING=true` for natural conversations

### **Database Optimization**
```bash
# Redis configuration
redis-cli CONFIG SET maxmemory 256mb
redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

## 🎯 **Testing**

### **Automated Tests**
```bash
# Health check test
curl -f http://localhost:8000/ari/health

# API test
curl http://localhost:8000/ari/calls

# Asterisk test
curl http://localhost:8088/ari/asterisk/info
```

### **Call Testing**
1. Configure SIP client to `localhost:5060`
2. Register with any username/password
3. Dial extension `1000`
4. Verify voice assistant responds

### **Load Testing**
```bash
# Use Apache Bench for API testing
ab -n 100 -c 10 http://localhost:8000/ari/health

# Use SIPp for call testing
sipp -sn uac localhost:5060 -d 30000 -s 1000
```

## 🎉 **Success Metrics**

### **Deployment Success Indicators**
- ✅ All containers healthy
- ✅ API endpoints responding
- ✅ Asterisk ARI accessible
- ✅ Test calls connecting
- ✅ Voice quality acceptable
- ✅ Logs showing normal operation

### **Performance Targets**
- **Response Time**: < 2 seconds for API calls
- **Call Setup**: < 5 seconds for voice assistant connection
- **Audio Quality**: Clear, natural voice output
- **Uptime**: 99.9% availability
- **Resource Usage**: < 80% CPU/Memory under normal load

**Your NPCL Voice Assistant is now ready for production Docker deployment!** 🐳📞🎤