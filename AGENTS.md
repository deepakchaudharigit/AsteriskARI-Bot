# Repository Guidelines

## Project Structure & Module Organization

The codebase is organized with `src/voice_assistant/` as the main application package containing modular components: `core/` for business logic and session management, `ai/` for OpenAI integration, `audio/` for real-time audio processing, `telephony/` for Asterisk ARI integration, and `tools/` for external services. Tests are located in `tests/` with comprehensive coverage including unit, integration, performance, and end-to-end tests. Configuration files are in `config/`, Docker setups in `docker/`, Kubernetes manifests in `kubernetes/`, and documentation in `docs/`.

## Build, Test, and Development Commands

```bash
# Start the voice assistant
python src/main.py

# Start ARI bot directly
python ari_bot.py

# Start real-time server
python src/run_realtime_server.py

# Run comprehensive tests
python tests/run_tests.py

# Run specific test categories
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest tests/performance/ -v

# Development with Docker
docker-compose up -d

# Production deployment
docker-compose -f docker-compose.production.yml up -d
```

## Coding Style & Naming Conventions

- **Indentation**: 4 spaces (no tabs)
- **File naming**: snake_case for Python files (e.g., `voice_assistant.py`, `session_manager.py`)
- **Function/variable naming**: snake_case with descriptive names
- **Class naming**: PascalCase (e.g., `VoiceAssistant`, `OpenAIRealtimeClient`)
- **Test files**: `test_*.py` pattern in appropriate test directories
- **Linting**: Follow PEP 8 standards with comprehensive type hints

## Testing Guidelines

- **Framework**: pytest with asyncio support and comprehensive markers
- **Test files**: Located in `tests/` with categories: unit, integration, performance, audio, websocket, e2e
- **Running tests**: `pytest tests/` or `python tests/run_tests.py --coverage`
- **Coverage**: Maintain >95% line coverage with `pytest --cov=src/voice_assistant --cov-report=html`
- **Test structure**: Each component has corresponding unit tests, integration tests validate component interactions

## Commit & Pull Request Guidelines

- **Commit format**: Descriptive messages focusing on features (e.g., "bhojpuri voice added", "multimodels language added")
- **PR process**: Include test validation with "100% testcases passing" confirmation
- **Branch naming**: Feature-based branches with clear naming conventions
- **Testing requirement**: All 200+ test cases must pass before merge

---

# Repository Tour

## 🎯 What This Repository Does

NPCL-Asterisk-ARI-Assistant is a sophisticated, enterprise-grade voice assistant system designed specifically for NPCL (Noida Power Corporation Limited) customer service. It combines OpenAI's GPT-4 Realtime API with Asterisk PBX telephony infrastructure to provide seamless, real-time voice-based customer support for power utility services.

**Key responsibilities:**
- Real-time voice conversation with <20ms audio processing latency
- Multi-language customer service (English, Hindi, Bhojpuri, Bengali)
- Power utility-specific services (bill inquiries, outage reporting, connection requests)

---

## 🏗️ Architecture Overview

### System Context
```
[Phone Callers] → [Asterisk PBX] → [FastAPI Server] → [OpenAI Realtime API]
                        ↓                ↓
              [External Media WebSocket] ← [Voice Assistant Core]
                        ↓
                   [Redis Cache] + [Session Management]
```

### Key Components
- **Voice Assistant Core** - Central orchestration, session management, and business logic
- **OpenAI Realtime Client** - Real-time AI conversation with WebSocket communication
- **Audio Processor** - Voice Activity Detection, format conversion, and real-time processing
- **ARI Handler** - Asterisk REST Interface integration for telephony events
- **External Media Handler** - Bidirectional audio streaming via WebSocket
- **Session Manager** - Conversation tracking, state management, and metrics collection

