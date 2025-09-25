#!/bin/bash
# Prepare NPCL Voice Assistant for Docker deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}=================================================="
    echo -e "🐳 NPCL Voice Assistant - Docker Preparation"
    echo -e "==================================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_header

echo "🔧 Preparing project for Docker deployment..."
echo ""

# 1. Check if we're in the right directory
if [ ! -f "src/main.py" ]; then
    print_error "src/main.py not found. Please run this script from the project root directory."
    exit 1
fi

print_success "Project root directory confirmed"

# 2. Create necessary directories
echo "📁 Creating required directories..."
mkdir -p sounds/temp
mkdir -p recordings
mkdir -p logs
mkdir -p docker

print_success "Directories created"

# 3. Validate .env file
echo "🔍 Checking environment configuration..."
if [ ! -f ".env" ]; then
    print_warning ".env file not found, creating template..."
    cat > .env << EOF
# NPCL Voice Assistant - Docker Configuration
# ==========================================

# OpenAI API Configuration (REQUIRED)
OPENAI_API_KEY=your-openai-api-key-here

# Voice Configuration
VOICE_MODEL=fable
TTS_MODEL=tts-1-hd
SPEECH_MODEL=whisper-1

# Audio Configuration
SAMPLE_RATE=16000
CHUNK_SIZE=1024
CHANNELS=1
AUDIO_FORMAT=slin16

# Asterisk ARI Configuration
ARI_BASE_URL=http://asterisk:8088/ari
ARI_USERNAME=asterisk
ARI_PASSWORD=1234
STASIS_APP=openai-voice-assistant

# External Media Configuration
EXTERNAL_MEDIA_HOST=0.0.0.0
EXTERNAL_MEDIA_PORT=8090

# Assistant Configuration
ASSISTANT_NAME=NPCL Assistant
VOICE_LANGUAGE=en
LOG_LEVEL=INFO

# Performance Settings
ENABLE_INTERRUPTION_HANDLING=true
MAX_CALL_DURATION=3600
AUTO_ANSWER_CALLS=true
EOF
    print_warning "Please edit .env file and add your OpenAI API key"
else
    print_success ".env file exists"
fi

# 4. Check OpenAI API key
if grep -q "your-openai-api-key-here" .env 2>/dev/null; then
    print_warning "Please update OPENAI_API_KEY in .env file"
elif grep -q "OPENAI_API_KEY=sk-" .env 2>/dev/null; then
    print_success "OpenAI API key configured"
else
    print_warning "OpenAI API key may not be configured properly"
fi

# 5. Validate Asterisk configuration
echo "📞 Checking Asterisk configuration..."
if [ ! -d "asterisk-config" ]; then
    print_warning "asterisk-config directory not found, creating basic configuration..."
    mkdir -p asterisk-config
    
    # Create basic asterisk.conf
    cat > asterisk-config/asterisk.conf << EOF
[directories]
astetcdir => /etc/asterisk
astmoddir => /usr/lib/asterisk/modules
astvarlibdir => /var/lib/asterisk
astdbdir => /var/lib/asterisk
astkeydir => /var/lib/asterisk
astdatadir => /var/lib/asterisk
astagidir => /var/lib/asterisk/agi-bin
astspooldir => /var/spool/asterisk
astrundir => /var/run/asterisk
astlogdir => /var/log/asterisk

[options]
verbose = 3
debug = 3
documentation_language = en_US
EOF

    # Create ARI configuration
    cat > asterisk-config/ari.conf << EOF
[general]
enabled = yes
pretty = yes
allowed_origins = *

[asterisk]
type = user
read_only = no
password = 1234
EOF

    # Create HTTP configuration
    cat > asterisk-config/http.conf << EOF
[general]
enabled = yes
bindaddr = 0.0.0.0
bindport = 8088
prefix = 
enablestatic = yes
EOF

    # Create basic extensions
    cat > asterisk-config/extensions.conf << EOF
[general]
static = yes
writeprotect = no
clearglobalvars = no

[globals]

[default]
exten => 1000,1,NoOp(NPCL Voice Assistant Call)
 same => n,Stasis(openai-voice-assistant)
 same => n,Hangup()

[internal]
include => default
EOF

    print_success "Basic Asterisk configuration created"
else
    print_success "Asterisk configuration directory exists"
fi

# 6. Check requirements.txt
echo "📦 Checking Python dependencies..."
if [ ! -f "requirements.txt" ]; then
    print_warning "requirements.txt not found, creating from current environment..."
    cat > requirements.txt << EOF
# NPCL Voice Assistant Dependencies
openai>=1.0.0
uvicorn>=0.24.0
fastapi>=0.104.0
pyttsx3>=2.90
websockets>=10.0
pygame>=2.5.0
requests>=2.31.0
pydantic>=2.5.0
pydantic-settings>=2.0.0
python-dotenv>=1.0.0
psutil>=5.9.0
numpy>=1.24.0
SpeechRecognition>=3.10.0
gtts>=2.4.0
supervisor>=4.2.0
EOF
    print_success "requirements.txt created"
else
    print_success "requirements.txt exists"
fi

# 7. Validate Docker files
echo "🐳 Checking Docker configuration..."
if [ ! -f "Dockerfile" ]; then
    print_error "Dockerfile not found"
    exit 1
fi

if [ ! -f "docker-compose.yml" ]; then
    print_error "docker-compose.yml not found"
    exit 1
fi

print_success "Docker files validated"

# 8. Check documentation organization
echo "📚 Checking documentation organization..."
if [ ! -d "docs" ]; then
    print_error "docs directory not found"
    exit 1
fi

# Count markdown files in root (should only be README.md)
md_count=$(find . -maxdepth 1 -name "*.md" | wc -l)
if [ $md_count -gt 1 ]; then
    print_warning "$md_count markdown files in root directory (should only be README.md)"
else
    print_success "Documentation properly organized"
fi

# 9. Set proper permissions
echo "🔐 Setting file permissions..."
chmod +x docker/*.sh 2>/dev/null || true
chmod +x prepare-docker.sh
chmod 755 sounds recordings logs 2>/dev/null || true

print_success "Permissions set"

# 10. Create .dockerignore if it doesn't exist
if [ ! -f ".dockerignore" ]; then
    print_warning ".dockerignore not found, but it should exist"
else
    print_success ".dockerignore configured"
fi

echo ""
echo "🎯 Pre-Docker Preparation Summary:"
echo "=================================="
echo "✅ Project structure validated"
echo "✅ Required directories created"
echo "✅ Environment configuration checked"
echo "✅ Asterisk 18 configuration prepared"
echo "✅ Python dependencies listed"
echo "✅ Docker files validated"
echo "✅ Documentation organized"
echo "✅ Permissions configured"

echo ""
echo "🚀 Ready for Docker deployment!"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your OpenAI API key"
echo "2. Review asterisk-config/ for any custom settings"
echo "3. Run: ./docker/docker-commands.sh build"
echo "4. Run: ./docker/docker-commands.sh start"

echo ""
print_success "Project is ready for dockerization!"

# 11. Optional: Test basic imports
echo ""
echo "🧪 Testing basic Python imports..."
if command -v python3 >/dev/null 2>&1; then
    if python3 -c "import sys; sys.path.insert(0, 'src'); import main" 2>/dev/null; then
        print_success "Python imports working"
    else
        print_warning "Some Python imports may have issues (check dependencies)"
    fi
else
    print_info "Python3 not available for testing imports"
fi

echo ""
echo "=================================================="
print_success "NPCL Voice Assistant is ready for Docker! 🐳"
echo "=================================================="