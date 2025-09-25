#!/bin/bash

# NPCL Voice Assistant - Quick Start Script
# Comprehensive startup script for different deployment modes

set -e

echo "🚀 NPCL Voice Assistant - Quick Start"
echo "====================================="
echo ""

# Function to show usage
show_usage() {
    echo "Usage: $0 [mode]"
    echo ""
    echo "Available modes:"
    echo "  local     - Start local development server (default)"
    echo "  docker    - Start with Docker containers"
    echo "  asterisk  - Start only Asterisk container"
    echo "  test      - Run integration tests"
    echo "  help      - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 local    # Start local development server"
    echo "  $0 docker   # Start full Docker setup"
    echo "  $0 asterisk # Start only Asterisk for local development"
}

# Function to start local development
start_local() {
    echo "🏠 Starting Local Development Mode"
    echo "================================="
    
    # Check virtual environment
    if [ ! -d ".venv" ]; then
        echo "❌ Virtual environment not found!"
        echo "🔧 Setting up environment first..."
        ./setup_environment.sh
    fi
    
    # Activate virtual environment
    echo "🔄 Activating virtual environment..."
    source .venv/bin/activate
    
    # Check if Asterisk container is running
    if ! docker ps | grep -q "voice-assistant-asterisk"; then
        echo "🐳 Starting Asterisk container..."
        docker-compose up -d asterisk
        echo "⏳ Waiting for Asterisk to start..."
        sleep 15
    fi
    
    # Start voice assistant server
    echo "🎤 Starting NPCL Voice Assistant..."
    echo "📡 Server will be available at: http://localhost:8000"
    echo "📞 Call extension 1000 to test voice assistant"
    echo ""
    python3 src/run_realtime_server.py
}

# Function to start Docker mode
start_docker() {
    echo "🐳 Starting Docker Mode"
    echo "======================"
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker not found. Please install Docker first."
        exit 1
    fi
    
    # Stop existing containers
    echo "🛑 Stopping existing containers..."
    docker-compose down
    
    # Start services
    echo "🚀 Starting Docker services..."
    docker-compose up -d --build
    
    # Wait for services
    echo "⏳ Waiting for services to start..."
    sleep 30
    
    # Show status
    echo "📊 Service Status:"
    docker-compose ps
    
    echo ""
    echo "🌐 Available endpoints:"
    echo "  • Voice Assistant: http://localhost:8000"
    echo "  • API Docs: http://localhost:8000/docs"
    echo "  • Asterisk ARI: http://localhost:8088/ari"
    echo ""
    echo "📞 SIP Configuration for Zoiper:"
    echo "  • Username: 1001"
    echo "  • Password: 1234"
    echo "  • Server: localhost:5060"
    echo "  • Call 1000 to test voice assistant"
}

# Function to start only Asterisk
start_asterisk() {
    echo "📞 Starting Asterisk Only"
    echo "========================"
    
    # Stop existing containers
    docker-compose down
    
    # Start only Asterisk
    echo "🚀 Starting Asterisk container..."
    docker-compose up -d asterisk
    
    # Wait for startup
    echo "⏳ Waiting for Asterisk to start..."
    sleep 15
    
    # Show status
    echo "📊 Asterisk Status:"
    docker ps --filter name=asterisk
    
    echo ""
    echo "✅ Asterisk is ready!"
    echo "📞 SIP Server: localhost:5060"
    echo "🔧 ARI Interface: http://localhost:8088/ari"
    echo ""
    echo "💡 Now you can start the local voice assistant:"
    echo "   ./activate_and_start.sh"
}

# Function to run tests
run_tests() {
    echo "🧪 Running Integration Tests"
    echo "============================"
    
    # Check virtual environment
    if [ ! -d ".venv" ]; then
        echo "❌ Virtual environment not found!"
        echo "🔧 Setting up environment first..."
        ./setup_environment.sh
    fi
    
    # Activate virtual environment
    source .venv/bin/activate
    
    # Run tests
    echo "🔍 Running OpenAI integration tests..."
    python3 test_openai_integration.py
    
    echo ""
    echo "🔍 Running system status check..."
    python3 check_system_status.py
}

# Main script logic
case "${1:-local}" in
    "local")
        start_local
        ;;\n    "docker")
        start_docker
        ;;\n    "asterisk")
        start_asterisk
        ;;\n    "test")
        run_tests
        ;;\n    "help"|"-h"|"--help")
        show_usage
        ;;\n    *)
        echo "❌ Unknown mode: $1"
        echo ""
        show_usage
        exit 1
        ;;\nesac