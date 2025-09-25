#!/bin/bash

# NPCL Voice Assistant Test Runner
# This script helps you run different types of tests easily

echo "🧪 NPCL Voice Assistant Test Runner"
echo "=================================="

# Activate virtual environment
source .venv/bin/activate

# Check if pytest is available
if ! command -v pytest &> /dev/null; then
    echo "❌ pytest not found. Please install it first."
    exit 1
fi

# Function to run tests with proper formatting
run_test_suite() {
    local test_path="$1"
    local test_name="$2"
    
    echo ""
    echo "🔍 Running $test_name..."
    echo "----------------------------------------"
    
    python -m pytest "$test_path" -v --tb=short
    
    if [ $? -eq 0 ]; then
        echo "✅ $test_name completed successfully!"
    else
        echo "❌ $test_name failed!"
        return 1
    fi
}

# Parse command line arguments
case "${1:-all}" in
    "unit")
        run_test_suite "tests/unit/" "Unit Tests"
        ;;
    "integration")
        run_test_suite "tests/integration/" "Integration Tests"
        ;;
    "audio")
        run_test_suite "tests/audio/" "Audio Tests"
        ;;
    "performance")
        run_test_suite "tests/performance/" "Performance Tests"
        ;;
    "e2e")
        run_test_suite "tests/e2e/" "End-to-End Tests"
        ;;
    "quick")
        echo "🚀 Running Quick Test Suite..."
        run_test_suite "tests/unit/test_configuration.py" "Configuration Tests"
        run_test_suite "tests/unit/test_npcl_prompts.py" "NPCL Prompts Tests"
        ;;
    "all")
        echo "🎯 Running All Tests..."
        run_test_suite "tests/unit/" "Unit Tests"
        run_test_suite "tests/integration/" "Integration Tests"
        run_test_suite "tests/audio/" "Audio Tests"
        ;;
    "help"|"-h"|"--help")
        echo ""
        echo "Usage: $0 [test_type]"
        echo ""
        echo "Available test types:"
        echo "  unit         - Run unit tests only"
        echo "  integration  - Run integration tests only"
        echo "  audio        - Run audio processing tests only"
        echo "  performance  - Run performance tests only"
        echo "  e2e          - Run end-to-end tests only"
        echo "  quick        - Run a quick subset of tests"
        echo "  all          - Run all tests (default)"
        echo "  help         - Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0 unit      # Run only unit tests"
        echo "  $0 quick     # Run quick test suite"
        echo "  $0           # Run all tests"
        ;;
    *)
        echo "❌ Unknown test type: $1"
        echo "Run '$0 help' for available options."
        exit 1
        ;;
esac

echo ""
echo "🎉 Test execution completed!"