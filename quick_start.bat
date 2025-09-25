@echo off
REM NPCL Voice Assistant - Quick Start Script for Windows
REM Comprehensive startup script for different deployment modes

setlocal enabledelayedexpansion

echo ========================================
echo   NPCL Voice Assistant - Quick Start
echo ========================================
echo.

REM Parse command line arguments
set "mode=%~1"
if "%mode%"=="" set "mode=docker"

if /i "%mode%"=="help" goto show_usage
if /i "%mode%"=="-h" goto show_usage
if /i "%mode%"=="--help" goto show_usage
if /i "%mode%"=="docker" goto start_docker
if /i "%mode%"=="asterisk" goto start_asterisk
if /i "%mode%"=="test" goto run_tests
if /i "%mode%"=="status" goto check_status

echo [ERROR] Unknown mode: %mode%
echo.
goto show_usage

:show_usage
echo Usage: %~nx0 [mode]
echo.
echo Available modes:
echo   docker    - Start with Docker containers (default)
echo   asterisk  - Start only Asterisk container
echo   test      - Run integration tests
echo   status    - Check system status
echo   help      - Show this help message
echo.
echo Examples:
echo   %~nx0 docker    # Start full Docker setup
echo   %~nx0 asterisk  # Start only Asterisk
echo   %~nx0 test      # Run tests
goto end

:start_docker
echo [INFO] Starting Docker Mode
echo ========================================
echo.

REM Check Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed. Please install Docker Desktop first.
    echo Visit: https://docs.docker.com/desktop/windows/
    goto end
)

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running. Please start Docker Desktop.
    goto end
)

echo [SUCCESS] Docker is available

REM Stop existing containers
echo [INFO] Stopping existing containers...
docker-compose down >nul 2>&1

REM Start services
echo [INFO] Starting Docker services...
docker-compose up -d --build
if errorlevel 1 (
    echo [ERROR] Failed to start Docker services
    goto end
)

REM Wait for services
echo [INFO] Waiting for services to start...
timeout /t 30 /nobreak >nul

REM Show status
echo [INFO] Service Status:
docker-compose ps

echo.
echo ========================================
echo   Service Information
echo ========================================
echo.
echo Web Interfaces:
echo   • Voice Assistant: http://localhost:8000
echo   • API Documentation: http://localhost:8000/docs
echo   • System Status: http://localhost:8000/ari/status
echo   • Asterisk ARI: http://localhost:8088/ari
echo.
echo SIP Configuration for Zoiper:
echo   ┌─────────────────────────────────────────┐
echo   │ Username: 1001                          │
echo   │ Password: 1234                          │
echo   │ Server:   localhost:5060                │
echo   │ Protocol: UDP                           │
echo   └─────────────────────────────────────────┘
echo.
echo Test Extensions:
echo   • Dial 1000 - AI Voice Assistant
echo   • Dial 9000 - Echo Test
echo   • Dial 1005 - IVR Menu
echo.
echo Useful Commands:
echo   • View logs: docker-compose logs -f
echo   • Restart: docker-compose restart
echo   • Stop: docker-compose down
goto end

:start_asterisk
echo [INFO] Starting Asterisk Only
echo ========================================
echo.

REM Stop existing containers
docker-compose down >nul 2>&1

REM Start only Asterisk
echo [INFO] Starting Asterisk container...
docker-compose up -d asterisk
if errorlevel 1 (
    echo [ERROR] Failed to start Asterisk container
    goto end
)

REM Wait for startup
echo [INFO] Waiting for Asterisk to start...
timeout /t 20 /nobreak >nul

REM Show status
echo [INFO] Asterisk Status:
docker ps --filter name=asterisk

echo.
echo [SUCCESS] Asterisk is ready!
echo   SIP Server: localhost:5060
echo   ARI Interface: http://localhost:8088/ari
echo.
echo [INFO] For local development, you can now run:
echo   python src\\run_realtime_server.py
goto end

:run_tests
echo [INFO] Running Integration Tests
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    goto end
)

REM Run tests
echo [INFO] Running OpenAI integration tests...
python test_openai_integration.py
if errorlevel 1 (
    echo [WARNING] Some tests failed
)

echo.
echo [INFO] Running system status check...
python check_system_status.py
goto end

:check_status
echo [INFO] Checking System Status
echo ========================================
echo.

REM Check Docker containers
echo Container Status:
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo.
echo Service Health Checks:

REM Check Voice Assistant
curl -s http://localhost:8000/ari/health >nul 2>&1
if not errorlevel 1 (
    echo [SUCCESS] ✓ Voice Assistant (http://localhost:8000)
) else (
    echo [ERROR] ✗ Voice Assistant not responding
)

REM Check Asterisk ARI
curl -s "http://localhost:8088/ari/asterisk/info" -u "asterisk:1234" >nul 2>&1
if not errorlevel 1 (
    echo [SUCCESS] ✓ Asterisk ARI (http://localhost:8088)
) else (
    echo [ERROR] ✗ Asterisk ARI not responding
)

REM Check SIP port
netstat -an | findstr ":5060 " >nul 2>&1
if not errorlevel 1 (
    echo [SUCCESS] ✓ Asterisk SIP (port 5060)
) else (
    echo [ERROR] ✗ Asterisk SIP port not listening
)
goto end

:end
echo.
pause