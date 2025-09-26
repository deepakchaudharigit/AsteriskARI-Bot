#!/bin/bash

# =============================================================================
# NPCL Asterisk ARI Voice Assistant - Project Launcher
# =============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

print_banner() {
    echo -e "${CYAN}===============================================================================${NC}"
    echo -e "${WHITE}🚀 NPCL Asterisk ARI Voice Assistant${NC}"
    echo -e "${WHITE}📞 Enterprise Voice Assistant with OpenAI GPT-4 Realtime API${NC}"
    echo -e "${WHITE}🏢 NPCL (Noida Power Corporation Limited)${NC}"
    echo -e "${CYAN}===============================================================================${NC}"
    echo ""
}

show_menu() {
    echo -e "${WHITE}Choose your startup method:${NC}"
    echo ""
    echo -e "${GREEN}1)${NC} ${BLUE}Native Python${NC} - Run directly with Python (recommended for development)"
    echo -e "${GREEN}2)${NC} ${PURPLE}Docker${NC} - Run with Docker containers (recommended for production)"
    echo -e "${GREEN}3)${NC} ${YELLOW}Help${NC} - Show detailed information"
    echo -e "${GREEN}4)${NC} ${RED}Exit${NC}"
    echo ""
}

run_native() {
    echo -e "${BLUE}🐍 Starting with Native Python...${NC}"
    echo ""
    
    if [ -f "run_project.sh" ]; then
        ./run_project.sh
    else
        echo -e "${RED}❌ run_project.sh not found${NC}"
        exit 1
    fi
}

run_docker() {
    echo -e "${PURPLE}🐳 Starting with Docker...${NC}"
    echo ""
    
    if [ -f "run_docker.sh" ]; then
        ./run_docker.sh
    else
        echo -e "${RED}❌ run_docker.sh not found${NC}"
        exit 1
    fi
}

show_help() {
    echo -e "${YELLOW}📚 NPCL Voice Assistant - Help${NC}"
    echo ""
    echo -e "${WHITE}Available Startup Methods:${NC}"
    echo ""
    echo -e "${BLUE}1. Native Python (./run_project.sh)${NC}"
    echo "   ✅ Faster startup"
    echo "   ✅ Direct access to logs"
    echo "   ✅ Easy debugging"
    echo "   ❌ Requires Python setup"
    echo "   ❌ Manual dependency management"
    echo ""
    echo -e "${PURPLE}2. Docker (./run_docker.sh)${NC}"
    echo "   ✅ Isolated environment"
    echo "   ✅ Includes Asterisk PBX"
    echo "   ✅ Production-ready"
    echo "   ✅ Easy deployment"
    echo "   ❌ Requires Docker"
    echo "   ❌ Slower startup"
    echo ""
    echo -e "${WHITE}Requirements:${NC}"
    echo ""
    echo -e "${GREEN}For Native Python:${NC}"
    echo "   • Python 3.8 or higher"
    echo "   • pip (Python package manager)"
    echo "   • Internet connection"
    echo "   • OpenAI API key"
    echo ""
    echo -e "${GREEN}For Docker:${NC}"
    echo "   • Docker Engine"
    echo "   • Docker Compose"
    echo "   • OpenAI API key"
    echo ""
    echo -e "${WHITE}Configuration:${NC}"
    echo ""
    echo "1. Copy .env.example to .env"
    echo "2. Edit .env and set your OpenAI API key:"
    echo "   OPENAI_API_KEY=sk-proj-your_actual_api_key_here"
    echo "3. Get your API key from: https://platform.openai.com/api-keys"
    echo ""
    echo -e "${WHITE}Service Endpoints (after startup):${NC}"
    echo ""
    echo "   🌐 Web Interface: http://localhost:8000"
    echo "   📚 API Documentation: http://localhost:8000/docs"
    echo "   🏥 Health Check: http://localhost:8000/health"
    echo "   📊 ARI Status: http://localhost:8000/ari/status"
    echo ""
    echo -e "${WHITE}Telephony Testing:${NC}"
    echo ""
    echo "   📞 Extension: 1000"
    echo "   🔐 SIP Username: 1000"
    echo "   🔑 SIP Password: 1234"
    echo "   🌐 SIP Server: localhost"
    echo ""
    echo -e "${WHITE}Troubleshooting:${NC}"
    echo ""
    echo "   📋 Check logs in logs/ directory"
    echo "   🔧 Verify .env configuration"
    echo "   🌐 Test health endpoints"
    echo "   📖 Read STARTUP_GUIDE.md for details"
    echo ""
    read -p "Press Enter to return to main menu..."
}

main() {
    print_banner
    
    while true; do
        show_menu
        read -p "Enter your choice (1-4): " choice
        echo ""
        
        case $choice in
            1)
                run_native
                break
                ;;
            2)
                run_docker
                break
                ;;
            3)
                show_help
                echo ""
                ;;
            4)
                echo -e "${GREEN}👋 Goodbye!${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}❌ Invalid choice. Please enter 1-4.${NC}"
                echo ""
                ;;
        esac
    done
}

# Handle command line arguments
if [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
    print_banner
    show_help
    exit 0
elif [[ "$1" == "--native" ]] || [[ "$1" == "-n" ]]; then
    print_banner
    run_native
elif [[ "$1" == "--docker" ]] || [[ "$1" == "-d" ]]; then
    print_banner
    run_docker
else
    main
fi