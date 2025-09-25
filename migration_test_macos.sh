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
