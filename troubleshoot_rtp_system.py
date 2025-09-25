#!/usr/bin/env python3
"""
Troubleshooting script for the RTP-based NPCL Voice Assistant system.
Checks all components and provides diagnostic information.
"""

import requests
import socket
import subprocess
import json
import sys
from typing import Dict, Any, List


def check_port(host: str, port: int, timeout: int = 5) -> bool:
    """Check if a port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False


def check_docker_containers() -> Dict[str, Any]:
    """Check Docker container status"""
    try:
        result = subprocess.run(
            ["docker-compose", "ps", "--format", "json"],
            capture_output=True,
            text=True,
            check=True
        )
        containers = []
        for line in result.stdout.strip().split('\n'):
            if line:
                containers.append(json.loads(line))
        return {"status": "success", "containers": containers}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def check_asterisk_ari() -> Dict[str, Any]:
    """Check Asterisk ARI connectivity"""
    try:
        response = requests.get(
            "http://localhost:8088/ari/asterisk/info",
            auth=("asterisk", "1234"),
            timeout=5
        )
        response.raise_for_status()
        return {"status": "success", "data": response.json()}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def check_voice_assistant() -> Dict[str, Any]:
    """Check Voice Assistant health"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        response.raise_for_status()
        return {"status": "success", "data": response.json()}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def check_voice_assistant_status() -> Dict[str, Any]:
    """Check Voice Assistant detailed status"""
    try:
        response = requests.get("http://localhost:8000/status", timeout=5)
        response.raise_for_status()
        return {"status": "success", "data": response.json()}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def check_network_connectivity() -> Dict[str, List[Dict[str, Any]]]:
    """Check network connectivity for key ports"""
    ports_to_check = [
        ("localhost", 5060, "Asterisk SIP"),
        ("localhost", 8088, "Asterisk ARI"),
        ("localhost", 8000, "Voice Assistant API"),
        ("localhost", 10000, "RTP Start Port"),
        ("localhost", 10100, "RTP End Port"),
        ("localhost", 20000, "Voice Assistant RTP Start"),
        ("localhost", 20100, "Voice Assistant RTP End"),
    ]
    
    results = []
    for host, port, description in ports_to_check:
        is_open = check_port(host, port)
        results.append({
            "host": host,
            "port": port,
            "description": description,
            "status": "open" if is_open else "closed"
        })
    
    return {"ports": results}


def print_section(title: str):
    """Print a section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def print_status(check_name: str, result: Dict[str, Any]):
    """Print check status"""
    status = result.get("status", "unknown")
    if status == "success":
        print(f"✓ {check_name}: OK")
        if "data" in result:
            data = result["data"]
            if isinstance(data, dict):
                for key, value in data.items():
                    if key in ["service", "status", "is_running", "version"]:
                        print(f"  - {key}: {value}")
    else:
        print(f"✗ {check_name}: FAILED")
        print(f"  Error: {result.get('message', 'Unknown error')}")


def main():
    """Main troubleshooting function"""
    print("🔍 NPCL Voice Assistant - RTP System Troubleshooting")
    print("This script will check all system components and connectivity.")
    
    # Check Docker containers
    print_section("Docker Containers")
    docker_result = check_docker_containers()
    if docker_result["status"] == "success":
        print("✓ Docker Compose: OK")
        for container in docker_result["containers"]:
            name = container.get("Name", "Unknown")
            state = container.get("State", "Unknown")
            status = container.get("Status", "Unknown")
            print(f"  - {name}: {state} ({status})")
    else:
        print(f"✗ Docker Compose: FAILED")
        print(f"  Error: {docker_result.get('message', 'Unknown error')}")
    
    # Check network connectivity
    print_section("Network Connectivity")
    network_result = check_network_connectivity()
    for port_check in network_result["ports"]:
        status_icon = "✓" if port_check["status"] == "open" else "✗"
        print(f"{status_icon} {port_check['description']}: {port_check['host']}:{port_check['port']} ({port_check['status']})")
    
    # Check Asterisk ARI
    print_section("Asterisk ARI")
    asterisk_result = check_asterisk_ari()
    print_status("Asterisk ARI", asterisk_result)
    
    # Check Voice Assistant
    print_section("Voice Assistant")
    va_health_result = check_voice_assistant()
    print_status("Voice Assistant Health", va_health_result)
    
    va_status_result = check_voice_assistant_status()
    if va_status_result["status"] == "success":
        print("✓ Voice Assistant Status: OK")
        data = va_status_result["data"]
        print(f"  - Running: {data.get('is_running', 'Unknown')}")
        print(f"  - Active Calls: {data.get('active_calls', 'Unknown')}")
        print(f"  - RTP Streams: {len(data.get('rtp_streams', {}))}")
        print(f"  - Bridges: {data.get('bridges', 'Unknown')}")
        
        openai_status = data.get('openai_status', {})
        if isinstance(openai_status, dict):
            print(f"  - OpenAI Connected: {openai_status.get('is_connected', 'Unknown')}")
    else:
        print_status("Voice Assistant Status", va_status_result)
    
    # Summary and recommendations
    print_section("Summary and Recommendations")
    
    all_checks = [docker_result, asterisk_result, va_health_result, va_status_result]
    failed_checks = [check for check in all_checks if check.get("status") != "success"]
    
    if not failed_checks:
        print("🎉 All systems are operational!")
        print("\nNext steps:")
        print("1. Configure Zoiper with: localhost:5060, user: 1000, pass: 1234")
        print("2. Call extension 1000 to test the voice assistant")
        print("3. Monitor logs: docker-compose logs -f")
    else:
        print(f"⚠️  {len(failed_checks)} issue(s) detected.")
        print("\nTroubleshooting steps:")
        
        if docker_result.get("status") != "success":
            print("1. Check Docker installation and docker-compose.yml")
            print("   - Run: docker-compose down && docker-compose up -d")
        
        if asterisk_result.get("status") != "success":
            print("2. Check Asterisk container and configuration")
            print("   - Run: docker-compose logs asterisk")
            print("   - Verify asterisk-config/ files")
        
        if va_health_result.get("status") != "success":
            print("3. Check Voice Assistant container")
            print("   - Run: docker-compose logs voice-assistant")
            print("   - Verify .env file has valid OPENAI_API_KEY")
        
        print("\nFor detailed logs:")
        print("  docker-compose logs asterisk")
        print("  docker-compose logs voice-assistant")
    
    print(f"\n{'='*60}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Troubleshooting interrupted by user")
    except Exception as e:
        print(f"\n❌ Troubleshooting error: {e}")
        sys.exit(1)