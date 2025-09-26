# 🚀 MANUAL FIX: Add Working Extensions

## 🎯 Problem Analysis

From the dialplan output, I can see:
- ✅ `default` context exists and includes `demo` context
- ✅ Extension `1000` exists in `demo` context but goes to `default,s,1`
- ❌ We need to override extension `1000` to connect to our voice assistant
- ❌ We need to add extension `1010` for testing

## 🔧 SOLUTION: Add Extensions to Demo Context

### Step 1: Edit Extensions Configuration

```bash
sudo nano /etc/asterisk/extensions.conf
```

**Scroll to the bottom of the file and add these lines:**

```
; NPCL Voice Assistant Extensions
[demo]
; Override existing 1000 extension
exten => 1000,1,NoOp(NPCL Voice Assistant)
same => n,Answer()
same => n,Wait(1)
same => n,Playback(demo-congrats)
same => n,Wait(2)
same => n,Stasis(openai-voice-assistant,${CALLERID(num)},${EXTEN})
same => n,Hangup()

; Add test extension
exten => 1010,1,NoOp(NPCL Test Extension)
same => n,Answer()
same => n,Wait(1)
same => n,Playback(demo-congrats)
same => n,Wait(3)
same => n,Hangup()

; Add echo test
exten => 9000,1,NoOp(Echo Test)
same => n,Answer()
same => n,Echo()
same => n,Hangup()
```

**Save with:** `Ctrl+X`, then `Y`, then `Enter`

### Step 2: Change PJSIP Context

```bash
sudo nano /etc/asterisk/pjsip.conf
```

**Find the `[1000]` endpoint section and change:**
```
FROM: context=openai-voice-assistant
TO:   context=demo
```

**Save with:** `Ctrl+X`, then `Y`, then `Enter`

### Step 3: Reload Configuration

```bash
# Reload dialplan
sudo asterisk -rx 'dialplan reload'

# Reload PJSIP
sudo asterisk -rx 'pjsip reload'
```

### Step 4: Verify Extensions

```bash
# Check if our extensions are now available
sudo asterisk -rx 'dialplan show 1000@demo'
sudo asterisk -rx 'dialplan show 1010@demo'
sudo asterisk -rx 'dialplan show 9000@demo'
```

## 🧪 TEST WITH ZOIPER

After completing the above steps:

1. **Dial 1010** - Should play demo message and stay connected
2. **Dial 1000** - Should play demo message then connect to voice assistant
3. **Dial 9000** - Should start echo test

## ✅ Expected Results

- ✅ **No 404 errors**
- ✅ **Extension 1010 works** (plays demo, stays connected)
- ✅ **Extension 1000 works** (plays demo, connects to AI)
- ✅ **Voice conversation with AI assistant**

## 🔍 Monitor Progress

```bash
# Watch ARI bot activity
tail -f logs/ari_bot_final.log

# Watch Asterisk logs
sudo tail -f /var/log/asterisk/messages
```

## 🎯 Why This Works

1. **Uses existing `demo` context** - No need to create new contexts
2. **Overrides extension 1000** - Replaces the existing one that just goes to demo
3. **Adds test extensions** - 1010 for simple testing, 9000 for echo
4. **Uses correct PJSIP context** - Changes from non-existent `openai-voice-assistant` to working `demo`

## 🚨 Alternative Quick Test

If you want to test immediately without editing files:

```bash
# Change PJSIP context to demo (this alone might work)
sudo asterisk -rx 'pjsip set endpoint 1000 context demo'

# Then try dialing 1000 - it should connect to the existing demo
```

**This should immediately fix the 404 error and get calls working!** 🚀