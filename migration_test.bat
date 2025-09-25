@echo off
REM =============================================================================
REM NPCL Voice Assistant - OpenAI Migration Test Script (Windows)
REM =============================================================================
REM This script validates the complete migration from Gemini to OpenAI
REM Tests all components, configurations, and functionality
REM =============================================================================

setlocal enabledelayedexpansion

REM Test counters
set TOTAL_TESTS=0
set PASSED_TESTS=0
set FAILED_TESTS=0

REM Logging
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YY=%dt:~2,2%" & set "YYYY=%dt:~0,4%" & set "MM=%dt:~4,2%" & set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%" & set "Min=%dt:~10,2%" & set "Sec=%dt:~12,2%"
set "LOG_FILE=migration_test_%YYYY%%MM%%DD%_%HH%%Min%%Sec%.log"

REM Helper functions
:log
echo %date% %time% - %~1 >> "%LOG_FILE%"
goto :eof

:print_header
echo.
echo ========================================
echo %~1
echo ========================================
echo.
goto :eof

:print_test
echo 🧪 Testing: %~1
set /a TOTAL_TESTS+=1
goto :eof

:print_success
echo ✅ PASS: %~1
set /a PASSED_TESTS+=1
call :log "PASS: %~1"
goto :eof

:print_failure
echo ❌ FAIL: %~1
set /a FAILED_TESTS+=1
call :log "FAIL: %~1"
goto :eof

:print_warning
echo ⚠️  WARNING: %~1
call :log "WARNING: %~1"
goto :eof

REM Test functions
:test_environment
call :print_header "ENVIRONMENT VALIDATION"

call :print_test "Python version"
python --version >nul 2>&1
if !errorlevel! equ 0 (
    for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
    call :print_success "Python available: !PYTHON_VERSION!"
) else (
    call :print_failure "Python not found"
    goto :eof
)

call :print_test "Virtual environment"
if exist ".venv" (
    call :print_success "Virtual environment detected"
) else (
    if defined VIRTUAL_ENV (
        call :print_success "Virtual environment detected"
    ) else (
        call :print_warning "No virtual environment detected"
    )
)

call :print_test "Required directories"
for %%d in (src config tests docs) do (
    if exist "%%d" (
        call :print_success "Directory exists: %%d"
    ) else (
        call :print_failure "Missing directory: %%d"
    )
)
goto :eof

:test_dependencies
call :print_header "DEPENDENCY VALIDATION"

call :print_test "OpenAI package"
python -c "import openai; print(f'OpenAI version: {openai.__version__}')" >nul 2>&1
if !errorlevel! equ 0 (
    call :print_success "OpenAI package installed"
) else (
    call :print_failure "OpenAI package not found"
)

call :print_test "FastAPI package"
python -c "import fastapi; print(f'FastAPI version: {fastapi.__version__}')" >nul 2>&1
if !errorlevel! equ 0 (
    call :print_success "FastAPI package installed"
) else (
    call :print_failure "FastAPI package not found"
)

call :print_test "WebSockets package"
python -c "import websockets; print(f'WebSockets version: {websockets.__version__}')" >nul 2>&1
if !errorlevel! equ 0 (
    call :print_success "WebSockets package installed"
) else (
    call :print_failure "WebSockets package not found"
)

call :print_test "Pydantic package"
python -c "import pydantic; print(f'Pydantic version: {pydantic.__version__}')" >nul 2>&1
if !errorlevel! equ 0 (
    call :print_success "Pydantic package installed"
) else (
    call :print_failure "Pydantic package not found"
)

call :print_test "Removed Gemini dependencies"
python -c "import google.generativeai" >nul 2>&1
if !errorlevel! equ 0 (
    call :print_warning "Google Generative AI still installed (should be removed)"
) else (
    call :print_success "Google Generative AI properly removed"
)
goto :eof

:test_configuration
call :print_header "CONFIGURATION VALIDATION"

call :print_test "Settings file exists"
if exist "config\settings.py" (
    call :print_success "Settings file found"
) else (
    call :print_failure "Settings file missing"
    goto :eof
)

call :print_test "OpenAI configuration in settings"
findstr /i "openai_api_key" config\settings.py >nul 2>&1
if !errorlevel! equ 0 (
    call :print_success "OpenAI API key configuration found"
) else (
    call :print_failure "OpenAI API key configuration missing"
)

findstr /i "openai_model" config\settings.py >nul 2>&1
if !errorlevel! equ 0 (
    call :print_success "OpenAI model configuration found"
) else (
    call :print_failure "OpenAI model configuration missing"
)

