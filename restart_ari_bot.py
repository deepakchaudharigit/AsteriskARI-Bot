#!/usr/bin/env python3
"""
Restart ARI Bot - Fix OpenAI Session Expired Issue
"""

import subprocess
import time
import signal
import os

def run_command(command, timeout=10):
    """Run a command and return output"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "", "Command timed out", 1
    except Exception as e:
        return "", str(e), 1

def stop_ari_bot():
    """Stop the current ARI bot process"""
    print("🛑 Stopping current ARI bot...")
    
    # Find ARI bot processes
    stdout, stderr, returncode = run_command("ps aux | grep 'ari_bot.py' | grep -v grep")
    if returncode == 0 and stdout:
        lines = stdout.split('\n')
        for line in lines:
            if 'ari_bot.py' in line:
                parts = line.split()
                if len(parts) > 1:
                    pid = parts[1]
                    print(f"   Stopping ARI bot process (PID {pid})")
                    try:
                        os.kill(int(pid), signal.SIGTERM)
                        time.sleep(2)
                        # Force kill if still running
                        try:
                            os.kill(int(pid), signal.SIGKILL)
                        except ProcessLookupError:
                            pass  # Process already terminated
                    except ProcessLookupError:
                        print(f"   Process {pid} already terminated")
                    except Exception as e:
                        print(f"   Error stopping process {pid}: {e}")
    
    print("✅ ARI bot stopped")

def start_ari_bot():
    """Start the ARI bot with fresh OpenAI session"""
    print("\n🚀 Starting ARI bot with fresh OpenAI session...")
    
    # Start ARI bot in background
    command = "nohup python3 ari_bot.py > logs/ari_bot_fresh.log 2>&1 &"
    stdout, stderr, returncode = run_command(command)
    
    if returncode == 0:
        print("✅ ARI bot started in background")
        print("   Logs: tail -f logs/ari_bot_fresh.log")
        return True
    else:
        print(f"❌ Failed to start ARI bot: {stderr}")
        return False

def wait_for_openai_connection():
    """Wait for OpenAI connection to be established"""
    print("\n⏳ Waiting for OpenAI connection...")
    
    max_attempts = 15
    for attempt in range(max_attempts):
        time.sleep(2)
        
        # Check logs for OpenAI connection
        stdout, stderr, returncode = run_command("tail -10 logs/ari_bot_fresh.log")
        if returncode == 0:
            if "ready for conversation" in stdout or "OpenAI Real-time session updated" in stdout:
                print("✅ OpenAI connection established!")
                return True
            elif "error" in stdout.lower() or "failed" in stdout.lower():
                print("❌ Error in ARI bot startup:")
                print(stdout)
                return False
        
        print(f"   Attempt {attempt + 1}/{max_attempts}...")
    
    print("⚠️  OpenAI connection timeout - check logs")
    return False

def verify_ari_bot_status():
    """Verify ARI bot is running and connected"""
    print("\n🔍 Verifying ARI bot status...")
    
    # Check if process is running
    stdout, stderr, returncode = run_command("ps aux | grep 'ari_bot.py' | grep -v grep")
    if returncode == 0 and stdout:
        print("✅ ARI bot process is running")
    else:
        print("❌ ARI bot process not found")
        return False
    
    # Check recent logs
    stdout, stderr, returncode = run_command("tail -5 logs/ari_bot_fresh.log")
    if returncode == 0:
        if "ready for conversation" in stdout:
            print("✅ ARI bot is ready for calls")
            return True
        elif "error" in stdout.lower():
            print("❌ ARI bot has errors:")
            print(stdout)
            return False
    
    print("⚠️  ARI bot status unclear - check logs")
    return False

def provide_testing_instructions():
    """Provide testing instructions"""
    print("\n" + "=" * 60)
    print("🎯 READY FOR TESTING")
    print("=" * 60)
    
    print("\n📞 Test with Zoiper:")
    print("1. Dial 1010 - Simple test (should work)")
    print("2. Dial 1000 - Voice assistant (should connect to AI)")
    
    print("\n🔍 Monitor Commands:")
    print("# Watch fresh ARI bot logs")
    print("tail -f logs/ari_bot_fresh.log")
    print()
    print("# Watch Asterisk logs")
    print("sudo tail -f /var/log/asterisk/messages")
    
    print("\n✅ Expected Results:")
    print("- Extension 1010: Plays demo, stays connected")
    print("- Extension 1000: Plays demo → AI conversation")
    print("- No session expired errors")
    print("- Fresh OpenAI session working")

def main():
    """Main function"""
    print("🔧 RESTART ARI BOT - Fix OpenAI Session Expired")
    print("=" * 60)
    print("Issue: OpenAI session expired (60-minute limit)")
    print("Solution: Restart ARI bot with fresh session")
    print()
    
    # Step 1: Stop current ARI bot
    stop_ari_bot()
    
    # Step 2: Start fresh ARI bot
    if start_ari_bot():
        # Step 3: Wait for OpenAI connection
        if wait_for_openai_connection():
            # Step 4: Verify status
            if verify_ari_bot_status():
                print("\n🎉 SUCCESS! ARI bot restarted with fresh OpenAI session")
            else:
                print("\n⚠️  ARI bot started but status unclear")
        else:
            print("\n❌ OpenAI connection failed")
    else:
        print("\n❌ Failed to start ARI bot")
        return 1
    
    # Step 5: Provide testing instructions
    provide_testing_instructions()
    
    print("\n" + "=" * 60)
    print("🎯 SUMMARY")
    print("=" * 60)
    print("✅ ARI bot restarted with fresh OpenAI session")
    print("✅ Ready for voice assistant testing")
    print("📞 Test with Zoiper: Dial 1000")
    print("=" * 60)
    
    return 0

if __name__ == "__main__":
    exit(main())