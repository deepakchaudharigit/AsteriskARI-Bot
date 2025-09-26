# 🔧 Commands to Fix 404 Extension Error

## 🎯 Issue
Zoiper is getting "404 Not Found" when dialing extensions because the dialplan needs to be reloaded.

## 🚀 Run These Commands

### Step 1: Reload the Dialplan
```bash
sudo asterisk -rx 'dialplan reload'
```

### Step 2: Verify Extensions are Available
```bash
# Check if extension 1010 exists
sudo asterisk -rx 'dialplan show 1010@openai-voice-assistant'

# Check if extension 1000 exists  
sudo asterisk -rx 'dialplan show 1000@openai-voice-assistant'

# Check endpoint configuration
sudo asterisk -rx 'pjsip show endpoint 1000'
```

### Step 3: Test with Zoiper
After running the above commands:
1. **Dial 1010** - Should play demo message
2. **Dial 1000** - Should connect to voice assistant

## 🔍 Expected Output

### For `dialplan show 1010@openai-voice-assistant`:
```
[ Context 'openai-voice-assistant' created by 'pbx_config' ]
  '1010' =>            1. NoOp(Codec Test - No Stasis)
                       2. Answer()
                       3. Wait(2)
                       4. Playback(demo-congrats)
                       5. Wait(5)
                       6. Hangup()
```

### For `dialplan show 1000@openai-voice-assistant`:
```
[ Context 'openai-voice-assistant' created by 'pbx_config' ]
  '1000' =>            1. NoOp(NPCL Telephonic Bot - Main Line)
                       2. Set(CHANNEL(hangup_handler_push)=hangup-handler,s,1)
                       3. Answer()
                       4. Set(TALK_DETECT(set)=4,160)
                       5. Wait(1)
                       6. Playback(/home/ameen/AsteriskARI-Bot/sounds/welcome)
                       7. Wait(1)
                       8. Stasis(openai-voice-assistant,${CALLERID(num)},${EXTEN})
                       9. Hangup()
```

## ✅ Success Indicators

After reloading:
- ✅ **No 404 errors** when dialing
- ✅ **Extension 1010 works** (plays demo message)
- ✅ **Extension 1000 works** (connects to voice assistant)
- ✅ **Zoiper shows call progress** instead of immediate disconnection

## 🚨 If Still Getting 404

If you still get 404 after reloading, try this alternative:

### Change PJSIP Context to Default
```bash
# Edit the PJSIP config to use 'default' context instead
sudo nano /etc/asterisk/pjsip.conf

# Find the [1000] endpoint section and change:
# context=openai-voice-assistant
# to:
# context=default

# Then reload PJSIP
sudo asterisk -rx 'pjsip reload'
```

## 🎯 What I Fixed

1. ✅ **Ensured all extensions are in the same context** (`openai-voice-assistant`)
2. ✅ **Fixed PJSIP dial syntax** (changed `SIP/` to `PJSIP/`)
3. ✅ **Added test extensions** (1010, 9000) to the correct context
4. ✅ **Updated extensions.conf** with proper structure

**Run the reload command above and test with Zoiper!** 🚀