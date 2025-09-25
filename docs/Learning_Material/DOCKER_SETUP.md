# 🐳 NPCL Voice Assistant - Docker Setup

## 🚀 **Complete Docker Solution**

Your NPCL Voice Assistant is now fully dockerized with production-ready containers!

## 📋 **What's Included**

### **🐳 Docker Files:**
- **`Dockerfile`** - Main application container
- **`docker-compose.yml`** - Production environment
- **`docker-compose.dev.yml`** - Development environment
- **`.dockerignore`** - Optimized build context

### **🔧 Management Scripts:**
- **`docker/docker-commands.sh`** - Complete management utility
- **`docker/entrypoint.sh`** - Production entrypoint
- **`docker/docker-entrypoint-dev.sh`** - Development entrypoint
- **`docker/supervisord.conf`** - Process management

### **🏗️ Services:**
- **NPCL Voice Assistant** - Main application (Port 8000, 8090)
- **Asterisk PBX** - Telephony system (Port 5060, 8088)
- **Redis** - Session management (Port 6379)
- **Portainer** - Container management (Port 9000)

## 🚀 **Quick Start Commands**

### **1. Build the Docker Image**
```bash
# Build the image
./docker/docker-commands.sh build
```

### **2. Start Production Environment**
```bash
# Start all services
./docker/docker-commands.sh start
```

### **3. Check Status**
```bash
# View service status and health
./docker/docker-commands.sh status
```

### **4. View Logs**
```bash
# View voice assistant logs
./docker/docker-commands.sh logs

# View specific service logs
./docker/docker-commands.sh logs asterisk
```

### **5. Stop Services**
```bash
# Stop all services
./docker/docker-commands.sh stop
```

## 🔧 **Environment Configuration**

### **Required: Create .env file**
```bash
# Create .env file with your OpenAI API key
cat > .env << EOF
OPENAI_API_KEY=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
VOICE_MODEL=fable
TTS_MODEL=tts-1-hd
EOF
```

## 🐳 **Docker Commands**

### **Production Environment**
```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f npcl-voice-assistant

# Stop
docker-compose down
```

### **Development Environment**
```bash
# Start with hot reload
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f npcl-voice-assistant-dev
```

### **Manual Docker Commands**
```bash
# Build image
docker build -t npcl-voice-assistant:latest .

# Run container
docker run -d \
  --name npcl-voice-assistant \
  -p 8000:8000 \
  -p 8090:8090 \
  -e OPENAI_API_KEY=your-api-key \
  -e VOICE_MODEL=fable \
  -e TTS_MODEL=tts-1-hd \
  npcl-voice-assistant:latest
```

## 🌐 **Service URLs**

After starting with `./docker/docker-commands.sh start`:

- **🎤 Voice Assistant**: http://localhost:8000
- **📋 API Documentation**: http://localhost:8000/docs
- **🌡️ Health Check**: http://localhost:8000/ari/health
- **📞 Asterisk ARI**: http://localhost:8088/ari
- **🐳 Portainer**: http://localhost:9000
- **📊 Redis**: localhost:6379

## 📞 **Testing the System**

### **1. Health Check**
```bash
curl http://localhost:8000/ari/health
```

### **2. API Status**
```bash
curl http://localhost:8000/ari/calls
```

### **3. Make Test Call**
- Configure SIP client to connect to `localhost:5060`
- Dial extension `1000`
- Experience the enhanced voice assistant

## 🔧 **Development Mode**

### **Start Development Environment**
```bash
# Start with hot reload
./docker/docker-commands.sh start-dev
```

**Features:**
- **Hot Reload** - Code changes restart the service automatically
- **Debug Logging** - Detailed logs for development
- **Volume Mounting** - Live code editing
- **Performance Monitoring** - Enhanced debugging

## 📊 **Container Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Network (npcl-network)            │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │ NPCL Voice      │  │ Asterisk PBX    │  │ Redis       │  │
│  │ Assistant       │  │                 │  │ Session     │  │
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

## 🔒 **Security Features**

- **Non-root user** - Application runs as `app` user
- **Network isolation** - Services communicate via Docker network
- **Environment variables** - Secure configuration management
- **Health checks** - Automatic service monitoring
- **Resource limits** - Controlled resource usage

## 📁 **Volume Mounts**

- **`./sounds`** → `/app/sounds` - Audio files
- **`./recordings`** → `/app/recordings` - Call recordings
- **`./logs`** → `/app/logs` - Application logs
- **`./asterisk-config`** → `/etc/asterisk` - Asterisk configuration

## 🧹 **Maintenance Commands**

### **View All Available Commands**
```bash
./docker/docker-commands.sh help
```

### **Clean Up Resources**
```bash
# Clean containers and images
./docker/docker-commands.sh clean

# Reset everything
./docker/docker-commands.sh reset
```

### **Monitor Resources**
```bash
# View container stats
docker stats

# View container processes
docker-compose top
```

## 🚨 **Troubleshooting**

### **Container Won't Start**
```bash
# Check logs
./docker/docker-commands.sh logs

# Check status
./docker/docker-commands.sh status

# Rebuild if needed
./docker/docker-commands.sh reset
```

### **Audio Issues**
```bash
# Check audio device access
docker run --rm -it --device /dev/snd npcl-voice-assistant:latest aplay -l
```

### **Network Issues**
```bash
# Check network connectivity
docker network ls
docker network inspect npcl_npcl-network
```

## 🎯 **Production Deployment**

### **Environment Variables for Production**
```bash
# Production .env file
OPENAI_API_KEY=your-production-api-key
VOICE_MODEL=fable
TTS_MODEL=tts-1-hd
LOG_LEVEL=INFO
ENABLE_PERFORMANCE_LOGGING=false
ARI_BASE_URL=http://asterisk:8088/ari
EXTERNAL_MEDIA_HOST=your-server-ip
```

### **Docker Swarm Deployment**
```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml npcl-stack
```

## 🎉 **Success!**

Your NPCL Voice Assistant is now fully containerized with:

- ✅ **Production-ready containers**
- ✅ **Development environment with hot reload**
- ✅ **Complete service orchestration**
- ✅ **Health monitoring and logging**
- ✅ **Easy management scripts**
- ✅ **Scalable architecture**

**Start your containerized voice assistant now:**
```bash
./docker/docker-commands.sh start
```

**Your professional AI voice assistant is ready for production deployment!** 🐳🎤📞