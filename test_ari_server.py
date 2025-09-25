#!/usr/bin/env python3
"""
Test NPCL ARI Server endpoints
"""

import requests
import time
import sys

def test_endpoint(url, name):
    """Test a server endpoint"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"✅ {name}: OK ({response.status_code})")
            return True
        else:
            print(f"⚠️  {name}: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ {name}: Connection failed")
        return False
    except Exception as e:
        print(f"❌ {name}: {e}")
        return False

def main():
    """Test all ARI server endpoints"""
    print("🧪 Testing NPCL ARI Server Endpoints")
    print("=" * 40)
    
    base_url = "http://localhost:8000"
    
    endpoints = [
        (f"{base_url}/ari/health", "Health Check"),
        (f"{base_url}/ari/status", "ARI Status"),
        (f"{base_url}/status", "Server Status"),
        (f"{base_url}/ari/calls", "Call Status"),
        (f"{base_url}/docs", "API Documentation")
    ]
    
    print("🔍 Testing endpoints...")
    print()
    
    success_count = 0
    for url, name in endpoints:
        if test_endpoint(url, name):
            success_count += 1
        time.sleep(0.5)  # Small delay between tests
    
    print()
    print("=" * 40)
    print(f"📊 Test Results: {success_count}/{len(endpoints)} endpoints working")
    
    if success_count == len(endpoints):
        print("🎉 All endpoints are working!")
        print("📞 ARI server is ready for Asterisk calls")
    elif success_count > 0:
        print("⚠️  Some endpoints are working")
        print("🔄 Server may still be starting up")
    else:
        print("❌ No endpoints responding")
        print("💡 Make sure the server is running:")
        print("   ./start_ari_server.sh")
    
    return success_count == len(endpoints)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)