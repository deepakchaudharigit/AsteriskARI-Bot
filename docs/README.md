# 🎤 NPCL Asterisk ARI Voice Assistant

**A comprehensive, enterprise-grade voice assistant system powered by OpenAI's GPT-4 Realtime API, designed specifically for NPCL (Noida Power Corporation Limited) customer service with advanced real-time telephony integration.**

## ✨ **Project Overview**

The NPCL Voice Assistant is a sophisticated, production-ready voice interaction system that combines cutting-edge AI technology with enterprise telephony infrastructure. It provides seamless voice-based customer support for power utility services through multiple interaction channels.

### **🎯 Key Capabilities**

- 🤖 **Advanced AI Integration**: OpenAI GPT-4 Realtime API for real-time conversational AI
- 📞 **Enterprise Telephony**: Complete Asterisk ARI integration with bidirectional audio streaming
- 🎤 **Real-time Audio Processing**: Voice Activity Detection with <20ms latency
- 🌐 **Multi-channel Support**: Phone calls, WebSocket, REST API, and web interfaces
- 🗣️ **Multilingual Support**: Hindi, Bhojpuri, Bengali, and English
- 🏢 **NPCL-Specific Features**: Power utility customer service optimization
- 🔒 **Enterprise Security**: Production-ready security and authentication
- 📊 **Comprehensive Monitoring**: Real-time metrics, logging, and performance tracking

## 🚀 **What's New in Version 2.0**

### **🎆 Real-time Features**
- **OpenAI Realtime API Integration**: Direct voice-to-voice conversation with ultra-low latency
- **External Media Streaming**: Bidirectional audio via Asterisk externalMedia WebSocket
- **Voice Activity Detection**: Intelligent interruption handling for natural conversations
- **Session Management**: Advanced conversation state tracking and metrics

### **🏗️ Professional Architecture**
- **Modular Design**: Clean separation of concerns with 10+ specialized modules
- **Event-Driven Architecture**: Async processing with comprehensive event handling
- **Configuration Management**: Pydantic-based settings with environment isolation
- **Error Recovery**: Robust error handling with graceful degradation

### **🧪 Enterprise Testing**
- **200+ Test Cases**: Comprehensive test coverage across all components
- **Performance Testing**: Real-time latency and load testing
- **Integration Testing**: End-to-end workflow validation
- **Audio Testing**: Specialized voice activity detection testing

### **🐳 Production Deployment**
- **Docker Support**: Multi-stage builds with security hardening
- **Kubernetes Ready**: Production orchestration with auto-scaling
- **Monitoring Stack**: Prometheus, Grafana, and comprehensive observability
- **CI/CD Integration**: Automated testing and deployment pipelines

## 📁 **Project Architecture**