call :print_test "Removed Gemini configurations"
findstr /i "gemini" config\settings.py >nul 2>&1
if !errorlevel! equ 0 (
    call :print_warning "Gemini references still found in settings"
) else (
    call :print_success "Gemini references properly removed from settings"
)

call :print_test "Environment file template"
if exist ".env.example" (
    findstr /i "OPENAI_API_KEY" .env.example >nul 2>&1
    if !errorlevel! equ 0 (
        call :print_success "OpenAI API key in .env.example"
    ) else (
        call :print_failure "OpenAI API key missing from .env.example"
    )
    
    findstr /i "GOOGLE_API_KEY GEMINI" .env.example >nul 2>&1
    if !errorlevel! equ 0 (
        call :print_warning "Gemini/Google references still in .env.example"
    ) else (
        call :print_success "Gemini references properly removed from .env.example"
    )
) else (
    call :print_warning ".env.example file not found"
)
goto :eof

:test_source_code
call :print_header "SOURCE CODE VALIDATION"

call :print_test "Main application file"
if exist "src\main.py" (
    call :print_success "Main application file found"
    
    findstr /i "openai" src\main.py >nul 2>&1
    if !errorlevel! equ 0 (
        call :print_success "OpenAI imports found in main.py"
    ) else (
        call :print_failure "OpenAI imports missing from main.py"
    )
    
    findstr /i "gemini google.generativeai" src\main.py >nul 2>&1
    if !errorlevel! equ 0 (
        call :print_warning "Gemini references still in main.py"
    ) else (
        call :print_success "Gemini references properly removed from main.py"
    )
) else (
    call :print_failure "Main application file missing"
)

call :print_test "OpenAI client implementation"
if exist "src\voice_assistant\ai\openai_realtime_client_enhanced.py" (
    call :print_success "OpenAI Realtime client found"
) else (
    call :print_failure "OpenAI Realtime client missing"
)

call :print_test "AI client factory"
if exist "src\voice_assistant\ai\ai_client_factory.py" (
    findstr /i "openai" src\voice_assistant\ai\ai_client_factory.py >nul 2>&1
    if !errorlevel! equ 0 (
        call :print_success "OpenAI support in AI client factory"
    ) else (
        call :print_failure "OpenAI support missing from AI client factory"
    )
) else (
    call :print_failure "AI client factory missing"
)

call :print_test "Removed Gemini client files"
if exist "src\voice_assistant\ai\gemini_client.py" (
    call :print_warning "Gemini client files still present"
) else (
    if exist "src\voice_assistant\ai\gemini_live_client.py" (
        call :print_warning "Gemini client files still present"
    ) else (
        call :print_success "Gemini client files properly removed"
    )
)
goto :eof

:test_asterisk_configuration
call :print_header "ASTERISK CONFIGURATION VALIDATION"

call :print_test "Asterisk extensions configuration"
if exist "asterisk-config\extensions.conf" (
    call :print_success "Asterisk extensions.conf found"
    
    findstr /i "openai-voice-assistant" asterisk-config\extensions.conf >nul 2>&1
    if !errorlevel! equ 0 (
        call :print_success "OpenAI voice assistant stasis app configured"
    ) else (
        call :print_failure "OpenAI voice assistant stasis app not configured"
    )
    
    findstr /i "gemini-voice-assistant" asterisk-config\extensions.conf >nul 2>&1
    if !errorlevel! equ 0 (
        call :print_warning "Gemini voice assistant references still in extensions.conf"
    ) else (
        call :print_success "Gemini references properly removed from extensions.conf"
    )
) else (
    call :print_failure "Asterisk extensions.conf missing"
)

call :print_test "Docker compose configuration"
if exist "docker-compose.yml" (
    call :print_success "Docker compose file found"
) else (
    call :print_warning "Docker compose file not found"
)
goto :eof

:test_kubernetes_deployment
call :print_header "KUBERNETES DEPLOYMENT VALIDATION"

call :print_test "Kubernetes namespace configuration"
if exist "kubernetes\namespace.yaml" (
    call :print_success "Kubernetes namespace file found"
    
    findstr /i "OPENAI_MODEL OPENAI_VOICE" kubernetes\namespace.yaml >nul 2>&1
    if !errorlevel! equ 0 (
        call :print_success "OpenAI configuration in Kubernetes"
    ) else (
        call :print_failure "OpenAI configuration missing from Kubernetes"
    )
    
    findstr /i "GEMINI" kubernetes\namespace.yaml >nul 2>&1
    if !errorlevel! equ 0 (
        call :print_warning "Gemini references still in Kubernetes config"
    ) else (
        call :print_success "Gemini references properly removed from Kubernetes"
    )
) else (
    call :print_warning "Kubernetes namespace file not found"
)
goto :eof

