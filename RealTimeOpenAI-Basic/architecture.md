# NPCL Voice Assistant - System Architecture

## Overview

The NPCL Voice Assistant is a real-time voice-to-voice conversational AI system designed for customer service applications. It leverages OpenAI's Realtime API to provide natural, empathetic customer support for power utility services.

## High-Level Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        A[User Voice Input] --> B[PyAudio Capture]
        B --> C[Audio Processing]
    end
    
    subgraph "Application Layer"
        C --> D[Voice Assistant Engine]
        D --> E[Conversation Manager]
        E --> F[State Management]
        F --> G[Response Generator]
    end
    
    subgraph "Communication Layer"
        G --> H[WebSocket Client]
        H --> I[OpenAI Realtime API]
        I --> J[Audio Response Stream]
    end
    
    subgraph "Output Layer"
        J --> K[Audio Decoder]
        K --> L[PyAudio Playback]
        L --> M[User Audio Output]
    end
    
    subgraph "Configuration Layer"
        N[Environment Config] --> D
        O[NPCL Domain Config] --> E
        P[Audio Config] --> C
    end
```

## Core Components

### 1. Audio Processing Engine

**Purpose**: Handles real-time audio capture, processing, and playback

**Key Features**:
- PCM16 audio format at 24kHz sample rate
- 1024-byte chunk processing for optimal latency
- Mono channel audio for telephony compatibility
- Real-time audio buffering with queue management

**Implementation**:
```python
# Audio Configuration
sample_rate = 24000
chunk_size = 1024
channels = 1
format = pyaudio.paInt16
```

**Components**:
- **Audio Input Handler**: Captures microphone input
- **Audio Output Handler**: Manages speaker output
- **Audio Queue Manager**: Buffers audio data
- **Format Converter**: Handles audio format conversions

### 2. WebSocket Communication Layer

**Purpose**: Manages real-time bidirectional communication with OpenAI

**Architecture**:
```mermaid
sequenceDiagram
    participant Client as Voice Assistant
    participant WS as WebSocket
    participant OpenAI as OpenAI Realtime API
    
    Client->>WS: Connect with Auth Headers
    WS->>OpenAI: Establish Connection
    OpenAI->>WS: session.created
    WS->>Client: Connection Confirmed
    
    Client->>WS: session.update (Config)
    WS->>OpenAI: Session Configuration
    OpenAI->>WS: session.updated
    
    loop Real-time Audio Exchange
        Client->>WS: input_audio_buffer.append
        WS->>OpenAI: Audio Data
        OpenAI->>WS: response.audio.delta
        WS->>Client: Audio Response
    end
```

**Key Features**:
- Persistent WebSocket connection with auto-reconnection
- Event-driven message handling
- Base64 audio encoding/decoding
- Error handling and recovery mechanisms

### 3. Conversation Management System

**Purpose**: Manages conversation flow, state, and context

**State Machine**:
```mermaid
stateDiagram-v2
    [*] --> Initial
    Initial --> Greeting: User connects
    Greeting --> Listening: Welcome message sent
    Listening --> Processing: Speech detected
    Processing --> Responding: Generate response
    Responding --> Listening: Response complete
    Listening --> Complaint: Complaint number provided
    Complaint --> Resolution: Status check
    Resolution --> Listening: Continue conversation
    Listening --> [*]: End conversation
```

**Components**:
- **State Manager**: Tracks conversation state
- **Context Manager**: Maintains conversation history
- **Intent Recognition**: Identifies customer needs
- **Response Orchestrator**: Coordinates appropriate responses

### 4. NPCL Domain Logic

**Purpose**: Implements NPCL-specific business logic and conversation patterns

**Domain Model**:
```mermaid
classDiagram
    class NPCLVoiceAssistant {
        +customer_names: List[str]
        +conversation_started: bool
        +selected_name: str
        +start_natural_conversation()
        +handle_realtime_event()
        +update_conversation_state()
    }
    
    class ConversationState {
        +state: str
        +customer_name: str
        +complaint_number: str
        +area: str
        +issue_type: str
    }
    
    class ResponseGenerator {
        +generate_greeting()
        +handle_complaint_inquiry()
        +process_power_outage()
        +provide_status_update()
    }
    
    NPCLVoiceAssistant --> ConversationState
    NPCLVoiceAssistant --> ResponseGenerator
