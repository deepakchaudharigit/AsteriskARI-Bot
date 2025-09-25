#!/bin/bash

# =============================================================================
# NPCL Voice Assistant - OpenAI Migration Test Script
# =============================================================================
# This script validates the complete migration from Gemini to OpenAI
# Tests all components, configurations, and functionality
# =============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Logging
LOG_FILE="migration_test_$(date +%Y%m%d_%H%M%S).log"

# Helper functions
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_test() {
    echo -e "${YELLOW}🧪 Testing: $1${NC}"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
}

print_success() {
    echo -e "${GREEN}✅ PASS: $1${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
    log "PASS: $1"
}

print_failure() {
    echo -e "${RED}❌ FAIL: $1${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
    log "FAIL: $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️  WARNING: $1${NC}"
    log "WARNING: $1"
}

# Test functions
test_environment() {
    print_header "ENVIRONMENT VALIDATION"
    
    print_test "Python version"
    if python3 --version >/dev/null 2>&1; then
        PYTHON_VERSION=$(python3 --version)
        print_success "Python available: $PYTHON_VERSION"
    else
        print_failure "Python 3 not found"
        return 1
    fi
    
    print_test "Virtual environment"
    if [ -d ".venv" ] || [ -n "$VIRTUAL_ENV" ]; then
        print_success "Virtual environment detected"
    else
        print_warning "No virtual environment detected"
    fi
    
    print_test "Required directories"
    for dir in "src" "config" "tests" "docs"; do
        if [ -d "$dir" ]; then
            print_success "Directory exists: $dir"
        else
            print_failure "Missing directory: $dir"
        fi
    done
}

test_dependencies() {
    print_header "DEPENDENCY VALIDATION"
    
    print_test "OpenAI package"
    if python3 -c "import openai; print(f'OpenAI version: {openai.__version__}')" 2>/dev/null; then
        print_success "OpenAI package installed"
    else
        print_failure "OpenAI package not found"
    fi
    
    print_test "FastAPI package"
    if python3 -c "import fastapi; print(f'FastAPI version: {fastapi.__version__}')" 2>/dev/null; then
        print_success "FastAPI package installed"
    else
        print_failure "FastAPI package not found"
    fi
    
    print_test "WebSockets package"
    if python3 -c "import websockets; print(f'WebSockets version: {websockets.__version__}')" 2>/dev/null; then
        print_success "WebSockets package installed"
    else
        print_failure "WebSockets package not found"
    fi
    
    print_test "Pydantic package"
    if python3 -c "import pydantic; print(f'Pydantic version: {pydantic.__version__}')" 2>/dev/null; then
        print_success "Pydantic package installed"
    else
        print_failure "Pydantic package not found"
    fi
    
    print_test "Removed Gemini dependencies"
    if python3 -c "import google.generativeai" 2>/dev/null; then
        print_warning "Google Generative AI still installed (should be removed)"
    else
        print_success "Google Generative AI properly removed"
    fi
}

test_configuration() {
    print_header "CONFIGURATION VALIDATION"
    
    print_test "Settings file exists"
    if [ -f "config/settings.py" ]; then
        print_success "Settings file found"
    else
        print_failure "Settings file missing"
        return 1
    fi
    
    print_test "OpenAI configuration in settings"
    if grep -q "openai_api_key" config/settings.py; then
        print_success "OpenAI API key configuration found"
    else
        print_failure "OpenAI API key configuration missing"
    fi
    
    if grep -q "openai_model" config/settings.py; then
        print_success "OpenAI model configuration found"
    else
        print_failure "OpenAI model configuration missing"
    fi
    
    print_test "Removed Gemini configurations"
    if grep -q "gemini" config/settings.py; then
        print_warning "Gemini references still found in settings"
    else
        print_success "Gemini references properly removed from settings"
    fi
    
    print_test "Environment file template"
    if [ -f ".env.example" ]; then
        if grep -q "OPENAI_API_KEY" .env.example; then
            print_success "OpenAI API key in .env.example"
        else
            print_failure "OpenAI API key missing from .env.example"
        fi
        
        if grep -q "OPENAI_API_KEY\|GEMINI" .env.example; then
            print_warning "Gemini/Google references still in .env.example"
        else
            print_success "Gemini references properly removed from .env.example"
        fi
    else
        print_warning ".env.example file not found"
    fi
}

