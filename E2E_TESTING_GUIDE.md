# 🧪 NPCL Voice Assistant - Comprehensive E2E Testing Guide

## 📋 Overview

This guide provides complete end-to-end testing for the NPCL Asterisk ARI Assistant with Zoiper 5 integration. The script supports both Docker and Linux Asterisk deployments with automated dependency installation, environment setup, and comprehensive testing.

## 🚀 Quick Start

```bash
# Make the script executable (if not already)
chmod +x comprehensive_e2e_test.sh

# Run the comprehensive testing script
./comprehensive_e2e_test.sh
```

## 🎯 Testing Scenarios

### 1. 🐳 Docker Testing (Recommended)
- **Use Case**: Asterisk running in Docker container
- **Features**: 
  - Automated Docker setup
  - Container-based Asterisk deployment
  - Isolated testing environment
  - Easy cleanup and reset

### 2. 🐧 Linux Testing
- **Use Case**: Asterisk installed directly on Linux system
- **Features**:
  - Native Linux Asterisk installation
  - System-level configuration
  - Production-like environment
  - Direct system integration

### 3. 🔧 Dependencies Only
- **Use Case**: Install all required dependencies without running tests
- **Features**:
  - System package installation
  - Python environment setup
  - Docker configuration
  - Environment file creation

### 4. 🧪 Tests Only
- **Use Case**: Run tests assuming services are already running
- **Features**:
  - Skip service startup
  - Run comprehensive test suite
  - Manual testing with Zoiper
  - Generate test reports

## 📦 What the Script Installs

### System Dependencies
- **Ubuntu/Debian**: `python3`, `python3-pip`, `python3-venv`, `build-essential`, `docker.io`, `docker-compose`, `portaudio19-dev`, `libasound2-dev`, `ffmpeg`, `jq`, `netcat-openbsd`
- **CentOS/RHEL**: `python3`, `python3-pip`, `python3-devel`, `gcc`, `docker`, `docker-compose`, `portaudio-devel`, `alsa-lib-devel`, `ffmpeg`, `jq`, `nc`
- **macOS**: `python3`, `portaudio`, `ffmpeg`, `docker`, `docker-compose`, `jq`, `netcat` (via Homebrew)

### Python Dependencies
- `fastapi`, `uvicorn`, `websockets`, `openai`, `pydantic`, `requests`, `pygame`, `numpy`, `pytest`, `pytest-asyncio`, `pytest-cov`

### Docker Services
- Asterisk 20 LTS container with ARI enabled
- PJSIP configuration for SIP endpoints
- External media support for real-time audio

## 🔧 Configuration

### Environment Variables (.env)
The script automatically creates a `.env` file with the following configuration:

```bash
# AI Configuration
AI_PROVIDER=openai
OPENAI_API_KEY=your_openai_api_key_here  # ⚠️ UPDATE THIS

# Voice Configuration
VOICE_MODEL=fable
TTS_MODEL=tts-1-hd
ENABLE_VOICE_INTERRUPTION=true

# Audio Configuration
AUDIO_SAMPLE_RATE=16000
AUDIO_FORMAT=slin16
AUDIO_BUFFER_SIZE=1024
AUDIO_LATENCY_TARGET=20

# Asterisk ARI Configuration
ARI_BASE_URL=http://localhost:8088/ari
ARI_USERNAME=asterisk
ARI_PASSWORD=1234
STASIS_APP=openai-voice-assistant

# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
```

**⚠️ IMPORTANT**: Update the `OPENAI_API_KEY` in the `.env` file with your actual OpenAI API key.

### Asterisk Configuration
The script automatically configures:

#### SIP Endpoints
- **1000**: Voice Assistant endpoint
- **1001**: Zoiper client endpoint (username: 1001, password: 1234)

#### Extensions
- **1000**: NPCL Voice Assistant (AI-powered)
- **1010**: Simple test extension (demo message)
- **9000**: Echo test extension

#### Network Ports
- **5060/UDP**: SIP signaling
- **8088/TCP**: Asterisk ARI HTTP interface
- **10000-10100/UDP**: RTP audio streams

## 📱 Zoiper 5 Configuration

### Basic Settings
```
Server: localhost:5060
Username: 1001
Password: 1234
Protocol: SIP
Transport: UDP
```

### Advanced Settings
```
Codec: G.711 μ-law (PCMU)
DTMF: RFC 2833
NAT Traversal: Enable
Keep Alive: Enable
```

### Test Extensions
- **1000**: NPCL Voice Assistant (AI-powered conversation)
- **1010**: Simple test (plays demo message)
- **9000**: Echo test (repeats what you say)

## 🧪 Testing Process

### Automated Tests
1. **System Health Checks**
   - Service availability
   - Port accessibility
   - API endpoint validation

2. **ARI Integration Tests**
   - Asterisk ARI connectivity
   - Application endpoints
   - Channel management

3. **Voice Assistant Tests**
   - Health endpoint validation
   - OpenAI integration check
   - Configuration validation

4. **Call Simulation**
   - Synthetic call event generation
   - Event processing validation
   - Active call tracking

### Manual Testing with Zoiper
1. **Call Setup**
   - Configure Zoiper with provided settings
   - Make test call to extension 1000
   - Verify call connection

2. **Audio Quality**
   - Test two-way audio communication
   - Verify codec negotiation (should show G.711 μ-law, NOT "None")
   - Check audio clarity and latency

3. **AI Interaction**
   - Speak to the AI assistant
   - Verify real-time responses
   - Test voice interruption capability

4. **Results Reporting**
   - Answer test result questions
   - Automatic logging of results
   - Generate comprehensive test report