### Data Flow
1. **Call Initiation**: Caller dials extension, Asterisk triggers StasisStart event to ARI handler
2. **Session Creation**: Voice assistant creates session, establishes external media WebSocket connection
3. **Audio Processing**: Real-time audio streaming with VAD, format conversion (slin16), and buffering
4. **AI Processing**: OpenAI Realtime API processes voice input and generates intelligent responses
5. **Response Delivery**: AI response converted to audio and streamed back through Asterisk to caller

---

## 📁 Project Structure [Partial Directory Tree]

```
NPCL-Asterisk-ARI-Assistant/
├── src/                           # Main application code
│   ├── voice_assistant/           # Core voice assistant package
│   │   ├── core/                  # Business logic and session management
│   │   ├── ai/                    # OpenAI integration and AI clients
│   │   ├── audio/                 # Real-time audio processing and VAD
│   │   ├── telephony/             # Asterisk ARI integration
│   │   ├── tools/                 # External service integrations
│   │   ├── i18n/                  # Multi-language support
│   │   ├── security/              # Security and validation
│   │   ├── observability/         # Monitoring and metrics
│   │   └── utils/                 # Utility functions and helpers
│   ├── main.py                    # Main application entry point
│   └── run_realtime_server.py     # Real-time FastAPI server
├── tests/                         # Comprehensive test suite (200+ tests)
│   ├── unit/                      # Unit tests for individual components
│   ├── integration/               # Component interaction tests
│   ├── performance/               # Real-time performance validation
│   ├── audio/                     # Audio processing and VAD tests
│   ├── websocket/                 # WebSocket communication tests
│   ├── e2e/                       # End-to-end workflow tests
│   ├── mocks/                     # Mock objects for testing
│   └── utils/                     # Test utilities and helpers
├── config/                        # Configuration management
│   └── settings.py                # Pydantic-based configuration
├── docker/                        # Docker configurations
│   └── Dockerfile.asterisk20      # Asterisk 20 LTS container
├── kubernetes/                    # Kubernetes deployment manifests
├── docs/                          # Comprehensive documentation
├── scripts/                       # Utility and setup scripts
├── asterisk-config/               # Asterisk PBX configuration
├── sounds/                        # Audio resources and recordings
└── ari_bot.py                     # Direct ARI bot entry point
```

### Key Files to Know

| File | Purpose | When You'd Touch It |
|------|---------|---------------------|
| `src/main.py` | Main application entry point | Adding new interaction modes |
| `ari_bot.py` | Direct ARI bot launcher | Quick ARI testing and debugging |
| `src/run_realtime_server.py` | Real-time FastAPI server | Modifying API endpoints |
| `config/settings.py` | Pydantic configuration management | Changing app settings or adding new config |
| `docker-compose.yml` | Development environment setup | Modifying development stack |
| `requirements.txt` | Python dependencies | Adding new libraries |
| `pytest.ini` | Test configuration | Modifying test behavior |
| `src/voice_assistant/core/assistant.py` | Main voice assistant orchestrator | Core business logic changes |
| `src/voice_assistant/ai/openai_realtime_client_enhanced.py` | OpenAI Realtime API integration | AI behavior modifications |
| `src/voice_assistant/telephony/realtime_ari_handler.py` | Advanced ARI event handling | Telephony integration changes |

---

## 🔧 Technology Stack

### Core Technologies
- **Language:** Python 3.8+ (3.11 recommended) - Chosen for AI/ML ecosystem and rapid development
- **AI Framework:** OpenAI GPT-4 Realtime API - Real-time conversational AI with voice capabilities
- **Web Framework:** FastAPI with uvicorn - High-performance async API framework
- **Telephony:** Asterisk 20 LTS with ARI - Enterprise-grade PBX integration

### Key Libraries
- **websockets** - Real-time WebSocket communication for audio streaming
- **pydantic** - Configuration management and data validation
- **pygame** - Audio playback and processing
- **numpy** - Audio data manipulation and processing
- **pytest** - Comprehensive testing framework with async support
- **requests** - HTTP client for API integrations

### Development Tools
- **Docker & Docker Compose** - Containerization and development environment
- **Kubernetes** - Production orchestration and scaling
- **Redis** - Session management and caching
- **Prometheus & Grafana** - Monitoring and observability
- **pytest with coverage** - Testing with >95% coverage requirement

