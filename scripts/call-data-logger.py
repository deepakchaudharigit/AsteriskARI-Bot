#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AGI Script for Call Data Logging
This script is called by Asterisk to log call data when calls end.
"""

import sys
import os
import time
import json
import sqlite3
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def log_call_data(caller_number, extension, duration):
    """Log call data to database and file"""
    try:
        # Log to file
        log_file = project_root / "logs" / "call_data.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp} - Caller: {caller_number}, Extension: {extension}, Duration: {duration}s\n"
        
        with open(log_file, "a") as f:
            f.write(log_entry)
        
        # Log to database if available
        db_path = project_root / "data" / "npcl_customer_data.db"
        if db_path.exists():
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                
                # Insert basic call log
                cursor.execute("""
                    INSERT INTO call_logs (caller_number, extension, duration, timestamp)
                    VALUES (?, ?, ?, ?)
                """, (caller_number, extension, duration, time.time()))
                
                conn.commit()
        
        print(f"VERBOSE \"Call data logged: {caller_number} -> {extension} ({duration}s)\" 1")
        
    except Exception as e:
        print(f"VERBOSE \"Error logging call data: {e}\" 1")

def main():
    """Main AGI function"""
    try:
        # Read AGI environment
        agi_env = {}
        while True:
            line = sys.stdin.readline().strip()
            if not line:
                break
            key, value = line.split(':', 1)
            agi_env[key.strip()] = value.strip()
        
        # Get parameters from command line
        if len(sys.argv) >= 4:
            caller_number = sys.argv[1]
            extension = sys.argv[2]
            duration = sys.argv[3]
        else:
            # Fallback to AGI environment
            caller_number = agi_env.get('agi_callerid', 'unknown')
            extension = agi_env.get('agi_extension', 'unknown')
            duration = agi_env.get('agi_arg_1', '0')
        
        # Log the call data
        log_call_data(caller_number, extension, duration)
        
        # Return success
        sys.exit(0)
        
    except Exception as e:
        print(f"VERBOSE \"AGI Error: {e}\" 1")
        sys.exit(1)

if __name__ == "__main__":
    main()