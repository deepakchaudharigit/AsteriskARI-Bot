# 🔧 CORRECT ARI RELOAD COMMANDS

## 🎯 Issue
The `ari reload` command doesn't exist in Asterisk.

## ✅ CORRECT COMMANDS

### Step 1: Reload ARI Module
```bash
# Reload the ARI module
sudo asterisk -rx 'module reload res_ari'

# Or reload all HTTP/ARI related modules
sudo asterisk -rx 'module reload res_http_websocket'
sudo asterisk -rx 'module reload res_ari'
```

### Step 2: Apply HTTP Configuration
```bash
# Copy HTTP config
sudo cp asterisk-config/http.conf /etc/asterisk/http.conf

# Reload HTTP server
sudo asterisk -rx 'http reload'
```

### Step 3: Alternative - Full Reload
```bash
# If module reload doesn't work, do a full reload
sudo asterisk -rx 'core reload'
```

### Step 4: Test ARI Authentication
```bash
curl http://localhost:8088/ari/asterisk/info -u asterisk:1234
```

### Step 5: Restart ARI Bot
```bash
# Stop current ARI bot (Ctrl+C)
# Wait 5 seconds
# Restart:
python3 ari_bot.py
```

### Step 6: Check Stasis Registration
```bash
sudo asterisk -rx 'ari show apps'
```

## 🎯 Expected Results

After running the correct reload commands:
- ✅ **ARI authentication should work**
- ✅ **Stasis app should register**
- ✅ **Extension 1000 should transfer to AI**

## 🚀 Quick Command Sequence

```bash
# Apply configs
sudo cp asterisk-config/ari.conf /etc/asterisk/ari.conf
sudo cp asterisk-config/http.conf /etc/asterisk/http.conf

# Reload modules
sudo asterisk -rx 'module reload res_ari'
sudo asterisk -rx 'http reload'

# Test authentication
curl http://localhost:8088/ari/asterisk/info -u asterisk:1234

# Restart ARI bot
# (Ctrl+C in ARI bot terminal, then restart)
python3 ari_bot.py
```

**Use `module reload res_ari` instead of `ari reload`!** 🚀