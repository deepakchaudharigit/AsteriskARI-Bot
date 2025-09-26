#!/bin/bash

# =============================================================================
# NPCL Asterisk ARI Voice Assistant - Docker Startup Script
# =============================================================================

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

print_banner() {
    echo -e "${CYAN}===============================================================================${NC}"
    echo -e "${WHITE}🐳 NPCL Voice Assistant - Docker Startup${NC}"
    echo -e "${WHITE}📞 Containerized Voice Assistant with Asterisk${NC}"
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

print_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

main() {
    print_banner
    
    # Check Docker
    print_step "Checking Docker installation"
    if command -v docker >/dev/null 2>&1; then
        print_success "Docker found"
    else
        echo "❌ Docker not found. Please install Docker first."
        echo "   Visit: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    # Check Docker Compose
    print_step "Checking Docker Compose"
    if command -v docker-compose >/dev/null 2>&1; then
        print_success "Docker Compose found"
    else
        echo "❌ Docker Compose not found. Please install Docker Compose."
        exit 1
    fi
    
    # Check .env file
    print_step "Checking environment configuration"
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp ".env.example" ".env"
            print_success ".env file created from template"
            print_warning "Please edit .env file and add your OpenAI API key"
        else
            echo "❌ .env.example not found"
            exit 1
        fi
    else
        print_success ".env file exists"
    fi
    
    # Create required directories
    print_step "Creating required directories"
    mkdir -p logs sounds recordings data
    print_success "Directories created"
    
    # Start services
    print_step "Starting Docker services"
    
    echo ""
    echo -e "${CYAN}===============================================================================${NC}"
    echo -e "${WHITE}🚀 Starting NPCL Voice Assistant with Docker...${NC}"
    echo -e "${CYAN}===============================================================================${NC}"
    echo -e "${GREEN}📞 Voice Assistant: http://localhost:8000${NC}"
    echo -e "${GREEN}📚 API Docs: http://localhost:8000/docs${NC}"
    echo -e "${GREEN}🏥 Health Check: http://localhost:8000/health${NC}"
    echo -e "${GREEN}🐳 Portainer: http://localhost:9000${NC}"
    echo -e "${YELLOW}⏹️  Press Ctrl+C to stop all services${NC}"
    echo -e "${CYAN}===============================================================================${NC}"
    echo ""
    
    # Start with docker-compose
    docker-compose up --build
}

cleanup() {
    echo ""
    print_info "Stopping Docker services..."
    docker-compose down
    print_success "Services stopped"
    exit 0
}

trap cleanup SIGINT SIGTERM

if [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
    echo "NPCL Voice Assistant - Docker Startup"
    echo ""
    echo "Usage: $0"
    echo ""
    echo "This script will:"
    echo "  1. Check Docker and Docker Compose"
    echo "  2. Set up environment configuration"
    echo "  3. Start all services with Docker Compose"
    echo ""
    echo "Services included:"
    echo "  - NPCL Voice Assistant (port 8000)"
    echo "  - Asterisk PBX (ports 5060, 8088)"
    echo "  - Redis Cache (port 6379)"
    echo "  - Portainer Management (port 9000)"
    echo ""
    exit 0
fi

main "$@"