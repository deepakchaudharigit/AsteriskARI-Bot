#!/bin/bash

# =============================================================================
# NPCL Asterisk ARI Voice Assistant - One-Click Startup Script
# =============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# =============================================================================
# Banner and Utility Functions
# =============================================================================

print_banner() {
    echo -e "${CYAN}===============================================================================${NC}"
    echo -e "${WHITE}🚀 NPCL Asterisk ARI Voice Assistant - One-Click Startup${NC}"
    echo -e "${WHITE}📞 Enterprise Voice Assistant with OpenAI GPT-4 Realtime API${NC}"
    echo -e "${WHITE}🏢 NPCL (Noida Power Corporation Limited)${NC}"
    echo -e "${CYAN}===============================================================================${NC}"
    echo ""
}

print_step() {
    echo -e "${BLUE}🔄 $1...${NC}"
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
    echo -e "${CYAN}ℹ️  $1${NC}"
}

# =============================================================================
# Main Setup and Run Function
# =============================================================================

main() {
    print_banner
    
    # Step 1: Check Python
    print_step "Checking Python installation"
    if command -v python3 >/dev/null 2>&1; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        print_success "Python $PYTHON_VERSION found"
    else
        print_error "Python 3 not found. Please install Python 3.8 or higher"
        exit 1
    fi
    
    # Step 2: Setup Virtual Environment
    print_step "Setting up virtual environment"
    if [ ! -d ".venv" ]; then
        python3 -m venv .venv
        print_success "Virtual environment created"
    else
        print_info "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source .venv/bin/activate
    print_success "Virtual environment activated"
    
    # Step 3: Upgrade pip and install dependencies
    print_step "Installing dependencies"
    pip install --upgrade pip >/dev/null 2>&1
    
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_success "Dependencies installed"
    else
        print_error "requirements.txt not found"
        exit 1
    fi
    
    # Step 4: Setup environment file
    print_step "Setting up environment configuration"
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp ".env.example" ".env"
            print_success ".env file created from template"
            print_warning "Please edit .env file and add your OpenAI API key"
        else
            print_error ".env.example not found"
            exit 1
        fi
    else
        print_success ".env file already exists"
    fi
    
    # Step 5: Create required directories
    print_step "Creating required directories"
    mkdir -p logs sounds sounds/temp recordings data
    print_success "Directories created"
    
    # Step 6: Check OpenAI API key
    print_step "Checking OpenAI API configuration"
    if [ -f ".env" ]; then
        source .env
        if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "your_actual_openai_api_key_here" ]; then
            print_warning "OpenAI API key not configured in .env file"
            print_info "Please edit .env and set OPENAI_API_KEY=your_actual_api_key"
            print_info "Get your API key from: https://platform.openai.com/api-keys"
        else
            print_success "OpenAI API key configured"
        fi
    fi
    
    # Step 7: Check Asterisk (optional)
    print_step "Checking Asterisk ARI connection"
    if curl -s -f -u "asterisk:1234" "http://localhost:8088/ari/asterisk/info" >/dev/null 2>&1; then
        print_success "Asterisk ARI: Connected"
    else
        print_warning "Asterisk ARI: Not accessible (will start anyway)"
        print_info "Telephony features may not work without Asterisk"
    fi
    
    # Step 8: Start the application
    echo ""
    echo -e "${CYAN}===============================================================================${NC}"
    echo -e "${WHITE}🎯 Starting NPCL Voice Assistant...${NC}"
    echo -e "${CYAN}===============================================================================${NC}"
    echo -e "${GREEN}📞 Ready for calls on extension 1000${NC}"
    echo -e "${GREEN}🌐 Web Interface: http://localhost:8000${NC}"
    echo -e "${GREEN}📚 API Docs: http://localhost:8000/docs${NC}"
    echo -e "${GREEN}🏥 Health Check: http://localhost:8000/health${NC}"
    echo -e "${YELLOW}⏹️  Press Ctrl+C to stop the service${NC}"
    echo -e "${CYAN}===============================================================================${NC}"
    echo ""
    
    # Set Python path and start the application
    export PYTHONPATH="$PWD/src:$PYTHONPATH"
    
    # Try different entry points
    if [ -f "ari_bot.py" ]; then
        print_info "Starting via ari_bot.py..."
        python3 ari_bot.py
    elif [ -f "start_voice_assistant.py" ]; then
        print_info "Starting via start_voice_assistant.py..."
        python3 start_voice_assistant.py
    elif [ -f "src/run_realtime_server.py" ]; then
        print_info "Starting via src/run_realtime_server.py..."
        python3 src/run_realtime_server.py
    else
        print_error "No main application file found"
        print_info "Expected: ari_bot.py, start_voice_assistant.py, or src/run_realtime_server.py"
        exit 1
    fi
}

# =============================================================================
# Cleanup on exit
# =============================================================================

cleanup() {
    echo ""
    print_info "Shutting down NPCL Voice Assistant..."
    print_success "Goodbye!"
    exit 0
}

trap cleanup SIGINT SIGTERM

# =============================================================================
# Help function
# =============================================================================

show_help() {
    echo "NPCL Asterisk ARI Voice Assistant - One-Click Startup"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --help, -h    Show this help message"
    echo ""
    echo "This script will:"
    echo "  1. Check Python installation"
    echo "  2. Set up virtual environment"
    echo "  3. Install dependencies"
    echo "  4. Configure environment"
    echo "  5. Start the voice assistant"
    echo ""
    echo "Requirements:"
    echo "  - Python 3.8 or higher"
    echo "  - Internet connection for dependencies"
    echo "  - OpenAI API key (configured in .env)"
    echo "  - Asterisk PBX (optional, for telephony)"
    echo ""
    echo "After startup, the service will be available at:"
    echo "  - Web Interface: http://localhost:8000"
    echo "  - API Documentation: http://localhost:8000/docs"
    echo "  - Health Check: http://localhost:8000/health"
}

# =============================================================================
# Entry Point
# =============================================================================

if [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
    show_help
    exit 0
fi

main "$@"