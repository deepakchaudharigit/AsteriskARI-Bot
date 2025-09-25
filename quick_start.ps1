# NPCL Voice Assistant - Quick Start Script for PowerShell
# Comprehensive startup script for different deployment modes

param(
    [Parameter(Position=0)]
    [ValidateSet("docker", "asterisk", "test", "status", "help")]
    [string]$Mode = "docker"
)

function Show-Usage {
    Write-Host ""
    Write-Host "NPCL Voice Assistant - Quick Start" -ForegroundColor Green
    Write-Host "=================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Usage: .\quick_start.ps1 [mode]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Available modes:" -ForegroundColor Cyan
    Write-Host "  docker    - Start with Docker containers (default)" -ForegroundColor White
    Write-Host "  asterisk  - Start only Asterisk container" -ForegroundColor White
    Write-Host "  test      - Run integration tests" -ForegroundColor White
    Write-Host "  status    - Check system status" -ForegroundColor White
    Write-Host "  help      - Show this help message" -ForegroundColor White
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Cyan
    Write-Host "  .\quick_start.ps1 docker    # Start full Docker setup" -ForegroundColor Gray
    Write-Host "  .\quick_start.ps1 asterisk  # Start only Asterisk" -ForegroundColor Gray
    Write-Host "  .\quick_start.ps1 test      # Run tests" -ForegroundColor Gray
}

function Start-DockerMode {
    Write-Host ""
    Write-Host "🐳 Starting Docker Mode" -ForegroundColor Green
    Write-Host "======================" -ForegroundColor Green
    Write-Host ""

    # Check Docker
    try {
        $dockerVersion = docker --version
        Write-Host "✅ Docker found: $dockerVersion" -ForegroundColor Green
    } catch {
        Write-Host "❌ Docker is not installed. Please install Docker Desktop first." -ForegroundColor Red
        Write-Host "Visit: https://docs.docker.com/desktop/windows/" -ForegroundColor Yellow
        return
    }

    # Check if Docker is running
    try {
        docker info | Out-Null
        Write-Host "✅ Docker is running" -ForegroundColor Green
    } catch {
        Write-Host "❌ Docker is not running. Please start Docker Desktop." -ForegroundColor Red
        return
    }

    # Stop existing containers
    Write-Host "🛑 Stopping existing containers..." -ForegroundColor Yellow
    docker-compose down 2>$null

    # Start services
    Write-Host "🚀 Starting Docker services..." -ForegroundColor Yellow
    $result = docker-compose up -d --build
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to start Docker services" -ForegroundColor Red
        return
    }

    # Wait for services
    Write-Host "⏳ Waiting for services to start..." -ForegroundColor Yellow
    Start-Sleep -Seconds 30

    # Show status
    Write-Host ""
    Write-Host "📊 Service Status:" -ForegroundColor Cyan
    docker-compose ps

    Write-Host ""
    Write-Host "🌐 Available Endpoints:" -ForegroundColor Green
    Write-Host "  • Voice Assistant: http://localhost:8000" -ForegroundColor White
    Write-Host "  • API Documentation: http://localhost:8000/docs" -ForegroundColor White
    Write-Host "  • System Status: http://localhost:8000/ari/status" -ForegroundColor White
    Write-Host "  • Asterisk ARI: http://localhost:8088/ari" -ForegroundColor White

    Write-Host ""
    Write-Host "📞 SIP Configuration for Zoiper:" -ForegroundColor Green
    Write-Host "  ┌─────────────────────────────────────────┐" -ForegroundColor Cyan
    Write-Host "  │ Username: 1001                          │" -ForegroundColor White
    Write-Host "  │ Password: 1234                          │" -ForegroundColor White
    Write-Host "  │ Server:   localhost:5060                │" -ForegroundColor White
    Write-Host "  │ Protocol: UDP                           │" -ForegroundColor White
    Write-Host "  └─────────────────────────────────────────┘" -ForegroundColor Cyan

    Write-Host ""
    Write-Host "🎯 Test Extensions:" -ForegroundColor Green
    Write-Host "  • Dial 1000 - AI Voice Assistant" -ForegroundColor White
    Write-Host "  • Dial 9000 - Echo Test" -ForegroundColor White
    Write-Host "  • Dial 1005 - IVR Menu" -ForegroundColor White

    Write-Host ""
    Write-Host "🛠️ Useful Commands:" -ForegroundColor Green
    Write-Host "  • View logs: docker-compose logs -f" -ForegroundColor Gray
    Write-Host "  • Restart: docker-compose restart" -ForegroundColor Gray
    Write-Host "  • Stop: docker-compose down" -ForegroundColor Gray
}

