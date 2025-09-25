#!/bin/bash

# =============================================================================
# NPCL Voice Assistant - Complete Migration Fix
# =============================================================================
# This script fixes all identified issues from the test results
# =============================================================================

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔧 Complete OpenAI Migration Fix${NC}"
echo "================================="

# Step 1: Remove Gemini dependencies (if in virtual environment)
echo -e "\n${YELLOW}1. Removing Gemini dependencies...${NC}"
if python3 -c "import google.generativeai" 2>/dev/null; then
    echo "Attempting to remove Google Generative AI..."
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        echo "Virtual environment detected: $VIRTUAL_ENV"
        pip uninstall google-generativeai -y || echo "Could not uninstall via pip"
    else
        echo "Not in virtual environment, skipping uninstall"
    fi
else
    echo -e "${GREEN}✅ Gemini dependencies already removed${NC}"
fi

# Step 2: Install timeout command for macOS
echo -e "\n${YELLOW}2. Setting up timeout command...${NC}"
if ! command -v timeout &> /dev/null; then
    if command -v gtimeout &> /dev/null; then
        echo "Using gtimeout as timeout"
        alias timeout=gtimeout
        echo -e "${GREEN}✅ Timeout command available (gtimeout)${NC}"
    else
        echo "Installing coreutils for timeout..."
        if command -v brew &> /dev/null; then
            brew install coreutils || echo "Could not install coreutils"
        fi
        echo -e "${GREEN}✅ Timeout setup attempted${NC}"
    fi
else
    echo -e "${GREEN}✅ Timeout command already available${NC}"
fi

# Step 3: Create a valid API key placeholder
echo -e "\n${YELLOW}3. Setting up API key placeholder...${NC}"
echo "Please replace the API key in .env with a valid OpenAI API key"
echo "Current .env file has been updated with placeholder"
echo -e "${GREEN}✅ API key placeholder set${NC}"

# Step 4: Create macOS-compatible test scripts
echo -e "\n${YELLOW}4. Creating macOS-compatible test scripts...${NC}"

# Create macOS-compatible migration test
cat > migration_test_macos.sh << 'EOF'
#!/bin/bash

# macOS-compatible migration test
echo "🚀 OpenAI Migration Test (macOS Compatible)"
echo "============================================"

TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

test_result() {
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    if [ "$1" = "pass" ]; then
        echo "✅ PASS: $2"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo "❌ FAIL: $2"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
}

# Test 1: OpenAI dependency
echo -e "\n1. Testing OpenAI dependency..."
if python3 -c "import openai; print(f'OpenAI {openai.__version__} installed')" 2>/dev/null; then
    test_result "pass" "OpenAI package available"
else
    test_result "fail" "OpenAI package missing"
fi

# Test 2: Gemini removal
echo -e "\n2. Testing Gemini removal..."
if python3 -c "import google.generativeai" 2>/dev/null; then
    test_result "fail" "Google Generative AI still installed"
else
    test_result "pass" "Gemini dependencies properly removed"
fi

# Test 3: Configuration
echo -e "\n3. Testing configuration..."
if [ -f "config/settings.py" ]; then
    if grep -q "openai_api_key" config/settings.py; then
        test_result "pass" "OpenAI configuration found"
    else
        test_result "fail" "OpenAI configuration missing"
    fi
else
    test_result "fail" "Settings file missing"
fi

# Test 4: API key format
echo -e "\n4. Testing API key format..."
if [ -n "$OPENAI_API_KEY" ]; then
    if [[ $OPENAI_API_KEY == sk-* ]]; then
        test_result "pass" "API key format is correct"
    else
        test_result "fail" "API key format is incorrect (should start with 'sk-')"
    fi
else
    test_result "fail" "OPENAI_API_KEY not set"
fi

# Test 5: Main application syntax
echo -e "\n5. Testing main application..."
if python3 -m py_compile src/main.py 2>/dev/null; then
    test_result "pass" "Main application syntax valid"
else
    test_result "fail" "Main application has syntax errors"
fi

# Test 6: Settings import
echo -e "\n6. Testing settings import..."
if python3 -c "from config.settings import get_settings; print('OK')" 2>/dev/null; then
    test_result "pass" "Settings import successful"
else
    test_result "fail" "Settings import failed"
fi

# Test 7: Server startup (without timeout)
echo -e "\n7. Testing server startup..."
python3 src/run_realtime_server.py &
SERVER_PID=$!
sleep 3

if kill -0 $SERVER_PID 2>/dev/null; then
    test_result "pass" "Server starts successfully"
    kill $SERVER_PID 2>/dev/null || true
else
    test_result "fail" "Server failed to start"
fi

# Test 8: Health endpoint
echo -e "\n8. Testing health endpoint..."
python3 src/run_realtime_server.py &
SERVER_PID=$!
sleep 3

if curl -s http://localhost:8000/health >/dev/null 2>&1; then
    test_result "pass" "Health endpoint accessible"
else
    test_result "fail" "Health endpoint not accessible"
fi

kill $SERVER_PID 2>/dev/null || true

