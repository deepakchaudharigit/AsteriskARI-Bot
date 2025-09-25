# Repository Guidelines

## Project Structure & Module Organization

The codebase is organized as a professional Python package under `src/voice_assistant/` with clear separation of concerns:
- **Core logic**: `src/voice_assistant/core/` - Assistant classes, session management, performance monitoring
- **AI integration**: `src/voice_assistant/ai/` - OpenAI GPT-4 Realtime client, function calling, NPCL prompts
- **Audio processing**: `src/voice_assistant/audio/` - Speech recognition, TTS, real-time audio processing, VAD
- **Telephony**: `src/voice_assistant/telephony/` - Asterisk ARI handlers, external media, RTP streaming
- **Configuration**: `config/` - Pydantic v2 settings management with validation
- **Tests**: `tests/` - Comprehensive test suite with 400+ test cases across unit, integration, performance, and e2e
- **Asterisk config**: `asterisk-config/` - PBX configuration files for telephony integration

## Build, Test, and Development Commands

```bash
# Start the voice assistant (standalone mode)
python src/main.py

# Run real-time ARI server for telephony integration
python src/run_realtime_server.py

# Run all tests (400+ test cases)
pytest
python run_all_tests.py

# Run with coverage reporting
pytest --cov=src/voice_assistant --cov-report=html

# Start Asterisk container for telephony features
docker-compose up asterisk

# Setup real-time environment
python scripts/setup_realtime.py
```

## Coding Style & Naming Conventions

- **Indentation**: 4 spaces (no tabs)
- **File naming**: snake_case for modules, PascalCase for classes
- **Function/variable naming**: snake_case with descriptive names
- **Type hints**: Full type annotations throughout codebase
- **Async patterns**: async/await for I/O operations and WebSocket handling
- **Configuration**: Pydantic v2 models with validation
- **Linting**: Black for formatting, flake8 for style checking

## Testing Guidelines

- **Framework**: pytest with asyncio support
- **Test structure**: `tests/unit/`, `tests/integration/`, `tests/performance/`, `tests/e2e/`
- **Running tests**: `pytest` or `python run_all_tests.py`
- **Coverage**: Comprehensive coverage with HTML reports
- **Markers**: Use `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.audio` for categorization

## Commit & Pull Request Guidelines

- **Commit format**: Descriptive messages focusing on functionality (e.g., "100% testcases passing", "added all pro features and testcases")
- **Testing requirement**: All 400+ test cases must pass before commits
- **Feature development**: Incremental commits with working functionality
- **Documentation**: Update relevant docs when adding new features

---

# Repository Tour

## 🎯 What This Repository Does

NPCL-Asterisk-ARI-Assistant is a professional voice assistant system powered by OpenAI's GPT-4 Realtime model, designed specifically for NPCL (Noida Power Corporation Limited) customer service with telephony integration through Asterisk PBX.

**Key responsibilities:**
- Handle incoming phone calls through Asterisk PBX with real-time voice processing
- Provide NPCL customer service for power connection inquiries and complaint management
- Process voice conversations using OpenAI GPT-4 Realtime for intelligent responses
- Support 12 languages including Hindi, Bengali, Bhojpuri, and other Indian languages

---

## 🏗️ Architecture Overview

### System Context
```
[Phone Caller] → [Asterisk PBX] → [FastAPI Server] → [OpenAI GPT-4 Realtime]
                       ↓              ↓                ↓
                 [Audio Files] ← [TTS Engine] ← [AI Response]
                       ↓
              [External Media WebSocket] ← [OpenAI Realtime API]
```

### Key Components
- **Asterisk PBX** - Handles SIP calls, audio recording/playback, and telephony events via ARI
- **FastAPI Server** - Processes ARI events and orchestrates conversation flow with async handling
- **OpenAI Integration** - Uses OpenAI GPT-4 Realtime for intelligent responses with function calling
- **Audio Processing Pipeline** - OpenAI Whisper for STT, OpenAI TTS for voice synthesis
- **External Media Handler** - WebSocket-based bidirectional audio streaming for real-time conversations
- **Session Manager** - Tracks conversation state, call duration, and user interactions
- **Multilingual Support** - 12 language support with automatic language detection

### Data Flow
1. **Caller dials extension 1000** - Asterisk answers and triggers Stasis application
2. **ARI events sent to FastAPI** - Call events (StasisStart, ChannelTalkingStarted) trigger handlers
3. **Real-time audio streaming** - External media WebSocket enables bidirectional audio with voice activity detection
4. **AI processing** - Speech converted to text, processed by OpenAI GPT-4 Realtime, and synthesized back to speech
5. **NPCL customer service** - Specialized prompts handle power connection inquiries and complaint management

---

## 📁 Project Structure [Partial Directory Tree]

