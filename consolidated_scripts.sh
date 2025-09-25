#!/bin/bash

# NPCL Voice Assistant - Consolidated Scripts
# Multi-mode launcher for different assistant configurations

echo "🎯 NPCL Voice Assistant - Consolidated Scripts"
echo "========================================"
echo ""
echo "🤖 BOT SELECTION MENU"
echo "========================================"
echo "Please choose your assistant bot:"
echo ""
echo "1. 🤖 NPCL Assistant"
echo "   └─ Full-featured assistant with voice chat, ARI, and weather"
echo ""
echo "2. 📞 Asterisk ARI Bot"
echo "   └─ Phone-call handling via Asterisk ARI, includes weather"
echo ""
echo "3. 📲 Zoiper Bot Test"
echo "   └─ SIP testing with Zoiper, includes weather"
echo ""
echo "0. ❌ Exit"
echo ""
echo "========================================"
read -p "Enter your choice (0-3): " choice

case $choice in
    1)
        echo ""
        echo "🤖 Starting NPCL Assistant..."
        echo "✨ Full-featured assistant with OpenAI Real-time API"
        echo "📞 Phone support: Call extension 1000"
        echo "🌤️ Weather support: Ask about weather in any city"
        echo ""
        ./activate_and_start.sh
        ;;
    2)
        echo ""
        echo "📞 Starting Asterisk ARI Bot..."
        echo "🎯 Phone-call handling focus"
        echo "📞 Configure Zoiper: 1001@localhost:5060, password: 1234"
        echo "📞 Test by calling extension 1000"
        echo ""
        # Start with ARI focus
        ./quick_start.sh docker
        ;;
    3)
        echo ""
        echo "📲 Starting Zoiper Bot Test..."
        echo "🧪 SIP testing configuration"
        echo "📞 Zoiper Settings:"
        echo "   • Username: 1001"
        echo "   • Password: 1234" 
        echo "   • Server: localhost:5060"
        echo "   • Protocol: UDP"
        echo "   • Test Extension: 1000"
        echo ""
        echo "🚀 Starting test environment..."
        ./quick_start.sh asterisk
        ;;
    0)
        echo ""
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo ""
        echo "❌ Invalid choice. Please select 0-3."
        echo "🔄 Rerun the script to try again."
        exit 1
        ;;
esac