#!/usr/bin/env python3
"""
Quick system test to verify everything is working
"""
import requests
import subprocess
import sys
import time
from pathlib import Path

def test_docker():
    """Test if Docker containers are running"""
    print("🐳 Testing Docker containers...")
    try:
        result = subprocess.run(["docker", "ps", "--filter", "name=asterisk"], 
                              capture_output=True, text=True)
        if "asterisk" in result.stdout:
            print("✅ Asterisk container is running")
            return True
        else:
            print("❌ Asterisk container not found")
            return False
    except Exception as e:
        print(f"❌ Docker test failed: {e}")
        return False

def test_ari_connection():
    """Test ARI connection"""
    print("🔌 Testing ARI connection...")
    try:
        response = requests.get(
            "http://localhost:8088/ari/asterisk/info",
            auth=("asterisk", "1234"),
            timeout=5
        )
        if response.status_code == 200:
            print("✅ ARI connection successful")
            return True
        else:
            print(f"❌ ARI connection failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ ARI connection failed: {e}")
        return False

def test_voice_server():
    """Test if voice assistant server is running"""
    print("🤖 Testing Voice Assistant server...")
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ Voice Assistant server is running")
            return True
        else:
            print(f"❌ Voice Assistant server error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Voice Assistant server not running: {e}")
        return False

def test_environment():
    """Test environment configuration"""
    print("⚙️ Testing environment...")
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file, 'r') as f:
            content = f.read()
            if "OPENAI_API_KEY=" in content and len(content.split("OPENAI_API_KEY=")[1].split("\n")[0]) > 10:
                print("✅ Google API key is configured")
                return True
            else:
                print("❌ Google API key not properly configured")
                return False
    else:
        print("❌ .env file not found")
        return False

def main():
    print("🧪 NPCL Voice Assistant System Test")
    print("=" * 50)
    
    tests = [
        ("Environment", test_environment),
        ("Docker", test_docker),
        ("ARI Connection", test_ari_connection),
        ("Voice Server", test_voice_server)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
        print()
    
    print("📊 Test Results Summary:")
    print("-" * 30)
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:15} {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! System is ready for Zoiper testing.")
        print("\n📞 Next steps:")
        print("1. Configure Zoiper 5 with: Username=1000, Password=1234, Domain=localhost")
        print("2. Dial 1000 to test the NPCL AI Assistant")
        print("3. You should hear: 'Welcome to NPCL...'")
    else:
        print("⚠️ Some tests failed. Please fix the issues before testing with Zoiper.")
        print("\n🔧 Common fixes:")
        print("- Start Docker: docker-compose up asterisk -d")
        print("- Start Voice Server: python src/run_realtime_server.py")
        print("- Check .env file for valid OPENAI_API_KEY")

if __name__ == "__main__":
    main()