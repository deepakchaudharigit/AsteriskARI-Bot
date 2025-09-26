#!/bin/bash

# Start ARI Bot Properly with Virtual Environment
# This script ensures the ARI bot runs in the correct environment

echo "🚀 Starting NPCL ARI Bot with Virtual Environment"
echo "================================================="

# Activate virtual environment
echo "📦 Activating virtual environment..."
source .venv/bin/activate

# Check if activation worked
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment activated: $VIRTUAL_ENV"
else
    echo "❌ Failed to activate virtual environment"
    exit 1
fi

# Check if required packages are available
echo "🔍 Checking dependencies..."
python3 -c "import dotenv; print('✅ python-dotenv available')" 2>/dev/null || {
    echo "❌ python-dotenv not found, installing..."
    pip install python-dotenv
}

python3 -c "import openai; print('✅ openai available')" 2>/dev/null || {
    echo "❌ openai not found, installing..."
    pip install openai
}

# Stop any existing ARI bot processes
echo "🛑 Stopping any existing ARI bot processes..."
pkill -f "ari_bot.py" 2>/dev/null || true
pkill -f "start_voice_assistant.py" 2>/dev/null || true

# Wait for processes to stop
sleep 2

# Start the ARI bot
echo "🚀 Starting ARI bot..."
echo "📋 Logs will be written to: logs/ari_bot_final.log"
echo "📋 Monitor with: tail -f logs/ari_bot_final.log"
echo ""

# Start in background with proper environment
nohup python3 ari_bot.py > logs/ari_bot_final.log 2>&1 &
ARI_PID=$!

echo "✅ ARI bot started with PID: $ARI_PID"
echo "⏳ Waiting 5 seconds for startup..."
sleep 5

# Check if process is still running
if kill -0 $ARI_PID 2>/dev/null; then
    echo "✅ ARI bot is running successfully"
    
    # Show first few lines of log
    echo ""
    echo "📋 Initial log output:"
    echo "====================="
    head -20 logs/ari_bot_final.log
    echo "====================="
    echo ""
    
    echo "🎯 Next Steps:"
    echo "1. Monitor logs: tail -f logs/ari_bot_final.log"
    echo "2. Test with Zoiper:"
    echo "   - Call 1010 first (simple test)"
    echo "   - Call 1000 second (voice assistant)"
    echo "3. Check Stasis registration: sudo asterisk -rx 'stasis show apps'"
    echo ""
    echo "✅ ARI bot is ready for testing!"
    
else
    echo "❌ ARI bot failed to start or crashed"
    echo "📋 Check logs: cat logs/ari_bot_final.log"
    exit 1
fi