```
NPCL-Asterisk-ARI-Assistant/
├── src/voice_assistant/              # 🎯 Core Application
│   ├── core/                         # 🧠 Business Logic & Session Management
│   │   ├── assistant.py              # Main VoiceAssistant orchestrator
│   │   ├── session_manager.py        # Advanced session tracking
│   │   ├── modern_assistant.py       # Modern AI integration
│   │   └── performance.py            # Performance monitoring
│   ├── ai/                           # 🤖 AI Services
│   │   ├── openai_realtime_client.py # Real-time OpenAI API
│   │   ├── ai_client_factory.py      # AI client factory
│   │   ├── function_calling.py       # AI tool integration
│   │   └── npcl_prompts.py           # NPCL-specific prompts
│   ├── audio/                        # 🎵 Audio Processing
│   │   ├── realtime_audio_processor.py  # Real-time audio pipeline
│   │   ├── improved_vad.py           # Voice Activity Detection
│   │   ├── multilingual_tts.py       # Multi-language TTS
│   │   └── audio_utils.py            # Audio utilities
│   ├── telephony/                    # 📞 Telephony Integration
│   │   ├── realtime_ari_handler.py   # Advanced ARI handler
│   │   ├── external_media_handler.py # WebSocket audio streaming
│   │   ├── rtp_streaming_handler.py  # RTP protocol handling
│   │   └── ari_handler.py            # Base ARI implementation
│   ├── tools/                        # 🛠️ External Tools
│   │   └── weather_tool.py           # Weather information tool
│   ├── i18n/                         # 🌐 Internationalization
│   │   └── locales/                  # Language-specific resources
│   ├── observability/                # 📊 Monitoring & Metrics
│   ├── security/                     # 🔒 Security Components
│   └── utils/                        # 🔧 Utilities
├── config/                           # ⚙️ Configuration
│   └── settings.py                   # Pydantic configuration management
├── tests/                            # 🧪 Comprehensive Test Suite
│   ├── unit/                         # Unit tests (11 files)
│   ├── integration/                  # Integration tests (3 files)
│   ├── e2e/                          # End-to-end tests
│   ├── performance/                  # Performance & latency tests
│   ├── audio/                        # Audio processing tests
│   ├── websocket/                    # WebSocket communication tests
│   ├── mocks/                        # Mock objects for testing
│   └── utils/                        # Test utilities
├── docs/                             # 📚 Documentation
│   ├── API_DOCUMENTATION.md         # Complete API reference
│   ├── ARCHITECTURE.md              # System architecture
│   ├── DEPLOYMENT.md                # Deployment guide
│   ├── REALTIME_SETUP.md            # Real-time setup guide
│   └── COMPREHENSIVE_TEST_CASES_REPORT.md
├── docker/                           # 🐳 Docker Configuration
│   └── entrypoint.sh                # Container initialization
├── kubernetes/                       # ☸️ Kubernetes Manifests
├── monitoring/                       # 📊 Monitoring Configuration
├── asterisk-config/                  # 📞 Asterisk Configuration
├── scripts/                          # 📜 Utility Scripts
└── sounds/                           # 🔊 Audio Resources
```

## 🛠️ **Installation & Setup**

### **Prerequisites**

- **Python**: 3.8+ (3.11 recommended)
- **OpenAI API Key**: For GPT-4 Realtime API access
- **Asterisk**: 16.0+ with ARI enabled (for telephony features)
- **System**: 4GB RAM minimum, 8GB recommended
- **Network**: Stable internet for AI services

### **Quick Start**

```bash
# 1. Clone the repository
git clone <repository-url>
cd NPCL-Asterisk-ARI-Assistant

# 2. Create virtual environment
python -m venv .venv

# Activate virtual environment
# Linux/Mac:
source .venv/bin/activate
# Windows:
.venv\\Scripts\\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env and add your OpenAI API key

# 5. Run the assistant
python src/main.py
```

### **Docker Deployment (Recommended)**

```bash
# Development environment
docker-compose up -d

# Production environment
docker-compose -f docker-compose.production.yml up -d

# Access the API
curl http://localhost:8000/health
```

## ⚙️ **Configuration**

### **Environment Variables**

```bash
# Required - OpenAI API Key
OPENAI_API_KEY=your-openai-api-key-here

# AI Configuration
OPENAI_MODEL=gpt-4o-realtime-preview-2024-10-01
OPENAI_VOICE=alloy
MAX_TOKENS=150
TEMPERATURE=0.7

# Real-time Audio Settings
AUDIO_FORMAT=slin16
AUDIO_SAMPLE_RATE=16000
AUDIO_CHUNK_SIZE=320
VAD_ENERGY_THRESHOLD=300

# Assistant Configuration
ASSISTANT_NAME=NPCL Assistant
VOICE_LANGUAGE=en
LISTEN_TIMEOUT=20.0

# Telephony Configuration (Optional)
ARI_BASE_URL=http://localhost:8088/ari
ARI_USERNAME=asterisk
ARI_PASSWORD=1234
STASIS_APP=openai-voice-assistant

# External Media Configuration
EXTERNAL_MEDIA_HOST=localhost
EXTERNAL_MEDIA_PORT=8090

# Performance Settings
ENABLE_INTERRUPTION_HANDLING=true
MAX_CALL_DURATION=3600
AUTO_ANSWER_CALLS=true
```

