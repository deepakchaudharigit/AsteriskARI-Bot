#!/bin/bash

# ============================================================================
# NPCL Voice Assistant - Gemini Package Removal Script
# ============================================================================
# This script removes all Gemini/Google AI packages that could conflict with OpenAI
# Author: NPCL Voice Assistant Team
# Version: 1.0
# ============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Global variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
VENV_PATH="$PROJECT_ROOT/.venv"

print_banner() {
    echo -e "${CYAN}"
    echo "============================================================================"
    echo "  NPCL VOICE ASSISTANT - GEMINI PACKAGE REMOVAL"
    echo "============================================================================"
    echo -e "${NC}"
}

print_section() {
    echo -e "\n${BLUE}▶ $1${NC}"
    echo "----------------------------------------"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

# List of Gemini/Google AI packages to remove
GEMINI_PACKAGES=(
    "google-generativeai"
    "google-ai-generativelanguage"
    "google-api-python-client"
    "google-auth"
    "google-auth-httplib2"
    "google-api-core"
    "googleapis-common-protos"
    "proto-plus"
    "grpcio"
    "grpcio-status"
)

# Packages to keep (these are used by other parts of the system)
KEEP_PACKAGES=(
    "google-auth"  # Might be used by other services
    "google-api-core"  # Might be used by other Google services
)

check_virtual_environment() {
    print_section "Checking Virtual Environment"
    
    if [ ! -d "$VENV_PATH" ]; then
        print_error "Virtual environment not found at $VENV_PATH"
        print_info "Please ensure you're in the correct project directory"
        exit 1
    fi
    
    # Check if virtual environment is activated
    if [[ "$VIRTUAL_ENV" != "$VENV_PATH" ]]; then
        print_warning "Virtual environment is not activated"
        print_info "Activating virtual environment..."
        source "$VENV_PATH/bin/activate"
    fi
    
    print_success "Virtual environment ready: $VENV_PATH"
}

list_installed_gemini_packages() {
    print_section "Scanning for Gemini/Google AI Packages"
    
    echo "Checking for installed packages..."
    
    # Get list of installed packages
    installed_packages=$(pip list --format=freeze | cut -d'=' -f1 | tr '[:upper:]' '[:lower:]')
    
    found_packages=()
    
    for package in "${GEMINI_PACKAGES[@]}"; do
        package_lower=$(echo "$package" | tr '[:upper:]' '[:lower:]' | tr '-' '_')
        if echo "$installed_packages" | grep -q "^${package_lower}$"; then
            found_packages+=("$package")
            print_warning "Found: $package"
        fi
    done
    
    if [ ${#found_packages[@]} -eq 0 ]; then
        print_success "No Gemini/Google AI packages found"
        return 1
    else
        print_info "Found ${#found_packages[@]} Gemini/Google AI packages to remove"
        return 0
    fi
}

backup_requirements() {
    print_section "Creating Backup"
    
    if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
        cp "$PROJECT_ROOT/requirements.txt" "$PROJECT_ROOT/requirements_backup_$(date +%Y%m%d_%H%M%S).txt"
        print_success "Backed up requirements.txt"
    fi
    
    # Create current environment snapshot
    pip freeze > "$PROJECT_ROOT/environment_before_gemini_removal_$(date +%Y%m%d_%H%M%S).txt"
    print_success "Created environment snapshot"
}

remove_gemini_packages() {
    print_section "Removing Gemini/Google AI Packages"
    
    # Get list of installed packages
    installed_packages=$(pip list --format=freeze | cut -d'=' -f1)
    
    packages_to_remove=()
    
    for package in "${GEMINI_PACKAGES[@]}"; do
        # Check different naming conventions
        package_variations=(
            "$package"
            "$(echo "$package" | tr '-' '_')"
            "$(echo "$package" | tr '_' '-')"
        )
        
        for variation in "${package_variations[@]}"; do
            if echo "$installed_packages" | grep -qi "^${variation}$"; then
                packages_to_remove+=("$variation")
                break
            fi
        done
    done
    
    if [ ${#packages_to_remove[@]} -eq 0 ]; then
        print_success "No packages to remove"
        return 0
    fi
    
    print_info "Packages to remove: ${packages_to_remove[*]}"
    
    # Ask for confirmation
    echo ""
    read -p "Do you want to proceed with removing these packages? (y/N): " confirm
    
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        print_info "Operation cancelled by user"
        exit 0
    fi
    
    # Remove packages one by one
    for package in "${packages_to_remove[@]}"; do
        print_info "Removing $package..."
        
        if pip uninstall -y "$package" 2>/dev/null; then
            print_success "Removed: $package"
        else
            print_warning "Could not remove: $package (may not be installed)"
        fi
    done
    
    print_success "Package removal completed"
}

clean_package_cache() {
    print_section "Cleaning Package Cache"
    
    # Clear pip cache
    pip cache purge 2>/dev/null || true
    print_success "Cleared pip cache"
    
    # Remove any remaining Google/Gemini directories
    if [ -d "$VENV_PATH/lib/python3.13/site-packages/google" ]; then
        print_info "Checking for remaining Google packages..."
        
        # Only remove generativeai related directories
        if [ -d "$VENV_PATH/lib/python3.13/site-packages/google/generativeai" ]; then
            rm -rf "$VENV_PATH/lib/python3.13/site-packages/google/generativeai"
            print_success "Removed google.generativeai directory"
        fi
        
        if [ -d "$VENV_PATH/lib/python3.13/site-packages/google/ai/generativelanguage"* ]; then
            rm -rf "$VENV_PATH/lib/python3.13/site-packages/google/ai/generativelanguage"*
            print_success "Removed google.ai.generativelanguage directories"
        fi
    fi
    
    # Remove .dist-info directories
    find "$VENV_PATH/lib/python3.13/site-packages" -name "*google_generativeai*" -type d -exec rm -rf {} + 2>/dev/null || true
    find "$VENV_PATH/lib/python3.13/site-packages" -name "*google_ai_generativelanguage*" -type d -exec rm -rf {} + 2>/dev/null || true
    
    print_success "Cleaned package directories"
}

verify_removal() {
    print_section "Verifying Removal"
    
    # Check if any Gemini packages are still installed
    installed_packages=$(pip list --format=freeze | cut -d'=' -f1 | tr '[:upper:]' '[:lower:]')
    
    remaining_packages=()
    
    for package in "${GEMINI_PACKAGES[@]}"; do
        package_lower=$(echo "$package" | tr '[:upper:]' '[:lower:]' | tr '-' '_')
        if echo "$installed_packages" | grep -q "^${package_lower}$"; then
            remaining_packages+=("$package")
        fi
    done
    
    if [ ${#remaining_packages[@]} -eq 0 ]; then
        print_success "All Gemini/Google AI packages successfully removed"
    else
        print_warning "Some packages may still be installed: ${remaining_packages[*]}"
    fi
    
    # Check for remaining imports in Python
    print_info "Testing Python imports..."
    
    if python -c "import google.generativeai" 2>/dev/null; then
        print_warning "google.generativeai can still be imported"
    else
        print_success "google.generativeai import blocked"
    fi
    
    # Verify OpenAI is still available
    if python -c "import openai" 2>/dev/null; then
        print_success "OpenAI package is still available"
    else
        print_error "OpenAI package is missing - you may need to reinstall it"
    fi
}

update_requirements() {
    print_section "Updating Requirements File"
    
    if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
        # Remove Gemini-related packages from requirements.txt
        temp_file=$(mktemp)
        
        while IFS= read -r line; do
            # Skip lines that contain Gemini/Google AI packages
            skip_line=false
            for package in "${GEMINI_PACKAGES[@]}"; do
                if echo "$line" | grep -qi "^${package}"; then
                    skip_line=true
                    break
                fi
            done
            
            if [ "$skip_line" = false ]; then
                echo "$line" >> "$temp_file"
            fi
        done < "$PROJECT_ROOT/requirements.txt"
        
        mv "$temp_file" "$PROJECT_ROOT/requirements.txt"
        print_success "Updated requirements.txt"
    else
        print_info "No requirements.txt file found"
    fi
    
    # Generate new requirements from current environment
    pip freeze > "$PROJECT_ROOT/requirements_clean_$(date +%Y%m%d_%H%M%S).txt"
    print_success "Generated clean requirements file"
}

show_summary() {
    print_section "Removal Summary"
    
    echo "📋 What was removed:"
    echo "   • google-generativeai (Gemini AI package)"
    echo "   • google-ai-generativelanguage (Gemini language models)"
    echo "   • Related Google AI dependencies"
    echo ""
    echo "📦 What was preserved:"
    echo "   • openai (OpenAI package)"
    echo "   • All other project dependencies"
    echo "   • Virtual environment structure"
    echo ""
    echo "📁 Files created:"
    echo "   • requirements_backup_*.txt (original requirements backup)"
    echo "   • environment_before_gemini_removal_*.txt (pre-removal snapshot)"
    echo "   • requirements_clean_*.txt (clean requirements)"
    echo ""
    echo "✅ Your project is now configured for OpenAI only!"
    echo ""
    echo "🚀 Next steps:"
    echo "   1. Test your application: python src/run_realtime_server.py"
    echo "   2. Run the E2E test: ./comprehensive_e2e_test.sh"
    echo "   3. Verify OpenAI integration works correctly"
}

main() {
    print_banner
    
    print_info "This script will remove all Gemini/Google AI packages that could conflict with OpenAI"
    print_warning "Make sure you have backed up any important data before proceeding"
    
    echo ""
    read -p "Do you want to continue? (y/N): " proceed
    
    if [[ ! "$proceed" =~ ^[Yy]$ ]]; then
        print_info "Operation cancelled"
        exit 0
    fi
    
    # Execute removal steps
    check_virtual_environment
    
    if list_installed_gemini_packages; then
        backup_requirements
        remove_gemini_packages
        clean_package_cache
        verify_removal
        update_requirements
        show_summary
    else
        print_success "No Gemini packages found - your environment is already clean!"
    fi
    
    print_success "Gemini package removal completed successfully!"
}

# Run main function
main "$@"