```
NPCL-Asterisk-ARI-Assistant/
├── src/                           # Main application source code
│   ├── voice_assistant/           # Core voice assistant package
│   │   ├── core/                  # Core assistant logic and session management
│   │   │   ├── assistant.py       # Main VoiceAssistant class with conversation loop
│   │   │   ├── modern_assistant.py # Modern assistant with OpenAI Realtime API integration
│   │   │   ├── multilingual_assistant.py # 12-language support assistant
│   │   │   ├── session_manager.py # Call session tracking and state management
│   │   │   └── performance.py     # Performance monitoring and metrics
│   │   ├── ai/                    # AI integration and language models
│   │   │   ├── openai_realtime_client.py   # OpenAI GPT-4 Realtime client with fallback handling
│   │   │   ├── openai_realtime_client_enhanced.py # Enhanced OpenAI Realtime API WebSocket client
│   │   │   ├── function_calling.py # Function calling capabilities
│   │   │   └── npcl_prompts.py    # NPCL-specific system prompts
│   │   ├── audio/                 # Audio processing and voice handling
│   │   │   ├── speech_recognition.py # OpenAI Whisper integration
│   │   │   ├── text_to_speech.py     # OpenAI TTS with audio file management
│   │   │   ├── realtime_audio_processor.py # Real-time audio processing with VAD
│   │   │   ├── multilingual_tts.py       # Multi-language TTS support
│   │   │   ├── multilingual_stt.py       # Multi-language STT support
│   │   │   └── improved_vad.py          # Voice Activity Detection algorithms
│   │   ├── telephony/             # Asterisk PBX and telephony integration
│   │   │   ├── ari_handler.py     # Basic Asterisk ARI event handling
│   │   │   ├── realtime_ari_handler.py # Advanced real-time ARI with external media
│   │   │   ├── external_media_handler.py # WebSocket handler for bidirectional audio
│   │   │   └── rtp_streaming_handler.py  # RTP audio streaming capabilities
│   │   ├── tools/                 # External tools and integrations
│   │   │   └── weather_tool.py    # Weather information tool for function calling
│   │   ├── i18n/locales/          # Multi-language support
│   │   │   ├── en-IN/             # English (India)
│   │   │   ├── hi-IN/             # Hindi
│   │   │   ├── bn-IN/             # Bengali
│   │   │   └── bho-IN/            # Bhojpuri
│   │   └── utils/                 # Utilities and helper functions
│   ├── main.py                    # Main entry point with 12-language support
│   └── run_realtime_server.py     # FastAPI server for real-time ARI integration
├── config/                        # Configuration management
│   └── settings.py                # Pydantic v2 settings with validation
├── tests/                         # Comprehensive test suite (400+ tests)
│   ├── unit/                      # Unit tests for individual components
│   ├── integration/               # Integration tests for component interactions
│   ├── performance/               # Performance and latency tests
│   ├── audio/                     # Audio processing quality tests
│   ├── e2e/                       # End-to-end workflow tests
│   └── conftest.py                # Test configuration and fixtures
├── asterisk-config/               # Asterisk PBX configuration
│   ├── extensions.conf            # Dialplan with OpenAI voice assistant extensions
│   ├── ari.conf                   # ARI user credentials and settings
│   └── sip.conf                   # SIP endpoint configuration
├── docker-compose.yml             # Asterisk container orchestration
├── requirements.txt               # Python dependencies
└── scripts/                       # Setup and utility scripts
    └── setup_realtime.py          # Automated environment setup
```

### Key Files to Know

| File | Purpose | When You'd Touch It |
|------|---------|---------------------|
| `src/main.py` | Main application entry point with 12-language support | Adding new assistant modes or languages |
| `src/run_realtime_server.py` | FastAPI server for real-time ARI integration | Modifying telephony API endpoints |
| `src/voice_assistant/core/assistant.py` | Core voice assistant with conversation management | Changing conversation flow or state handling |
| `src/voice_assistant/core/multilingual_assistant.py` | 12-language support assistant | Adding new languages or language features |
| `src/voice_assistant/ai/openai_realtime_client.py` | OpenAI GPT-4 Realtime integration with fallbacks | Modifying AI model parameters or prompts |
| `src/voice_assistant/telephony/realtime_ari_handler.py` | Advanced ARI handler with external media | Adding new telephony features or call handling |
| `config/settings.py` | Pydantic configuration with validation | Adding new configuration options |
| `asterisk-config/extensions.conf` | Asterisk dialplan configuration | Adding new phone extensions or call routing |
| `docker-compose.yml` | Asterisk container setup | Modifying telephony infrastructure |
| `pytest.ini` | Test configuration and markers | Changing test execution parameters |

---

## 🔧 Technology Stack

