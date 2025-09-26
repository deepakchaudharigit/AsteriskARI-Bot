@echo off
REM =============================================================================
REM NPCL Asterisk ARI Voice Assistant - One-Click Startup Script (Windows)
REM =============================================================================

setlocal enabledelayedexpansion

echo ===============================================================================
echo 🚀 NPCL Asterisk ARI Voice Assistant - One-Click Startup
echo 📞 Enterprise Voice Assistant with OpenAI GPT-4 Realtime API
echo 🏢 NPCL (Noida Power Corporation Limited)
echo ===============================================================================
echo.

REM Step 1: Check Python
echo 🔄 Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.8 or higher
    echo    Download from: https://python.org
    pause
    exit /b 1
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo ✅ Python !PYTHON_VERSION! found
)

REM Step 2: Setup Virtual Environment
echo 🔄 Setting up virtual environment...
if not exist ".venv" (
    python -m venv .venv
    echo ✅ Virtual environment created
) else (
    echo ℹ️  Virtual environment already exists
)

REM Activate virtual environment
call .venv\Scripts\activate.bat
echo ✅ Virtual environment activated

REM Step 3: Install dependencies
echo 🔄 Installing dependencies...
python -m pip install --upgrade pip >nul 2>&1

if exist "requirements.txt" (
    pip install -r requirements.txt
    echo ✅ Dependencies installed
) else (
    echo ❌ requirements.txt not found
    pause
    exit /b 1
)

REM Step 4: Setup environment file
echo 🔄 Setting up environment configuration...
if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
        echo ✅ .env file created from template
        echo ⚠️  Please edit .env file and add your OpenAI API key
    ) else (
        echo ❌ .env.example not found
        pause
        exit /b 1
    )
) else (
    echo ✅ .env file already exists
)

REM Step 5: Create required directories
echo 🔄 Creating required directories...
if not exist "logs" mkdir logs
if not exist "sounds" mkdir sounds
if not exist "sounds\temp" mkdir sounds\temp
if not exist "recordings" mkdir recordings
if not exist "data" mkdir data
echo ✅ Directories created

REM Step 6: Check OpenAI API key
echo 🔄 Checking OpenAI API configuration...
if exist ".env" (
    findstr /C:"your_actual_openai_api_key_here" .env >nul
    if not errorlevel 1 (
        echo ⚠️  OpenAI API key not configured in .env file
        echo ℹ️  Please edit .env and set OPENAI_API_KEY=your_actual_api_key
        echo ℹ️  Get your API key from: https://platform.openai.com/api-keys
    ) else (
        echo ✅ OpenAI API key appears to be configured
    )
)

REM Step 7: Check Asterisk (optional)
echo 🔄 Checking Asterisk ARI connection...
curl -s -f -u "asterisk:1234" "http://localhost:8088/ari/asterisk/info" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Asterisk ARI: Not accessible (will start anyway)
    echo ℹ️  Telephony features may not work without Asterisk
) else (
    echo ✅ Asterisk ARI: Connected
)

REM Step 8: Start the application
echo.
echo ===============================================================================
echo 🎯 Starting NPCL Voice Assistant...
echo ===============================================================================
echo 📞 Ready for calls on extension 1000
echo 🌐 Web Interface: http://localhost:8000
echo 📚 API Docs: http://localhost:8000/docs
echo 🏥 Health Check: http://localhost:8000/health
echo ⏹️  Press Ctrl+C to stop the service
echo ===============================================================================
echo.

REM Set Python path and start the application
set PYTHONPATH=%CD%\src;%PYTHONPATH%

REM Try different entry points
if exist "ari_bot.py" (
    echo ℹ️  Starting via ari_bot.py...
    python ari_bot.py
) else if exist "start_voice_assistant.py" (
    echo ℹ️  Starting via start_voice_assistant.py...
    python start_voice_assistant.py
) else if exist "src\run_realtime_server.py" (
    echo ℹ️  Starting via src\run_realtime_server.py...
    python src\run_realtime_server.py
) else (
    echo ❌ No main application file found
    echo ℹ️  Expected: ari_bot.py, start_voice_assistant.py, or src\run_realtime_server.py
    pause
    exit /b 1
)

echo.
echo ℹ️  Shutting down NPCL Voice Assistant...
echo ✅ Goodbye!
pause