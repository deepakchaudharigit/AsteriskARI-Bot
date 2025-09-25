#!/bin/bash

# ============================================================================
# NPCL Asterisk ARI Assistant - Comprehensive End-to-End Testing Script
# ============================================================================
# This script provides complete testing for both Docker and Linux scenarios
# Author: NPCL Voice Assistant Team
# Version: 1.0
# ============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Global variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
VENV_PATH="$PROJECT_ROOT/.venv"
LOG_DIR="$PROJECT_ROOT/test_logs"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
TEST_LOG="$LOG_DIR/e2e_test_$TIMESTAMP.log"

# Test configuration
ASTERISK_DOCKER_CONTAINER="npcl-asterisk-20"
SIP_USER="1001"
SIP_PASSWORD="1234"
SIP_SERVER="localhost:5060"
TEST_EXTENSION="1000"
ARI_BASE_URL="http://localhost:8088/ari"
ARI_USERNAME="asterisk"
ARI_PASSWORD="1234"
VOICE_ASSISTANT_PORT="8000"

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

print_banner() {
    echo -e "${CYAN}"
    echo "============================================================================"
    echo "  NPCL ASTERISK ARI ASSISTANT - COMPREHENSIVE E2E TESTING"
    echo "============================================================================"
    echo -e "${NC}"
}

print_section() {
    echo -e "\n${BLUE}▶ $1${NC}"
    echo "----------------------------------------"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$TEST_LOG"
    echo "$1"
}

check_command() {
    if command -v "$1" &> /dev/null; then
        print_success "$1 is installed"
        return 0
    else
        print_error "$1 is not installed"
        return 1
    fi
}

wait_for_service() {
    local service_name="$1"
    local check_command="$2"
    local max_attempts=30
    local attempt=1
    
    print_info "Waiting for $service_name to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if eval "$check_command" &>/dev/null; then
            print_success "$service_name is ready!"
            return 0
        fi
        
        echo -n "."
        sleep 2
        ((attempt++))
    done
    
    print_error "$service_name failed to start within $((max_attempts * 2)) seconds"
    return 1
}

# ============================================================================
# DEPENDENCY INSTALLATION FUNCTIONS
# ============================================================================

install_system_dependencies() {
    print_section "Installing System Dependencies"
    
    # Detect OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v apt-get &> /dev/null; then
            # Ubuntu/Debian
            print_info "Detected Ubuntu/Debian system"
            sudo apt-get update
            sudo apt-get install -y \
                python3 \
                python3-pip \
                python3-venv \
                python3-dev \
                build-essential \
                curl \
                wget \
                git \
                docker.io \
                docker-compose \
                portaudio19-dev \
                libasound2-dev \
                ffmpeg \
                jq \
                netcat-openbsd
        elif command -v yum &> /dev/null; then
            # CentOS/RHEL
            print_info "Detected CentOS/RHEL system"
            sudo yum update -y
            sudo yum install -y \
                python3 \
                python3-pip \
                python3-devel \
                gcc \
                gcc-c++ \
                make \
                curl \
                wget \
                git \
                docker \
                docker-compose \
                portaudio-devel \
                alsa-lib-devel \
                ffmpeg \
                jq \
                nc
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        print_info "Detected macOS system"
        if ! command -v brew &> /dev/null; then
            print_info "Installing Homebrew..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        fi
        
        brew update
        brew install \
            python3 \
            portaudio \
            ffmpeg \
            docker \
            docker-compose \
            jq \
            netcat
    fi
    
    print_success "System dependencies installed"
}

install_python_dependencies() {
    print_section "Setting Up Python Environment"
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "$VENV_PATH" ]; then
        print_info "Creating Python virtual environment..."
        python3 -m venv "$VENV_PATH"
    fi
    
    # Activate virtual environment
    source "$VENV_PATH/bin/activate"
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
        print_info "Installing Python dependencies from requirements.txt..."
        pip install -r "$PROJECT_ROOT/requirements.txt"
    else
        print_info "Installing essential Python dependencies..."
        pip install \
            fastapi \
            uvicorn \
            websockets \
            openai \
            pydantic \
            requests \
            pygame \
            numpy \
            pytest \
            pytest-asyncio \
            pytest-cov
    fi
    
    print_success "Python environment set up successfully"
}

