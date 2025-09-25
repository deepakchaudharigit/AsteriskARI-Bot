#!/bin/bash

# Complete Git permissions fix and push botv3 branch
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔧 Complete Git Permissions Fix and Push botv3${NC}"
echo -e "${YELLOW}Current branch: $(git branch --show-current)${NC}"

# Step 1: Fix all Git directory permissions
echo -e "${YELLOW}🔒 Fixing Git repository permissions...${NC}"
echo "Fixing .git directory permissions..."
chmod -R 755 .git/

echo "Fixing .git/objects permissions..."
chmod -R 755 .git/objects/

echo "Fixing .git/refs permissions..."
chmod -R 755 .git/refs/

# Step 2: Clean up any lock files
echo -e "${YELLOW}🧹 Cleaning up lock files...${NC}"
rm -f .git/index.lock 2>/dev/null || true
rm -f .git/refs/heads/*.lock 2>/dev/null || true
rm -f .git/config.lock 2>/dev/null || true
rm -f .git/objects/*/tmp_* 2>/dev/null || true

# Step 3: Reset Git index
echo -e "${YELLOW}🔄 Resetting Git index...${NC}"
git reset --mixed HEAD 2>/dev/null || true

# Step 4: Verify we're on botv3 branch
echo -e "${YELLOW}📍 Verifying branch...${NC}"
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "botv3" ]; then
    echo -e "${RED}❌ Not on botv3 branch. Switching...${NC}"
    git checkout botv3
else
    echo -e "${GREEN}✅ Already on botv3 branch${NC}"
fi

# Step 5: Test if we can add files now
echo -e "${YELLOW}🧪 Testing Git add functionality...${NC}"
if git add .env.example 2>/dev/null; then
    echo -e "${GREEN}✅ Git add is working now${NC}"
    
    # Add all files
    echo -e "${YELLOW}📁 Adding all files...${NC}"
    git add .
    
    # Commit changes
    echo -e "${YELLOW}💾 Committing changes...${NC}"
    git commit -m "Final botv3 updates - $(date '+%Y-%m-%d %H:%M:%S')" || echo "Nothing new to commit"
    
else
    echo -e "${RED}❌ Still having permission issues. Trying alternative approach...${NC}"
    
    # Alternative: Add files one by one
    echo -e "${YELLOW}📁 Adding files individually...${NC}"
    
    # Add specific directories that are likely to work
    git add src/ 2>/dev/null || echo "src/ already added or permission issue"
    git add config/ 2>/dev/null || echo "config/ already added or permission issue"
    git add docs/ 2>/dev/null || echo "docs/ already added or permission issue"
    git add tests/ 2>/dev/null || echo "tests/ already added or permission issue"
    
    # Try to add individual files
    for file in *.py *.md *.txt *.yml *.yaml requirements.txt; do
        if [ -f "$file" ]; then
            git add "$file" 2>/dev/null || echo "Could not add $file"
        fi
    done
    
    # Commit what we could add
    git commit -m "Partial commit - botv3 updates $(date)" 2>/dev/null || echo "Nothing to commit"
fi

# Step 6: Create README for new repo
echo -e "${YELLOW}📄 Creating README.md...${NC}"
echo "# botv3

This is the botv3 branch of the NPCL Asterisk ARI Assistant project.

## Features
- Voice Assistant with OpenAI integration
- Asterisk ARI telephony support
- Multi-language support (English, Hindi, Bhojpuri, Bengali)
- Real-time audio processing

## Quick Start
\`\`\`bash
python src/main.py
\`\`\`

## Documentation
See the docs/ directory for detailed documentation.
" > README.md

git add README.md 2>/dev/null || echo "Could not add README.md"
git commit -m "Add README for botv3 repository" 2>/dev/null || echo "README already exists or could not commit"

# Step 7: Setup remote
echo -e "${YELLOW}🔗 Setting up remote repository...${NC}"
git remote remove origin 2>/dev/null || echo "No existing origin to remove"
git remote add origin https://github.com/deepakchaudharigit/botv3.git

# Step 8: Push to GitHub
echo -e "${YELLOW}🚀 Pushing botv3 branch to GitHub...${NC}"
echo "This will push your botv3 branch as 'main' in the new repository..."

if git push -u origin botv3:main; then
    echo -e "${GREEN}✅ SUCCESS! botv3 branch has been pushed to GitHub!${NC}"
    echo -e "${GREEN}🎯 Repository URL: https://github.com/deepakchaudharigit/botv3.git${NC}"
    echo -e "${GREEN}🌟 Your botv3 branch is now available as 'main' branch${NC}"
else
    echo -e "${RED}❌ Push failed. This might be due to:${NC}"
    echo -e "${YELLOW}   1. Authentication issues (check your GitHub credentials)${NC}"
    echo -e "${YELLOW}   2. Repository doesn't exist or is private${NC}"
    echo -e "${YELLOW}   3. Network connectivity issues${NC}"
    echo ""
    echo -e "${BLUE}💡 Manual steps to try:${NC}"
    echo "   1. Make sure the repository exists at: https://github.com/deepakchaudharigit/botv3.git"
    echo "   2. Check your GitHub authentication"
    echo "   3. Try: git push -u origin botv3:main"
fi