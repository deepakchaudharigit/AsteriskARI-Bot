#!/bin/bash
set -e

echo "🚀 Starting Asterisk 18 for NPCL Voice Assistant"
echo "================================================"

# Set default values
ASTERISK_USER=${ASTERISK_USER:-asterisk}
ASTERISK_GROUP=${ASTERISK_GROUP:-asterisk}

echo "✅ Asterisk Version: $(asterisk -V)"
echo "👤 Running as: $ASTERISK_USER:$ASTERISK_GROUP"
echo "📁 Config directory: /etc/asterisk"
echo "📁 Data directory: /var/lib/asterisk"

# Validate configuration files
if [ ! -f /etc/asterisk/asterisk.conf ]; then
    echo "❌ asterisk.conf not found, creating basic configuration..."
    cat > /etc/asterisk/asterisk.conf << EOF
[directories]
astetcdir => /etc/asterisk
astmoddir => /usr/lib/asterisk/modules
astvarlibdir => /var/lib/asterisk
astdbdir => /var/lib/asterisk
astkeydir => /var/lib/asterisk
astdatadir => /var/lib/asterisk
astagidir => /var/lib/asterisk/agi-bin
astspooldir => /var/spool/asterisk
astrundir => /var/run/asterisk
astlogdir => /var/log/asterisk

[options]
verbose = 3
debug = 3
documentation_language = en_US
EOF
fi

# Ensure ARI is enabled
if [ ! -f /etc/asterisk/ari.conf ]; then
    echo "⚠️  ari.conf not found, creating default ARI configuration..."
    cat > /etc/asterisk/ari.conf << EOF
[general]
enabled = yes
pretty = yes
allowed_origins = *

[asterisk]
type = user
read_only = no
password = 1234
EOF
fi

# Ensure HTTP is enabled for ARI
if [ ! -f /etc/asterisk/http.conf ]; then
    echo "⚠️  http.conf not found, creating HTTP configuration for ARI..."
    cat > /etc/asterisk/http.conf << EOF
[general]
enabled = yes
bindaddr = 0.0.0.0
bindport = 8088
prefix = 
enablestatic = yes
EOF
fi

# Check if extensions.conf exists
if [ ! -f /etc/asterisk/extensions.conf ]; then
    echo "⚠️  extensions.conf not found, creating basic dialplan..."
    cat > /etc/asterisk/extensions.conf << EOF
[general]
static = yes
writeprotect = no
clearglobalvars = no

[globals]

[default]
exten => 1000,1,NoOp(NPCL Voice Assistant Call)
 same => n,Stasis(openai-voice-assistant)
 same => n,Hangup()

[internal]
include => default
EOF
fi

echo "🔧 Configuration validated"
echo "🎯 Starting Asterisk with ARI enabled..."
echo "📞 Extension 1000 will connect to NPCL Voice Assistant"
echo "🌐 ARI available at: http://localhost:8088/ari"
echo "================================================"

# Execute the main command
exec "$@"