# 🔧 CORRECT HTTP RELOAD COMMANDS

## ✅ Progress So Far
- ✅ **ARI config applied** to system
- ✅ **ARI module reloaded** successfully

## 🔧 CORRECT HTTP RELOAD

The `http reload` command doesn't exist. Use this instead:

### Step 1: Reload HTTP Module
```bash
sudo asterisk -rx 'module reload res_http_websocket'
```

### Step 2: Alternative - Core Reload
```bash
# If module reload doesn't work, do full reload
sudo asterisk -rx 'core reload'
```

### Step 3: Test ARI Authentication
```bash
curl http://localhost:8088/ari/asterisk/info -u asterisk:1234
```

### Step 4: Check HTTP Status
```bash
sudo asterisk -rx 'http show status'
```

## 🚀 QUICK SEQUENCE

```bash
# Reload HTTP module
sudo asterisk -rx 'module reload res_http_websocket'

# Test ARI authentication
curl http://localhost:8088/ari/asterisk/info -u asterisk:1234

# If authentication works, restart ARI bot
# (Ctrl+C in ARI bot terminal, then restart)
python3 ari_bot.py

# Check Stasis registration
sudo asterisk -rx 'ari show apps'
```

## ✅ Expected Results

After HTTP module reload:
- ✅ **ARI authentication should work** (JSON response, not "Authentication required")
- ✅ **ARI bot can connect** to Asterisk
- ✅ **Stasis app registers**

**Try `module reload res_http_websocket` for HTTP reload!** 🚀