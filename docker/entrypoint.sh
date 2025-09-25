#!/bin/bash
set -e

echo "🚀 Starting NPCL Voice Assistant Docker Container"
echo "=================================================="

# Set default environment variables if not provided
export OPENAI_API_KEY=${OPENAI_API_KEY:-""}
export VOICE_MODEL=${VOICE_MODEL:-"alloy"}
export TTS_MODEL=${TTS_MODEL:-"tts-1-hd"}
export ARI_BASE_URL=${ARI_BASE_URL:-"http://asterisk:8088/ari"}
export ARI_USERNAME=${ARI_USERNAME:-"asterisk"}
export ARI_PASSWORD=${ARI_PASSWORD:-"1234"}
export STASIS_APP=${STASIS_APP:-"openai-voice-assistant"}
export EXTERNAL_MEDIA_HOST=${EXTERNAL_MEDIA_HOST:-"0.0.0.0"}
export EXTERNAL_MEDIA_PORT=${EXTERNAL_MEDIA_PORT:-"8090"}

# Validate required environment variables
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ ERROR: OPENAI_API_KEY environment variable is required"
    echo "💡 Set it with: docker run -e OPENAI_API_KEY=your-key-here ..."
    exit 1
fi

echo "✅ OpenAI API Key: Configured"
echo "🎤 Voice Model: $VOICE_MODEL"
echo "🎛️  TTS Model: $TTS_MODEL"
echo "📞 ARI URL: $ARI_BASE_URL"
echo "🌐 External Media: $EXTERNAL_MEDIA_HOST:$EXTERNAL_MEDIA_PORT"

# Create required directories
mkdir -p /app/sounds/temp /app/recordings /app/logs

# Set permissions
chmod 755 /app/sounds /app/recordings /app/logs

# Initialize audio system (if available)
if command -v pulseaudio >/dev/null 2>&1; then
    echo "🔊 Initializing audio system..."
    pulseaudio --start --exit-idle-time=-1 || true
fi

echo "🎯 Container ready - starting services..."
echo "=================================================="

# Execute the main command
exec "$@"