#!/usr/bin/env python3
"""
Test script to monitor NPCL Voice Assistant call flow and demonstrate functionality
"""

import asyncio
import json
import time
import requests
from datetime import datetime

def print_banner():
    """Print test banner"""
    print("\n" + "=" * 80)
    print("🧪 NPCL VOICE ASSISTANT - CALL MONITORING TEST")
    print("=" * 80)
    print("📞 This script will help you verify your voice assistant is working")
    print("🔍 Monitor the terminal running the voice assistant for detailed logs")
    print("=" * 80)

def check_services():
    """Check if all services are running"""
    print("\n🔍 CHECKING SERVICES...")
    
    services = {
        "Voice Assistant": "http://localhost:8000/ari/health",
        "Asterisk ARI": "http://localhost:8088/ari/asterisk/info",
        "Voice Assistant Status": "http://localhost:8000/ari/status"
    }
    
    for service_name, url in services.items():
        try:
            if "asterisk" in url:
                response = requests.get(url, auth=("asterisk", "1234"), timeout=5)
            else:
                response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                print(f"✅ {service_name}: HEALTHY")
                if service_name == "Voice Assistant Status":
                    data = response.json()
                    print(f"   📊 Active calls: {data.get('active_calls', 0)}")
                    print(f"   🏃 Running: {data.get('is_running', False)}")
            else:
                print(f"⚠️  {service_name}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {service_name}: ERROR - {e}")

def monitor_calls():
    """Monitor active calls"""
    print("\n📞 MONITORING CALLS...")
    
    try:
        response = requests.get("http://localhost:8000/ari/calls", timeout=5)
        if response.status_code == 200:
            data = response.json()
            active_calls = data.get('active_calls', [])
            call_count = data.get('call_count', 0)
            
            print(f"📊 Active calls: {call_count}")
            if active_calls:
                for call_id in active_calls:
                    print(f"   📞 Call ID: {call_id}")
                    
                    # Get detailed call info
                    try:
                        call_response = requests.get(f"http://localhost:8000/ari/calls/{call_id}", timeout=5)
                        if call_response.status_code == 200:
                            call_data = call_response.json()
                            print(f"      📋 Details: {json.dumps(call_data, indent=6)}")
                    except Exception as e:
                        print(f"      ❌ Error getting call details: {e}")
            else:
                print("   📭 No active calls")
        else:
            print(f"❌ Failed to get calls: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Error monitoring calls: {e}")

def show_test_instructions():
    """Show test instructions"""
    print("\n🧪 HOW TO TEST YOUR VOICE ASSISTANT:")
    print("=" * 60)
    print("1️⃣  SETUP ZOIPER (or any SIP client):")
    print("   📱 Server: localhost:5060")
    print("   👤 Username: 1001")
    print("   🔐 Password: 1001")
    print("   📞 Domain: localhost")
    
    print("\n2️⃣  MAKE A TEST CALL:")
    print("   📞 Dial: 1000")
    print("   🎤 Speak clearly when connected")
    print("   👂 Listen for AI responses")
    
    print("\n3️⃣  WHAT TO EXPECT IN TERMINAL:")
    print("   📞 INCOMING CALL: [channel_id]")
    print("   📱 From: 1001")
    print("   📞 To: 1000")
    print("   ✅ CALL ANSWERED: [channel_id]")
    print("   🌐 EXTERNAL MEDIA STARTED: [channel_id]")
    print("   🎤 USER SPEAKING...")
    print("   🔇 USER STOPPED SPEAKING - Processing...")
    print("   🤖 AI RESPONSE: [response text]")
    print("   🔊 AUDIO RECEIVED: [bytes] from [channel_id]")
    print("   📴 CALL ENDING: [channel_id]")
    
    print("\n4️⃣  CONVERSATION FLOW:")
    print("   🎤 You speak → AI processes → 🔊 AI responds")
    print("   🔄 Continues until you hang up")
    
    print("\n5️⃣  TROUBLESHOOTING:")
    print("   🔍 Check terminal logs for detailed flow")
    print("   📊 Monitor this script for call status")
    print("   🌐 Verify all services are healthy above")

async def continuous_monitoring():
    """Continuously monitor the system"""
    print("\n🔄 STARTING CONTINUOUS MONITORING...")
    print("   Press Ctrl+C to stop")
    
    try:
        while True:
            print(f"\n⏰ {datetime.now().strftime('%H:%M:%S')} - Checking system...")
            
            # Quick health check
            try:
                response = requests.get("http://localhost:8000/ari/health", timeout=3)
                if response.status_code == 200:
                    print("✅ Voice Assistant: Healthy")
                else:
                    print(f"⚠️  Voice Assistant: HTTP {response.status_code}")
            except:
                print("❌ Voice Assistant: Not responding")
            
            # Check for active calls
            try:
                response = requests.get("http://localhost:8000/ari/calls", timeout=3)
                if response.status_code == 200:
                    data = response.json()
                    call_count = data.get('call_count', 0)
                    if call_count > 0:
                        print(f"📞 Active calls: {call_count}")
                        active_calls = data.get('active_calls', [])
                        for call_id in active_calls:
                            print(f"   🔗 {call_id}")
                    else:
                        print("📭 No active calls")
            except:
                print("❌ Cannot check calls")
            
            await asyncio.sleep(10)  # Check every 10 seconds
            
    except KeyboardInterrupt:
        print("\n👋 Monitoring stopped")

def main():
    """Main function"""
    print_banner()
    check_services()
    monitor_calls()
    show_test_instructions()
    
    print("\n🤔 What would you like to do?")
    print("1. 🔄 Start continuous monitoring")
    print("2. 🔍 Check services again")
    print("3. 📞 Check calls again")
    print("4. ❌ Exit")
    
    try:
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            asyncio.run(continuous_monitoring())
        elif choice == "2":
            check_services()
        elif choice == "3":
            monitor_calls()
        elif choice == "4":
            print("👋 Goodbye!")
        else:
            print("❌ Invalid choice")
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()