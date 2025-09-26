#!/usr/bin/env python3
import subprocess
import sys

def check_asterisk_users():
    """Check what SIP users are configured in Asterisk"""
    print("🔍 Checking Asterisk SIP configuration...")
    
    commands = [
        ("SIP Users", "sudo asterisk -rx 'sip show users'"),
        ("SIP Peers", "sudo asterisk -rx 'sip show peers'"),
        ("PJSIP Endpoints", "sudo asterisk -rx 'pjsip show endpoints'")
    ]
    
    for name, cmd in commands:
        print(f"\n📋 {name}:")
        print("-" * 40)
        try:
            result = subprocess.run(cmd.split(), capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                output = result.stdout.strip()
                if output:
                    print(output)
                else:
                    print("No output")
            else:
                print(f"Error: {result.stderr}")
        except subprocess.TimeoutExpired:
            print("Command timed out")
        except Exception as e:
            print(f"Error running command: {e}")

if __name__ == "__main__":
    check_asterisk_users()
