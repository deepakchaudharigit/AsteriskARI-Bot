#!/bin/bash

# Final Call Tracking Fix Test
echo "🎯 FINAL CALL TRACKING FIX TEST"
echo "==============================="

# Function to cleanup
cleanup() {
    echo "🧹 Cleaning up..."
    docker-compose down > /dev/null 2>&1 || true
    pkill -f "src/main.py" > /dev/null 2>&1 || true
    pkill -f "fix_ari_registration.py" > /dev/null 2>&1 || true
}

trap cleanup EXIT

# Start services with the fix
echo "📞 Starting Asterisk..."
docker-compose up -d asterisk > /dev/null 2>&1
sleep 8

echo "🤖 Starting ARI Bot (with FINAL fix)..."
.venv/bin/python3 src/main.py --ari-bot > ari_bot_final.log 2>&1 &
ARI_BOT_PID=$!
sleep 5

echo "🌉 Starting ARI Bridge..."
.venv/bin/python3 fix_ari_registration.py > ari_bridge_final.log 2>&1 &
ARI_BRIDGE_PID=$!
sleep 5

# Test all endpoints
echo "🧪 Testing all endpoints..."

# Test health
if curl -s http://localhost:8000/ari/health | grep -q "healthy"; then
    echo "✅ Health endpoint: OK"
else
    echo "❌ Health endpoint: Failed"
    exit 1
fi

# Test calls
if curl -s http://localhost:8000/ari/calls | grep -q "call_count"; then
    echo "✅ Calls endpoint: OK"
else
    echo "❌ Calls endpoint: Failed"
    exit 1
fi

# Test status
if curl -s http://localhost:8000/ari/status | grep -q "is_running"; then
    echo "✅ Status endpoint: OK"
else
    echo "❌ Status endpoint: Failed"
    exit 1
fi

# Test events endpoint (THE CRITICAL FIX)
echo "🔧 Testing events endpoint (the critical fix)..."
EVENTS_RESPONSE=$(curl -s -X POST http://localhost:8000/ari/events \
   -H "Content-Type: application/json" \
   -d '{"type":"test","timestamp":"2024-01-01T00:00:00Z","channel":{"id":"test-123"}}')

if echo "$EVENTS_RESPONSE" | grep -q "status"; then
    echo "✅ Events endpoint: WORKING! 🎉"
    echo "   Response: $EVENTS_RESPONSE"
else
    echo "❌ Events endpoint: Still failing"
    echo "   Response: $EVENTS_RESPONSE"
    exit 1
fi

# Check OpenAPI spec
echo "📚 Checking OpenAPI spec..."
if curl -s http://localhost:8000/openapi.json | grep -q "ari/events"; then
    echo "✅ Events endpoint in OpenAPI: YES"
else
    echo "⚠️  Events endpoint in OpenAPI: Not listed (but working)"
fi

# Show initial call count
CALL_COUNT=$(curl -s http://localhost:8000/ari/calls | grep -o '"call_count":[0-9]*' | cut -d: -f2)
echo "📊 Initial call count: $CALL_COUNT"

echo ""
echo "🎯 CALL TRACKING TEST - READY FOR LIVE TEST!"
echo "============================================="
echo "📞 Make a test call to 1000 and watch for:"
echo "   1. Call events forwarded successfully"
echo "   2. Active call count increases to 1"
echo "   3. Call tracking works properly"
echo ""
echo "📊 Monitor: curl http://localhost:8000/ari/calls"
echo "📄 Logs: tail -f ari_bridge_final.log"
echo ""

# Enhanced monitoring with better detection
echo "🔍 ENHANCED MONITORING (30 seconds):"
echo "===================================="

for i in {1..6}; do
    TIMESTAMP=$(date +'%H:%M:%S')
    
    # Get call count
    CALL_COUNT=$(curl -s http://localhost:8000/ari/calls 2>/dev/null | grep -o '"call_count":[0-9]*' | cut -d: -f2 2>/dev/null || echo "0")
    
    # Check for events in bridge log
    if [ -f "ari_bridge_final.log" ]; then
        RECENT_EVENTS=$(tail -n 10 ari_bridge_final.log | grep -c "INCOMING CALL DETECTED" || echo "0")
        FORWARDED_EVENTS=$(tail -n 10 ari_bridge_final.log | grep -c "Event forwarded successfully" || echo "0")
    else
        RECENT_EVENTS=0
        FORWARDED_EVENTS=0
    fi
    
    if [ "$CALL_COUNT" -gt 0 ]; then
        echo "🎉 [$TIMESTAMP] SUCCESS! Active calls: $CALL_COUNT (Events: $RECENT_EVENTS, Forwarded: $FORWARDED_EVENTS)"
    elif [ "$FORWARDED_EVENTS" -gt 0 ]; then
        echo "🔄 [$TIMESTAMP] Events forwarding: $FORWARDED_EVENTS (Calls: $CALL_COUNT)"
    elif [ "$RECENT_EVENTS" -gt 0 ]; then
        echo "📨 [$TIMESTAMP] Events detected: $RECENT_EVENTS (Calls: $CALL_COUNT)"
    else
        echo "⏰ [$TIMESTAMP] Waiting... (Calls: $CALL_COUNT, Events: $RECENT_EVENTS)"
    fi
    
    sleep 5
done

echo ""
echo "📊 FINAL STATUS:"
echo "==============="

# Final call count
FINAL_CALL_COUNT=$(curl -s http://localhost:8000/ari/calls | grep -o '"call_count":[0-9]*' | cut -d: -f2)
echo "📞 Final call count: $FINAL_CALL_COUNT"

# Check logs for success indicators
if [ -f "ari_bridge_final.log" ]; then
    TOTAL_EVENTS=$(grep -c "INCOMING CALL DETECTED" ari_bridge_final.log || echo "0")
    TOTAL_FORWARDED=$(grep -c "Event forwarded successfully" ari_bridge_final.log || echo "0")
    echo "📨 Total events detected: $TOTAL_EVENTS"
    echo "✅ Total events forwarded: $TOTAL_FORWARDED"
    
    if [ "$TOTAL_FORWARDED" -gt 0 ]; then
        echo ""
        echo "🎉 SUCCESS! Call tracking is now working!"
        echo "   Events are being forwarded to ARI bot"
        echo "   Call counting should now be accurate"
    fi
fi

echo ""
echo "📄 Check detailed logs:"
echo "   ARI Bot: ari_bot_final.log"
echo "   ARI Bridge: ari_bridge_final.log"
echo ""
echo "Press Enter to stop services..."
read

echo "✅ Final test completed!"