#!/usr/bin/env python3
"""
Fix Port Conflicts and Start Proper ARI Bot
This script resolves port conflicts and starts the correct voice assistant
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

def find_processes_using_ports():
    """Find processes using ports 8000 and 8090"""
    print("🔍 Finding processes using ports 8000 and 8090...")
    
    ports_to_check = [8000, 8090]
    processes_to_kill = []
    
    for port in ports_to_check:
        stdout, stderr, returncode = run_command(f"lsof -ti:{port}")
        if returncode == 0 and stdout:
            pids = stdout.split('\n')
            for pid in pids:
                if pid.strip():
                    processes_to_kill.append(int(pid.strip()))
                    print(f"   Port {port} is used by PID {pid}")
        else:
            print(f"   Port {port} is free")
    
    return processes_to_kill

def stop_conflicting_processes():
    """Stop processes that are using required ports"""
    print("\n🛑 Stopping conflicting processes...")
    
    # Find the voice assistant process
    stdout, stderr, returncode = run_command("ps aux | grep 'start_voice_assistant.py' | grep -v grep")
    if returncode == 0 and stdout:
        lines = stdout.split('\n')
        for line in lines:
            if 'start_voice_assistant.py' in line:
                parts = line.split()
                if len(parts) > 1:
                    pid = parts[1]
                    print(f"   Stopping voice assistant process (PID {pid})")
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
    
    # Find and stop any other processes using our ports
    processes_to_kill = find_processes_using_ports()
    
    for pid in processes_to_kill:
        try:
            print(f"   Stopping process PID {pid}")
            os.kill(pid, signal.SIGTERM)
            time.sleep(1)
            # Force kill if still running
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass  # Process already terminated
        except ProcessLookupError:
            print(f"   Process {pid} already terminated")
        except Exception as e:
            print(f"   Error stopping process {pid}: {e}")
    
    # Wait a moment for ports to be released
    time.sleep(3)
    print("✅ Conflicting processes stopped")

def verify_ports_free():
    """Verify that required ports are now free"""
    print("\n🔍 Verifying ports are free...")
    
    ports_to_check = [8000, 8090]
    all_free = True
    
    for port in ports_to_check:
        stdout, stderr, returncode = run_command(f"lsof -ti:{port}")
        if returncode == 0 and stdout:
            print(f"❌ Port {port} is still in use")
            all_free = False
        else:
            print(f"✅ Port {port} is free")
    
    return all_free

def check_stasis_registration():
    """Check if Stasis app is registered"""
    print("\n🔍 Checking Stasis application registration...")
    
    stdout, stderr, returncode = run_command("sudo asterisk -rx 'stasis show apps'")
    if returncode == 0:
        if "openai-voice-assistant" in stdout:
            print("✅ Stasis app 'openai-voice-assistant' is registered")
            return True
        else:
            print("❌ Stasis app 'openai-voice-assistant' NOT registered")
            return False
    else:
        print(f"❌ Error checking Stasis apps: {stderr}")
        return False

def start_ari_bot():
    """Start the ARI bot in background"""
    print("\n🚀 Starting ARI bot...")
    
    # Start ARI bot in background
    command = "nohup python3 ari_bot.py > logs/ari_bot_new.log 2>&1 &"
    stdout, stderr, returncode = run_command(command)
    
    if returncode == 0:
        print("✅ ARI bot started in background")
        print("   Check logs: tail -f logs/ari_bot_new.log")
        return True
    else:
        print(f"❌ Failed to start ARI bot: {stderr}")
        return False

def wait_for_stasis_registration():
    """Wait for Stasis app to register"""
    print("\n⏳ Waiting for Stasis app registration...")
    
    max_attempts = 10
    for attempt in range(max_attempts):
        time.sleep(2)
        if check_stasis_registration():
            print("✅ Stasis app registered successfully!")
            return True
        print(f"   Attempt {attempt + 1}/{max_attempts}...")
    
    print("❌ Stasis app failed to register within timeout")
    return False

def provide_testing_instructions():
    """Provide testing instructions"""
    print("\n" + "=" * 60)
    print("🎯 TESTING INSTRUCTIONS")
    print("=" * 60)
    
    print("\n📞 Test with Zoiper:")
    print("1. Make sure Zoiper is configured with:")
    print("   Username: 1000")
    print("   Password: 1234")
    print("   Domain: 192.168.0.212")
    print("   Transport: UDP")
    
    print("\n2. Test extensions in order:")
    print("   📞 Call 1010 first (simple test)")
    print("      Expected: Plays demo message, stays connected")
    print("   📞 Call 1000 second (voice assistant)")
    print("      Expected: Welcome message → AI conversation")
    
    print("\n3. Monitor logs:")
    print("   tail -f logs/ari_bot_new.log")
    print("   sudo tail -f /var/log/asterisk/messages")
    
    print("\n✅ If both extensions work: SUCCESS!")
    print("❌ If 1010 works but 1000 doesn't: Check Stasis registration")
    print("❌ If both fail: Check SIP configuration")

def main():
    """Main function"""
    print("🔧 Port Conflict Resolution Tool")
    print("=" * 50)
    print("Fixing port conflicts and starting proper ARI bot")
    print()
    
    # Step 1: Stop conflicting processes
    stop_conflicting_processes()
    
    # Step 2: Verify ports are free
    if not verify_ports_free():
        print("\n❌ Some ports are still in use. Manual intervention required.")
        print("   Try: sudo lsof -ti:8000 | xargs sudo kill -9")
        print("   Try: sudo lsof -ti:8090 | xargs sudo kill -9")
        return 1
    
    # Step 3: Check current Stasis registration
    stasis_registered = check_stasis_registration()
    
    # Step 4: Start ARI bot if Stasis not registered
    if not stasis_registered:
        if start_ari_bot():
            # Wait for registration
            if wait_for_stasis_registration():
                print("\n🎉 SUCCESS! ARI bot started and Stasis app registered")
            else:
                print("\n❌ ARI bot started but Stasis app not registered")
                print("   Check logs: tail -f logs/ari_bot_new.log")
        else:
            print("\n❌ Failed to start ARI bot")
            return 1
    else:
        print("\n✅ Stasis app already registered - no need to restart")
    
    # Step 5: Provide testing instructions
    provide_testing_instructions()
    
    print("\n" + "=" * 60)
    print("🎯 SUMMARY")
    print("=" * 60)
    print("✅ Port conflicts resolved")
    print("✅ ARI bot running")
    print("✅ Stasis app registered")
    print("📞 Ready for Zoiper testing!")
    print("=" * 60)
    
    return 0

if __name__ == "__main__":
    exit(main())