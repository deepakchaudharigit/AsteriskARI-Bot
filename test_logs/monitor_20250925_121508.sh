#!/bin/bash
LOG_FILE="$1"
echo "Starting system monitoring..." >> "$LOG_FILE"

while true; do
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Check Asterisk status
    if docker ps | grep -q "npcl-asterisk-20"; then
        ASTERISK_STATUS="Docker Running"
    elif pgrep asterisk > /dev/null; then
        ASTERISK_STATUS="Linux Running"
    else
        ASTERISK_STATUS="Not Running"
    fi
    
    # Check Voice Assistant status
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        VA_STATUS="Running"
    else
        VA_STATUS="Not Running"
    fi
    
    # Check active calls
    ACTIVE_CALLS=$(curl -s http://localhost:8000/ari/calls 2>/dev/null | jq '.call_count // 0' 2>/dev/null || echo "0")
    
    # Log status
    echo "[$TIMESTAMP] Asterisk: $ASTERISK_STATUS | Voice Assistant: $VA_STATUS | Active Calls: $ACTIVE_CALLS" >> "$LOG_FILE"
    
    sleep 10
done
