# 🔧 EXACT PJSIP EDIT INSTRUCTIONS

## 🎯 What You Need to Change

In the `[1000]` endpoint section, you need to change this line:

```
FROM: context=openai-voice-assistant
TO:   context=demo
```

## 📝 EXACT EDIT

**Find this section:**
```
[1000]
type=endpoint
context=openai-voice-assistant    ← CHANGE THIS LINE
disallow=all
allow=ulaw
allow=alaw
auth=1000
aors=1000
; NAT-friendly settings for Zoiper
rtp_symmetric=yes
force_rport=yes
rewrite_contact=yes
direct_media=no
; Media settings for proper codec negotiation
media_address=127.0.0.1
bind_rtp_to_media_address=yes
ice_support=no
```

**Change it to:**
```
[1000]
type=endpoint
context=demo                      ← CHANGED TO demo
disallow=all
allow=ulaw
allow=alaw
auth=1000
aors=1000
; NAT-friendly settings for Zoiper
rtp_symmetric=yes
force_rport=yes
rewrite_contact=yes
direct_media=no
; Media settings for proper codec negotiation
media_address=127.0.0.1
bind_rtp_to_media_address=yes
ice_support=no
```

## 🔧 Also Fix Media Address

While you're editing, also change:
```
FROM: media_address=127.0.0.1
TO:   media_address=192.168.0.212
```

## 💾 Save and Apply

1. **Save the file:** `Ctrl+X`, then `Y`, then `Enter`
2. **Reload PJSIP:** `sudo asterisk -rx 'pjsip reload'`
3. **Test with Zoiper:** Dial 1000

## ✅ Expected Result

After making these changes:
- ✅ **No more 404 errors**
- ✅ **Extension 1000 connects to demo**
- ✅ **You'll hear the Asterisk demo menu**

This proves the connection is working, then we can add the voice assistant extensions!

## 🎯 Summary of Changes

1. **context=openai-voice-assistant** → **context=demo**
2. **media_address=127.0.0.1** → **media_address=192.168.0.212**

**Make these two changes, save, reload PJSIP, and test!** 🚀