setup_docker() {
    print_section "Setting Up Docker"
    
    # Start Docker service
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo systemctl start docker
        sudo systemctl enable docker
        
        # Add user to docker group
        sudo usermod -aG docker $USER
        print_warning "You may need to log out and back in for Docker group changes to take effect"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # On macOS, Docker Desktop should be started manually
        if ! docker info &>/dev/null; then
            print_warning "Please start Docker Desktop manually"
            read -p "Press Enter when Docker Desktop is running..."
        fi
    fi
    
    # Verify Docker is working
    if docker info &>/dev/null; then
        print_success "Docker is running"
    else
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# ============================================================================
# ENVIRONMENT SETUP FUNCTIONS
# ============================================================================

setup_environment() {
    print_section "Setting Up Environment Variables"
    
    # Check if .env file exists
    if [ -f "$PROJECT_ROOT/.env" ]; then
        print_success ".env file already exists"
        
        # Check if OpenAI API key is configured
        source "$PROJECT_ROOT/.env"
        if [ -n "$OPENAI_API_KEY" ] && [ "$OPENAI_API_KEY" != "your_openai_api_key_here" ]; then
            print_success "OpenAI API key is already configured"
        else
            print_warning "OpenAI API key needs to be configured in .env file"
        fi
    else
        print_info "Creating .env file with default configuration..."
        cat > "$PROJECT_ROOT/.env" << EOF
# AI Configuration
AI_PROVIDER=openai
OPENAI_API_KEY=your_openai_api_key_here

# Voice Configuration
VOICE_MODEL=fable
TTS_MODEL=tts-1-hd
ENABLE_VOICE_INTERRUPTION=true

# Audio Configuration
AUDIO_SAMPLE_RATE=16000
AUDIO_FORMAT=slin16
AUDIO_BUFFER_SIZE=1024
AUDIO_LATENCY_TARGET=20
ENABLE_AUDIO_PROCESSING=true
ENABLE_REALTIME_AUDIO=true

# Asterisk ARI Configuration
ARI_BASE_URL=http://localhost:8088/ari
ARI_USERNAME=asterisk
ARI_PASSWORD=1234
STASIS_APP=openai-voice-assistant

# External Media Configuration
EXTERNAL_MEDIA_HOST=localhost
EXTERNAL_MEDIA_PORT=8090

# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# Logging Configuration
LOG_LEVEL=INFO
ENABLE_PERFORMANCE_LOGGING=true

# Testing Configuration
ENABLE_TEST_MODE=false
TEST_AUDIO_FILE=test_audio.wav
EOF
        print_warning "Please update the OPENAI_API_KEY in .env file"
    fi
    
    # Create log directory
    mkdir -p "$LOG_DIR"
    
    print_success "Environment setup completed"
}

validate_openai_key() {
    print_section "Validating OpenAI API Key"
    
    # Load environment variables
    if [ -f "$PROJECT_ROOT/.env" ]; then
        source "$PROJECT_ROOT/.env"
    else
        print_error ".env file not found"
        return 1
    fi
    
    # Check if API key is configured
    if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "your_openai_api_key_here" ]; then
        print_error "OpenAI API key is not configured"
        echo "Please update the OPENAI_API_KEY in .env file"
        echo "You can get an API key from: https://platform.openai.com/api-keys"
        echo "Current .env file location: $PROJECT_ROOT/.env"
        return 1
    fi
    
    # Validate API key format
    if [[ ! "$OPENAI_API_KEY" =~ ^sk-[a-zA-Z0-9_-]+$ ]]; then
        print_warning "OpenAI API key format looks unusual (should start with 'sk-')"
    fi
    
    print_success "OpenAI API key is configured: ${OPENAI_API_KEY:0:20}..."
    
    # Test API key with a simple request
    print_info "Testing API key validity..."
    response=$(curl -s -H "Authorization: Bearer $OPENAI_API_KEY" \
        "https://api.openai.com/v1/models" \
        -w "%{http_code}" \
        --connect-timeout 10 \
        --max-time 30)
    
    http_code="${response: -3}"
    
    case "$http_code" in
        "200")
            print_success "OpenAI API key is valid and working"
            return 0
            ;;
        "401")
            print_error "OpenAI API key is invalid or expired"
            echo "Please check your API key at: https://platform.openai.com/api-keys"
            return 1
            ;;
        "429")
            print_warning "OpenAI API rate limit reached, but key appears valid"
            return 0
            ;;
        "000")
            print_warning "Could not connect to OpenAI API (network issue)"
            print_info "Proceeding with testing - API key format looks correct"
            return 0
            ;;
        *)
            print_warning "OpenAI API validation returned HTTP $http_code"
            print_info "Proceeding with testing - will validate during actual usage"
            return 0
            ;;
    esac
}

# ============================================================================
# DOCKER TESTING FUNCTIONS
# ============================================================================

start_docker_services() {
    print_section "Starting Docker Services"
    
    # Check if docker-compose.yml exists
    if [ ! -f "$PROJECT_ROOT/docker-compose.yml" ]; then
        print_info "Creating docker-compose.yml..."
        create_docker_compose_file
    fi
    
    # Start services
    print_info "Starting Asterisk container..."
    docker-compose up -d asterisk
    
    # Wait for Asterisk to be ready
    wait_for_service "Asterisk ARI" "curl -s -u $ARI_USERNAME:$ARI_PASSWORD $ARI_BASE_URL/asterisk/info"
    
    print_success "Docker services started successfully"
}