### Core Technologies
- **Language:** Python 3.8+ (Python 3.13 recommended) - Chosen for rich AI/ML ecosystem and async capabilities
- **Framework:** FastAPI - High-performance async web framework for ARI event handling and API endpoints
- **PBX:** Asterisk with ARI - Open-source telephony platform with REST interface for call control
- **Containerization:** Docker - Simplified Asterisk deployment with volume mounting for audio files

### Key Libraries
- **openai>=1.0.0** - OpenAI GPT-4 Realtime for conversation and real-time voice
- **websockets>=10.0,<13.0** - WebSocket communication for OpenAI Realtime API and external media
- **fastapi>=0.104.0** - Async web framework with automatic API documentation
- **pydantic>=2.5.0** - Data validation and serialization with v2 features
- **SpeechRecognition>=3.10.0** - OpenAI Whisper for voice input
- **gtts>=2.4.0** - OpenAI Text-to-Speech for voice output
- **numpy>=1.24.0** - Audio processing and Voice Activity Detection algorithms
- **requests>=2.31.0** - HTTP client for Asterisk REST Interface communication

### Development Tools
- **pytest>=7.4.0** - Testing framework with 400+ comprehensive test cases
- **black>=23.0.0** - Code formatting for consistent style
- **uvicorn>=0.24.0** - ASGI server for running FastAPI applications
- **python-dotenv>=1.0.0** - Environment variable management from .env files

---

## 🌐 External Dependencies

### Required Services
- **OpenAI API** - GPT-4 Realtime model access for conversation and real-time voice
- **Asterisk PBX** - Telephony platform for SIP call handling, audio recording, and ARI event generation
- **Audio System** - Microphone and speakers for standalone voice mode, or SIP endpoints for telephony

### Optional Integrations
- **Docker** - Containerized Asterisk deployment with pre-configured settings
- **SIP Phones** - Hardware or software SIP clients for testing telephony integration
- **Prometheus/Grafana** - Monitoring and metrics collection (enterprise features)

### Environment Variables

```bash
# Required
OPENAI_API_KEY=          # OpenAI API key for GPT-4 Realtime access
ARI_BASE_URL=            # Asterisk ARI endpoint (default: http://localhost:8088/ari)
ARI_USERNAME=            # ARI authentication username (default: asterisk)
ARI_PASSWORD=            # ARI authentication password (default: 1234)

# Audio Configuration
AUDIO_FORMAT=slin16      # Audio format optimized for Asterisk (16-bit signed linear PCM)
AUDIO_SAMPLE_RATE=16000  # Sample rate in Hz for optimal OpenAI Realtime API performance
AUDIO_CHUNK_SIZE=320     # Audio chunk size for real-time processing

# AI Settings
OPENAI_MODEL=gpt-4o-realtime-preview-2024-10-01        # AI model version
OPENAI_VOICE=alloy   # Voice for real-time voice
# Using OpenAI for AI integrationng
MAX_TOKENS=150                       # Maximum tokens for AI responses
TEMPERATURE=0.7                      # AI response creativity

# Voice Activity Detection
VAD_ENERGY_THRESHOLD=300             # VAD energy threshold
VAD_SILENCE_THRESHOLD=0.5            # VAD silence threshold in seconds
VAD_SPEECH_THRESHOLD=0.1             # VAD speech threshold in seconds

# Assistant Settings
ASSISTANT_NAME=NPCL Assistant        # Assistant name
VOICE_LANGUAGE=en                    # Default voice language
LISTEN_TIMEOUT=20.0                  # Listen timeout in seconds
PHRASE_TIME_LIMIT=15.0               # Phrase time limit in seconds

# External Media Settings
EXTERNAL_MEDIA_HOST=localhost        # External media host
EXTERNAL_MEDIA_PORT=8090             # WebSocket port for external media
STASIS_APP=openai-voice-assistant    # Asterisk Stasis application name

# Optional
LOG_LEVEL=INFO                       # Logging level
ENABLE_INTERRUPTION_HANDLING=true   # Enable interruption handling
MAX_CALL_DURATION=3600               # Maximum call duration in seconds
AUTO_ANSWER_CALLS=true               # Auto answer incoming calls
```

---

## 🔄 Common Workflows

### Phone Call Conversation Flow
1. **Caller dials extension 1000** - Asterisk routes call to Stasis application "openai-voice-assistant"
2. **StasisStart event triggers** - FastAPI receives ARI event and initializes session with call details
3. **External media WebSocket established** - Bidirectional audio streaming setup for real-time processing
4. **Voice Activity Detection active** - System detects when caller starts/stops speaking
5. **Real-time AI processing** - Speech converted to text, processed by OpenAI GPT-4 Realtime, synthesized to speech
6. **NPCL customer service context** - AI responds with power connection assistance and complaint handling
7. **Session cleanup on hangup** - Resources cleaned up when call ends