---

## 🌐 External Dependencies

### Required Services
- **OpenAI Realtime API** - Core AI conversation engine, critical for all voice interactions
- **Asterisk PBX** - Telephony infrastructure, required for phone call handling
- **Redis** - Session state management and caching, important for multi-session support

### Optional Integrations
- **Weather API** - External weather information service, fallback to basic responses
- **Prometheus** - Metrics collection, system continues without monitoring
- **Grafana** - Visualization dashboard, optional for production monitoring

### Environment Variables

```bash
# Required
OPENAI_API_KEY=          # OpenAI API key for GPT-4 Realtime access
ARI_BASE_URL=            # Asterisk ARI endpoint (default: http://localhost:8088/ari)
ARI_USERNAME=            # Asterisk ARI username (default: asterisk)
ARI_PASSWORD=            # Asterisk ARI password (default: 1234)

# Audio Configuration
AUDIO_SAMPLE_RATE=       # Audio sample rate (default: 16000)
AUDIO_FORMAT=            # Audio format (default: slin16)
EXTERNAL_MEDIA_PORT=     # External media WebSocket port (default: 8090)

# Optional
WEATHER_API_KEY=         # Weather service API key
LOG_LEVEL=               # Logging verbosity (default: INFO)
ENABLE_PERFORMANCE_LOGGING= # Performance monitoring (default: false)
```

---

## 🔄 Common Workflows

### Voice Interaction Workflow
1. **Call Setup**: Caller dials extension (1000), Asterisk sends StasisStart event to ARI handler
2. **Session Initialization**: Voice assistant creates session, establishes external media WebSocket
3. **Audio Streaming**: Bidirectional audio streaming begins with real-time processing
4. **Conversation Loop**: VAD detects speech → OpenAI processes → AI responds → Audio output
5. **Call Termination**: Caller hangs up, session cleanup and metrics collection

**Code path:** `ari_handler.py` → `session_manager.py` → `openai_realtime_client.py` → `external_media_handler.py`

### Real-time Audio Processing
1. **Audio Input**: Asterisk streams slin16 audio via external media WebSocket
2. **Format Processing**: Audio processor handles format conversion and buffering
3. **Voice Activity Detection**: VAD analyzes audio for speech vs silence
4. **AI Integration**: Speech segments sent to OpenAI Realtime API
5. **Response Generation**: AI response audio streamed back to caller

**Code path:** `external_media_handler.py` → `realtime_audio_processor.py` → `openai_realtime_client_enhanced.py`

---

## 📈 Performance & Scale

### Performance Considerations
- **Audio Processing Latency**: <20ms requirement for real-time conversation
- **Voice Activity Detection**: <10ms processing time for natural flow
- **Memory Usage**: <100MB per active session for scalability
- **Concurrent Sessions**: Designed for 100+ simultaneous calls

### Monitoring
- **Real-time Metrics**: Audio latency, session count, error rates
- **Health Checks**: Component status monitoring via `/health` endpoints
- **Performance Tracking**: Built-in performance monitor with detailed metrics
- **Observability**: Prometheus metrics and Grafana dashboards available

---

## 🚨 Things to Be Careful About

### 🔒 Security Considerations
- **API Key Management**: OpenAI API keys stored in environment variables, never in code
- **Input Validation**: All user input sanitized through security manager
- **Rate Limiting**: Built-in protection against abuse and DDoS attacks
- **Audio Data**: Real-time audio streams not persisted unless explicitly configured

### ⚠️ Critical Dependencies
- **OpenAI API Availability**: System requires active OpenAI API connection for AI features
- **Asterisk Configuration**: Proper ARI configuration essential for telephony integration
- **Network Latency**: Real-time performance depends on low-latency network connections
- **Resource Management**: Monitor memory usage with multiple concurrent sessions

*Update to last commit: d3a4d487605273f1504a21c9c449b3d61c5fe203*