create_docker_compose_file() {
    cat > "$PROJECT_ROOT/docker-compose.yml" << 'EOF'
version: '3.8'

services:
  asterisk:
    container_name: npcl-asterisk-20
    build:
      context: .
      dockerfile: docker/Dockerfile.asterisk20
    ports:
      - "5060:5060/udp"
      - "8088:8088"
      - "10000-10100:10000-10100/udp"
    volumes:
      - ./asterisk-config:/etc/asterisk
      - ./sounds:/var/lib/asterisk/sounds/custom
    environment:
      - ASTERISK_UID=1000
      - ASTERISK_GID=1000
    restart: unless-stopped
    networks:
      - npcl-network

networks:
  npcl-network:
    driver: bridge
EOF
}

test_docker_asterisk() {
    print_section "Testing Docker Asterisk Configuration"
    
    # Test ARI connectivity
    print_info "Testing ARI connectivity..."
    if curl -s -u "$ARI_USERNAME:$ARI_PASSWORD" "$ARI_BASE_URL/asterisk/info" | jq . &>/dev/null; then
        print_success "ARI is accessible"
    else
        print_error "ARI is not accessible"
        return 1
    fi
    
    # Test SIP configuration
    print_info "Testing SIP configuration..."
    if docker exec "$ASTERISK_DOCKER_CONTAINER" asterisk -rx "pjsip show endpoints" | grep -q "1001"; then
        print_success "SIP endpoint 1001 is configured"
    else
        print_error "SIP endpoint 1001 is not configured"
        return 1
    fi
    
    # Test dialplan
    print_info "Testing dialplan configuration..."
    if docker exec "$ASTERISK_DOCKER_CONTAINER" asterisk -rx "dialplan show openai-voice-assistant" | grep -q "1000"; then
        print_success "Extension 1000 is configured"
    else
        print_error "Extension 1000 is not configured"
        return 1
    fi
    
    print_success "Docker Asterisk configuration is valid"
}

# ============================================================================
# LINUX ASTERISK TESTING FUNCTIONS
# ============================================================================

install_linux_asterisk() {
    print_section "Installing Asterisk on Linux"
    
    if command -v asterisk &> /dev/null; then
        print_success "Asterisk is already installed"
        asterisk -V
        return 0
    fi
    
    print_info "Installing Asterisk..."
    
    if command -v apt-get &> /dev/null; then
        # Ubuntu/Debian
        sudo apt-get update
        sudo apt-get install -y asterisk asterisk-config asterisk-modules
    elif command -v yum &> /dev/null; then
        # CentOS/RHEL
        sudo yum install -y epel-release
        sudo yum install -y asterisk asterisk-configs
    fi
    
    print_success "Asterisk installed successfully"
}

configure_linux_asterisk() {
    print_section "Configuring Linux Asterisk"
    
    # Backup original configs
    sudo cp /etc/asterisk/ari.conf /etc/asterisk/ari.conf.backup 2>/dev/null || true
    sudo cp /etc/asterisk/http.conf /etc/asterisk/http.conf.backup 2>/dev/null || true
    sudo cp /etc/asterisk/pjsip.conf /etc/asterisk/pjsip.conf.backup 2>/dev/null || true
    sudo cp /etc/asterisk/extensions.conf /etc/asterisk/extensions.conf.backup 2>/dev/null || true
    
    # Configure ARI
    print_info "Configuring ARI..."
    sudo tee /etc/asterisk/ari.conf > /dev/null << 'EOF'
[general]
enabled = yes
pretty = yes
allowed_origins = *

[asterisk]
type = user
read_only = no
password = 1234
EOF
    
    # Configure HTTP
    print_info "Configuring HTTP..."
    sudo tee /etc/asterisk/http.conf > /dev/null << 'EOF'
[general]
enabled=yes
bindaddr=0.0.0.0
bindport=8088
prefix=asterisk
EOF
    
    # Configure PJSIP
    print_info "Configuring PJSIP..."
    sudo tee /etc/asterisk/pjsip.conf > /dev/null << 'EOF'
[global]
type=global
endpoint_identifier_order=ip,username,anonymous

[transport-udp]
type=transport
protocol=udp
bind=0.0.0.0:5060

; Test extension 1000
[1000]
type=endpoint
context=openai-voice-assistant
disallow=all
allow=ulaw
allow=alaw
auth=1000
aors=1000
rtp_symmetric=yes
force_rport=yes
rewrite_contact=yes
direct_media=no

[1000]
type=auth
auth_type=userpass
password=1234
username=1000

[1000]
type=aor
max_contacts=1

; SIP Client 1001 (Zoiper)
[1001]
type=endpoint
context=openai-voice-assistant
disallow=all
allow=ulaw
allow=alaw
auth=1001
aors=1001
rtp_symmetric=yes
force_rport=yes
rewrite_contact=yes
direct_media=no

[1001]
type=auth
auth_type=userpass
password=1234
username=1001

[1001]
type=aor
max_contacts=1
EOF
    
    # Configure Extensions
    print_info "Configuring Extensions..."
    sudo tee /etc/asterisk/extensions.conf > /dev/null << 'EOF'
[general]
static=yes
writeprotect=no
clearglobalvars=no

[globals]
OPENAI_APP=openai-voice-assistant

[openai-voice-assistant]
; Main NPCL Voice Assistant Extension
exten => 1000,1,NoOp(NPCL Voice Assistant - Main Line)
same => n,Answer()
same => n,Wait(1)
same => n,Playback(silence/1)
same => n,Stasis(${OPENAI_APP},${CALLERID(num)},${EXTEN})
same => n,Hangup()

; Simple test extension (no Stasis)
exten => 1010,1,NoOp(Simple Test Extension)
same => n,Answer()
same => n,Wait(2)
same => n,Playback(demo-congrats)
same => n,Wait(5)
same => n,Hangup()

; Echo test
exten => 9000,1,NoOp(Echo Test)
same => n,Answer()
same => n,Echo()
same => n,Hangup()

[default]
include => openai-voice-assistant

[from-sip]
include => openai-voice-assistant
EOF
    
    print_success "Asterisk configuration completed"
}

