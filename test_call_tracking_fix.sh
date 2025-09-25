#!/bin/bash

# Test Call Tracking Fix
echo "🔧 TESTING CALL TRACKING FIX"
echo "============================"

# Function to cleanup
cleanup() {
    echo "🧹 Cleaning up..."
    docker-compose down > /dev/null 2>&1 || true
    pkill -f "src/main.py" > /dev/null 2>&1 || true
    pkill -f "fix_ari_registration.py" > /dev/null 2>&1 || true
}

trap cleanup EXIT

# Start services
echo "📞 Starting Asterisk..."
docker-compose up -d asterisk > /dev/null 2>&1
sleep 8

echo "🤖 Starting ARI Bot (with fix)..."
.venv/bin/python3 src/main.py --ari-bot > ari_bot_fixed.log 2>&1 &
ARI_BOT_PID=$!
sleep 5

echo "🌉 Starting ARI Bridge..."
.venv/bin/python3 fix_ari_registration.py > ari_bridge_fixed.log 2>&1 &
ARI_BRIDGE_PID=$!
sleep 5

# Test the fix
echo "🧪 Testing endpoints..."

# Test health
if curl -s http://localhost:8000/ari/health | grep -q "healthy"; then
    echo "✅ Health endpoint: OK"
else
    echo "❌ Health endpoint: Failed"
    exit 1
fi

# Test calls endpoint
if curl -s http://localhost:8000/ari/calls | grep -q "call_count"; then
    echo "✅ Calls endpoint: OK"
else
    echo "❌ Calls endpoint: Failed"
    exit 1
fi

# Test events endpoint (the fix)
echo "🔧 Testing events endpoint..."
if curl -s -X POST http://localhost:8000/ari/events \
   -H "Content-Type: application/json" \
   -d '{"type":"test","timestamp":"2024-01-01T00:00:00Z"}' | grep -q "status"; then
    echo "✅ Events endpoint: WORKING!"
else
    echo "❌ Events endpoint: Still failing"
fi

# Show current call count
CALL_COUNT=$(curl -s http://localhost:8000/ari/calls | grep -o '"call_count":[0-9]*' | cut -d: -f2)
echo "📊 Current call count: $CALL_COUNT"

echo ""
echo "🎯 CALL TRACKING TEST READY!"
echo "============================"
echo "📞 Make a test call to 1000 and watch for:"
echo "   - Call events in ARI bridge log"
echo "   - Active call count increase"
echo "   - Proper call tracking"
echo ""
echo "📊 Monitor with: curl http://localhost:8000/ari/calls"
echo "📄 Check logs: tail -f ari_bridge_fixed.log"
echo ""

# Monitor for 30 seconds
for i in {1..6}; do
    TIMESTAMP=$(date +'%H:%M:%S')
    CALL_COUNT=$(curl -s http://localhost:8000/ari/calls 2>/dev/null | grep -o '"call_count":[0-9]*' | cut -d: -f2 2>/dev/null || echo "0")
    
    if [ "$CALL_COUNT" -gt 0 ]; then
        echo "🎉 [$TIMESTAMP] SUCCESS! Active calls: $CALL_COUNT"
    else
        echo "⏰ [$TIMESTAMP] Waiting for calls... (count: $CALL_COUNT)"
    fi
    
    sleep 5
done

echo ""
echo "📄 Check the logs for detailed information:"
echo "   ARI Bot: ari_bot_fixed.log"
echo "   ARI Bridge: ari_bridge_fixed.log"
echo ""
echo "Press Enter to stop services..."
read

echo "✅ Test completed!"