### **Getting OpenAI API Key**

1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Sign in with your OpenAI account
3. Create a new API key
4. Copy the key to your `.env` file

## 🎯 **Usage Modes**

### **1. Standalone Voice Assistant**

```bash
python src/main.py
# Choose option 2 (Voice Mode) for full voice conversation
```

**Features:**
- 🎤 Voice input with 15-second timeout
- 🧠 AI processing with OpenAI GPT-4 Realtime
- 🗣️ Speech output with OpenAI TTS
- 📊 Real-time status updates
- 📈 Session statistics

### **2. Real-time Telephony Integration**

```bash
# Start real-time server
python src/run_realtime_server.py

# Or use the startup script
./start_realtime.sh
```

**Features:**
- 📡 Bidirectional audio streaming via WebSocket
- 🎤 Voice Activity Detection with interruption handling
- ⚡ Ultra-low latency (<20ms audio processing)
- 🔄 Real-time conversation state management
- 📞 Complete Asterisk ARI integration

### **3. API Server Mode**

```bash
# Start FastAPI server
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

**Access Points:**
- 🌐 **API**: http://localhost:8000
- 📚 **Documentation**: http://localhost:8000/docs
- 🏥 **Health Check**: http://localhost:8000/health
- 📊 **Status**: http://localhost:8000/status

### **4. WebSocket Real-time Mode**

```javascript
// Connect to WebSocket for real-time interaction
const ws = new WebSocket('ws://localhost:8000/ws/voice/session_id');