start_linux_asterisk() {
    print_section "Starting Linux Asterisk"
    
    # Start Asterisk service
    sudo systemctl start asterisk
    sudo systemctl enable asterisk
    
    # Wait for Asterisk to be ready
    wait_for_service "Asterisk" "sudo asterisk -rx 'core show version'"
    
    # Load required modules
    print_info "Loading required modules..."
    sudo asterisk -rx "module load res_ari.so"
    sudo asterisk -rx "module load res_ari_channels.so"
    sudo asterisk -rx "module load res_ari_bridges.so"
    sudo asterisk -rx "module load res_ari_applications.so"
    sudo asterisk -rx "module load res_ari_events.so"
    sudo asterisk -rx "module load res_http_websocket.so"
    sudo asterisk -rx "core reload"
    
    print_success "Linux Asterisk started successfully"
}

test_linux_asterisk() {
    print_section "Testing Linux Asterisk Configuration"
    
    # Test ARI connectivity
    print_info "Testing ARI connectivity..."
    if curl -s -u "$ARI_USERNAME:$ARI_PASSWORD" "$ARI_BASE_URL/asterisk/info" | jq . &>/dev/null; then
        print_success "ARI is accessible"
    else
        print_error "ARI is not accessible"
        return 1
    fi
    
    # Test SIP configuration
    print_info "Testing SIP configuration..."
    if sudo asterisk -rx "pjsip show endpoints" | grep -q "1001"; then
        print_success "SIP endpoint 1001 is configured"
    else
        print_error "SIP endpoint 1001 is not configured"
        return 1
    fi
    
    # Test dialplan
    print_info "Testing dialplan configuration..."
    if sudo asterisk -rx "dialplan show openai-voice-assistant" | grep -q "1000"; then
        print_success "Extension 1000 is configured"
    else
        print_error "Extension 1000 is not configured"
        return 1
    fi
    
    print_success "Linux Asterisk configuration is valid"
}

# ============================================================================
# VOICE ASSISTANT TESTING FUNCTIONS
# ============================================================================

start_voice_assistant() {
    print_section "Starting Voice Assistant"
    
    # Activate virtual environment
    source "$VENV_PATH/bin/activate"
    
    # Check if main server file exists
    if [ -f "$PROJECT_ROOT/src/run_realtime_server.py" ]; then
        SERVER_FILE="$PROJECT_ROOT/src/run_realtime_server.py"
    elif [ -f "$PROJECT_ROOT/src/main.py" ]; then
        SERVER_FILE="$PROJECT_ROOT/src/main.py"
    else
        print_error "Voice assistant server file not found"
        return 1
    fi
    
    # Start the voice assistant server
    print_info "Starting voice assistant server..."
    cd "$PROJECT_ROOT"
    python "$SERVER_FILE" > "$LOG_DIR/voice_assistant_$TIMESTAMP.log" 2>&1 &
    VOICE_ASSISTANT_PID=$!
    
    # Wait for server to be ready
    wait_for_service "Voice Assistant" "curl -s http://localhost:$VOICE_ASSISTANT_PORT/health"
    
    print_success "Voice assistant started (PID: $VOICE_ASSISTANT_PID)"
    echo "$VOICE_ASSISTANT_PID" > "$LOG_DIR/voice_assistant.pid"
}