function Start-AsteriskOnly {
    Write-Host ""
    Write-Host "📞 Starting Asterisk Only" -ForegroundColor Green
    Write-Host "========================" -ForegroundColor Green
    Write-Host ""

    # Stop existing containers
    docker-compose down 2>$null

    # Start only Asterisk
    Write-Host "🚀 Starting Asterisk container..." -ForegroundColor Yellow
    $result = docker-compose up -d asterisk
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to start Asterisk container" -ForegroundColor Red
        return
    }

    # Wait for startup
    Write-Host "⏳ Waiting for Asterisk to start..." -ForegroundColor Yellow
    Start-Sleep -Seconds 20

    # Show status
    Write-Host ""
    Write-Host "📊 Asterisk Status:" -ForegroundColor Cyan
    docker ps --filter name=asterisk

    # Get IP for Zoiper configuration
    $ipAddresses = Get-NetIPAddress -AddressFamily IPv4 | Where-Object { 
        $_.IPAddress -ne "127.0.0.1" -and 
        $_.IPAddress -notlike "169.254.*" -and 
        $_.InterfaceAlias -notlike "*Loopback*"
    }
    $primaryIP = $ipAddresses[0].IPAddress

    Write-Host ""
    Write-Host "✅ Asterisk is ready!" -ForegroundColor Green
    Write-Host "📞 SIP Server: localhost:5060 (or $primaryIP:5060)" -ForegroundColor White
    Write-Host "🔧 ARI Interface: http://localhost:8088/ari" -ForegroundColor White

    Write-Host ""
    Write-Host "💡 For local development, you can now run:" -ForegroundColor Yellow
    Write-Host "   python src\run_realtime_server.py" -ForegroundColor Gray
}

function Run-Tests {
    Write-Host ""
    Write-Host "🧪 Running Integration Tests" -ForegroundColor Green
    Write-Host "============================" -ForegroundColor Green
    Write-Host ""

    # Check if Python is available
    try {
        $pythonVersion = python --version
        Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
    } catch {
        Write-Host "❌ Python is not installed or not in PATH" -ForegroundColor Red
        return
    }

    # Run tests
    Write-Host "🔍 Running OpenAI integration tests..." -ForegroundColor Yellow
    try {
        python test_openai_integration.py
        Write-Host "✅ Integration tests completed" -ForegroundColor Green
    } catch {
        Write-Host "⚠️ Some tests failed" -ForegroundColor Yellow
    }

    Write-Host ""
    Write-Host "🔍 Running system status check..." -ForegroundColor Yellow
    try {
        python check_system_status.py
        Write-Host "✅ Status check completed" -ForegroundColor Green
    } catch {
        Write-Host "⚠️ Status check failed" -ForegroundColor Yellow
    }
}

function Check-Status {
    Write-Host ""
    Write-Host "🔍 Checking System Status" -ForegroundColor Green
    Write-Host "=========================" -ForegroundColor Green
    Write-Host ""

    # Check Docker containers
    Write-Host "📊 Container Status:" -ForegroundColor Cyan
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

    Write-Host ""
    Write-Host "🏥 Service Health Checks:" -ForegroundColor Cyan

    # Check Voice Assistant
    try {
        Invoke-RestMethod -Uri "http://localhost:8000/ari/health" -TimeoutSec 5 | Out-Null
        Write-Host "✅ Voice Assistant (http://localhost:8000)" -ForegroundColor Green
    } catch {
        Write-Host "❌ Voice Assistant not responding" -ForegroundColor Red
    }

    # Check Asterisk ARI
    try {
        $headers = @{Authorization = "Basic " + [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("asterisk:1234"))}
        Invoke-RestMethod -Uri "http://localhost:8088/ari/asterisk/info" -Headers $headers -TimeoutSec 5 | Out-Null
        Write-Host "✅ Asterisk ARI (http://localhost:8088)" -ForegroundColor Green
    } catch {
        Write-Host "❌ Asterisk ARI not responding" -ForegroundColor Red
    }

    # Check SIP port
    $sipPort = Get-NetTCPConnection -LocalPort 5060 -ErrorAction SilentlyContinue
    if ($sipPort) {
        Write-Host "✅ Asterisk SIP (port 5060)" -ForegroundColor Green
    } else {
        Write-Host "❌ Asterisk SIP port not listening" -ForegroundColor Red
    }
}

# Main script logic
switch ($Mode) {
    "docker" { Start-DockerMode }
    "asterisk" { Start-AsteriskOnly }
    "test" { Run-Tests }
    "status" { Check-Status }
    "help" { Show-Usage }
    default { 
        Write-Host "❌ Unknown mode: $Mode" -ForegroundColor Red
        Show-Usage 
    }
}

Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")