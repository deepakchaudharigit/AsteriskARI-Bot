#!/usr/bin/env python3
"""
Restart ARI Bot Properly to Register Stasis Application
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
    """Stop any running ARI bot processes"""
    print("🛑 Stopping any running ARI bot processes...")
    
    # Find and stop ARI bot processes
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
    
    # Also stop any python processes running the bot
    stdout, stderr, returncode = run_command("pkill -f 'python.*ari_bot'")
    
    print("✅ ARI bot processes stopped")
    time.sleep(3)  # Wait for cleanup

def check_ari_connectivity():
    """Check ARI connectivity before starting bot"""
    print("\n🔍 Checking ARI connectivity...")
    
    # Test ARI authentication
    stdout, stderr, returncode = run_command("curl -s http://localhost:8088/ari/asterisk/info -u asterisk:1234")
    if returncode == 0:
        if "{" in stdout:  # JSON response
            print("✅ ARI authentication working")
            return True
        else:
            print(f"❌ ARI authentication failed: {stdout}")
            return False
    else:
        print(f"❌ ARI connection failed: {stderr}")
        return False

def start_ari_bot_foreground():
    """Start ARI bot in foreground for monitoring"""
    print("\n🚀 Starting ARI bot in foreground...")
    print("📋 Monitor the output for:")
    print("   - 'Connected to OpenAI Real-time API successfully'")
    print("   - 'Enhanced Real-time ARI Handler started successfully'")
    print("   - 'ready for conversation'")
    print()
    print("🔍 After you see 'ready for conversation', check Stasis registration:")
    print("   sudo asterisk -rx 'ari show apps'")
    print()
    print("📞 Then test with Zoiper: dial 1000")
    print()
    print("🚀 Starting ARI bot now...")
    print("=" * 60)
    
    # Start ARI bot in foreground so user can monitor
    os.system("python3 ari_bot.py")

def provide_monitoring_instructions():
    """Provide monitoring instructions"""
    print("\n" + "=" * 60)
    print("🔍 MONITORING INSTRUCTIONS")
    print("=" * 60)
    
    print("\n📋 Watch for these messages in ARI bot output:")
    print("1. ✅ 'OpenAI Real-time API connected'")
    print("2. ✅ 'Enhanced Real-time ARI Handler started successfully'")
    print("3. ✅ 'ready for conversation'")
    
    print("\n🧪 After seeing 'ready for conversation':")
    print("1. Open new terminal")
    print("2. Check Stasis registration:")
    print("   sudo asterisk -rx 'ari show apps'")
    print("3. Should show: openai-voice-assistant")
    
    print("\n📞 Test Voice Assistant:")
    print("1. Dial 1000 in Zoiper")
    print("2. Should hear welcome message")
    print("3. Should transfer to AI (no disconnection)")
    print("4. Voice conversation should begin")
    
    print("\n🔍 Monitor Logs During Call:")
    print("# In another terminal:")
    print("tail -f logs/ari_bot_final.log")
    print("# Look for: 'Stasis application started'")

def main():
    """Main function"""
    print("🔧 RESTART ARI BOT PROPERLY")
    print("=" * 50)
    print("Goal: Register Stasis application with Asterisk")
    print()
    
    # Step 1: Stop any running ARI bot
    stop_ari_bot()
    
    # Step 2: Check ARI connectivity
    if not check_ari_connectivity():
        print("\n❌ ARI connectivity issue - fix this first")
        return 1
    
    # Step 3: Provide monitoring instructions
    provide_monitoring_instructions()
    
    # Step 4: Start ARI bot in foreground
    start_ari_bot_foreground()
    
    return 0

if __name__ == "__main__":
    exit(main())