test_voice_assistant_health() {
    print_section "Testing Voice Assistant Health"
    
    # Test health endpoint
    print_info "Testing health endpoint..."
    if curl -s "http://localhost:$VOICE_ASSISTANT_PORT/health" | jq . &>/dev/null; then
        print_success "Health endpoint is accessible"
    else
        print_error "Health endpoint is not accessible"
        return 1
    fi
    
    # Test ARI endpoint
    print_info "Testing ARI endpoint..."
    if curl -s "http://localhost:$VOICE_ASSISTANT_PORT/ari/health" | jq . &>/dev/null; then
        print_success "ARI endpoint is accessible"
    else
        print_error "ARI endpoint is not accessible"
        return 1
    fi
    
    # Test OpenAI integration
    print_info "Testing OpenAI integration..."
    source "$PROJECT_ROOT/.env"
    if [ -n "$OPENAI_API_KEY" ] && [ "$OPENAI_API_KEY" != "your_openai_api_key_here" ]; then
        print_success "OpenAI API key is configured"
    else
        print_warning "OpenAI API key is not configured - some features may not work"
    fi
    
    print_success "Voice assistant health check completed"
}

# ============================================================================
# END-TO-END TESTING FUNCTIONS
# ============================================================================

run_automated_tests() {
    print_section "Running Automated Tests"
    
    # Activate virtual environment
    source "$VENV_PATH/bin/activate"
    
    # Run unit tests
    if [ -f "$PROJECT_ROOT/tests/run_tests.py" ]; then
        print_info "Running comprehensive test suite..."
        cd "$PROJECT_ROOT"
        python tests/run_tests.py --category unit > "$LOG_DIR/unit_tests_$TIMESTAMP.log" 2>&1
        if [ $? -eq 0 ]; then
            print_success "Unit tests passed"
        else
            print_warning "Some unit tests failed - check logs"
        fi
        
        # Run integration tests
        print_info "Running integration tests..."
        python tests/run_tests.py --category integration > "$LOG_DIR/integration_tests_$TIMESTAMP.log" 2>&1
        if [ $? -eq 0 ]; then
            print_success "Integration tests passed"
        else
            print_warning "Some integration tests failed - check logs"
        fi
    else
        print_warning "Test suite not found - skipping automated tests"
    fi
}

test_ari_integration() {
    print_section "Testing ARI Integration"
    
    # Test ARI connection
    print_info "Testing ARI connection..."
    response=$(curl -s -u "$ARI_USERNAME:$ARI_PASSWORD" "$ARI_BASE_URL/asterisk/info")
    if echo "$response" | jq . &>/dev/null; then
        print_success "ARI connection successful"
        echo "$response" | jq '.build.date' | sed 's/"//g' | xargs -I {} echo "Asterisk build date: {}"
    else
        print_error "ARI connection failed"
        return 1
    fi
    
    # Test applications endpoint
    print_info "Testing applications endpoint..."
    if curl -s -u "$ARI_USERNAME:$ARI_PASSWORD" "$ARI_BASE_URL/applications" | jq . &>/dev/null; then
        print_success "Applications endpoint accessible"
    else
        print_error "Applications endpoint not accessible"
        return 1
    fi
    
    # Test channels endpoint
    print_info "Testing channels endpoint..."
    if curl -s -u "$ARI_USERNAME:$ARI_PASSWORD" "$ARI_BASE_URL/channels" | jq . &>/dev/null; then
        print_success "Channels endpoint accessible"
    else
        print_error "Channels endpoint not accessible"
        return 1
    fi
    
    print_success "ARI integration test completed"
}

test_sip_configuration() {
    print_section "Testing SIP Configuration"
    
    # Test SIP port
    print_info "Testing SIP port (5060)..."
    if nc -z localhost 5060; then
        print_success "SIP port 5060 is open"
    else
        print_error "SIP port 5060 is not accessible"
        return 1
    fi
    
    # Test RTP port range
    print_info "Testing RTP port range (10000-10100)..."
    if nc -z localhost 10000; then
        print_success "RTP port range is accessible"
    else
        print_warning "RTP ports may not be accessible - this could affect audio"
    fi
    
    print_success "SIP configuration test completed"
}

simulate_call_test() {
    print_section "Simulating Call Test"
    
    print_info "Simulating incoming call to extension 1000..."
    
    # Create a test call event
    call_event='{
        "type": "StasisStart",
        "application": "openai-voice-assistant",
        "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)'",
        "channel": {
            "id": "test-channel-'$TIMESTAMP'",
            "name": "SIP/test-'$TIMESTAMP'",
            "state": "Ring",
            "caller": {
                "name": "E2E Test",
                "number": "1001"
            },
            "connected": {
                "name": "Voice Assistant",
                "number": "1000"
            },
            "dialplan": {
                "context": "openai-voice-assistant",
                "exten": "1000",
                "priority": 1
            }
        }
    }'
    
    # Send test event to voice assistant
    response=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -d "$call_event" \
        "http://localhost:$VOICE_ASSISTANT_PORT/ari/events")
    
    if [ $? -eq 0 ]; then
        print_success "Call simulation sent successfully"
        echo "Response: $response"
    else
        print_error "Call simulation failed"
        return 1
    fi
    
    # Wait a moment for processing
    sleep 2
    
    # Check active calls
    print_info "Checking active calls..."
    active_calls=$(curl -s "http://localhost:$VOICE_ASSISTANT_PORT/ari/calls")
    if echo "$active_calls" | jq . &>/dev/null; then
        call_count=$(echo "$active_calls" | jq '.call_count // 0')
        print_info "Active calls: $call_count"
    else
        print_warning "Could not retrieve active calls information"
    fi
    
    print_success "Call simulation test completed"
}