:test_documentation
call :print_header "DOCUMENTATION VALIDATION"

call :print_test "Main README file"
if exist "README.md" (
    call :print_success "README.md found"
    
    findstr /i "openai gpt-4" README.md >nul 2>&1
    if !errorlevel! equ 0 (
        call :print_success "OpenAI references in README"
    ) else (
        call :print_failure "OpenAI references missing from README"
    )
) else (
    call :print_failure "README.md missing"
)

call :print_test "API documentation"
if exist "docs\API_DOCUMENTATION.md" (
    call :print_success "API documentation found"
    
    findstr /i "OPENAI_API_KEY" docs\API_DOCUMENTATION.md >nul 2>&1
    if !errorlevel! equ 0 (
        call :print_success "OpenAI API key documented"
    ) else (
        call :print_failure "OpenAI API key not documented"
    )
) else (
    call :print_warning "API documentation not found"
)

call :print_test "Architecture documentation"
if exist "docs\ARCHITECTURE.md" (
    findstr /i "openai" docs\ARCHITECTURE.md >nul 2>&1
    if !errorlevel! equ 0 (
        call :print_success "OpenAI references in architecture docs"
    ) else (
        call :print_failure "OpenAI references missing from architecture docs"
    )
) else (
    call :print_warning "Architecture documentation not found"
)
goto :eof

:test_import_syntax
call :print_header "IMPORT SYNTAX VALIDATION"

call :print_test "Python syntax validation"
python -m py_compile src\main.py >nul 2>&1
if !errorlevel! equ 0 (
    call :print_success "Main application syntax valid"
) else (
    call :print_failure "Main application syntax errors"
)

call :print_test "Settings import validation"
python -c "from config.settings import get_settings; settings = get_settings(); print('Settings loaded successfully')" >nul 2>&1
if !errorlevel! equ 0 (
    call :print_success "Settings import successful"
) else (
    call :print_failure "Settings import failed"
)

call :print_test "AI client factory import"
python -c "from src.voice_assistant.ai.ai_client_factory import AIClientFactory; print('AI client factory imported')" >nul 2>&1
if !errorlevel! equ 0 (
    call :print_success "AI client factory import successful"
) else (
    call :print_failure "AI client factory import failed"
)
goto :eof

:test_server_startup
call :print_header "SERVER STARTUP VALIDATION"

call :print_test "FastAPI server startup test"

REM Start server in background
start /b python src\run_realtime_server.py
timeout /t 5 /nobreak >nul

REM Test if server is responding
curl -s http://localhost:8000/health >nul 2>&1
if !errorlevel! equ 0 (
    call :print_success "FastAPI server started and responding"
) else (
    call :print_failure "FastAPI server failed to start or not responding"
)

REM Kill any python processes (cleanup)
taskkill /f /im python.exe >nul 2>&1
goto :eof

:test_environment_variables
call :print_header "ENVIRONMENT VARIABLES VALIDATION"

call :print_test "OpenAI API key environment"
if defined OPENAI_API_KEY (
    call :print_success "OPENAI_API_KEY environment variable set"
) else (
    call :print_warning "OPENAI_API_KEY environment variable not set"
)

call :print_test "Removed Google API key"
if defined GOOGLE_API_KEY (
    call :print_warning "GOOGLE_API_KEY still set (should be removed)"
) else (
    call :print_success "GOOGLE_API_KEY properly removed"
)

call :print_test ".env file"
if exist ".env" (
    findstr /i "OPENAI_API_KEY" .env >nul 2>&1
    if !errorlevel! equ 0 (
        call :print_success "OPENAI_API_KEY in .env file"
    ) else (
        call :print_warning "OPENAI_API_KEY not in .env file"
    )
    
    findstr /i "GOOGLE_API_KEY GEMINI" .env >nul 2>&1
    if !errorlevel! equ 0 (
        call :print_warning "Gemini/Google references still in .env file"
    ) else (
        call :print_success "Gemini references properly removed from .env"
    )
) else (
    call :print_warning ".env file not found"
)
goto :eof

:test_requirements
call :print_header "REQUIREMENTS VALIDATION"

