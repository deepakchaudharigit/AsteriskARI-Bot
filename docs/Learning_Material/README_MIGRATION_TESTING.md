# 🧪 OpenAI Migration Testing Guide

This guide provides comprehensive testing scripts to validate the complete migration from Google Gemini to OpenAI GPT-4 Realtime API.

## 📋 Available Test Scripts

### 1. **Full Migration Test** (Recommended)
Comprehensive validation of all migration components:

**Linux/macOS:**
```bash
chmod +x migration_test.sh
./migration_test.sh
```

**Windows:**
```cmd
migration_test.bat
```

**What it tests:**
- ✅ Environment setup and dependencies
- ✅ OpenAI package installation and Gemini removal
- ✅ Configuration files (settings.py, .env, etc.)
- ✅ Source code migration (imports, references)
- ✅ Asterisk configuration updates
- ✅ Kubernetes deployment configs
- ✅ Documentation updates
- ✅ Server startup and API endpoints
- ✅ Requirements and scripts validation

### 2. **Quick Migration Test**
Fast validation of critical components:

**Linux/macOS:**
```bash
chmod +x quick_migration_test.sh
./quick_migration_test.sh
```

**Windows:**
```cmd
quick_migration_test.bat
```

**What it tests:**
- ✅ OpenAI dependency check
- ✅ Gemini removal verification
- ✅ Basic configuration validation
- ✅ Main application syntax
- ✅ Server startup test
- ✅ Environment variables

### 3. **OpenAI Integration Test**
Deep validation of OpenAI API functionality:

```bash
python test_openai_integration.py
```

**What it tests:**
- ✅ OpenAI package import and version
- ✅ API key configuration and format
- ✅ OpenAI client creation
- ✅ Basic API connectivity
- ✅ GPT-4 Realtime model access
- ✅ Voice capabilities (TTS)
- ✅ Function calling support
- ✅ Settings integration
- ✅ AI client factory
- ✅ Realtime client implementation

## 🚀 Quick Start Testing

### Step 1: Set up environment
```bash
# Set your OpenAI API key
export OPENAI_API_KEY="sk-your-openai-api-key-here"

# Or create .env file
echo "OPENAI_API_KEY=sk-your-openai-api-key-here" > .env
```

### Step 2: Run quick test
```bash
./quick_migration_test.sh
```

### Step 3: Run full validation
```bash
./migration_test.sh
```

### Step 4: Test OpenAI integration
```bash
python test_openai_integration.py
```

## 📊 Understanding Test Results

### ✅ Success Indicators
- **All tests pass**: Migration is complete and system is ready
- **Green checkmarks**: Individual components working correctly
- **Pass rate 100%**: Perfect migration

### ⚠️ Warning Indicators
- **Yellow warnings**: Non-critical issues that should be addressed
- **Pass rate 80-99%**: Mostly successful with minor issues

### ❌ Failure Indicators
- **Red failures**: Critical issues that must be fixed
- **Pass rate <80%**: Significant problems requiring attention

## 🔧 Common Issues and Solutions

### Issue: OpenAI package not found
```bash
# Solution: Install OpenAI
pip install openai>=1.0.0
```

### Issue: Gemini dependencies still present
```bash
# Solution: Remove Gemini packages
pip uninstall google-generativeai
```

### Issue: API key not configured
```bash
# Solution: Set environment variable
export OPENAI_API_KEY="your-key-here"
```

### Issue: Server startup fails
```bash
# Solution: Check dependencies and configuration
pip install -r requirements.txt
python -c "from config.settings import get_settings; print('OK')"
```

### Issue: Realtime model access denied
```bash
# Note: GPT-4 Realtime requires beta access
# Contact OpenAI for beta access or use standard models
```

## 📁 Test Output Files

After running tests, you'll find these files:

- **`migration_test_YYYYMMDD_HHMMSS.log`** - Detailed test execution log
- **`migration_test_summary.txt`** - Summary of test results
- **`openai_integration_test.log`** - OpenAI integration test log
- **`openai_integration_report.json`** - Detailed JSON report

## 🎯 Test Categories

### 1. Environment Tests
- Python version and virtual environment
- Required directories and file structure
- Package installations and versions

### 2. Configuration Tests
- Settings file validation
- Environment variables
- API key configuration
- Removed Gemini references

### 3. Source Code Tests
- Import syntax validation
- OpenAI client implementation
- Removed Gemini client files
- AI client factory integration

### 4. Infrastructure Tests
- Asterisk configuration
- Kubernetes deployment
- Docker compose setup
- Requirements files

### 5. Documentation Tests
- README updates
- API documentation
- Architecture documentation
- Migration documentation

### 6. Functional Tests
- Server startup and health
- API endpoint accessibility
- OpenAI API connectivity
- Voice capabilities
- Function calling

## 🔄 Continuous Testing

### Pre-deployment Testing
```bash
# Run before deploying to production
./migration_test.sh
python test_openai_integration.py
```

### Development Testing
```bash
# Quick check during development
./quick_migration_test.sh
```

### CI/CD Integration
Add to your CI/CD pipeline:
```yaml
# Example GitHub Actions
- name: Test OpenAI Migration
  run: |
    chmod +x migration_test.sh
    ./migration_test.sh
    python test_openai_integration.py
```

## 📈 Performance Benchmarks

Expected test durations:
- **Quick test**: 10-30 seconds
- **Full migration test**: 2-5 minutes
- **OpenAI integration test**: 30-60 seconds

Expected pass rates:
- **Fresh migration**: 95-100%
- **Partial migration**: 70-90%
- **Failed migration**: <70%

## 🆘 Getting Help

If tests fail:

1. **Check the log files** for detailed error messages
2. **Review the test output** for specific failure reasons
3. **Verify your OpenAI API key** is valid and has sufficient quota
4. **Ensure all dependencies** are installed correctly
5. **Check network connectivity** to OpenAI APIs

## 🎉 Success Criteria

Your migration is successful when:
- ✅ All migration tests pass (100% pass rate)
- ✅ OpenAI integration tests pass
- ✅ Server starts without errors
- ✅ API endpoints respond correctly
- ✅ No Gemini references remain in critical files
- ✅ OpenAI API connectivity confirmed

## 📞 Production Readiness Checklist

Before going to production:
- [ ] All test scripts pass
- [ ] OpenAI API key configured
- [ ] Asterisk configuration updated
- [ ] Documentation updated
- [ ] Team trained on new system
- [ ] Monitoring configured
- [ ] Backup procedures updated

---

**🚀 Ready to test your migration? Start with the quick test and work your way up to the full validation!**