```

## Data Flow Architecture

### Audio Processing Pipeline

```mermaid
flowchart LR
    A[Microphone] --> B[PyAudio Capture]
    B --> C[PCM16 Conversion]
    C --> D[Chunk Processing]
    D --> E[Base64 Encoding]
    E --> F[WebSocket Send]
    F --> G[OpenAI Processing]
    G --> H[Response Generation]
    H --> I[Audio Response]
    I --> J[Base64 Decoding]
    J --> K[Audio Queue]
    K --> L[PyAudio Playback]
    L --> M[Speaker Output]
```

### Event Processing Flow

```mermaid
flowchart TD
    A[WebSocket Message] --> B{Event Type}
    B -->|session.created| C[Initialize Session]
    B -->|session.updated| D[Start Conversation]
    B -->|speech_started| E[Update UI State]
    B -->|speech_stopped| F[Trigger Response]
    B -->|audio.delta| G[Queue Audio]
    B -->|transcript.completed| H[Process Text]
    B -->|response.done| I[Reset State]
    B -->|error| J[Handle Error]
    
    C --> K[Session Ready]
    D --> L[Send Greeting]
    E --> M[Show Speaking]
    F --> N[Generate Response]
    G --> O[Play Audio]
    H --> P[Update Context]
    I --> Q[Ready for Next]
    J --> R[Error Recovery]
```

## Technical Stack

### Core Technologies

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| Runtime | Python | 3.13.7 | Main application runtime |
| AI API | OpenAI Realtime API | v1 | Voice-to-voice AI processing |
| Audio | PyAudio | 0.2.11+ | Audio I/O operations |
| Networking | WebSockets | 12.0+ | Real-time communication |
| Async | asyncio | Built-in | Concurrent operations |
| UI | Colorama | 0.4.6+ | Terminal output formatting |
| Config | python-dotenv | 1.0.0+ | Environment management |

### Audio Processing Stack

```mermaid
graph LR
    subgraph "Audio Input"
        A[Hardware Microphone] --> B[System Audio Driver]
        B --> C[PyAudio Interface]
    end
    
    subgraph "Processing"
        C --> D[PCM16 Format]
        D --> E[24kHz Sample Rate]
        E --> F[1024-byte Chunks]
        F --> G[Base64 Encoding]
    end
    
    subgraph "Transmission"
        G --> H[WebSocket Protocol]
        H --> I[OpenAI Realtime API]
    end
    
    subgraph "Response"
        I --> J[Audio Response]
        J --> K[Base64 Decoding]
        K --> L[Audio Queue]
        L --> M[Speaker Output]
    end
```

## Deployment Architecture

### Development Environment

```mermaid
graph TB
    subgraph "Local Development"
        A[Python 3.13 Virtual Environment]
        B[PyAudio Dependencies]
        C[OpenAI API Key]
        D[Local Audio Devices]
    end
    
    subgraph "Configuration"
        E[.env File]
        F[requirements.txt]
        G[Config Module]
    end
    
    subgraph "Application"
        H[npcl_voice_assistant.py]
        I[voice_chatbot.py]
        J[Support Modules]
    end
    
    A --> H
    B --> H
    C --> H
    D --> H
    E --> G
    F --> A
    G --> H
```

### Production Considerations

```mermaid
graph TB
    subgraph "Infrastructure"
        A[Load Balancer]
        B[Application Servers]
        C[WebSocket Connections]
        D[Audio Processing Nodes]
    end
    
    subgraph "Monitoring"
        E[Performance Metrics]
        F[Audio Quality Monitoring]
        G[Error Tracking]
        H[Usage Analytics]
    end
    
    subgraph "Security"
        I[API Key Management]
        J[SSL/TLS Encryption]
        K[Rate Limiting]
        L[Input Validation]
    end
    
    A --> B
    B --> C
    C --> D
    B --> E
    D --> F
    C --> G
    B --> H
    I --> B
    J --> C
    K --> A
    L --> B
```

## Performance Architecture

### Latency Optimization

```mermaid
graph LR
    A[Audio Capture] -->|<50ms| B[Processing]
    B -->|<100ms| C[Encoding]
    C -->|<200ms| D[Network]
    D -->|<500ms| E[OpenAI API]
    E -->|<200ms| F[Response]
    F -->|<100ms| G[Decoding]
    G -->|<50ms| H[Playback]
    
    style A fill:#e1f5fe
    style H fill:#e8f5e8
    style E fill:#fff3e0
