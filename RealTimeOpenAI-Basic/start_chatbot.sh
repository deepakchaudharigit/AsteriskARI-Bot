#!/bin/bash

# Real-time Voice Chatbot Launcher
# Clean and simple - only the working version

echo "🎙️ Starting Real-time Voice Chatbot..."
echo "=================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please create it with your OPENAI_API_KEY."
    exit 1
fi

# Check if OpenAI API key is set
if ! grep -q "OPENAI_API_KEY=" .env; then
    echo "❌ OPENAI_API_KEY not found in .env file."
    exit 1
fi

# Check Python dependencies
echo "🔍 Checking dependencies..."
source venv/bin/activate
if ! python3 -c "import pyaudio, websockets, openai, colorama, dotenv" 2>/dev/null; then
    echo "❌ Missing dependencies. Please run: pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment and run chatbot
echo "✅ Environment check passed!"
echo ""
echo "Choose voice assistant:"
echo "1) ✨ General AI Assistant (clean conversation)"
echo "2) 🏢 NPCL Customer Care (power issue support)"
echo ""
read -p "Enter choice (1 or 2): " choice

case $choice in
    1)
        echo "🎙️ Starting General AI Voice Assistant..."
        echo "✨ Clean conversation mode - speak naturally!"
        source venv/bin/activate && python3 voice_chatbot.py
        ;;
    2)
        echo "🏢 Starting NPCL Customer Care Assistant..."
        echo "📞 Power issue support simulation"
        source venv/bin/activate && python3 npcl_voice_assistant.py
        ;;
    *)
        echo "🎙️ Starting General AI Voice Assistant (default)..."
        echo "✨ Clean conversation mode - speak naturally!"
        source venv/bin/activate && python3 voice_chatbot.py
        ;;
esac