test_source_code() {
    print_header "SOURCE CODE VALIDATION"
    
    print_test "Main application file"
    if [ -f "src/main.py" ]; then
        print_success "Main application file found"
        
        if grep -q "openai" src/main.py; then
            print_success "OpenAI imports found in main.py"
        else
            print_failure "OpenAI imports missing from main.py"
        fi
        
        if grep -q "gemini\|google\.generativeai" src/main.py; then
            print_warning "Gemini references still in main.py"
        else
            print_success "Gemini references properly removed from main.py"
        fi
    else
        print_failure "Main application file missing"
    fi
    
    print_test "OpenAI client implementation"
    if [ -f "src/voice_assistant/ai/openai_realtime_client_enhanced.py" ]; then
        print_success "OpenAI Realtime client found"
    else
        print_failure "OpenAI Realtime client missing"
    fi
    
    print_test "AI client factory"
    if [ -f "src/voice_assistant/ai/ai_client_factory.py" ]; then
        if grep -q "openai" src/voice_assistant/ai/ai_client_factory.py; then
            print_success "OpenAI support in AI client factory"
        else
            print_failure "OpenAI support missing from AI client factory"
        fi
    else
        print_failure "AI client factory missing"
    fi
    
    print_test "Removed Gemini client files"
    if [ -f "src/voice_assistant/ai/openai_client.py" ] || [ -f "src/voice_assistant/ai/gemini_live_client.py" ]; then
        print_warning "Gemini client files still present"
    else
        print_success "Gemini client files properly removed"
    fi
}

test_asterisk_configuration() {
    print_header "ASTERISK CONFIGURATION VALIDATION"
    
    print_test "Asterisk extensions configuration"
    if [ -f "asterisk-config/extensions.conf" ]; then
        print_success "Asterisk extensions.conf found"
        
        if grep -q "openai-voice-assistant" asterisk-config/extensions.conf; then
            print_success "OpenAI voice assistant stasis app configured"
        else
            print_failure "OpenAI voice assistant stasis app not configured"
        fi
        
        if grep -q "openai-voice-assistant" asterisk-config/extensions.conf; then
            print_warning "Gemini voice assistant references still in extensions.conf"
        else
            print_success "Gemini references properly removed from extensions.conf"
        fi
    else
        print_failure "Asterisk extensions.conf missing"
    fi
    
    print_test "Docker compose configuration"
    if [ -f "docker-compose.yml" ]; then
        print_success "Docker compose file found"
    else
        print_warning "Docker compose file not found"
    fi
}

test_kubernetes_deployment() {
    print_header "KUBERNETES DEPLOYMENT VALIDATION"
    
    print_test "Kubernetes namespace configuration"
    if [ -f "kubernetes/namespace.yaml" ]; then
        print_success "Kubernetes namespace file found"
        
        if grep -q "OPENAI_MODEL\|OPENAI_VOICE" kubernetes/namespace.yaml; then
            print_success "OpenAI configuration in Kubernetes"
        else
            print_failure "OpenAI configuration missing from Kubernetes"
        fi
        
        if grep -q "GEMINI" kubernetes/namespace.yaml; then
            print_warning "Gemini references still in Kubernetes config"
        else
            print_success "Gemini references properly removed from Kubernetes"
        fi
    else
        print_warning "Kubernetes namespace file not found"
    fi
}

test_documentation() {
    print_header "DOCUMENTATION VALIDATION"
    
    print_test "Main README file"
    if [ -f "README.md" ]; then
        print_success "README.md found"
        
        if grep -q -i "openai\|gpt-4" README.md; then
            print_success "OpenAI references in README"
        else
            print_failure "OpenAI references missing from README"
        fi
    else
        print_failure "README.md missing"
    fi
    
    print_test "API documentation"
    if [ -f "docs/API_DOCUMENTATION.md" ]; then
        print_success "API documentation found"
        
        if grep -q "OPENAI_API_KEY" docs/API_DOCUMENTATION.md; then
            print_success "OpenAI API key documented"
        else
            print_failure "OpenAI API key not documented"
        fi
    else
        print_warning "API documentation not found"
    fi
    
    print_test "Architecture documentation"
    if [ -f "docs/ARCHITECTURE.md" ]; then
        if grep -q -i "openai" docs/ARCHITECTURE.md; then
            print_success "OpenAI references in architecture docs"
        else
            print_failure "OpenAI references missing from architecture docs"
        fi
    else
        print_warning "Architecture documentation not found"
    fi
}