**Code path:** `extensions.conf` → `realtime_ari_handler.handle_stasis_start()` → `external_media_handler.handle_audio()` → `openai_realtime_client.process_audio()`

### Standalone Voice Assistant Mode
1. **Language selection** - User chooses from 12 supported languages (English, Hindi, Bengali, Bhojpuri, etc.)
2. **Microphone initialization** - PyAudio setup with ambient noise calibration
3. **Continuous listening loop** - Speech recognition with 15-second timeout and phrase limits
4. **AI conversation processing** - User input processed by OpenAI GPT-4 Realtime with NPCL context
5. **Local audio playback** - TTS responses played through system speakers with volume control
6. **Command handling** - Voice commands like "quit", "exit" for graceful termination

**Code path:** `main.py` → `MultilingualVoiceAssistant.run_conversation_loop()` → `process_conversation_turn()` → `openai_client.generate_response()`

### Real-time OpenAI Realtime API Integration
1. **WebSocket connection establishment** - Direct connection to OpenAI Realtime API with authentication
2. **Audio format negotiation** - slin16 format setup for optimal Asterisk compatibility
3. **Bidirectional streaming** - Simultaneous audio input/output with voice activity detection
4. **Interruption handling** - Natural conversation flow with mid-response interruptions
5. **Session state management** - Complete conversation context tracking and cleanup

**Code path:** `modern_assistant.py` → `OpenAIRealtimeClient.start_session()` → WebSocket message handling → `external_media_handler.process_audio()`

---

## 📈 Performance & Scale

### Performance Considerations
- **Real-time audio processing** - 320-sample chunks (20ms) for low-latency voice interaction
- **Async architecture** - FastAPI with async/await for handling multiple concurrent calls
- **Audio file management** - Efficient temporary file handling with automatic cleanup
- **Memory optimization** - Streaming audio processing to minimize memory footprint
- **Connection pooling** - Reusable HTTP connections for Asterisk ARI communication

### Monitoring
- **Call metrics** - Session duration, success rates, audio quality measurements
- **Performance tracking** - Response times, CPU usage, memory consumption via psutil
- **Error handling** - Comprehensive logging with structured error context
- **Health checks** - System status endpoints for monitoring external dependencies
- **Audio quality** - Voice Activity Detection accuracy and audio processing latency

### Scalability Features
- **Horizontal scaling** - Multiple FastAPI instances can handle different call volumes
- **Load balancing** - Enterprise features for distributing calls across instances
- **Database clustering** - Redis and PostgreSQL clustering support for session storage
- **Service discovery** - Consul integration for dynamic service registration
- **Auto-scaling** - Automatic instance scaling based on call volume and system metrics

---

## 🚨 Things to Be Careful About

### 🔒 Security Considerations
- **API key protection** - Google API keys stored in environment variables, never in code
- **ARI authentication** - Basic auth credentials for Asterisk REST Interface access
- **Input validation** - Pydantic v2 models with comprehensive validation and sanitization
- **Rate limiting** - Token bucket rate limiting for API calls and user interactions
- **Audit logging** - Comprehensive audit trails for security events and user actions
- **Encryption** - TLS/SSL for all external communications and sensitive data handling

### ⚠️ Operational Notes
- **Audio file timing** - 2-second delay after recording to ensure file completion before processing
- **WebSocket management** - Automatic reconnection and error handling for Live API connections
- **Container dependencies** - FastAPI server requires Asterisk container for telephony features
- **Resource monitoring** - CPU and memory usage tracking with configurable thresholds
- **Call duration limits** - Maximum call duration enforcement to prevent resource exhaustion
- **Graceful shutdown** - Proper cleanup of active calls and resources during system shutdown

### 🔧 Maintenance Tasks
- **Log rotation** - Automatic cleanup of audio files and application logs
- **API key rotation** - Periodic renewal of Google API credentials
- **Dependency updates** - Regular updates of Python packages with compatibility testing
- **Performance tuning** - Monitoring and optimization of audio processing parameters
- **Health monitoring** - Continuous verification of Asterisk connectivity and AI service availability

### 🌍 Multilingual Considerations
- **Language detection** - Automatic language detection may require training data updates
- **TTS voice quality** - Different languages may have varying voice quality and availability
- **Cultural context** - NPCL prompts are customized for Indian cultural context and power utility terminology
- **Character encoding** - Proper UTF-8 handling for non-Latin scripts (Hindi, Bengali, etc.)
- **Audio processing** - Some languages may require different audio processing parameters

---

*Last updated: 2025-01-20 UTC*
*Project version: 3.0 - OpenAI GPT-4 Realtime Edition with ARI Integration*
*Test coverage: 400+ comprehensive test cases*
*Language support: 12 Indian languages including Hindi, Bengali, Bhojpuri*