#!/bin/bash

# NPCL Voice Assistant - Environment Setup Script
# Sets up virtual environment and installs dependencies

echo "🚀 NPCL Voice Assistant - Environment Setup"
echo "============================================"

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found. Please run this script from the project root directory."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "🐍 Python version: $PYTHON_VERSION"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Verify key dependencies
echo "🔍 Verifying key dependencies..."
python3 -c "import pydantic_settings; print('✅ pydantic_settings')" 2>/dev/null || echo "❌ pydantic_settings"
python3 -c "import openai; print('✅ openai')" 2>/dev/null || echo "❌ openai"
python3 -c "import websockets; print('✅ websockets')" 2>/dev/null || echo "❌ websockets"
python3 -c "import fastapi; print('✅ fastapi')" 2>/dev/null || echo "❌ fastapi"
python3 -c "import pyaudio; print('✅ pyaudio')" 2>/dev/null || echo "❌ pyaudio (optional for standalone mode)"

echo ""
echo "🎉 Environment setup complete!"
echo ""
echo "To activate the environment in the future, run:"
echo "   source .venv/bin/activate"
echo ""
echo "To start the NPCL Voice Assistant:"
echo "   source .venv/bin/activate"
echo "   python3 src/run_realtime_server.py"
echo ""
echo "To test the OpenAI integration:"
echo "   source .venv/bin/activate"
echo "   python3 test_openai_integration.py"