test_import_syntax() {
    print_header "IMPORT SYNTAX VALIDATION"
    
    print_test "Python syntax validation"
    if python3 -m py_compile src/main.py 2>/dev/null; then
        print_success "Main application syntax valid"
    else
        print_failure "Main application syntax errors"
    fi
    
    print_test "Settings import validation"
    if python3 -c "from config.settings import get_settings; settings = get_settings(); print('Settings loaded successfully')" 2>/dev/null; then
        print_success "Settings import successful"
    else
        print_failure "Settings import failed"
    fi
    
    print_test "AI client factory import"
    if python3 -c "from src.voice_assistant.ai.ai_client_factory import AIClientFactory; print('AI client factory imported')" 2>/dev/null; then
        print_success "AI client factory import successful"
    else
        print_failure "AI client factory import failed"
    fi
}

test_server_startup() {
    print_header "SERVER STARTUP VALIDATION"
    
    print_test "FastAPI server startup test"
    
    # Start server in background
    timeout 10s python3 src/run_realtime_server.py &
    SERVER_PID=$!
    
    # Wait for server to start
    sleep 5
    
    # Test if server is responding
    if curl -s http://localhost:8000/health >/dev/null 2>&1; then
        print_success "FastAPI server started and responding"
        kill $SERVER_PID 2>/dev/null || true
    else
        print_failure "FastAPI server failed to start or not responding"
        kill $SERVER_PID 2>/dev/null || true
    fi
}

test_api_endpoints() {
    print_header "API ENDPOINTS VALIDATION"
    
    # Start server for testing
    python3 src/run_realtime_server.py &
    SERVER_PID=$!
    sleep 5
    
    print_test "Health endpoint"
    if curl -s http://localhost:8000/health | grep -q "healthy"; then
        print_success "Health endpoint working"
    else
        print_failure "Health endpoint not working"
    fi
    
    print_test "Status endpoint"
    if curl -s http://localhost:8000/ari/status >/dev/null 2>&1; then
        print_success "Status endpoint accessible"
    else
        print_failure "Status endpoint not accessible"
    fi
    
    print_test "OpenAPI documentation"
    if curl -s http://localhost:8000/docs >/dev/null 2>&1; then
        print_success "OpenAPI docs accessible"
    else
        print_failure "OpenAPI docs not accessible"
    fi
    
    # Cleanup
    kill $SERVER_PID 2>/dev/null || true
}

test_environment_variables() {
    print_header "ENVIRONMENT VARIABLES VALIDATION"
    
    print_test "OpenAI API key environment"
    if [ -n "$OPENAI_API_KEY" ]; then
        print_success "OPENAI_API_KEY environment variable set"
    else
        print_warning "OPENAI_API_KEY environment variable not set"
    fi
    
    print_test "Removed Google API key"
    if [ -n "$OPENAI_API_KEY" ]; then
        print_warning "OPENAI_API_KEY still set (should be removed)"
    else
        print_success "OPENAI_API_KEY properly removed"
    fi
    
    print_test ".env file"
    if [ -f ".env" ]; then
        if grep -q "OPENAI_API_KEY" .env; then
            print_success "OPENAI_API_KEY in .env file"
        else
            print_warning "OPENAI_API_KEY not in .env file"
        fi
        
        if grep -q "OPENAI_API_KEY\|GEMINI" .env; then
            print_warning "Gemini/Google references still in .env file"
        else
            print_success "Gemini references properly removed from .env"
        fi
    else
        print_warning ".env file not found"
    fi
}

test_requirements() {
    print_header "REQUIREMENTS VALIDATION"
    
    print_test "Requirements.txt file"
    if [ -f "requirements.txt" ]; then
        print_success "requirements.txt found"
        
        if grep -q "openai" requirements.txt; then
            print_success "OpenAI dependency in requirements.txt"
        else
            print_failure "OpenAI dependency missing from requirements.txt"
        fi
        
        if grep -q "google-generativeai" requirements.txt; then
            print_warning "Google Generative AI still in requirements.txt"
        else
            print_success "Google Generative AI properly removed from requirements.txt"
        fi
    else
        print_failure "requirements.txt missing"
    fi
    
    print_test "Docker requirements"
    if [ -f "requirements-docker.txt" ]; then
        if grep -q "openai" requirements-docker.txt; then
            print_success "OpenAI in Docker requirements"
        else
            print_failure "OpenAI missing from Docker requirements"
        fi
    else
        print_warning "Docker requirements file not found"
    fi
}