## 📊 Test Results and Logging

### Log Files
All test results are saved in the `test_logs/` directory:

- `e2e_test_TIMESTAMP.log`: Main test execution log
- `voice_assistant_TIMESTAMP.log`: Voice assistant server logs
- `unit_tests_TIMESTAMP.log`: Unit test results
- `integration_tests_TIMESTAMP.log`: Integration test results
- `system_monitor_TIMESTAMP.log`: Real-time system monitoring
- `manual_test_results_TIMESTAMP.log`: Manual testing results

### Test Report
An HTML test report is generated at: `test_logs/test_report_TIMESTAMP.html`

The report includes:
- Test configuration summary
- All log file links
- Zoiper configuration details
- Test execution timeline

## 🔍 Monitoring

### Real-time Monitoring
The script includes continuous monitoring that tracks:
- Asterisk service status (Docker or Linux)
- Voice Assistant health
- Active call count
- System resource usage

### Monitoring Output
```
[2024-01-01 12:00:00] Asterisk: Docker Running | Voice Assistant: Running | Active Calls: 0
[2024-01-01 12:00:10] Asterisk: Docker Running | Voice Assistant: Running | Active Calls: 1
```

## ✅ Expected Results

### Successful Test Indicators
1. **Service Startup**
   - ✅ Asterisk: Running
   - ✅ Voice Assistant: Running
   - ✅ All health checks pass

2. **Network Connectivity**
   - ✅ SIP port 5060 accessible
   - ✅ ARI port 8088 accessible
   - ✅ RTP ports 10000-10100 accessible

3. **Zoiper Call Test**
   - ✅ Call connects immediately
   - ✅ Local codecs: G.711 μ-law
   - ✅ Remote codecs: G.711 μ-law (NOT "None")
   - ✅ Two-way audio working
   - ✅ AI responds in real-time
   - ✅ Voice interruption works

## 🚨 Troubleshooting

### Common Issues

#### 1. OpenAI API Key Not Configured
```
❌ OpenAI API key is not configured
```
**Solution**: Update `OPENAI_API_KEY` in `.env` file with valid API key from https://platform.openai.com/api-keys

#### 2. Docker Not Running
```
❌ Docker is not running
```
**Solution**: 
- Linux: `sudo systemctl start docker`
- macOS: Start Docker Desktop application

#### 3. Port Already in Use
```
❌ SIP port 5060 is not accessible
```
**Solution**: 
- Check for existing Asterisk: `sudo systemctl stop asterisk`
- Check for other SIP services: `sudo netstat -tulpn | grep 5060`

#### 4. Permission Denied
```
❌ Permission denied
```
**Solution**: 
- Add user to docker group: `sudo usermod -aG docker $USER`
- Log out and back in, or run: `newgrp docker`

#### 5. Asterisk Configuration Issues
```
❌ SIP endpoint 1001 is not configured
```
**Solution**: 
- Check Asterisk logs: `docker logs npcl-asterisk-20`
- Verify configuration files in `asterisk-config/`

### Debug Commands

#### Check Service Status
```bash
# Docker scenario
docker ps | grep asterisk
curl -s http://localhost:8000/health | jq .

# Linux scenario
sudo systemctl status asterisk
sudo asterisk -rx "core show version"
```

#### Check Network Connectivity
```bash
# Test SIP port
nc -z localhost 5060

# Test ARI
curl -u asterisk:1234 http://localhost:8088/ari/asterisk/info

# Test Voice Assistant
curl http://localhost:8000/health
```

#### Check Logs
```bash
# View recent logs
tail -f test_logs/e2e_test_*.log
tail -f test_logs/voice_assistant_*.log

# Check Asterisk logs (Docker)
docker logs npcl-asterisk-20

# Check Asterisk logs (Linux)
sudo tail -f /var/log/asterisk/messages
```

## 🔄 Cleanup

The script automatically cleans up on exit:
- Stops voice assistant server
- Stops Docker containers
- Stops monitoring processes
- Preserves all log files for analysis

### Manual Cleanup
```bash
# Stop all services
docker-compose down
sudo systemctl stop asterisk

# Remove test logs (optional)
rm -rf test_logs/

# Reset environment (optional)
rm .env
```

## 📞 Support

### Test Validation Checklist
- [ ] All dependencies installed successfully
- [ ] Asterisk service running (Docker or Linux)
- [ ] Voice Assistant health check passes
- [ ] ARI endpoints accessible
- [ ] SIP ports open and accessible
- [ ] Zoiper configured correctly
- [ ] Test call to extension 1000 successful
- [ ] Remote codecs show "G.711 μ-law" (NOT "None")
- [ ] Two-way audio communication working
- [ ] AI responds to voice input
- [ ] Voice interruption functional

### Getting Help
1. **Check Logs**: Review generated log files in `test_logs/`
2. **Verify Configuration**: Ensure `.env` file has correct settings
3. **Test Network**: Verify all required ports are accessible
4. **Check Dependencies**: Ensure all system packages are installed
5. **Review Test Report**: Check the generated HTML report for details

## 🎯 Production Deployment

After successful testing:

1. **Update Configuration**: Modify `.env` for production settings
2. **Security**: Change default passwords and enable security features
3. **Monitoring**: Set up production monitoring and logging
4. **Scaling**: Configure for multiple concurrent calls
5. **Backup**: Implement configuration and data backup procedures

---

**🎉 Congratulations!** You now have a comprehensive testing framework for the NPCL Voice Assistant with Zoiper 5 integration. The script handles both Docker and Linux scenarios with complete automation and detailed reporting.