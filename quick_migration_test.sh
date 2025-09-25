#!/bin/bash

# =============================================================================
# NPCL Voice Assistant - Quick OpenAI Migration Test
# =============================================================================
# Quick validation script to test the most critical migration components
# =============================================================================

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Quick OpenAI Migration Test${NC}"
echo "=================================="

# Test 1: Check OpenAI dependency
echo -e "\n${YELLOW}1. Testing OpenAI dependency...${NC}"
if python3 -c "import openai; print(f'✅ OpenAI {openai.__version__} installed')" 2>/dev/null; then
    echo -e "${GREEN}✅ OpenAI package available${NC}"
else
    echo -e "${RED}❌ OpenAI package missing${NC}"
    echo "Run: pip install openai"
    exit 1
fi

# Test 2: Check Gemini removal
echo -e "\n${YELLOW}2. Testing Gemini removal...${NC}"
if python3 -c "import google.generativeai" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Google Generative AI still installed${NC}"
    echo "Consider removing: pip uninstall google-generativeai"
else
    echo -e "${GREEN}✅ Gemini dependencies properly removed${NC}"
fi

# Test 3: Check configuration
echo -e "\n${YELLOW}3. Testing configuration...${NC}"
if [ -f "config/settings.py" ]; then
    if grep -q "openai_api_key" config/settings.py; then
        echo -e "${GREEN}✅ OpenAI configuration found${NC}"
    else
        echo -e "${RED}❌ OpenAI configuration missing${NC}"
    fi
    
    if grep -q "gemini" config/settings.py; then
        echo -e "${YELLOW}⚠️  Gemini references still in settings${NC}"
    else
        echo -e "${GREEN}✅ Gemini references removed from settings${NC}"
    fi
else
    echo -e "${RED}❌ Settings file missing${NC}"
fi

# Test 4: Check main application
echo -e "\n${YELLOW}4. Testing main application...${NC}"
if [ -f "src/main.py" ]; then
    if python3 -m py_compile src/main.py 2>/dev/null; then
        echo -e "${GREEN}✅ Main application syntax valid${NC}"
    else
        echo -e "${RED}❌ Main application has syntax errors${NC}"
    fi
else
    echo -e "${RED}❌ Main application missing${NC}"
fi

# Test 5: Check OpenAI client
echo -e "\n${YELLOW}5. Testing OpenAI client...${NC}"
if [ -f "src/voice_assistant/ai/openai_realtime_client_enhanced.py" ]; then
    echo -e "${GREEN}✅ OpenAI Realtime client found${NC}"
else
    echo -e "${RED}❌ OpenAI Realtime client missing${NC}"
fi

# Test 6: Check imports
echo -e "\n${YELLOW}6. Testing imports...${NC}"
if python3 -c "from config.settings import get_settings; print('Settings import OK')" 2>/dev/null; then
    echo -e "${GREEN}✅ Settings import successful${NC}"
else
    echo -e "${RED}❌ Settings import failed${NC}"
fi

# Test 7: Check server startup (quick test)
echo -e "\n${YELLOW}7. Testing server startup...${NC}"
timeout 5s python3 src/run_realtime_server.py &
SERVER_PID=$!
sleep 2

if kill -0 $SERVER_PID 2>/dev/null; then
    echo -e "${GREEN}✅ Server starts successfully${NC}"
    kill $SERVER_PID 2>/dev/null || true
else
    echo -e "${RED}❌ Server failed to start${NC}"
fi

# Test 8: Check environment variables
echo -e "\n${YELLOW}8. Testing environment variables...${NC}"
if [ -n "$OPENAI_API_KEY" ]; then
    echo -e "${GREEN}✅ OPENAI_API_KEY is set${NC}"
else
    echo -e "${YELLOW}⚠️  OPENAI_API_KEY not set${NC}"
    echo "Set your OpenAI API key: export OPENAI_API_KEY='your-key-here'"
fi

# Test 9: Check Asterisk configuration
echo -e "\n${YELLOW}9. Testing Asterisk configuration...${NC}"
if [ -f "asterisk-config/extensions.conf" ]; then
    if grep -q "openai-voice-assistant" asterisk-config/extensions.conf; then
        echo -e "${GREEN}✅ OpenAI stasis app configured${NC}"
    else
        echo -e "${RED}❌ OpenAI stasis app not configured${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Asterisk config not found${NC}"
fi

# Test 10: Check requirements
echo -e "\n${YELLOW}10. Testing requirements...${NC}"
if [ -f "requirements.txt" ]; then
    if grep -q "openai" requirements.txt; then
        echo -e "${GREEN}✅ OpenAI in requirements.txt${NC}"
    else
        echo -e "${RED}❌ OpenAI missing from requirements.txt${NC}"
    fi
    
    if grep -q "google-generativeai" requirements.txt; then
        echo -e "${YELLOW}⚠️  Gemini still in requirements.txt${NC}"
    else
        echo -e "${GREEN}✅ Gemini removed from requirements.txt${NC}"
    fi
else
    echo -e "${RED}❌ requirements.txt missing${NC}"
fi

echo -e "\n${BLUE}=================================="
echo -e "Quick Migration Test Complete${NC}"
echo -e "${GREEN}✅ Run the full test with: ./migration_test.sh${NC}"