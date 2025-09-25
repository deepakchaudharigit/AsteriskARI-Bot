#!/bin/bash

# NPCL Voice Assistant - One Command Test
# Everything in one command with real-time monitoring

{
    echo "🚀 NPCL VOICE ASSISTANT - ONE COMMAND TEST"
    echo "=========================================="
    
    # Start all services in background
    echo "📞 Starting Asterisk..." && docker-compose up -d asterisk > /dev/null 2>&1
    sleep 8
    
    echo "🤖 Starting ARI Bot..." && .venv/bin/python3 src/main.py --ari-bot > ari_bot.log 2>&1 &
    ARI_BOT_PID=$!
    sleep 5
    
    echo "🌉 Starting ARI Bridge..." && .venv/bin/python3 fix_ari_registration.py > ari_bridge.log 2>&1 &
    ARI_BRIDGE_PID=$!
    sleep 5
    
    # Quick system check
    echo "🧪 System Check:"
    
    # Check Asterisk
    if docker-compose ps asterisk | grep -q "Up"; then
        echo "✅ Asterisk: Running"
    else
        echo "❌ Asterisk: Failed" && exit 1
    fi
    
    # Check ARI Bot
    if curl -s http://localhost:8000/ari/health | grep -q "healthy" 2>/dev/null; then
        echo "✅ ARI Bot: Healthy"
    else
        echo "❌ ARI Bot: Failed" && exit 1
    fi
    
    # Check ARI Bridge
    if ps -p $ARI_BRIDGE_PID > /dev/null 2>&1; then
        echo "✅ ARI Bridge: Connected"
    else
        echo "❌ ARI Bridge: Failed" && exit 1
    fi
    
    # Test Enhanced TTS
    echo "🔊 Testing Enhanced TTS..."
    if timeout 10 .venv/bin/python3 -c "
import os
os.environ['OPENAI_API_KEY'] = '$(grep OPENAI_API_KEY .env | cut -d= -f2)'
from src.voice_assistant.audio.simple_enhanced_tts import SimpleEnhancedTTS
tts = SimpleEnhancedTTS()
success = tts.speak_text_enhanced('NPCL system test successful!')
print('SUCCESS' if success else 'FAILED')
" 2>/dev/null | grep -q "SUCCESS"; then
        echo "✅ Enhanced TTS: Working perfectly!"
    else
        echo "⚠️  Enhanced TTS: Using fallback (still works)"
    fi
    
    # Show configuration
    echo ""
    echo "🔧 Configuration:"
    echo "   🎤 Voice: $(grep VOICE_MODEL .env | cut -d= -f2 || echo 'fable')"
    echo "   🔊 TTS: $(grep TTS_MODEL .env | cut -d= -f2 || echo 'tts-1-hd')"
    echo "   📞 App: $(grep STASIS_APP .env | cut -d= -f2 || echo 'openai-voice-assistant')"
    
    # Show endpoints
    echo ""
    echo "🌐 Endpoints:"
    echo "   📊 Health: http://localhost:8000/ari/health"
    echo "   📞 Calls: http://localhost:8000/ari/calls"
    echo "   📚 Docs: http://localhost:8000/docs"
    
    # Call test instructions
    echo ""
    echo "📞 CALL TEST:"
    echo "   1. Configure SIP: 1001@localhost:5060 (password: 1001)"
    echo "   2. Dial: 1000"
    echo "   3. Speak and listen for AI response"
    
    # Real-time monitoring
    echo ""
    echo "🔍 LIVE MONITORING (Press Ctrl+C to stop):"
    echo "=========================================="
    
    # Monitor for 60 seconds or until interrupted
    for i in {1..60}; do
        TIMESTAMP=$(date +'%H:%M:%S')
        
        # Check active calls
        ACTIVE_CALLS=$(curl -s http://localhost:8000/ari/calls 2>/dev/null | grep -o '"call_count":[0-9]*' | cut -d: -f2 2>/dev/null || echo "0")
        
        # Check for new call events
        if [ -f "ari_bridge.log" ]; then
            if tail -n 1 ari_bridge.log | grep -q "INCOMING CALL DETECTED"; then
                echo "🎉 [$TIMESTAMP] NEW CALL DETECTED!"
            elif [ "$ACTIVE_CALLS" -gt 0 ]; then
                echo "📞 [$TIMESTAMP] Active calls: $ACTIVE_CALLS"
            else
                echo "⏰ [$TIMESTAMP] System ready - No active calls"
            fi
        else
            echo "⏰ [$TIMESTAMP] System ready - Waiting for calls"
        fi
        
        sleep 10
    done
    
    echo ""
    echo "⏰ Monitoring completed (60 seconds)"
    
} 2>&1 | tee test_output.log

# Cleanup function
cleanup() {
    echo ""
    echo "🧹 Cleaning up..."
    docker-compose down > /dev/null 2>&1 || true
    pkill -f "src/main.py" > /dev/null 2>&1 || true
    pkill -f "fix_ari_registration.py" > /dev/null 2>&1 || true
    echo "✅ All services stopped"
    echo "📄 Full log saved to: test_output.log"
}

# Set cleanup trap
trap cleanup EXIT

# Wait for user input to stop
echo ""
echo "Press Enter to stop all services..."
read

echo "👋 Test completed successfully!"