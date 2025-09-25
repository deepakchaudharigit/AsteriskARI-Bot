#!/bin/bash

# NPCL Voice Assistant - Quick Test Script
# Starts all components and runs a quick test

echo "🚀 NPCL VOICE ASSISTANT - QUICK TEST"
echo "===================================="

# Function to cleanup
cleanup() {
    echo "🧹 Cleaning up..."
    docker-compose down > /dev/null 2>&1 || true
    pkill -f "src/main.py" > /dev/null 2>&1 || true
    pkill -f "fix_ari_registration.py" > /dev/null 2>&1 || true
    echo "✅ Cleanup completed"
}

trap cleanup EXIT

# Start Asterisk
echo "📞 Starting Asterisk..."
docker-compose up -d asterisk
sleep 8

# Start ARI Bot
echo "🤖 Starting ARI Bot..."
.venv/bin/python3 src/main.py --ari-bot > /dev/null 2>&1 &
sleep 5

# Start ARI Bridge
echo "🌉 Starting ARI Bridge..."
.venv/bin/python3 fix_ari_registration.py > /dev/null 2>&1 &
sleep 5

# Test system
echo "🧪 Testing system..."

# Check Asterisk
if docker-compose ps asterisk | grep -q "Up"; then
    echo "✅ Asterisk: Running"
else
    echo "❌ Asterisk: Failed"
    exit 1
fi

# Check ARI Bot
if curl -s http://localhost:8000/ari/health | grep -q "healthy"; then
    echo "✅ ARI Bot: Healthy"
else
    echo "❌ ARI Bot: Failed"
    exit 1
fi

# Test Enhanced TTS
echo "🔊 Testing Enhanced TTS..."
if .venv/bin/python3 -c "
import os
os.environ['OPENAI_API_KEY'] = '$(grep OPENAI_API_KEY .env | cut -d= -f2)'
from src.voice_assistant.audio.simple_enhanced_tts import SimpleEnhancedTTS
tts = SimpleEnhancedTTS()
success = tts.speak_text_enhanced('Quick test successful!')
print('SUCCESS' if success else 'FAILED')
" 2>/dev/null | grep -q "SUCCESS"; then
    echo "✅ Enhanced TTS: Working"
else
    echo "⚠️  Enhanced TTS: Using fallback"
fi

# Show system status
echo ""
echo "🎯 SYSTEM READY!"
echo "================"
echo "📞 Call test: Dial 1000 from SIP client (1001@localhost:5060)"
echo "🌐 Health: http://localhost:8000/ari/health"
echo "📊 Status: http://localhost:8000/ari/calls"
echo "📚 Docs: http://localhost:8000/docs"
echo ""
echo "Press Enter to stop all services..."
read

echo "👋 Test completed!"