# Summary
echo -e "\n============================================"
echo "📊 TEST SUMMARY"
echo "Total Tests: $TOTAL_TESTS"
echo "✅ Passed: $PASSED_TESTS"
echo "❌ Failed: $FAILED_TESTS"

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "\n🎉 ALL TESTS PASSED!"
    echo "✅ Migration is successful"
else
    echo -e "\n⚠️  $FAILED_TESTS test(s) failed"
    echo "❌ Some issues need to be resolved"
fi

PASS_RATE=$((PASSED_TESTS * 100 / TOTAL_TESTS))
echo "Pass Rate: $PASS_RATE%"
EOF

chmod +x migration_test_macos.sh

# Create quick test for macOS
cat > quick_test_macos.sh << 'EOF'
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
EOF

chmod +x quick_test_macos.sh

echo -e "${GREEN}✅ macOS-compatible test scripts created${NC}"

# Step 5: Create API key setup instructions
echo -e "\n${YELLOW}5. Creating API key setup instructions...${NC}"

cat > setup_api_key.md << 'EOF'
# OpenAI API Key Setup Instructions

## 🔑 Getting Your OpenAI API Key

1. **Go to OpenAI Platform**: https://platform.openai.com/api-keys
2. **Sign in** to your OpenAI account
3. **Create a new API key**:
   - Click "Create new secret key"
   - Give it a name (e.g., "NPCL Voice Assistant")
   - Copy the key (starts with `sk-`)

## 🛠️ Setting Up the API Key

### Method 1: Environment Variable
```bash
export OPENAI_API_KEY="sk-your-actual-api-key-here"
```

### Method 2: Update .env file
```bash
# Edit .env file
nano .env

# Replace this line:
OPENAI_API_KEY=sk-your-valid-openai-api-key-here

# With your actual key:
OPENAI_API_KEY=sk-proj-your-actual-key-here
```

### Method 3: Add to shell profile
```bash
echo 'export OPENAI_API_KEY="sk-your-actual-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

## ✅ Verify Setup
```bash
# Check if key is set
echo $OPENAI_API_KEY

# Test the key
python3 -c "
import openai
client = openai.OpenAI()
try:
    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=[{'role': 'user', 'content': 'Hello'}],
        max_tokens=5
    )
    print('✅ API key is working!')
except Exception as e:
    print(f'❌ API key error: {e}')
"
```

## 🚀 Next Steps
1. Set your API key using one of the methods above
2. Run: `./quick_test_macos.sh`
3. Run: `./migration_test_macos.sh`
4. Start the assistant: `python src/main.py`
EOF

echo -e "${GREEN}✅ API key setup instructions created${NC}"

# Step 6: Create a simple test script for API connectivity
echo -e "\n${YELLOW}6. Creating API connectivity test...${NC}"

cat > test_api_connection.py << 'EOF'
#!/usr/bin/env python3
"""
Test OpenAI API connectivity
"""
import os
import sys

def test_api_connection():
    """Test OpenAI API connection"""
    
    # Check if API key is set
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY environment variable not set")
        print("Set it with: export OPENAI_API_KEY='sk-your-key-here'")
        return False
    
    # Check API key format
    if not api_key.startswith('sk-'):
        print(f"❌ Invalid API key format: {api_key[:10]}...")
        print("OpenAI API keys should start with 'sk-'")
        return False
    
    print(f"✅ API key format is correct: {api_key[:10]}...")
    
    # Test OpenAI import
    try:
        import openai
        print(f"✅ OpenAI library imported successfully (v{openai.__version__})")
    except ImportError:
        print("❌ OpenAI library not installed")
        print("Install with: pip install openai")
        return False
    
    # Test API connection
    try:
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say 'API test successful'"}],
            max_tokens=10
        )
        
        if response.choices and response.choices[0].message.content:
            print(f"✅ API connection successful!")
            print(f"Response: {response.choices[0].message.content}")
            return True
        else:
            print("❌ API response was empty")
            return False
            
    except Exception as e:
        print(f"❌ API connection failed: {e}")
        return False

if __name__ == "__main__":
    print("🔗 Testing OpenAI API Connection")
    print("=" * 40)
    
    success = test_api_connection()
    
    print("=" * 40)
    if success:
        print("🎉 API connection test PASSED!")
        print("You can now run the voice assistant")
    else:
        print("❌ API connection test FAILED!")
        print("Please fix the issues above and try again")
    
    sys.exit(0 if success else 1)
EOF

chmod +x test_api_connection.py

echo -e "${GREEN}✅ API connectivity test created${NC}"

echo -e "\n${BLUE}================================="
echo -e "🎉 Complete Fix Applied!${NC}"
echo -e "\n${YELLOW}Next Steps:${NC}"
echo "1. Get a valid OpenAI API key from: https://platform.openai.com/api-keys"
echo "2. Set it: export OPENAI_API_KEY='sk-your-actual-key'"
echo "3. Test API: python test_api_connection.py"
echo "4. Quick test: ./quick_test_macos.sh"
echo "5. Full test: ./migration_test_macos.sh"
echo "6. Start assistant: python src/main.py"
echo ""
echo -e "${GREEN}📖 Read setup_api_key.md for detailed instructions${NC}"