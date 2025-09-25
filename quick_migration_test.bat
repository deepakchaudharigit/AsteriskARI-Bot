@echo off
REM =============================================================================
REM NPCL Voice Assistant - Quick OpenAI Migration Test (Windows)
REM =============================================================================
REM Quick validation script to test the most critical migration components
REM =============================================================================

echo 🚀 Quick OpenAI Migration Test
echo ==================================

REM Test 1: Check OpenAI dependency
echo.
echo 1. Testing OpenAI dependency...
python -c "import openai; print(f'✅ OpenAI {openai.__version__} installed')" >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ OpenAI package available
) else (
    echo ❌ OpenAI package missing
    echo Run: pip install openai
    exit /b 1
)

REM Test 2: Check Gemini removal
echo.
echo 2. Testing Gemini removal...
python -c "import google.generativeai" >nul 2>&1
if !errorlevel! equ 0 (
    echo ⚠️  Google Generative AI still installed
    echo Consider removing: pip uninstall google-generativeai
) else (
    echo ✅ Gemini dependencies properly removed
)

REM Test 3: Check configuration
echo.
echo 3. Testing configuration...
if exist "config\settings.py" (
    findstr /i "openai_api_key" config\settings.py >nul 2>&1
    if !errorlevel! equ 0 (
        echo ✅ OpenAI configuration found
    ) else (
        echo ❌ OpenAI configuration missing
    )
    
    findstr /i "gemini" config\settings.py >nul 2>&1
    if !errorlevel! equ 0 (
        echo ⚠️  Gemini references still in settings
    ) else (
        echo ✅ Gemini references removed from settings
    )
) else (
    echo ❌ Settings file missing
)

REM Test 4: Check main application
echo.
echo 4. Testing main application...
if exist "src\main.py" (
    python -m py_compile src\main.py >nul 2>&1
    if !errorlevel! equ 0 (
        echo ✅ Main application syntax valid
    ) else (
        echo ❌ Main application has syntax errors
    )
) else (
    echo ❌ Main application missing
)

REM Test 5: Check OpenAI client
echo.
echo 5. Testing OpenAI client...
if exist "src\voice_assistant\ai\openai_realtime_client_enhanced.py" (
    echo ✅ OpenAI Realtime client found
) else (
    echo ❌ OpenAI Realtime client missing
)

REM Test 6: Check imports
echo.
echo 6. Testing imports...
python -c "from config.settings import get_settings; print('Settings import OK')" >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ Settings import successful
) else (
    echo ❌ Settings import failed
)

REM Test 7: Check server startup (quick test)
echo.
echo 7. Testing server startup...
start /b python src\run_realtime_server.py
timeout /t 2 /nobreak >nul
tasklist /fi "imagename eq python.exe" | find "python.exe" >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ Server starts successfully
    taskkill /f /im python.exe >nul 2>&1
) else (
    echo ❌ Server failed to start
)

REM Test 8: Check environment variables
echo.
echo 8. Testing environment variables...
if defined OPENAI_API_KEY (
    echo ✅ OPENAI_API_KEY is set
) else (
    echo ⚠️  OPENAI_API_KEY not set
    echo Set your OpenAI API key: set OPENAI_API_KEY=your-key-here
)

REM Test 9: Check Asterisk configuration
echo.
echo 9. Testing Asterisk configuration...
if exist "asterisk-config\extensions.conf" (
    findstr /i "openai-voice-assistant" asterisk-config\extensions.conf >nul 2>&1
    if !errorlevel! equ 0 (
        echo ✅ OpenAI stasis app configured
    ) else (
        echo ❌ OpenAI stasis app not configured
    )
) else (
    echo ⚠️  Asterisk config not found
)

REM Test 10: Check requirements
echo.
echo 10. Testing requirements...
if exist "requirements.txt" (
    findstr /i "openai" requirements.txt >nul 2>&1
    if !errorlevel! equ 0 (
        echo ✅ OpenAI in requirements.txt
    ) else (
        echo ❌ OpenAI missing from requirements.txt
    )
    
    findstr /i "google-generativeai" requirements.txt >nul 2>&1
    if !errorlevel! equ 0 (
        echo ⚠️  Gemini still in requirements.txt
    ) else (
        echo ✅ Gemini removed from requirements.txt
    )
) else (
    echo ❌ requirements.txt missing
)

echo.
echo ==================================
echo Quick Migration Test Complete
echo ✅ Run the full test with: migration_test.bat