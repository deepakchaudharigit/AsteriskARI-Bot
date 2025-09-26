
# 🚀 QUICK TEST: Register Stasis Application

## Option 1: Test WebSocket Connection (Recommended)

1. **Run the WebSocket client:**
   ```bash
   python3 ari_websocket_client.py
   ```

2. **Check Stasis registration:**
   ```bash
   sudo asterisk -rx 'ari show apps'
   ```
   Should show: openai-voice-assistant

3. **Test with Zoiper:**
   Dial 1000 - should now transfer to AI

## Option 2: Quick Manual Test

1. **Test WebSocket connection manually:**
   ```bash
   # Install wscat if not available
   npm install -g wscat
   
   # Connect to ARI WebSocket
   wscat -c "ws://localhost:8088/ari/events?app=openai-voice-assistant" -H "Authorization: Basic YXN0ZXJpc2s6MTIzNA=="
   ```

2. **Check registration:**
   ```bash
   sudo asterisk -rx 'ari show apps'
   ```

## Expected Results

✅ **WebSocket connects successfully**
✅ **Stasis app appears in 'ari show apps'**
✅ **Extension 1000 transfers to AI**
✅ **Voice conversation works**

## Why This Fixes It

Your ARI bot was missing the WebSocket subscription to Asterisk's ARI events endpoint. Without this subscription:
- Asterisk doesn't know about your Stasis application
- Calls to Stasis() fail and disconnect
- No ARI events reach your bot

The WebSocket connection with `?app=openai-voice-assistant` parameter registers your Stasis application with Asterisk.