# ============================================================================
# ZOIPER TESTING FUNCTIONS
# ============================================================================

provide_zoiper_instructions() {
    print_section "Zoiper Configuration Instructions"
    
    echo -e "${YELLOW}"
    echo "============================================================================"
    echo "                        ZOIPER 5 CONFIGURATION"
    echo "============================================================================"
    echo -e "${NC}"
    
    echo "📱 Configure Zoiper 5 with the following settings:"
    echo ""
    echo "   🌐 Server Settings:"
    echo "      • Server: $SIP_SERVER"
    echo "      • Username: $SIP_USER"
    echo "      • Password: $SIP_PASSWORD"
    echo "      • Protocol: SIP"
    echo "      • Transport: UDP"
    echo ""
    echo "   🔧 Advanced Settings:"
    echo "      • Codec: G.711 μ-law (PCMU)"
    echo "      • DTMF: RFC 2833"
    echo "      • NAT Traversal: Enable"
    echo "      • Keep Alive: Enable"
    echo ""
    echo "   📞 Test Extensions:"
    echo "      • $TEST_EXTENSION - NPCL Voice Assistant (AI-powered)"
    echo "      • 1010 - Simple test extension (plays demo message)"
    echo "      • 9000 - Echo test (repeats what you say)"
    echo ""
    echo "   ✅ Expected Results:"
    echo "      • Call connects immediately"
    echo "      • Local codecs: G.711 μ-law"
    echo "      • Remote codecs: G.711 μ-law (NOT 'None')"
    echo "      • Two-way audio working"
    echo "      • AI responds in real-time"
    echo ""
    echo -e "${YELLOW}"
    echo "============================================================================"
    echo -e "${NC}"
}

wait_for_manual_test() {
    print_section "Manual Testing Phase"
    
    provide_zoiper_instructions
    
    echo ""
    echo "🧪 Manual Testing Steps:"
    echo "1. Configure Zoiper 5 with the settings above"
    echo "2. Make a test call to extension $TEST_EXTENSION"
    echo "3. Speak to the AI assistant"
    echo "4. Verify two-way audio communication"
    echo "5. Test voice interruption (speak while AI is talking)"
    echo ""
    
    read -p "Press Enter when you have completed the manual testing..."
    
    # Ask for test results
    echo ""
    echo "📋 Please report your test results:"
    echo ""
    
    read -p "Did the call connect successfully? (y/n): " call_connected
    read -p "Was audio quality good? (y/n): " audio_quality
    read -p "Did the AI respond correctly? (y/n): " ai_response
    read -p "Did voice interruption work? (y/n): " voice_interruption
    read -p "Were remote codecs negotiated (not 'None')? (y/n): " codec_negotiation
    
    # Log results
    {
        echo "Manual Test Results - $TIMESTAMP"
        echo "=================================="
        echo "Call Connected: $call_connected"
        echo "Audio Quality: $audio_quality"
        echo "AI Response: $ai_response"
        echo "Voice Interruption: $voice_interruption"
        echo "Codec Negotiation: $codec_negotiation"
    } >> "$LOG_DIR/manual_test_results_$TIMESTAMP.log"
    
    # Provide feedback
    if [[ "$call_connected" == "y" && "$audio_quality" == "y" && "$ai_response" == "y" ]]; then
        print_success "Manual testing completed successfully!"
    else
        print_warning "Some issues were reported during manual testing"
        echo "Please check the logs and configuration"
    fi
}

# ============================================================================
# MONITORING AND LOGGING FUNCTIONS
# ============================================================================