```

### Concurrency Model

```mermaid
flowchart TB
    subgraph MainLoop ["Main Event Loop"]
        A[asyncio.run]
        A --> B[WebSocket Handler]
        A --> C[Audio Input Handler]
        A --> D[Audio Output Handler]
        A --> E[Event Processor]
    end
    
    subgraph Tasks ["Concurrent Tasks"]
        F[Message Processing]
        G[Audio Capture]
        H[Audio Playback]
        I[State Management]
    end
    
    subgraph Resources ["Shared Resources"]
        J[Audio Queue]
        K[WebSocket Connection]
        L[Conversation State]
    end
    
    B --> F
    C --> G
    D --> H
    E --> I
    
    F --> K
    G --> J
    H --> J
    I --> L
```

## Security Architecture

### Data Protection

```mermaid
graph TB
    subgraph "Input Security"
        A[Audio Input Validation]
        B[Rate Limiting]
        C[Input Sanitization]
    end
    
    subgraph "Transmission Security"
        D[WSS Encryption]
        E[API Authentication]
        F[Token Management]
    end
    
    subgraph "Data Handling"
        G[No Audio Storage]
        H[Temporary Processing]
        I[Memory Cleanup]
    end
    
    A --> D
    B --> E
    C --> F
    D --> G
    E --> H
    F --> I
```

### Authentication Flow

```mermaid
sequenceDiagram
    participant App as Application
    participant Env as Environment
    participant OpenAI as OpenAI API
    
    App->>Env: Load API Key
    Env->>App: Return Encrypted Key
    App->>OpenAI: Connect with Bearer Token
    OpenAI->>App: Validate & Establish Session
    
    Note over App,OpenAI: Secure WebSocket Connection (WSS)
    
    loop Authenticated Session
        App->>OpenAI: Send Audio Data
        OpenAI->>App: Return Processed Response
    end
```

## Error Handling Architecture

### Error Recovery Strategy

```mermaid
flowchart TD
    A[Error Detected] --> B{Error Type}
    B -->|Network| C[Reconnection Logic]
    B -->|Audio| D[Device Recovery]
    B -->|API| E[Rate Limit Handling]
    B -->|Processing| F[Graceful Degradation]
    
    C --> G[Exponential Backoff]
    D --> H[Device Reinitialization]
    E --> I[Queue Management]
    F --> J[Fallback Response]
    
    G --> K[Resume Operation]
    H --> K
    I --> K
    J --> K
    
    K --> L[Continue Service]
```

### Monitoring and Logging

```mermaid
graph LR
    subgraph "Application Metrics"
        A[Response Time]
        B[Audio Quality]
        C[Connection Stability]
        D[Error Rates]
    end
    
    subgraph "System Metrics"
        E[CPU Usage]
        F[Memory Usage]
        G[Network Latency]
        H[Disk I/O]
    end
    
    subgraph "Business Metrics"
        I[Conversation Success]
        J[Customer Satisfaction]
        K[Issue Resolution]
        L[Usage Patterns]
    end
    
    A --> M[Monitoring Dashboard]
    B --> M
    C --> M
    D --> M
    E --> M
    F --> M
    G --> M
    H --> M
    I --> N[Analytics Platform]
    J --> N
    K --> N
    L --> N
```

## Scalability Considerations

### Horizontal Scaling

```mermaid
graph TB
    subgraph "Load Distribution"
        A[Load Balancer] --> B[Instance 1]
        A --> C[Instance 2]
        A --> D[Instance N]
    end
    
    subgraph "Session Management"
        E[Session Affinity]
        F[State Synchronization]
        G[Connection Pooling]
    end
    
    subgraph "Resource Management"
        H[Auto Scaling]
        I[Resource Monitoring]
        J[Performance Optimization]
    end
    
    B --> E
    C --> F
    D --> G
    E --> H
    F --> I
    G --> J
```

### Future Architecture Enhancements

1. **Multi-Language Support**
   - Language detection and routing
   - Locale-specific voice models
   - Cultural adaptation layers

2. **Advanced Analytics**
   - Real-time conversation analytics
   - Sentiment analysis integration
   - Performance optimization insights

3. **Integration Capabilities**
   - CRM system integration
   - Telephony system connectivity
   - Third-party service APIs

4. **Enhanced AI Features**
   - Custom model fine-tuning
   - Domain-specific knowledge bases
   - Advanced conversation flows

This architecture provides a robust, scalable foundation for real-time voice AI applications while maintaining high performance and reliability standards.