#!/bin/bash

echo "🔧 Installing websockets in virtual environment"
echo "================================================"

# Activate virtual environment
source .venv/bin/activate

# Check if activation worked
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment activated: $VIRTUAL_ENV"
else
    echo "❌ Failed to activate virtual environment"
    exit 1
fi

# Install websockets
echo "📦 Installing websockets..."
pip install websockets

# Verify installation
echo "🔍 Verifying installation..."
python3 -c "import websockets; print('✅ websockets installed successfully')"

echo "🎯 Ready to test WebSocket connection"