// Send audio data
ws.send(JSON.stringify({
    type: 'audio_data',
    data: base64AudioData
}));
```

## 📞 **Telephony Integration**

### **Test Extensions**

- **1000**: Main OpenAI Voice Assistant (full real-time integration)
- **1001**: External Media Test (direct WebSocket audio)
- **1002**: Basic Audio Test (echo and playback)
- **1003**: Conference Test
- **1004**: Recording Test

### **Asterisk Configuration**

```bash
# Copy Asterisk configuration
sudo cp asterisk-config/* /etc/asterisk/

# Restart Asterisk
sudo systemctl restart asterisk

# Test ARI connectivity
curl -u asterisk:1234 http://localhost:8088/ari/asterisk/info
```

## 🧪 **Testing**

### **Run Test Suite**

```bash
# Run all tests (200+ test cases)
pytest tests/ -v

# Run specific test categories
pytest tests/unit/ -v                    # Unit tests
pytest tests/integration/ -v             # Integration tests
pytest tests/performance/ -v             # Performance tests
pytest tests/e2e/ -v                     # End-to-end tests

# Run with coverage
pytest tests/ --cov=src/voice_assistant --cov-report=html
```

### **Test Categories**

| Category | Files | Test Cases | Purpose |
|----------|-------|------------|----------|
| **Unit Tests** | 11 | 150+ | Component isolation testing |
| **Integration Tests** | 3 | 30+ | Component interaction testing |
| **E2E Tests** | 1 | 10+ | Complete workflow testing |
| **Performance Tests** | 1 | 15+ | Latency and load testing |
| **Audio Tests** | 1 | 10+ | Voice activity detection |
| **WebSocket Tests** | 1 | 10+ | Real-time communication |

## 📊 **Monitoring & Observability**

### **Built-in Monitoring**

- **Real-time Metrics**: Performance and usage statistics
- **Health Checks**: Component status monitoring
- **Session Tracking**: Complete conversation analytics
- **Error Tracking**: Comprehensive error logging
- **Performance Monitoring**: Latency and throughput metrics

### **Production Monitoring Stack**

```bash
# Start monitoring stack (production)
docker-compose -f docker-compose.production.yml up -d

# Access monitoring dashboards
# Grafana: http://localhost:3000
# Prometheus: http://localhost:9090
```

**Available Dashboards:**
- 🎤 Voice Assistant Performance
- 📞 Asterisk Call Metrics
- 🗄️ Database Performance
- 🔄 Redis Cache Metrics
- 🌐 API Request Analytics

## 🔒 **Security Features**

### **Built-in Security**

- **API Key Authentication**: Secure OpenAI API integration
- **Input Validation**: Comprehensive input sanitization
- **Rate Limiting**: DDoS protection and abuse prevention
- **Secure Configuration**: Environment-based secrets management
- **Audit Logging**: Complete security event tracking

### **Production Security**

```bash
# Enable security features
ENABLE_RATE_LIMITING=true
ENABLE_INPUT_SANITIZATION=true
ENABLE_AUDIT_LOGGING=true

# Configure SSL/TLS
# See deployment documentation for details
```

## 🌐 **Multilingual Support**

### **Supported Languages**

- **English (en-IN)**: Primary language
- **Hindi (hi-IN)**: Full support with native TTS
- **Bhojpuri (bho-IN)**: Regional language support
- **Bengali (bn-IN)**: Eastern region support

### **Language Configuration**

```bash
# Set default language
VOICE_LANGUAGE=hi

# Enable multilingual detection
ENABLE_LANGUAGE_DETECTION=true
```

## 🏢 **NPCL-Specific Features**

### **Power Utility Services**

- **Bill Inquiries**: Electricity bill status and payment
- **Outage Reporting**: Power outage reporting and tracking
- **Connection Services**: New connection requests
- **Complaint Management**: Customer complaint handling
- **Service Areas**: Noida, Greater Noida, Ghaziabad coverage

### **Customer Service Optimization**

```python
# NPCL-specific prompts and responses
from voice_assistant.ai.npcl_prompts import NPCLPrompts

# Specialized customer service workflows
# Automated complaint registration
# Bill payment assistance
# Service request handling
```

## 🚀 **Performance Specifications**

### **Real-time Performance**

| Metric | Target | Production Requirement |
|--------|--------|------------------------|
| **Audio Processing Latency** | <20ms | Critical for real-time |
| **VAD Processing** | <10ms | Voice Activity Detection |
| **Session Creation** | <100ms | Session management |
| **WebSocket Response** | <100ms | Real-time communication |
| **Memory Usage** | <100MB per session | Production target |
| **CPU Usage** | <80% | Under normal load |

### **Quality Metrics**

| Metric | Target | Description |
|--------|--------|-------------|
| **Audio Quality Preservation** | >95% | Energy retention |
| **Speech Detection Accuracy** | >90% | Precision |
| **Silence Detection Accuracy** | >95% | Precision |
| **Error Rate** | <1% | Production deployment |
| **Concurrent Sessions** | 100+ | Simultaneous calls |

## 🔧 **Development**

### **Development Setup**

```bash
# Install development dependencies
pip install -r requirements-test.txt

# Install pre-commit hooks
pre-commit install

# Run code formatting
black src/
flake8 src/

# Run type checking
mypy src/
```

### **Code Quality Standards**

- **Type Safety**: Comprehensive type hints throughout
- **Code Formatting**: Black for consistent formatting
- **Linting**: Flake8 for code quality
- **Documentation**: Docstrings for all classes and methods
- **Testing**: Minimum 90% test coverage

### **Adding Features**

The modular architecture makes it easy to extend:

```python
# Add new AI provider
from voice_assistant.ai.base_client import BaseAIClient

class NewAIClient(BaseAIClient):
    def generate_response(self, text: str) -> str:
        # Your implementation
        pass

# Add new audio processor
from voice_assistant.audio.base_processor import BaseAudioProcessor

class NewAudioProcessor(BaseAudioProcessor):
    def process_audio(self, audio_data: bytes) -> str:
        # Your implementation
        pass
```

## 🐳 **Docker Deployment**

### **Development Deployment**

```bash
# Start development environment
docker-compose up -d

# View logs
docker-compose logs -f voice-assistant

# Stop services
docker-compose down
```

### **Production Deployment**

```bash
# Set environment variables
export OPENAI_API_KEY=\"your-key\"
export DB_PASSWORD=\"secure-password\"

# Start production stack
docker-compose -f docker-compose.production.yml up -d

# Monitor deployment
docker-compose -f docker-compose.production.yml logs -f
```

### **Kubernetes Deployment**

```bash
# Deploy to Kubernetes
kubectl apply -f kubernetes/

# Check deployment status
kubectl get pods -n voice-assistant

# Scale deployment
kubectl scale deployment voice-assistant --replicas=5
```

## 🚨 **Troubleshooting**

### **Common Issues**

1. **OpenAI API Key Issues**:
   ```bash
   # Verify API key
   python -c \"import openai; openai.api_key='your-key'; print('Valid')\"
   ```

2. **Audio Processing Issues**:
   ```bash
   # Check audio dependencies
   python -c \"import pyaudio; import pydub; print('Audio OK')\"
   ```

3. **Asterisk Connection Issues**:
   ```bash
   # Test ARI connectivity
   curl -u asterisk:1234 http://localhost:8088/ari/asterisk/info
   ```

### **Debug Mode**

```bash
# Enable debug logging
LOG_LEVEL=DEBUG

# Enable performance monitoring
ENABLE_PERFORMANCE_MONITORING=true

# Run with verbose output
python src/main.py --debug
```

## 📚 **Documentation**

### **Complete Documentation Set**

- **[API Documentation](API_DOCUMENTATION.md)**: Complete API reference
- **[Architecture Guide](ARCHITECTURE.md)**: System architecture and design
- **[Deployment Guide](DEPLOYMENT.md)**: Production deployment instructions
- **[Real-time Setup](REALTIME_SETUP.md)**: Real-time integration guide
- **[Test Cases Report](COMPREHENSIVE_TEST_CASES_REPORT.md)**: Complete testing documentation
- **[Docker Guide](../DOCKER_DEPLOYMENT_GUIDE.md)**: Docker deployment guide

### **Additional Resources**

- **[Technical Assessment](../TECHNICAL_EXPERT_ASSESSMENT.md)**: Expert technical evaluation
- **[Feature Verification](../FEATURE_VERIFICATION_REPORT.md)**: Feature implementation verification
- **[Agents Guide](../AGENTS.md)**: Development guidelines

## 🤝 **Contributing**

### **Development Workflow**

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes with proper tests
4. Run the test suite: `pytest tests/`
5. Commit: `git commit -m 'Add amazing feature'`
6. Push: `git push origin feature/amazing-feature`
7. Open a Pull Request

### **Code Standards**

- Follow PEP 8 style guidelines
- Add type hints for all functions
- Write comprehensive docstrings
- Include unit tests for new features
- Update documentation as needed

## 📄 **License**

This project is licensed under the MIT License. See the [LICENSE](../LICENSE) file for details.

## 📞 **Support**

### **Getting Help**

- 📚 **Documentation**: Check the comprehensive docs/ directory
- 🐛 **Issues**: Report bugs on GitHub Issues
- 💡 **Features**: Request features on GitHub Discussions
- 📧 **Contact**: Open an issue for support questions

### **Community**

- **GitHub Discussions**: For questions and community support
- **Issue Tracker**: For bug reports and feature requests
- **Documentation**: Comprehensive guides and API reference

---

## 🎉 **Ready to Get Started?**

```bash
# Quick start for voice interaction
cp .env.example .env
# Add your OpenAI API key to .env
python src/main.py
# Choose option 2 (Voice Mode)
# Start speaking - full conversation ready! 🎤
```

**Your NPCL Voice Assistant is production-ready and fully functional! 🚀**

---

**📝 Last Updated**: December 2024  
**🎯 Version**: 2.0  
**🏢 Organization**: NPCL (Noida Power Corporation Limited)  
**⭐ Status**: Production Ready