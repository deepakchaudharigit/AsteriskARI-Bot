#!/bin/bash

# NPCL ARI Server Startup Script
echo "🚀 Starting NPCL Asterisk ARI Voice Assistant Bot"
echo "=================================================="

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment: $VIRTUAL_ENV"
    PYTHON_CMD="python"
else
    echo "⚠️  Virtual environment not detected, using .venv/bin/python"
    PYTHON_CMD=".venv/bin/python"
fi

# Start the ARI bot
echo "🎤 Starting ARI bot with enhanced voice..."
echo "📞 Server will be available at: http://localhost:8000"
echo "🌡️ Health check: http://localhost:8000/ari/health"
echo "📋 API docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=================================================="

# Run the ARI bot
$PYTHON_CMD src/main.py --ari-bot