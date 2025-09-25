#!/bin/bash
# Docker management commands for NPCL Voice Assistant

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo -e "${BLUE}=================================================="
    echo -e "🐳 NPCL Voice Assistant - Docker Management"
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

# Check if .env file exists
check_env() {
    if [ ! -f .env ]; then
        print_error ".env file not found!"
        echo "Create .env file with your OpenAI API key:"
        echo "OPENAI_API_KEY=your-api-key-here"
        exit 1
    fi
    
    if ! grep -q "OPENAI_API_KEY=" .env; then
        print_error "OPENAI_API_KEY not found in .env file!"
        exit 1
    fi
    
    print_success ".env file configured"
}

# Build the Docker images
build() {
    print_header
    echo "🔨 Building NPCL Voice Assistant Docker images..."
    
    check_env
    
    echo "📦 Building Voice Assistant image..."
    docker build -t npcl-voice-assistant:latest .
    
    echo "📞 Building custom Asterisk 20 LTS image..."
    docker build -f docker/Dockerfile.asterisk20 -t npcl-asterisk:20 .
    
    print_success "Docker images built successfully!"
    echo "  • npcl-voice-assistant:latest - Main application"
    echo "  • npcl-asterisk:20 - Custom Asterisk 20 LTS PBX"
}

# Start production environment
start() {
    print_header
    echo "🚀 Starting NPCL Voice Assistant (Production)..."
    
    check_env
    
    docker-compose up -d
    
    print_success "Services started!"
    echo ""
    echo "📋 Available services:"
    echo "  • Voice Assistant: http://localhost:8000"
    echo "  • API Docs: http://localhost:8000/docs"
    echo "  • Health Check: http://localhost:8000/ari/health"
    echo "  • Asterisk ARI: http://localhost:8088/ari"
    echo "  • Portainer: http://localhost:9000"
    echo ""
    echo "📞 To test: Configure SIP client to call extension 1000"
}

# Start development environment
start_dev() {
    print_header
    echo "🔧 Starting NPCL Voice Assistant (Development)..."
    
    check_env
    
    docker-compose -f docker-compose.dev.yml up -d
    
    print_success "Development environment started!"
    echo ""
    echo "🔄 Hot reload enabled - code changes will restart the service"
}

# Stop all services
stop() {
    print_header
    echo "🛑 Stopping NPCL Voice Assistant services..."
    
    docker-compose down
    docker-compose -f docker-compose.dev.yml down 2>/dev/null || true
    
    print_success "Services stopped!"
}

# View logs
logs() {
    service=${1:-npcl-voice-assistant}
    
    print_header
    echo "📋 Viewing logs for: $service"
    echo "Press Ctrl+C to exit"
    echo ""
    
    docker-compose logs -f $service
}

# Show status
status() {
    print_header
    echo "📊 Service Status:"
    echo ""
    
    docker-compose ps
    
    echo ""
    echo "🌡️ Health Checks:"
    
    # Check Voice Assistant
    if curl -s http://localhost:8000/ari/health >/dev/null 2>&1; then
        print_success "Voice Assistant: Healthy"
    else
        print_error "Voice Assistant: Unhealthy"
    fi
    
    # Check Asterisk
    if curl -s http://localhost:8088/ari/asterisk/info >/dev/null 2>&1; then
        print_success "Asterisk: Healthy"
    else
        print_error "Asterisk: Unhealthy"
    fi
    
    # Check Redis
    if docker exec npcl-redis redis-cli ping >/dev/null 2>&1; then
        print_success "Redis: Healthy"
    else
        print_error "Redis: Unhealthy"
    fi
}

# Clean up
clean() {
    print_header
    echo "🧹 Cleaning up Docker resources..."
    
    # Stop services
    docker-compose down
    docker-compose -f docker-compose.dev.yml down 2>/dev/null || true
    
    # Remove containers
    docker container prune -f
    
    # Remove images
    docker image prune -f
    
    # Remove volumes (optional)
    read -p "Remove volumes (this will delete all data)? [y/N]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker volume prune -f
        print_warning "Volumes removed - all data deleted!"
    fi
    
    print_success "Cleanup completed!"
}

# Reset everything
reset() {
    print_header
    echo "🔄 Resetting NPCL Voice Assistant..."
    
    # Stop everything
    stop
    
    # Remove containers and images
    docker-compose down --rmi all --volumes --remove-orphans
    
    # Rebuild
    build
    
    print_success "Reset completed!"
}

# Show help
help() {
    print_header
    echo "Available commands:"
    echo ""
    echo "  build     - Build Docker image"
    echo "  start     - Start production environment"
    echo "  start-dev - Start development environment (with hot reload)"
    echo "  stop      - Stop all services"
    echo "  logs      - View logs (optional: service name)"
    echo "  status    - Show service status and health"
    echo "  clean     - Clean up Docker resources"
    echo "  reset     - Reset everything and rebuild"
    echo "  help      - Show this help"
    echo ""
    echo "Examples:"
    echo "  ./docker/docker-commands.sh build"
    echo "  ./docker/docker-commands.sh start"
    echo "  ./docker/docker-commands.sh logs npcl-voice-assistant"
    echo "  ./docker/docker-commands.sh status"
}

# Main command handler
case "${1:-help}" in
    build)
        build
        ;;
    start)
        start
        ;;
    start-dev)
        start_dev
        ;;
    stop)
        stop
        ;;
    logs)
        logs $2
        ;;
    status)
        status
        ;;
    clean)
        clean
        ;;
    reset)
        reset
        ;;
    help|*)
        help
        ;;
esac