call :print_test "Requirements.txt file"
if exist "requirements.txt" (
    call :print_success "requirements.txt found"
    
    findstr /i "openai" requirements.txt >nul 2>&1
    if !errorlevel! equ 0 (
        call :print_success "OpenAI dependency in requirements.txt"
    ) else (
        call :print_failure "OpenAI dependency missing from requirements.txt"
    )
    
    findstr /i "google-generativeai" requirements.txt >nul 2>&1
    if !errorlevel! equ 0 (
        call :print_warning "Google Generative AI still in requirements.txt"
    ) else (
        call :print_success "Google Generative AI properly removed from requirements.txt"
    )
) else (
    call :print_failure "requirements.txt missing"
)

call :print_test "Docker requirements"
if exist "requirements-docker.txt" (
    findstr /i "openai" requirements-docker.txt >nul 2>&1
    if !errorlevel! equ 0 (
        call :print_success "OpenAI in Docker requirements"
    ) else (
        call :print_failure "OpenAI missing from Docker requirements"
    )
) else (
    call :print_warning "Docker requirements file not found"
)
goto :eof

:test_scripts
call :print_header "SCRIPTS VALIDATION"

call :print_test "Setup script"
if exist "scripts\setup.py" (
    findstr /i "openai" scripts\setup.py >nul 2>&1
    if !errorlevel! equ 0 (
        call :print_success "OpenAI references in setup script"
    ) else (
        call :print_failure "OpenAI references missing from setup script"
    )
    
    findstr /i "gemini google.*generative" scripts\setup.py >nul 2>&1
    if !errorlevel! equ 0 (
        call :print_warning "Gemini references still in setup script"
    ) else (
        call :print_success "Gemini references properly removed from setup script"
    )
) else (
    call :print_warning "Setup script not found"
)

call :print_test "Realtime setup script"
if exist "scripts\setup_realtime.py" (
    findstr /i "openai" scripts\setup_realtime.py >nul 2>&1
    if !errorlevel! equ 0 (
        call :print_success "OpenAI references in realtime setup script"
    ) else (
        call :print_failure "OpenAI references missing from realtime setup script"
    )
) else (
    call :print_warning "Realtime setup script not found"
)
goto :eof

:generate_report
call :print_header "MIGRATION TEST REPORT"

echo.
echo 📊 TEST SUMMARY
echo Total Tests: !TOTAL_TESTS!
echo Passed: !PASSED_TESTS!
echo Failed: !FAILED_TESTS!

set /a PASS_RATE=!PASSED_TESTS! * 100 / !TOTAL_TESTS!
echo Pass Rate: !PASS_RATE!%%

if !FAILED_TESTS! equ 0 (
    echo.
    echo 🎉 ALL TESTS PASSED! Migration is successful.
    echo ✅ The system is ready for production with OpenAI integration.
) else (
    if !PASS_RATE! geq 80 (
        echo.
        echo ⚠️  Most tests passed but some issues need attention.
        echo 📝 Check the log file for details: !LOG_FILE!
    ) else (
        echo.
        echo ❌ Multiple test failures detected.
        echo 🔧 Migration needs additional work before production use.
    )
)

echo.
echo 📋 Detailed log saved to: !LOG_FILE!

REM Save summary to file
(
echo NPCL Voice Assistant - OpenAI Migration Test Summary
echo Generated: %date% %time%
echo.
echo Total Tests: !TOTAL_TESTS!
echo Passed: !PASSED_TESTS!
echo Failed: !FAILED_TESTS!
echo Pass Rate: !PASS_RATE!%%
echo.
if !FAILED_TESTS! equ 0 (
    echo Status: SUCCESS
) else (
    echo Status: NEEDS ATTENTION
)
echo.
echo Detailed log: !LOG_FILE!
) > migration_test_summary.txt

echo 📄 Summary saved to: migration_test_summary.txt
goto :eof

REM Main execution
:main
echo.
echo =============================================================================
echo 🚀 NPCL Voice Assistant - OpenAI Migration Validation
echo =============================================================================
echo.
echo This script validates the complete migration from Gemini to OpenAI
echo Testing all components, configurations, and functionality...
echo.

call :log "Starting OpenAI migration validation tests"

REM Run all tests
call :test_environment
call :test_dependencies
call :test_configuration
call :test_source_code
call :test_asterisk_configuration
call :test_kubernetes_deployment
call :test_documentation
call :test_import_syntax
call :test_environment_variables
call :test_requirements
call :test_scripts
call :test_server_startup

REM Generate final report
call :generate_report

call :log "Migration validation tests completed"

REM Exit with appropriate code
if !FAILED_TESTS! equ 0 (
    exit /b 0
) else (
    exit /b 1
)

REM Call main function
call :main