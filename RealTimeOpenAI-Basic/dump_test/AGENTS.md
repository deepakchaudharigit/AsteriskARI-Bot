# Repository Guidelines

## Project Structure & Module Organization

- **Root directory**: Main application files and launcher scripts
- **Source code**: `voice_chatbot.py` (general AI), `npcl_voice_assistant.py` (NPCL customer care)
- **Configuration**: `.env` (API keys), `requirements.txt` (dependencies), `.env.example` (template)
- **Extended modules**: `npcl_assistant/` (additional NPCL functionality with Asterisk integration)
- **Development archive**: `dump_test/` (test versions and development history)
- **Virtual environment**: `venv/` (Python dependencies, auto-generated)

## Build, Test, and Development Commands

```bash
# Setup virtual environment and dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure API key
cp .env.example .env
# Edit .env with your OPENAI_API_KEY

# Start the voice assistant
chmod +x start_chatbot.sh
./start_chatbot.sh

# Run individual assistants directly
python3 voice_chatbot.py          # General AI assistant
python3 npcl_voice_assistant.py   # NPCL customer care assistant
```

## Coding Style & Naming Conventions

- **Indentation**: 4 spaces (Python standard)
- **File naming**: Snake_case for Python files (`voice_chatbot.py`, `npcl_voice_assistant.py`)
- **Class naming**: PascalCase (`RealtimeVoiceChatbot`, `NPCLVoiceAssistant`)
- **Function/variable naming**: Snake_case (`_handle_realtime_event`, `audio_output_queue`)
- **Constants**: UPPER_CASE (`OPENAI_API_KEY`, `NPCL_CUSTOMER_NAMES`)

## Testing Guidelines

- **Framework**: Manual testing with real voice interaction
- **Test files**: Located in `dump_test/` directory with various test scenarios
- **Running tests**: Execute test files individually: `python3 dump_test/test_*.py`
- **Audio testing**: `dump_test/test_audio.py` for microphone and speaker verification

## Commit & Pull Request Guidelines

- **Commit format**: Descriptive messages focusing on functionality (based on file analysis)
- **Development process**: Archive working versions in `dump_test/` before major changes
- **Production code**: Keep main directory clean with only production-ready versions
- **Branch naming**: Feature-based development with clean main branch

---

# Repository Tour

## 🎯 What This Repository Does

RealTimeOpenAI-Basic is a production-ready voice chatbot system that enables natural voice-to-voice conversations with AI using OpenAI's Realtime API. It provides both a general AI assistant and a specialized NPCL customer care assistant for power issue support.

**Key responsibilities:**
- Real-time bidirectional voice communication with AI
- Natural conversation interruption and flow management
- Specialized customer service simulation for power utilities
- Clean terminal-based user interface with audio streaming

---

## 🏗️ Architecture Overview

### System Context
```
[User Voice Input] → [PyAudio] → [WebSocket] → [OpenAI Realtime API]
                                      ↓
[Audio Output] ← [PyAudio] ← [WebSocket] ← [AI Response Stream]
```

### Key Components
- **RealtimeVoiceChatbot** - Core voice interaction engine with WebSocket management
- **NPCLVoiceAssistant** - Specialized customer care assistant with predefined workflows
- **Audio Handlers** - Separate input/output processors for real-time audio streaming
- **Event System** - Real-time event processing for conversation flow management
- **Configuration Manager** - Environment-based settings and API key management

### Data Flow
1. **Audio Capture** - PyAudio captures microphone input in 24kHz PCM16 format
2. **WebSocket Streaming** - Audio data is base64-encoded and streamed to OpenAI API
3. **AI Processing** - OpenAI Realtime API processes voice and generates responses
4. **Response Streaming** - AI audio responses are streamed back via WebSocket
5. **Audio Playback** - Decoded audio is played through speakers with real-time output

---

## 📁 Project Structure [Partial Directory Tree]

```
RealTimeOpenAI-Basic/
├── voice_chatbot.py              # Main general AI voice assistant
├── npcl_voice_assistant.py       # NPCL customer care assistant
├── start_chatbot.sh              # Interactive launcher script
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment configuration template
├── .env                         # API keys (create from template)
├── README.md                    # Project documentation
├── algo_steps.txt               # Development notes (empty)
├── npcl_assistant/              # Extended NPCL functionality
│   ├── main.py                  # NPCL application coordinator
│   ├── config.py                # NPCL-specific configuration
│   ├── audio_processor.py       # Audio processing utilities
│   ├── asterisk_ari.py          # Asterisk integration (future)
│   └── npcl_voice_assistant.py  # Alternative NPCL implementation
└── dump_test/                   # Development archive
    ├── README.md                # Archive documentation
    ├── test_*.py                # Various test implementations
    ├── voice_chatbot_*.py       # Development versions
    └── setup.py                 # Setup utilities
```

### Key Files to Know