test_scripts() {
    print_header "SCRIPTS VALIDATION"
    
    print_test "Setup script"
    if [ -f "scripts/setup.py" ]; then
        if grep -q "openai" scripts/setup.py; then
            print_success "OpenAI references in setup script"
        else
            print_failure "OpenAI references missing from setup script"
        fi
        
        if grep -q "gemini\|google.*generative" scripts/setup.py; then
            print_warning "Gemini references still in setup script"
        else
            print_success "Gemini references properly removed from setup script"
        fi
    else
        print_warning "Setup script not found"
    fi
    
    print_test "Realtime setup script"
    if [ -f "scripts/setup_realtime.py" ]; then
        if grep -q "openai" scripts/setup_realtime.py; then
            print_success "OpenAI references in realtime setup script"
        else
            print_failure "OpenAI references missing from realtime setup script"
        fi
    else
        print_warning "Realtime setup script not found"
    fi
}

generate_report() {
    print_header "MIGRATION TEST REPORT"
    
    echo -e "\n${BLUE}📊 TEST SUMMARY${NC}"
    echo -e "Total Tests: ${TOTAL_TESTS}"
    echo -e "${GREEN}Passed: ${PASSED_TESTS}${NC}"
    echo -e "${RED}Failed: ${FAILED_TESTS}${NC}"
    
    PASS_RATE=$((PASSED_TESTS * 100 / TOTAL_TESTS))
    echo -e "Pass Rate: ${PASS_RATE}%"
    
    if [ $FAILED_TESTS -eq 0 ]; then
        echo -e "\n${GREEN}🎉 ALL TESTS PASSED! Migration is successful.${NC}"
        echo -e "${GREEN}✅ The system is ready for production with OpenAI integration.${NC}"
    elif [ $PASS_RATE -ge 80 ]; then
        echo -e "\n${YELLOW}⚠️  Most tests passed but some issues need attention.${NC}"
        echo -e "${YELLOW}📝 Check the log file for details: $LOG_FILE${NC}"
    else
        echo -e "\n${RED}❌ Multiple test failures detected.${NC}"
        echo -e "${RED}🔧 Migration needs additional work before production use.${NC}"
    fi
    
    echo -e "\n${BLUE}📋 Detailed log saved to: $LOG_FILE${NC}"
    
    # Save summary to file
    cat > migration_test_summary.txt << EOF
NPCL Voice Assistant - OpenAI Migration Test Summary
Generated: $(date)

Total Tests: $TOTAL_TESTS
Passed: $PASSED_TESTS
Failed: $FAILED_TESTS
Pass Rate: $PASS_RATE%

Status: $([ $FAILED_TESTS -eq 0 ] && echo "SUCCESS" || echo "NEEDS ATTENTION")

Detailed log: $LOG_FILE
EOF
    
    echo -e "${BLUE}📄 Summary saved to: migration_test_summary.txt${NC}"
}

# Main execution
main() {
    echo -e "${BLUE}"
    echo "============================================================================="
    echo "🚀 NPCL Voice Assistant - OpenAI Migration Validation"
    echo "============================================================================="
    echo -e "${NC}"
    echo "This script validates the complete migration from Gemini to OpenAI"
    echo "Testing all components, configurations, and functionality..."
    echo ""
    
    log "Starting OpenAI migration validation tests"
    
    # Run all tests
    test_environment
    test_dependencies
    test_configuration
    test_source_code
    test_asterisk_configuration
    test_kubernetes_deployment
    test_documentation
    test_import_syntax
    test_environment_variables
    test_requirements
    test_scripts
    test_server_startup
    test_api_endpoints
    
    # Generate final report
    generate_report
    
    log "Migration validation tests completed"
    
    # Exit with appropriate code
    if [ $FAILED_TESTS -eq 0 ]; then
        exit 0
    else
        exit 1
    fi
}

# Run main function
main "$@"