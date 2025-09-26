# 🚀 QUICK FIX: Context Not Found Error

## 🎯 Problem
The `openai-voice-assistant` context doesn't exist, causing 404 errors.

## 🔧 IMMEDIATE SOLUTION

### Option 1: Change PJSIP to Use Default Context (FASTEST)

```bash
# Check what contexts exist
sudo asterisk -rx 'dialplan show contexts'

# Check what's in default context
sudo asterisk -rx 'dialplan show default'

# Change endpoint 1000 to use default context
sudo nano /etc/asterisk/pjsip.conf
```

**In the nano editor:**
1. Find the `[1000]` endpoint section
2. Change `context=openai-voice-assistant` to `context=default`
3. Save with `Ctrl+X`, then `Y`, then `Enter`

```bash
# Reload PJSIP
sudo asterisk -rx 'pjsip reload'
```

### Option 2: Fix Extensions.conf File

```bash
# Copy the simple working config I created
sudo cp asterisk-config/extensions_simple.conf /etc/asterisk/extensions.conf

# Reload dialplan
sudo asterisk -rx 'dialplan reload'

# Check if contexts now exist
sudo asterisk -rx 'dialplan show contexts'
```

## 🧪 TEST AFTER FIX

### Check Extensions
```bash
# Check if extensions exist in default context
sudo asterisk -rx 'dialplan show 1010@default'
sudo asterisk -rx 'dialplan show 1000@default'
```

### Test with Zoiper
1. **Dial 1010** - Should play demo message
2. **Dial 1000** - Should connect to voice assistant

## ✅ Expected Results

After the fix:
- ✅ **No 404 errors**
- ✅ **Extensions found in dialplan**
- ✅ **Calls connect successfully**

## 🎯 RECOMMENDED APPROACH

**Try Option 1 first** (change PJSIP context to default) because:
- It's faster
- Less chance of syntax errors
- Uses existing Asterisk default context

If that doesn't work, then try Option 2.

## 📋 Commands Summary

```bash
# Quick fix - change context to default
sudo nano /etc/asterisk/pjsip.conf
# (change context=openai-voice-assistant to context=default)
sudo asterisk -rx 'pjsip reload'

# Test
sudo asterisk -rx 'dialplan show default'
# Then dial 1010 and 1000 in Zoiper
```

**This should immediately fix the 404 error!** 🚀