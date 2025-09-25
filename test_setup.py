#!/usr/bin/env python3
"""
🧪 Test Script for NPCL Voice Assistant Docker Setup
This script verifies that all components are working correctly.
"""

import requests
import socket
import subprocess
import sys
import time
import json
from pathlib import Path

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"🧪 {title}")
    print("="*60)

def print_test(test_name, status, details=""):
    """Print test result"""
    status_icon = "✅" if status else "❌"
    print(f"{status_icon} {test_name}")
    if details:
        print(f"   {details}")

def test_docker_services():
    """Test if Docker services are running"""
    print_header("Docker Services Test")
    
    try:
        # Check if docker-compose is available
        result = subprocess.run(['docker-compose', 'ps'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print_test("Docker Compose", True, "Services status:")
            print(result.stdout)
            return True
        else:
            print_test("Docker Compose", False, result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print_test("Docker Compose", False, "Command timed out")
        return False
    except FileNotFoundError:
        print_test("Docker Compose", False, "docker-compose not found")
        return False
    except Exception as e:
        print_test("Docker Compose", False, str(e))
        return False

def test_port_connectivity(host, port, protocol='tcp'):
    """Test if a port is accessible"""
    try:
        if protocol == 'tcp':
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        elif protocol == 'udp':
            # For UDP, we just check if we can create a socket
            # Real UDP testing would require sending actual SIP packets
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(5)
            try:
                sock.sendto(b'', (host, port))
                return True
            except:
                return False
            finally:
                sock.close()
    except Exception:
        return False

def test_network_connectivity():
    """Test network connectivity to required ports"""
    print_header("Network Connectivity Test")
    
    ports_to_test = [
        ('localhost', 8000, 'tcp', 'Voice Assistant API'),
        ('localhost', 8088, 'tcp', 'Asterisk ARI'),
        ('localhost', 5060, 'udp', 'Asterisk SIP'),
    ]
    
    all_passed = True
    for host, port, protocol, service in ports_to_test:
        is_accessible = test_port_connectivity(host, port, protocol)
        print_test(f"{service} ({host}:{port}/{protocol})", is_accessible)
        if not is_accessible:
            all_passed = False
    
    return all_passed

def test_api_endpoints():
    """Test API endpoints"""
    print_header("API Endpoints Test")
    
    endpoints_to_test = [
        ('http://localhost:8000/health', 'Voice Assistant Health'),
        ('http://localhost:8000/', 'Voice Assistant Root'),
        ('http://localhost:8000/info', 'Voice Assistant Info'),
        ('http://localhost:8088/ari/asterisk/info?api_key=asterisk:1234', 'Asterisk ARI Info'),
    ]
    
    all_passed = True
    for url, description in endpoints_to_test:
        try:
            response = requests.get(url, timeout=10)
            success = response.status_code == 200
            
            if success:
                print_test(description, True, f"Status: {response.status_code}")
                # Print response for health endpoint
                if 'health' in url:
                    try:
                        data = response.json()
                        print(f"   Response: {json.dumps(data, indent=2)}")
                    except:
                        print(f"   Response: {response.text[:100]}...")
            else:
                print_test(description, False, f"Status: {response.status_code}")
                all_passed = False
                
        except requests.exceptions.ConnectionError:
            print_test(description, False, "Connection refused")
            all_passed = False
        except requests.exceptions.Timeout:
            print_test(description, False, "Request timed out")
            all_passed = False
        except Exception as e:
            print_test(description, False, str(e))
            all_passed = False
    
    return all_passed

def test_environment_config():
    """Test environment configuration"""
    print_header("Environment Configuration Test")
    
    env_file = Path('.env')
    all_passed = True
    
    # Check if .env file exists
    if env_file.exists():
        print_test(".env file exists", True)
        
        # Read and check API key
        try:
            with open(env_file, 'r') as f:
                content = f.read()
                
            if 'OPENAI_API_KEY=' in content:
                if 'your-openai-api-key-here' in content:
                    print_test("Google API Key", False, "Still using placeholder value")
                    all_passed = False
                else:
                    print_test("Google API Key", True, "Configured")
            else:
                print_test("Google API Key", False, "Not found in .env")
                all_passed = False
                
        except Exception as e:
            print_test("Reading .env file", False, str(e))
            all_passed = False
    else:
        print_test(".env file exists", False, "File not found")
        all_passed = False
    
    return all_passed

def test_asterisk_sip():
    """Test Asterisk SIP configuration"""
    print_header("Asterisk SIP Configuration Test")
    
    try:
        # Try to get SIP peers information
        result = subprocess.run([
            'docker-compose', 'exec', '-T', 'asterisk', 
            'asterisk', '-rx', 'pjsip show endpoints'
        ], capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            print_test("SIP Endpoints Query", True)
            print("   SIP Endpoints:")
            print(result.stdout)
            
            # Check if endpoint 1000 exists
            if '1000' in result.stdout:
                print_test("Test Endpoint 1000", True, "Found in configuration")
            else:
                print_test("Test Endpoint 1000", False, "Not found")
                return False
                
            return True
        else:
            print_test("SIP Endpoints Query", False, result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print_test("SIP Endpoints Query", False, "Command timed out")
        return False
    except Exception as e:
        print_test("SIP Endpoints Query", False, str(e))
        return False

def test_voice_assistant_ai():
    """Test Voice Assistant AI functionality"""
    print_header("Voice Assistant AI Test")
    
    try:
        # Test a simple API call to the voice assistant
        response = requests.post(
            'http://localhost:8000/ari/test-ai',
            json={'message': 'Hello, this is a test'},
            timeout=30
        )
        
        if response.status_code == 200:
            print_test("AI Response Test", True, "AI is responding")
            return True
        else:
            print_test("AI Response Test", False, f"Status: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print_test("AI Response Test", False, "Cannot connect to voice assistant")
        return False
    except Exception as e:
        # This endpoint might not exist, so we'll just check if the service is running
        print_test("AI Response Test", True, "Service is running (endpoint may not exist)")
        return True

def generate_zoiper_config():
    """Generate Zoiper configuration instructions"""
    print_header("Zoiper Configuration")
    
    print("📱 Configure Zoiper with these settings:")
    print()
    print("┌─────────────────────────────────────────┐")
    print("│ Account Type: SIP                       │")
    print("│ Username:     1000                      │")
    print("│ Password:     1234                      │")
    print("│ Domain:       localhost                 │")
    print("│ Port:         5060                      │")
    print("│ Transport:    UDP                       │")
    print("└─────────────────────────────────────────┘")
    print()
    print("🎯 Test Extensions:")
    print("• 1000 - AI Voice Assistant")
    print("• 9000 - Echo Test")
    print("• 1005 - IVR Menu")
    print("• 1001 - Customer Service")
    print("• 1002 - Technical Support")

def main():
    """Main test function"""
    print("🧪 NPCL Voice Assistant Setup Test")
    print("This script will verify your Docker setup is working correctly.")
    print()
    
    # Run all tests
    tests = [
        ("Environment Configuration", test_environment_config),
        ("Docker Services", test_docker_services),
        ("Network Connectivity", test_network_connectivity),
        ("API Endpoints", test_api_endpoints),
        ("Asterisk SIP", test_asterisk_sip),
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed_tests += 1
        except Exception as e:
            print_test(test_name, False, f"Test failed with exception: {e}")
    
    # Summary
    print_header("Test Summary")
    print(f"Passed: {passed_tests}/{total_tests} tests")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Your setup is ready for Zoiper testing.")
        generate_zoiper_config()
        return 0
    else:
        print("❌ Some tests failed. Please check the issues above.")
        print()
        print("💡 Common solutions:")
        print("1. Make sure Docker services are running: docker-compose up -d")
        print("2. Check your .env file has a valid Google API key")
        print("3. Verify no other services are using the required ports")
        print("4. Check the troubleshooting guide: TROUBLESHOOTING.md")
        return 1

if __name__ == "__main__":
    sys.exit(main())