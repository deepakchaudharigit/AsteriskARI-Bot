#!/bin/bash

# =============================================================================
# NPCL Voice Assistant - OpenAI API Key Setup Script
# =============================================================================
# This script sets up the OpenAI API key for the voice assistant
# =============================================================================

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔑 Setting up OpenAI API Key for NPCL Voice Assistant${NC}"
echo "================================================================"

# The OpenAI API key
OPENAI_API_KEY="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"

echo -e "\n${YELLOW}1. Setting environment variable...${NC}"
export OPENAI_API_KEY="$OPENAI_API_KEY"
echo -e "${GREEN}✅ OPENAI_API_KEY environment variable set${NC}"

echo -e "\n${YELLOW}2. Adding to shell profile...${NC}"
# Add to bash profile
if [ -f ~/.bashrc ]; then
    if ! grep -q "OPENAI_API_KEY" ~/.bashrc; then
        echo "export OPENAI_API_KEY=\"$OPENAI_API_KEY\"" >> ~/.bashrc
        echo -e "${GREEN}✅ Added to ~/.bashrc${NC}"
    else
        echo -e "${YELLOW}⚠️  Already exists in ~/.bashrc${NC}"
    fi
fi

# Add to zsh profile (if using zsh)
if [ -f ~/.zshrc ]; then
    if ! grep -q "OPENAI_API_KEY" ~/.zshrc; then
        echo "export OPENAI_API_KEY=\"$OPENAI_API_KEY\"" >> ~/.zshrc
        echo -e "${GREEN}✅ Added to ~/.zshrc${NC}"
    else
        echo -e "${YELLOW}⚠️  Already exists in ~/.zshrc${NC}"
    fi
fi

echo -e "\n${YELLOW}3. Verifying .env file...${NC}"
if [ -f ".env" ]; then
    echo -e "${GREEN}✅ .env file already exists and configured${NC}"
else
    echo -e "${RED}❌ .env file not found${NC}"
    exit 1
fi

echo -e "\n${YELLOW}4. Testing API key...${NC}"
if command -v python3 &> /dev/null; then
    python3 -c "
import os
import sys
try:
    import openai
    client = openai.OpenAI(api_key='$OPENAI_API_KEY')
    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=[{'role': 'user', 'content': 'Say: API key working'}],
        max_tokens=10
    )
    print('✅ API key is valid and working!')
    print(f'Response: {response.choices[0].message.content}')
except ImportError:
    print('⚠️  OpenAI package not installed. Run: pip install openai')
    sys.exit(1)
except Exception as e:
    print(f'❌ API key test failed: {e}')
    sys.exit(1)
"
else
    echo -e "${YELLOW}⚠️  Python3 not found, skipping API test${NC}"
fi

echo -e "\n${BLUE}================================================================${NC}"
echo -e "${GREEN}🎉 OpenAI API Key Setup Complete!${NC}"
echo -e "\n${YELLOW}Next steps:${NC}"
echo "1. Restart your terminal or run: source ~/.bashrc"
echo "2. Test the migration: ./quick_migration_test.sh"
echo "3. Run full validation: ./migration_test.sh"
echo "4. Start the voice assistant: python src/main.py"
echo -e "\n${BLUE}Your OpenAI API key is now configured and ready to use!${NC}"