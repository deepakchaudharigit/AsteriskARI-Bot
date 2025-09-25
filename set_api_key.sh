#!/bin/bash

# =============================================================================
# Set OpenAI API Key
# =============================================================================

# Set the API key
export OPENAI_API_KEY="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"

echo "✅ OpenAI API Key set successfully!"
echo "Key: ${OPENAI_API_KEY:0:20}..."

# Add to shell profile for persistence
if [ -f ~/.bashrc ]; then
    if ! grep -q "OPENAI_API_KEY" ~/.bashrc; then
        echo "export OPENAI_API_KEY=\"$OPENAI_API_KEY\"" >> ~/.bashrc
        echo "✅ Added to ~/.bashrc"
    fi
fi

if [ -f ~/.zshrc ]; then
    if ! grep -q "OPENAI_API_KEY" ~/.zshrc; then
        echo "export OPENAI_API_KEY=\"$OPENAI_API_KEY\"" >> ~/.zshrc
        echo "✅ Added to ~/.zshrc"
    fi
fi

echo "🚀 Ready to test! Run: python test_api_connection.py"