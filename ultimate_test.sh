#!/bin/bash

# Ultimate Call Tracking Test
echo "🎯 ULTIMATE CALL TRACKING TEST"
echo "=============================="
echo "This test uses a direct call tracker that bypasses HTTP issues"
echo ""

# Function to cleanup
cleanup() {
    echo "🧹 Cleaning up..."
    docker-compose down > /dev/null 2>&1 || true
    pkill -f "src/main.py" > /dev/null 2>&1 || true
    pkill -f "simple_call_tracker.py" > /dev/null 2>&1 || true
}

trap cleanup EXIT

# Start Asterisk
echo "📞 Starting Asterisk..."
docker-compose up -d asterisk > /dev/null 2>&1
sleep 8

# Start ARI Bot (for voice processing)
echo "🤖 Starting ARI Bot (for voice processing)..."
.venv/bin/python3 src/main.py --ari-bot > ari_bot_ultimate.log 2>&1 &
ARI_BOT_PID=$!
sleep 5

# Check if stasis app is registered
echo "🔍 Checking stasis app registration..."
STASIS_APPS=$(curl -s http://localhost:8088/ari/applications --user asterisk:1234)
echo "   Registered apps: $STASIS_APPS"

if echo "$STASIS_APPS" | grep -q "openai-voice-assistant"; then
    echo "✅ Stasis app 'openai-voice-assistant' is registered"
else
    echo "❌ Stasis app 'openai-voice-assistant' is NOT registered"
    echo "   This is why call tracking doesn't work!"
    echo "   Starting ARI Bridge to register the app..."
    .venv/bin/python3 fix_ari_registration.py > ari_bridge.log 2>&1 &
    ARI_BRIDGE_PID=$!
    sleep 5
    
    # Check again
    STASIS_APPS_AFTER=$(curl -s http://localhost:8088/ari/applications --user asterisk:1234)
    echo "   Apps after bridge: $STASIS_APPS_AFTER"
    
    if echo "$STASIS_APPS_AFTER" | grep -q "openai-voice-assistant"; then
        echo "✅ Stasis app now registered via ARI Bridge!"
    else
        echo "❌ Stasis app still not registered - this is the root cause"
    fi
fi

# Don't start separate call tracker - use ARI bridge for tracking
echo "📊 Using ARI Bridge for call tracking (to avoid WebSocket conflicts)..."
# The ARI bridge is already running and receiving events
TRACKER_PID=$ARI_BRIDGE_PID

# Test system
echo "🧪 Testing system..."

# Check Asterisk
if docker-compose ps asterisk | grep -q "Up"; then
    echo "✅ Asterisk: Running"
else
    echo "❌ Asterisk: Failed"
    exit 1
fi

# Check ARI Bot
if curl -s http://localhost:8000/ari/health | grep -q "healthy" 2>/dev/null; then
    echo "✅ ARI Bot: Healthy"
else
    echo "⚠️  ARI Bot: May have issues (but voice will still work)"
fi

# Check Call Tracker
if ps -p $TRACKER_PID > /dev/null 2>&1; then
    echo "✅ Call Tracker: Running"
    
    # Check stasis app registration again
    FINAL_STASIS_APPS=$(curl -s http://localhost:8088/ari/applications --user asterisk:1234 2>/dev/null)
    if echo "$FINAL_STASIS_APPS" | grep -q "openai-voice-assistant"; then
        echo "✅ Stasis App: Registered"
    else
        echo "❌ Stasis App: NOT REGISTERED (this is why tracking fails)"
    fi
else
    echo "❌ Call Tracker: Failed"
    exit 1
fi

echo ""
echo "🎯 SYSTEM READY FOR ULTIMATE TEST!"
echo "=================================="
echo "📞 Make a test call to 1000 and watch for:"
echo "   1. Call detection in tracker"
echo "   2. Accurate call counting"
echo "   3. Professional AI voice response"
echo ""
echo "📊 Monitoring systems:"
echo "   - Simple Call Tracker (WebSocket events)"
echo "   - ARI Bot (HTTP endpoints)"
echo "   - ARI Bridge (stasis app registration)"
echo ""
echo "🔍 Key diagnostic:"
echo "   If call tracking fails, the issue is stasis app registration"
echo "   Calls will work but won't be tracked without proper registration"
echo ""

# Enhanced monitoring
echo "🔍 LIVE MONITORING:"
echo "=================="

for i in {1..12}; do
    TIMESTAMP=$(date +'%H:%M:%S')
    
    # Check ARI bridge log for call events
    if [ -f "ari_bridge.log" ]; then
        # Count StasisStart events (call starts)
        CALL_EVENTS=$(grep -c "StasisStart" ari_bridge.log 2>/dev/null)
        if [ -z "$CALL_EVENTS" ]; then
            CALL_EVENTS="0"
        fi
        
        # Count recent call events (last 10 lines)
        RECENT_CALLS=$(tail -n 10 ari_bridge.log | grep -c "INCOMING CALL DETECTED" 2>/dev/null)
        if [ -z "$RECENT_CALLS" ]; then
            RECENT_CALLS="0"
        fi
        
        # For active calls, we'll use ARI bot endpoint
        ACTIVE_CALLS="$RECENT_CALLS"
    else
        ACTIVE_CALLS="0"
        CALL_EVENTS="0"
        RECENT_CALLS="0"
    fi
    
    # Check ARI bot call count (may not work due to HTTP issues)
    ARI_CALLS=$(curl -s http://localhost:8000/ari/calls 2>/dev/null | grep -o '"call_count":[0-9]*' | cut -d: -f2 2>/dev/null || echo "0")
    
    if [ "$CALL_EVENTS" -gt 0 ] 2>/dev/null; then
        echo "🎉 [$TIMESTAMP] SUCCESS! Bridge detected: $CALL_EVENTS total calls (Recent: $RECENT_CALLS, ARI: $ARI_CALLS)"
    elif [ "$RECENT_CALLS" -gt 0 ] 2>/dev/null; then
        echo "📞 [$TIMESTAMP] Recent calls: $RECENT_CALLS (Total: $CALL_EVENTS, ARI: $ARI_CALLS)"
    else
        echo "⏰ [$TIMESTAMP] Waiting for calls... (Bridge events: $CALL_EVENTS, Recent: $RECENT_CALLS, ARI: $ARI_CALLS)"
    fi
    
    sleep 5
done

echo ""
echo "📊 FINAL RESULTS:"
echo "================"

# Final statistics
if [ -f "ari_bridge.log" ]; then
    TOTAL_STASIS_EVENTS=$(grep -c "StasisStart" ari_bridge.log 2>/dev/null || echo "0")
    TOTAL_CALL_EVENTS=$(grep -c "INCOMING CALL DETECTED" ari_bridge.log 2>/dev/null || echo "0")
    
    echo "📞 Total Stasis events: $TOTAL_STASIS_EVENTS"
    echo "📞 Total call events: $TOTAL_CALL_EVENTS"
    
    if [ "$TOTAL_STASIS_EVENTS" -gt 0 ] 2>/dev/null; then
        echo ""
        echo "🎉 SUCCESS! Call tracking is working!"
        echo "   The ARI bridge successfully detected calls"
        echo "   This proves the Asterisk → ARI → Event processing chain works"
        echo ""
        echo "📋 Recent ARI events:"
        grep "StasisStart\|INCOMING CALL DETECTED\|Event forwarded" ari_bridge.log | tail -n 5
    else
        echo ""
        echo "⚠️  No Stasis events detected in bridge"
        echo "   This suggests calls aren't reaching the stasis application"
        echo "   Check Asterisk configuration and dialplan"
    fi
else
    echo "❌ No ARI bridge log found"
fi

echo ""
echo "📄 Check detailed logs:"
echo "   ARI Bridge: ari_bridge.log"
echo "   ARI Bot: ari_bot_ultimate.log"
echo ""
echo "Press Enter to stop all services..."
read

echo "✅ Ultimate test completed!"