| File | Purpose | When You'd Touch It |
|------|---------|---------------------|
| `voice_chatbot.py` | Main general AI assistant | Adding features to general conversation |
| `npcl_voice_assistant.py` | NPCL customer care assistant | Modifying customer service workflows |
| `start_chatbot.sh` | Interactive launcher | Changing startup options or checks |
| `requirements.txt` | Python dependencies | Adding new libraries |
| `.env` | API keys and configuration | Setting up OpenAI API access |
| `npcl_assistant/config.py` | NPCL configuration | Modifying NPCL-specific settings |
| `dump_test/README.md` | Development history | Understanding project evolution |

---

## 🔧 Technology Stack

### Core Technologies
- **Language:** Python 3.8+ (3.13 in development) - Chosen for excellent audio processing libraries
- **API:** OpenAI Realtime API - Provides state-of-the-art voice AI capabilities
- **Audio:** PyAudio - Cross-platform audio I/O for real-time processing
- **Communication:** WebSockets - Enables bidirectional real-time streaming

### Key Libraries
- **openai>=1.40.0** - Official OpenAI API client with Realtime API support
- **websockets>=12.0** - WebSocket client for real-time communication
- **pyaudio>=0.2.11** - Audio input/output handling
- **colorama>=0.4.6** - Cross-platform terminal color support
- **python-dotenv>=1.0.0** - Environment variable management
- **numpy>=1.24.0** - Audio data processing and manipulation

### Development Tools
- **Virtual Environment** - Isolated Python dependency management
- **Shell Scripts** - Automated setup and launch procedures
- **Environment Configuration** - Secure API key and settings management

---

## 🌐 External Dependencies

### Required Services
- **OpenAI Realtime API** - Core AI voice processing service (requires API key with Realtime access)
- **Audio System** - Microphone and speakers for voice input/output
- **Internet Connection** - Stable connection for WebSocket streaming

### Optional Integrations
- **Asterisk ARI** - Future telephony integration for NPCL assistant
- **OpenAI GPT-4 API** - Alternative AI backend (configured but not implemented)

### Environment Variables

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here    # OpenAI API key with Realtime access

# Optional Voice Configuration
VOICE_MODEL=alloy                          # AI voice model (alloy, echo, fable, onyx, nova, shimmer)
SPEECH_MODEL=whisper-1                     # Speech recognition model
TTS_MODEL=tts-1-hd                         # Text-to-speech model

# Optional Audio Configuration
SAMPLE_RATE=16000                          # Audio sample rate
CHUNK_SIZE=1024                            # Audio buffer size
CHANNELS=1                                 # Audio channels (mono)
```

---

## 🔄 Common Workflows

### General AI Conversation
1. **Launch Assistant** - Run `./start_chatbot.sh` and select option 1
2. **Voice Interaction** - Speak naturally when prompted
3. **AI Response** - Assistant processes speech and responds with voice
4. **Interruption Support** - Speak during AI response to interrupt naturally
5. **Session Management** - Say "quit", "bye", or "exit" to end conversation

**Code path:** `voice_chatbot.py` → `RealtimeVoiceChatbot` → `WebSocket` → `OpenAI API`

### NPCL Customer Care Simulation
1. **Launch NPCL Assistant** - Run `./start_chatbot.sh` and select option 2
2. **Automated Greeting** - Assistant starts with customer care greeting
3. **Name Verification** - Responds to customer name confirmation
4. **Complaint Handling** - Processes power outage complaints and provides updates
5. **Professional Interaction** - Maintains customer service tone and procedures

**Code path:** `npcl_voice_assistant.py` → `NPCLVoiceAssistant` → `Specialized Prompts` → `OpenAI API`

---

## 📈 Performance & Scale

### Performance Considerations
- **Audio Latency** - 24kHz PCM16 format optimized for real-time processing
- **WebSocket Streaming** - Direct streaming without file uploads for minimal delay
- **Memory Management** - Queue-based audio buffering to prevent memory leaks
- **Connection Stability** - Automatic reconnection and error handling

### Monitoring
- **Audio Quality** - Real-time audio level monitoring and voice activity detection
- **Connection Status** - WebSocket connection health and API response monitoring
- **Error Handling** - Comprehensive exception handling with user-friendly messages

---

## 🚨 Things to Be Careful About

### 🔒 Security Considerations
- **API Key Management** - Store OpenAI API key securely in `.env` file (never commit)
- **Audio Privacy** - Voice data is streamed to OpenAI servers for processing
- **Network Security** - Ensure secure WebSocket connections (WSS protocol)

### ⚠️ Development Notes
- **API Access** - OpenAI Realtime API is in preview/beta and requires special access
- **Audio Dependencies** - PyAudio requires system audio libraries (may need platform-specific setup)
- **Version Archive** - `dump_test/` contains development history - avoid modifying production code there
- **Environment Setup** - Always use virtual environment to avoid dependency conflicts

*Updated at: 2024-12-19 UTC*