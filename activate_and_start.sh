#!/bin/bash

# NPCL Voice Assistant - Activation and Start Script
# Activates virtual environment and starts the assistant

echo "🚀 NPCL Voice Assistant - Quick Start"
echo "====================================="

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "🔧 Please run setup first:"
    echo "   ./setup_environment.sh"
    exit 1
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source .venv/bin/activate

# Check if activation was successful
if [ "$VIRTUAL_ENV" != "" ]; then
    echo "✅ Virtual environment activated: $VIRTUAL_ENV"
else
    echo "❌ Failed to activate virtual environment"
    exit 1
fi

# Start the assistant
echo "🚀 Starting NPCL Voice Assistant..."
python3 start_openai_assistant.py