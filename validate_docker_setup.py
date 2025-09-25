#!/usr/bin/env python3
"""
Quick validation script to check if Docker setup is ready for Zoiper testing
"""

import subprocess
import sys
import time

def run_command(cmd, timeout=10):
    """Run a command and return success status"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def check_docker():
    """Check if Docker is running"""
    print("🐳 Checking Docker...")
    success, stdout, stderr = run_command("docker --version")
    if not success:
        print("❌ Docker not found. Please install Docker.")
        return False
    
    success, stdout, stderr = run_command("docker info")
    if not success:
        print("❌ Docker not running. Please start Docker.")
        return False
    
    print("✅ Docker is running")
    return True

def check_compose():
    """Check if docker-compose is available"""
    print("🔧 Checking Docker Compose...")
    success, stdout, stderr = run_command("docker-compose --version")
    if not success:
        success, stdout, stderr = run_command("docker compose version")
        if not success:
            print("❌ Docker Compose not found.")
            return False
    
    print("✅ Docker Compose is available")
    return True

def check_env_file():
    """Check if .env file exists and has API key"""
    print("⚙️ Checking environment configuration...")
    try:
        with open('.env', 'r') as f:
            content = f.read()
        
        if 'your-openai-api-key-here' in content:
            print("❌ Google API key not configured in .env file")
            print("   Please edit .env and add your Google API key")
            return False
        
        if 'OPENAI_API_KEY=' not in content:
            print("❌ OPENAI_API_KEY not found in .env file")
            return False
        
        print("✅ Environment configuration looks good")
        return True
        
    except FileNotFoundError:
        print("❌ .env file not found. Please copy .env.example to .env")
        return False

def check_services():
    """Check if services are running"""
    print("🚀 Checking Docker services...")
    success, stdout, stderr = run_command("docker-compose ps")
    if not success:
        print("❌ Cannot check service status")
        return False
    
    # Check for the actual service names in our docker-compose.yml
    required_services = ["npcl-asterisk-20", "npcl-voice-assistant", "npcl-redis"]
    running_services = []
    
    for service in required_services:
        if service in stdout and "Up" in stdout:
            running_services.append(service)
    
    if len(running_services) >= 2:  # At least Asterisk and one other service
        print(f"✅ Docker services are running ({len(running_services)}/{len(required_services)} services up)")
        if len(running_services) < len(required_services):
            print(f"   Note: Some services may still be starting up")
        return True
    else:
        print("❌ Services not running. Try: docker-compose up -d")
        print(f"   Found {len(running_services)} of {len(required_services)} required services")
        return False

def check_ports():
    """Check if required ports are accessible"""
    print("🌐 Checking port accessibility...")
    
    import socket
    
    ports = [
        (8000, "Voice Assistant API"),
        (8088, "Asterisk ARI"),
        (5060, "Asterisk SIP")
    ]
    
    all_good = True
    for port, service in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        if result == 0:
            print(f"✅ {service} (port {port}) is accessible")
        else:
            print(f"❌ {service} (port {port}) is not accessible")
            all_good = False
    
    return all_good

def main():
    """Main validation function"""
    print("🧪 NPCL Voice Assistant - Docker Setup Validation")
    print("=" * 50)
    
    checks = [
        ("Docker Installation", check_docker),
        ("Docker Compose", check_compose),
        ("Environment File", check_env_file),
        ("Docker Services", check_services),
        ("Port Accessibility", check_ports),
    ]
    
    passed = 0
    total = len(checks)
    
    for name, check_func in checks:
        print(f"\n{name}:")
        if check_func():
            passed += 1
        else:
            print(f"   Fix this issue before proceeding")
    
    print("\n" + "=" * 50)
    print(f"Validation Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 All checks passed! Your setup is ready for Zoiper testing.")
        print("\n📱 Zoiper Configuration:")
        print("   Username: 1000")
        print("   Password: 1234")
        print("   Domain: localhost")
        print("   Port: 5060")
        print("   Transport: UDP")
        print("\n🎯 Test by dialing: 1000 (AI Assistant) or 9000 (Echo Test)")
        return 0
    else:
        print(f"\n❌ {total - passed} issues need to be fixed.")
        print("\n💡 Quick fixes:")
        if passed < 2:
            print("   1. Install and start Docker")
        if passed < 3:
            print("   2. Copy .env.example to .env and add your OPENAI API key")
        if passed < 4:
            print("   3. Run: docker-compose up -d")
        if passed < 5:
            print("   4. Check firewall settings and port conflicts")
        return 1

if __name__ == "__main__":
    sys.exit(main())