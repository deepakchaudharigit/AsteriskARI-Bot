#!/bin/bash

# =============================================================================
# NPCL Voice Assistant - Migration Issues Fix Script
# =============================================================================
# This script fixes all identified migration issues
# =============================================================================

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔧 Fixing OpenAI Migration Issues${NC}"
echo "=================================="

# Issue 1: Remove Gemini dependencies
echo -e "\n${YELLOW}1. Removing Gemini dependencies...${NC}"
if python -c "import google.generativeai" 2>/dev/null; then
    echo "Removing Google Generative AI..."
    pip uninstall google-generativeai -y
    echo -e "${GREEN}✅ Gemini dependencies removed${NC}"
else
    echo -e "${GREEN}✅ Gemini dependencies already removed${NC}"
fi

# Issue 2: Install gtimeout for macOS (if needed)
echo -e "\n${YELLOW}2. Installing timeout command for macOS...${NC}"
if ! command -v timeout &> /dev/null; then
    if command -v brew &> /dev/null; then
        echo "Installing coreutils for timeout command..."
        brew install coreutils
        echo -e "${GREEN}✅ Timeout command installed${NC}"
    else
        echo -e "${YELLOW}⚠️  Homebrew not found. Installing timeout alternative...${NC}"
        # Create a simple timeout function
        cat > /usr/local/bin/timeout << 'EOF'
#!/bin/bash
duration=$1
shift
command="$@"

# Run command in background
$command &
pid=$!

# Wait for specified duration
sleep $duration

# Kill the process if still running
if kill -0 $pid 2>/dev/null; then
    kill $pid 2>/dev/null
    exit 124
fi

wait $pid
EOF
        chmod +x /usr/local/bin/timeout 2>/dev/null || echo "Note: Could not install timeout globally"
        echo -e "${GREEN}✅ Timeout alternative created${NC}"
    fi
else
    echo -e "${GREEN}✅ Timeout command already available${NC}"
fi

# Issue 3: Fix API key format
echo -e "\n${YELLOW}3. Checking API key format...${NC}"
if [ -n "$OPENAI_API_KEY" ]; then
    if [[ $OPENAI_API_KEY == sk-* ]]; then
        echo -e "${GREEN}✅ API key format is correct${NC}"
    else
        echo -e "${RED}❌ API key format is incorrect${NC}"
        echo "Please set a valid OpenAI API key that starts with 'sk-'"
        echo "Current key starts with: ${OPENAI_API_KEY:0:10}..."
        echo ""
        echo "To fix this:"
        echo "1. Go to https://platform.openai.com/api-keys"
        echo "2. Create a new API key"
        echo "3. Set it with: export OPENAI_API_KEY='sk-your-new-key'"
    fi
else
    echo -e "${RED}❌ OPENAI_API_KEY not set${NC}"
fi

# Issue 4: Update .env with correct API key format check
echo -e "\n${YELLOW}4. Updating .env file...${NC}"
if [ -f ".env" ]; then
    # Comment out the invalid key and add placeholder
    sed -i.bak 's/^OPENAI_API_KEY=sk-proj.*/# OPENAI_API_KEY=sk-proj... (INVALID - Please replace with valid key)/' .env
    echo "OPENAI_API_KEY=sk-your-valid-openai-api-key-here" >> .env
    echo -e "${GREEN}✅ .env file updated with placeholder${NC}"
else
    echo -e "${RED}❌ .env file not found${NC}"
fi

# Issue 5: Fix model configuration in settings
echo -e "\n${YELLOW}5. Fixing model configuration...${NC}"
if [ -f "config/settings.py" ]; then
    # Update to use a compatible model for chat completions
    sed -i.bak 's/gpt-4o-realtime-preview-2024-10-01/gpt-4o-mini/g' config/settings.py
    echo -e "${GREEN}✅ Model configuration updated to gpt-4o-mini${NC}"
else
    echo -e "${RED}❌ Settings file not found${NC}"
fi

# Issue 6: Create macOS-compatible test scripts
echo -e "\n${YELLOW}6. Creating macOS-compatible test scripts...${NC}"

# Create macOS-compatible quick test
cat > quick_migration_test_macos.sh << 'EOF'
#!/bin/bash

# macOS-compatible quick migration test
echo "🚀 Quick OpenAI Migration Test (macOS)"
echo "=================================="

# Test 1: OpenAI dependency
echo -e "\n1. Testing OpenAI dependency..."
if python3 -c "import openai; print(f'✅ OpenAI {openai.__version__} installed')" 2>/dev/null; then
    echo "✅ OpenAI package available"
else
    echo "❌ OpenAI package missing"
    exit 1
fi

# Test 2: Gemini removal
echo -e "\n2. Testing Gemini removal..."
if python3 -c "import google.generativeai" 2>/dev/null; then
    echo "⚠️  Google Generative AI still installed"
else
    echo "✅ Gemini dependencies properly removed"
fi

# Test 3: Configuration
echo -e "\n3. Testing configuration..."
if [ -f "config/settings.py" ]; then
    if grep -q "openai_api_key" config/settings.py; then
        echo "✅ OpenAI configuration found"
    else
        echo "❌ OpenAI configuration missing"
    fi
else
    echo "❌ Settings file missing"
fi

# Test 4: API key format
echo -e "\n4. Testing API key format..."
if [ -n "$OPENAI_API_KEY" ]; then
    if [[ $OPENAI_API_KEY == sk-* ]]; then
        echo "✅ API key format is correct"
    else
        echo "❌ API key format is incorrect (should start with 'sk-')"
    fi
else
    echo "⚠️  OPENAI_API_KEY not set"
fi

# Test 5: Server startup (without timeout)
echo -e "\n5. Testing server startup..."
python3 src/run_realtime_server.py &
SERVER_PID=$!
sleep 3

if kill -0 $SERVER_PID 2>/dev/null; then
    echo "✅ Server starts successfully"
    kill $SERVER_PID 2>/dev/null || true
else
    echo "❌ Server failed to start"
fi

echo -e "\n=================================="
echo "Quick Migration Test Complete (macOS)"
EOF

chmod +x quick_migration_test_macos.sh
echo -e "${GREEN}✅ macOS-compatible test script created${NC}"

echo -e "\n${BLUE}=================================="
echo -e "🎉 Migration Issues Fix Complete!${NC}"
echo -e "\n${YELLOW}Next steps:${NC}"
echo "1. Get a valid OpenAI API key from: https://platform.openai.com/api-keys"
echo "2. Set it: export OPENAI_API_KEY='sk-your-valid-key'"
echo "3. Update .env file with the valid key"
echo "4. Run: ./quick_migration_test_macos.sh"
echo "5. Test the system: python src/main.py"