#!/bin/bash

# NPCL Voice Assistant - Complete System Test
# This script starts all components and runs comprehensive tests

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
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

# Function to cleanup on exit
cleanup() {
    print_status "Cleaning up processes..."
    
    # Kill background processes
    if [ ! -z "$ASTERISK_PID" ]; then
        docker-compose down > /dev/null 2>&1 || true
    fi
    
    if [ ! -z "$ARI_BOT_PID" ]; then
        kill $ARI_BOT_PID > /dev/null 2>&1 || true
    fi
    
    if [ ! -z "$ARI_BRIDGE_PID" ]; then
        kill $ARI_BRIDGE_PID > /dev/null 2>&1 || true
    fi
    
    if [ ! -z "$MONITOR_PID" ]; then
        kill $MONITOR_PID > /dev/null 2>&1 || true
    fi
    
    print_success "Cleanup completed"
}

# Set trap for cleanup
trap cleanup EXIT INT TERM

# Main function
main() {
    echo "🚀 NPCL VOICE ASSISTANT - COMPLETE SYSTEM TEST"
    echo "=" * 60
    echo ""
    
    # Check prerequisites
    print_status "Checking prerequisites..."
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "docker-compose not found. Please install Docker Compose."
        exit 1
    fi
    
    if [ ! -f ".env" ]; then
        print_error ".env file not found. Please create it with your OpenAI API key."
        exit 1
    fi
    
    if [ ! -d ".venv" ]; then
        print_error "Virtual environment not found. Please run: python3 -m venv .venv && .venv/bin/pip install -r requirements.txt"
        exit 1
    fi
    
    print_success "Prerequisites check passed"
    
    # Step 1: Start Asterisk
    print_status "Starting Asterisk in Docker..."
    docker-compose up -d asterisk
    ASTERISK_PID="docker"
    
    # Wait for Asterisk to be ready
    print_status "Waiting for Asterisk to be ready..."
    sleep 10
    
    # Check if Asterisk is running
    if ! docker-compose ps asterisk | grep -q "Up"; then
        print_error "Asterisk failed to start"
        exit 1
    fi
    print_success "Asterisk is running"
    
    # Step 2: Start ARI Bot
    print_status "Starting ARI Bot..."
    .venv/bin/python3 src/main.py --ari-bot > ari_bot.log 2>&1 &
    ARI_BOT_PID=$!
    
    # Wait for ARI Bot to be ready
    print_status "Waiting for ARI Bot to be ready..."
    sleep 5
    
    # Check if ARI Bot is running
    for i in {1..10}; do
        if curl -s http://localhost:8000/ari/health > /dev/null 2>&1; then
            print_success "ARI Bot is running"
            break
        fi
        if [ $i -eq 10 ]; then
            print_error "ARI Bot failed to start"
            exit 1
        fi
        sleep 2
    done
    
    # Step 3: Start ARI Bridge
    print_status "Starting ARI Bridge..."
    .venv/bin/python3 fix_ari_registration.py > ari_bridge.log 2>&1 &
    ARI_BRIDGE_PID=$!
    
    # Wait for ARI Bridge to connect
    print_status "Waiting for ARI Bridge to connect..."
    sleep 5
    
    # Check if ARI Bridge is connected
    if ! ps -p $ARI_BRIDGE_PID > /dev/null 2>&1; then
        print_error "ARI Bridge failed to start"
        exit 1
    fi
    print_success "ARI Bridge is running"
    
    # Step 4: Run System Diagnostics
    print_status "Running system diagnostics..."
    .venv/bin/python3 diagnose_call_flow.py > diagnostic.log 2>&1
    
    # Check diagnostic results
    if grep -q "ALL SYSTEMS OPERATIONAL" diagnostic.log; then
        print_success "System diagnostics passed"
    else
        print_warning "System diagnostics show some issues (check diagnostic.log)"
    fi
    
    # Step 5: Start Call Monitoring
    print_status "Starting call monitoring..."
    .venv/bin/python3 test_call_monitoring.py > monitor.log 2>&1 &
    MONITOR_PID=$!
    
    sleep 3
    print_success "Call monitoring started"
    
    # Step 6: System Status Summary
    echo ""
    echo "🎯 SYSTEM STATUS SUMMARY"
    echo "=" * 40
    
    # Check Asterisk
    if docker-compose ps asterisk | grep -q "Up"; then
        print_success "Asterisk: Running"
    else
        print_error "Asterisk: Not running"
    fi
    
    # Check ARI Bot
    if curl -s http://localhost:8000/ari/health | grep -q "healthy"; then
        print_success "ARI Bot: Healthy"
    else
        print_error "ARI Bot: Not healthy"
    fi
    
    # Check ARI Bridge
    if ps -p $ARI_BRIDGE_PID > /dev/null 2>&1; then
        print_success "ARI Bridge: Connected"
    else
        print_error "ARI Bridge: Not connected"
    fi
    
    # Check Call Monitoring
    if ps -p $MONITOR_PID > /dev/null 2>&1; then
        print_success "Call Monitor: Active"
    else
        print_error "Call Monitor: Not active"
    fi
    
    # Step 7: Enhanced TTS Test
    echo ""
    print_status "Testing Enhanced TTS..."
    
    if .venv/bin/python3 -c "
import os
os.environ['OPENAI_API_KEY'] = '$(grep OPENAI_API_KEY .env | cut -d= -f2)'
from src.voice_assistant.audio.simple_enhanced_tts import SimpleEnhancedTTS
tts = SimpleEnhancedTTS()
success = tts.speak_text_enhanced('NPCL Enhanced TTS test successful!')
print('SUCCESS' if success else 'FAILED')
" 2>/dev/null | grep -q "SUCCESS"; then
        print_success "Enhanced TTS: Working"
    else
        print_warning "Enhanced TTS: Using fallback"
    fi
    
    # Step 8: API Endpoints Test
    echo ""
    print_status "Testing API endpoints..."
    
    # Test health endpoint
    if curl -s http://localhost:8000/ari/health | grep -q "healthy"; then
        print_success "Health endpoint: OK"
    else
        print_error "Health endpoint: Failed"
    fi
    
    # Test calls endpoint
    if curl -s http://localhost:8000/ari/calls | grep -q "active_calls"; then
        print_success "Calls endpoint: OK"
    else
        print_error "Calls endpoint: Failed"
    fi
    
    # Test status endpoint
    if curl -s http://localhost:8000/ari/status | grep -q "is_running"; then
        print_success "Status endpoint: OK"
    else
        print_error "Status endpoint: Failed"
    fi
    
    # Step 9: Configuration Summary
    echo ""
    echo "🔧 CONFIGURATION SUMMARY"
    echo "=" * 40
    
    # Extract key configuration
    OPENAI_KEY=$(grep OPENAI_API_KEY .env | cut -d= -f2 | cut -c1-20)
    VOICE_MODEL=$(grep VOICE_MODEL .env | cut -d= -f2)
    TTS_MODEL=$(grep TTS_MODEL .env | cut -d= -f2)
    STASIS_APP=$(grep STASIS_APP .env | cut -d= -f2)
    
    echo "🔑 OpenAI API Key: ${OPENAI_KEY}..."
    echo "🎤 Voice Model: ${VOICE_MODEL:-fable}"
    echo "🔊 TTS Model: ${TTS_MODEL:-tts-1-hd}"
    echo "📞 Stasis App: ${STASIS_APP:-openai-voice-assistant}"
    
    # Step 10: Test Instructions
    echo ""
    echo "📞 CALL TEST INSTRUCTIONS"
    echo "=" * 40
    echo "1. Configure SIP client:"
    echo "   📱 Server: localhost:5060"
    echo "   👤 Username: 1001"
    echo "   🔐 Password: 1001"
    echo ""
    echo "2. Make test call:"
    echo "   📞 Dial: 1000"
    echo "   🎤 Speak when connected"
    echo "   👂 Listen for AI responses"
    echo ""
    echo "3. Expected behavior:"
    echo "   ✅ Call connects immediately"
    echo "   ✅ Professional AI voice responds"
    echo "   ✅ Real-time conversation"
    echo "   ✅ Call appears in monitoring"
    echo ""
    
    # Step 11: Live Monitoring
    echo "🔍 LIVE SYSTEM MONITORING"
    echo "=" * 40
    echo "Press Ctrl+C to stop monitoring and exit"
    echo ""
    
    # Monitor system in real-time
    while true; do
        # Check system health
        TIMESTAMP=$(date +'%H:%M:%S')
        
        # Check active calls
        ACTIVE_CALLS=$(curl -s http://localhost:8000/ari/calls 2>/dev/null | grep -o '"call_count":[0-9]*' | cut -d: -f2 || echo "0")
        
        if [ "$ACTIVE_CALLS" -gt 0 ]; then
            print_success "[$TIMESTAMP] Active calls: $ACTIVE_CALLS"
        else
            print_info "[$TIMESTAMP] No active calls"
        fi
        
        # Check for new events in logs
        if [ -f "ari_bridge.log" ]; then
            NEW_EVENTS=$(tail -n 5 ari_bridge.log | grep "INCOMING CALL DETECTED" | wc -l)
            if [ "$NEW_EVENTS" -gt 0 ]; then
                print_success "[$TIMESTAMP] New call events detected!"
            fi
        fi
        
        sleep 10
    done
}

# Run main function
main "$@"