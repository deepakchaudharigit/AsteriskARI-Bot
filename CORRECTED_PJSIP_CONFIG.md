# 🔧 CORRECTED PJSIP CONFIGURATION

## 📝 Replace Your Current [1000] Section With This:

```
[1000]
type=endpoint
context=demo
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
media_address=192.168.0.212
bind_rtp_to_media_address=yes
ice_support=no

[1000]
type=auth
auth_type=userpass
password=1234
username=1000

[1000]
type=aor
max_contacts=1
```

## 🎯 Key Changes Made:

1. **context=demo** (instead of openai-voice-assistant)
2. **media_address=192.168.0.212** (instead of 127.0.0.1)
3. **Removed the incorrect "FROM/TO" lines**

## 💾 What to Do:

1. **Replace your [1000] sections** with the corrected version above
2. **Save the file:** `Ctrl+X`, then `Y`, then `Enter`
3. **Reload PJSIP:** `sudo asterisk -rx 'pjsip reload'`
4. **Test with Zoiper:** Dial 1000

## ✅ Expected Result:

- ✅ **No 404 error**
- ✅ **Call connects to Asterisk demo**
- ✅ **Audio works properly**

**Copy the corrected configuration above and replace your current [1000] sections!** 🚀