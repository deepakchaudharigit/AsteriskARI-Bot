#!/bin/bash
# Start voice assistant server with proper environment variables

echo "🚀 Starting NPCL Voice Assistant Server"
echo "=================================================="

# Set environment variables
export STASIS_APP=openai-voice-assistant
export EXTERNAL_MEDIA_HOST=localhost
export OPENAI_API_KEY=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

echo "✅ Environment variables set:"
echo "   STASIS_APP: $STASIS_APP"
echo "   EXTERNAL_MEDIA_HOST: $EXTERNAL_MEDIA_HOST"
echo "   OPENAI_API_KEY: ${OPENAI_API_KEY:0:20}..."

echo ""
echo "🎯 Starting voice assistant server..."
echo "📞 Server will be ready for calls on extension 1000"
echo ""

# Activate virtual environment and start server
source .venv/bin/activate
python src/run_realtime_server.py