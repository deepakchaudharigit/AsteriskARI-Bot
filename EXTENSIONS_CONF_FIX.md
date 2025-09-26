# 🔧 EXTENSIONS.CONF FIX

## 🎯 Issue
Your PJSIP endpoint 1000 is configured to use `context=demo`, but you're adding extensions to the `[default]` context.

## 📝 SOLUTION: Add [demo] Context

Add this section to your extensions.conf file:

```
[general]
static=yes
writeprotect=no

[default]
exten => s,1,Answer()
same => n,Playback(demo-congrats)
same => n,Hangup()

exten => 1010,1,Answer()
same => n,Playback(demo-congrats)
same => n,Wait(3)
same => n,Hangup()

exten => 1000,1,Answer()
same => n,Playback(demo-congrats)
same => n,Wait(2)
same => n,Stasis(openai-voice-assistant)
same => n,Hangup()

exten => _X.,1,Answer()
same => n,Playback(demo-congrats)
same => n,Hangup()

[demo]
exten => 1000,1,NoOp(NPCL Voice Assistant)
same => n,Answer()
same => n,Wait(1)
same => n,Playback(demo-congrats)
same => n,Wait(2)
same => n,Stasis(openai-voice-assistant,${CALLERID(num)},${EXTEN})
same => n,Hangup()

exten => 1010,1,NoOp(NPCL Test Extension)
same => n,Answer()
same => n,Wait(1)
same => n,Playback(demo-congrats)
same => n,Wait(3)
same => n,Hangup()

exten => 9000,1,NoOp(Echo Test)
same => n,Answer()
same => n,Echo()
same => n,Hangup()

exten => _X.,1,Answer()
same => n,Playback(demo-congrats)
same => n,Hangup()
```

## 💾 Steps:
1. **Add the [demo] section** at the bottom
2. **Save:** Ctrl+X, Y, Enter
3. **Reload:** `sudo asterisk -rx 'dialplan reload'`
4. **Test:** Dial 1000

## ✅ Expected Result:
Extension 1000 will connect to your voice assistant!

**Add the [demo] section above to your file!** 🚀