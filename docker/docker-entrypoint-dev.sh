#!/bin/bash
# Development entrypoint with hot reload

set -e

echo "🔧 Starting NPCL Voice Assistant - Development Mode"
echo "=================================================="

# Install development dependencies
pip install watchdog

# Set development environment variables
export PYTHONPATH="/app/src"
export LOG_LEVEL="DEBUG"
export ENABLE_PERFORMANCE_LOGGING="true"

# Run with auto-reload
exec python -m watchdog.watchmedo auto-restart \
    --directory=/app/src \
    --pattern="*.py" \
    --recursive \
    -- python src/main.py --ari-bot