start_monitoring() {
    print_section "Starting System Monitoring"
    
    # Create monitoring script
    cat > "$LOG_DIR/monitor_$TIMESTAMP.sh" << 'EOF'
#!/bin/bash
LOG_FILE="$1"
echo "Starting system monitoring..." >> "$LOG_FILE"

while true; do
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Check Asterisk status
    if docker ps | grep -q "npcl-asterisk-20"; then
        ASTERISK_STATUS="Docker Running"
    elif pgrep asterisk > /dev/null; then
        ASTERISK_STATUS="Linux Running"
    else
        ASTERISK_STATUS="Not Running"
    fi
    
    # Check Voice Assistant status
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        VA_STATUS="Running"
    else
        VA_STATUS="Not Running"
    fi
    
    # Check active calls
    ACTIVE_CALLS=$(curl -s http://localhost:8000/ari/calls 2>/dev/null | jq '.call_count // 0' 2>/dev/null || echo "0")
    
    # Log status
    echo "[$TIMESTAMP] Asterisk: $ASTERISK_STATUS | Voice Assistant: $VA_STATUS | Active Calls: $ACTIVE_CALLS" >> "$LOG_FILE"
    
    sleep 10
done
EOF
    
    chmod +x "$LOG_DIR/monitor_$TIMESTAMP.sh"
    
    # Start monitoring in background
    "$LOG_DIR/monitor_$TIMESTAMP.sh" "$LOG_DIR/system_monitor_$TIMESTAMP.log" &
    MONITOR_PID=$!
    echo "$MONITOR_PID" > "$LOG_DIR/monitor.pid"
    
    print_success "System monitoring started (PID: $MONITOR_PID)"
}

stop_monitoring() {
    if [ -f "$LOG_DIR/monitor.pid" ]; then
        MONITOR_PID=$(cat "$LOG_DIR/monitor.pid")
        if kill "$MONITOR_PID" 2>/dev/null; then
            print_success "System monitoring stopped"
        fi
        rm -f "$LOG_DIR/monitor.pid"
    fi
}

generate_test_report() {
    print_section "Generating Test Report"
    
    REPORT_FILE="$LOG_DIR/test_report_$TIMESTAMP.html"
    
    cat > "$REPORT_FILE" << EOF
<!DOCTYPE html>
<html>
<head>
    <title>NPCL Voice Assistant E2E Test Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #f0f0f0; padding: 20px; border-radius: 5px; }
        .section { margin: 20px 0; padding: 15px; border-left: 4px solid #007acc; }
        .success { color: green; }
        .error { color: red; }
        .warning { color: orange; }
        .code { background-color: #f5f5f5; padding: 10px; border-radius: 3px; font-family: monospace; }
    </style>
</head>
<body>
    <div class="header">
        <h1>NPCL Voice Assistant E2E Test Report</h1>
        <p>Generated: $(date)</p>
        <p>Test ID: $TIMESTAMP</p>
    </div>
    
    <div class="section">
        <h2>Test Configuration</h2>
        <div class="code">
            SIP Server: $SIP_SERVER<br>
            Test Extension: $TEST_EXTENSION<br>
            ARI URL: $ARI_BASE_URL<br>
            Voice Assistant Port: $VOICE_ASSISTANT_PORT
        </div>
    </div>
    
    <div class="section">
        <h2>Test Results</h2>
        <p>Detailed test results are available in the following log files:</p>
        <ul>
EOF
    
    # Add log files to report
    for log_file in "$LOG_DIR"/*_"$TIMESTAMP".log; do
        if [ -f "$log_file" ]; then
            filename=$(basename "$log_file")
            echo "            <li><a href=\"$filename\">$filename</a></li>" >> "$REPORT_FILE"
        fi
    done
    
    cat >> "$REPORT_FILE" << EOF
        </ul>
    </div>
    
    <div class="section">
        <h2>Zoiper Configuration</h2>
        <div class="code">
            Server: $SIP_SERVER<br>
            Username: $SIP_USER<br>
            Password: $SIP_PASSWORD<br>
            Test Extension: $TEST_EXTENSION
        </div>
    </div>
</body>
</html>
EOF
    
    print_success "Test report generated: $REPORT_FILE"
}

# ============================================================================
# CLEANUP FUNCTIONS
# ============================================================================

cleanup() {
    print_section "Cleaning Up"
    
    # Stop monitoring
    stop_monitoring
    
    # Stop voice assistant
    if [ -f "$LOG_DIR/voice_assistant.pid" ]; then
        VA_PID=$(cat "$LOG_DIR/voice_assistant.pid")
        if kill "$VA_PID" 2>/dev/null; then
            print_success "Voice assistant stopped"
        fi
        rm -f "$LOG_DIR/voice_assistant.pid"
    fi
    
    print_success "Cleanup completed (Docker containers preserved)"
}

cleanup_docker() {
    print_section "Cleaning Up Docker Services"
    
    # Stop Docker services if running
    if docker ps | grep -q "$ASTERISK_DOCKER_CONTAINER"; then
        print_info "Stopping Docker services..."
        docker-compose down
        print_success "Docker services stopped"
    else
        print_info "No Docker services running"
    fi
}

# Note: Cleanup is now manual - no automatic cleanup on exit
# This allows Docker containers to persist for testing

# ============================================================================
# MAIN MENU AND EXECUTION
# ============================================================================

show_main_menu() {
    clear
    print_banner
    
    echo "Please select your testing scenario:"
    echo ""
    echo "1) 🐳 Docker Testing (Asterisk in Docker container)"
    echo "2) 🐧 Linux Testing (Asterisk installed directly on Linux)"
    echo "3) 🔧 Install Dependencies Only"
    echo "4) 🧪 Run Tests Only (assumes services are running)"
    echo "5) 📊 Generate Test Report"
    echo "6) 🧹 Cleanup Docker Services"
    echo "7) 🚪 Exit"
    echo ""
    read -p "Enter your choice (1-7): " choice
    
    case $choice in
        1) run_docker_testing ;;
        2) run_linux_testing ;;
        3) install_dependencies_only ;;
        4) run_tests_only ;;
        5) generate_test_report ;;
        6) cleanup_docker && show_main_menu ;;
        7) cleanup && exit 0 ;;
        *) echo "Invalid choice. Please try again." && sleep 2 && show_main_menu ;;
    esac
}

run_docker_testing() {
    print_section "Starting Docker Testing Scenario"
    
    # Install dependencies
    install_system_dependencies
    install_python_dependencies
    setup_docker
    setup_environment
    
    # Validate OpenAI key
    if ! validate_openai_key; then
        print_warning "OpenAI API key validation failed, but continuing with testing"
        print_info "Some AI features may not work properly"
        sleep 2
    fi
    
    # Start services
    start_docker_services
    test_docker_asterisk
    start_voice_assistant
    
    # Start monitoring
    start_monitoring
    
    # Run tests
    test_voice_assistant_health
    run_automated_tests
    test_ari_integration
    test_sip_configuration
    simulate_call_test
    
    # Manual testing
    wait_for_manual_test
    
    # Generate report
    generate_test_report
    
    print_success "Docker testing scenario completed!"
    
    echo ""
    echo "🐳 Docker containers are still running for additional testing"
    echo "📋 Available services:"
    echo "   • Asterisk: http://localhost:8088/ari/asterisk/info"
    echo "   • Voice Assistant: http://localhost:8000/health"
    echo ""
    echo "💡 To stop Docker services, select option 6 from the main menu"
    echo ""
    read -p "Press Enter to return to main menu..." 
    show_main_menu
}

run_linux_testing() {
    print_section "Starting Linux Testing Scenario"
    
    # Install dependencies
    install_system_dependencies
    install_python_dependencies
    setup_environment
    
    # Validate OpenAI key
    if ! validate_openai_key; then
        print_warning "OpenAI API key validation failed, but continuing with testing"
        print_info "Some AI features may not work properly"
        sleep 2
    fi
    
    # Install and configure Asterisk
    install_linux_asterisk
    configure_linux_asterisk
    start_linux_asterisk
    test_linux_asterisk
    
    # Start voice assistant
    start_voice_assistant
    
    # Start monitoring
    start_monitoring
    
    # Run tests
    test_voice_assistant_health
    run_automated_tests
    test_ari_integration
    test_sip_configuration
    simulate_call_test
    
    # Manual testing
    wait_for_manual_test
    
    # Generate report
    generate_test_report
    
    print_success "Linux testing scenario completed!"
    
    echo ""
    echo "🐧 Linux Asterisk services are still running"
    echo "📋 Available services:"
    echo "   • Asterisk: http://localhost:8088/ari/asterisk/info"
    echo "   • Voice Assistant: http://localhost:8000/health"
    echo ""
    read -p "Press Enter to return to main menu..." 
    show_main_menu
}

install_dependencies_only() {
    print_section "Installing Dependencies Only"
    
    install_system_dependencies
    install_python_dependencies
    setup_docker
    setup_environment
    
    print_success "Dependencies installation completed!"
    echo "You can now run the tests using option 4"
    read -p "Press Enter to return to main menu..."
    show_main_menu
}

run_tests_only() {
    print_section "Running Tests Only"
    
    # Assume services are already running
    print_info "Assuming services are already running..."
    
    # Start monitoring
    start_monitoring
    
    # Run tests
    test_voice_assistant_health
    run_automated_tests
    test_ari_integration
    test_sip_configuration
    simulate_call_test
    
    # Manual testing
    wait_for_manual_test
    
    # Generate report
    generate_test_report
    
    print_success "Tests completed!"
}

# ============================================================================
# SCRIPT ENTRY POINT
# ============================================================================

main() {
    # Create log directory
    mkdir -p "$LOG_DIR"
    
    # Start logging
    log_message "Starting NPCL Voice Assistant E2E Testing Script"
    log_message "Script directory: $SCRIPT_DIR"
    log_message "Project root: $PROJECT_ROOT"
    
    # Check if running as root (not recommended)
    if [ "$EUID" -eq 0 ]; then
        print_warning "Running as root is not recommended"
        read -p "Continue anyway? (y/n): " continue_as_root
        if [ "$continue_as_root" != "y" ]; then
            exit 1
        fi
    fi
    
    # Show main menu
    show_main_menu
}

# Run main function
main "$@"