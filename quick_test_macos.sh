#!/bin/bash

echo "🚀 Quick OpenAI Test (macOS)"
echo "============================"

# Test OpenAI
if python3 -c "import openai; print('✅ OpenAI available')" 2>/dev/null; then
    echo "✅ OpenAI package: OK"
else
    echo "❌ OpenAI package: MISSING"
fi

# Test Gemini removal
if python3 -c "import google.generativeai" 2>/dev/null; then
    echo "⚠️  Gemini: Still installed"
else
    echo "✅ Gemini: Properly removed"
fi

# Test API key
if [ -n "$OPENAI_API_KEY" ] && [[ $OPENAI_API_KEY == sk-* ]]; then
    echo "✅ API Key: Valid format"
else
    echo "❌ API Key: Invalid or missing"
fi

# Test configuration
if grep -q "openai_api_key" config/settings.py 2>/dev/null; then
    echo "✅ Configuration: OK"
else
    echo "❌ Configuration: Missing"
fi

echo "============================"
echo "Run full test: ./migration_test_macos.sh"
