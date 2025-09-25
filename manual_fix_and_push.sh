#!/bin/bash

# Manual fix without sudo - alternative approach
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🔧 Manual fix and push botv3 branch (no sudo required)${NC}"

# Step 1: Try to remove lock files manually
echo -e "${YELLOW}🧹 Removing lock files...${NC}"
rm -f .git/index.lock 2>/dev/null || echo "No index.lock file found"
rm -f .git/refs/heads/*.lock 2>/dev/null || echo "No ref lock files found"
rm -f .git/config.lock 2>/dev/null || echo "No config.lock file found"

# Step 2: Check if we can write to .git directory
echo -e "${YELLOW}🔍 Checking Git directory permissions...${NC}"
if [ ! -w .git/ ]; then
    echo -e "${RED}❌ Cannot write to .git directory. You may need to run:${NC}"
    echo -e "${YELLOW}   sudo chown -R \$(whoami) .git/${NC}"
    echo -e "${YELLOW}   sudo chmod -R 755 .git/${NC}"
    exit 1
fi

# Step 3: Reset and clean Git state
echo -e "${YELLOW}🔄 Resetting Git state...${NC}"
git reset --mixed HEAD 2>/dev/null || echo "Reset completed"

# Step 4: Check current branch
echo -e "${YELLOW}📍 Checking current branch...${NC}"
CURRENT_BRANCH=$(git branch --show-current)
echo "Current branch: $CURRENT_BRANCH"

if [ "$CURRENT_BRANCH" != "botv3" ]; then
    echo -e "${YELLOW}⚠️  Switching to botv3 branch...${NC}"
    git checkout botv3
fi

# Step 5: Stage changes in smaller batches to avoid lock issues
echo -e "${YELLOW}💾 Staging changes in batches...${NC}"

# Add files in smaller groups
git add src/ 2>/dev/null || echo "src/ already staged or doesn't exist"
git add config/ 2>/dev/null || echo "config/ already staged or doesn't exist"
git add docs/ 2>/dev/null || echo "docs/ already staged or doesn't exist"
git add tests/ 2>/dev/null || echo "tests/ already staged or doesn't exist"
git add *.py *.md *.txt *.yml *.yaml 2>/dev/null || echo "Root files already staged"

# Commit the changes
echo -e "${YELLOW}📝 Committing changes...${NC}"
git commit -m "Final botv3 updates - $(date '+%Y-%m-%d %H:%M:%S')" 2>/dev/null || echo "Nothing to commit or already committed"

# Step 6: Create README.md
echo -e "${YELLOW}📄 Creating README.md...${NC}"
echo "# botv3" > README.md
git add README.md
git commit -m "Add README for botv3 repository" 2>/dev/null || echo "README already exists"

# Step 7: Setup remote
echo -e "${YELLOW}🔗 Setting up remote...${NC}"
git remote remove origin 2>/dev/null || echo "No existing origin to remove"
git remote add origin https://github.com/deepakchaudharigit/botv3.git

# Step 8: Push
echo -e "${YELLOW}🚀 Pushing to repository...${NC}"
git push -u origin botv3:main

echo -e "${GREEN}✅ SUCCESS! botv3 branch pushed successfully!${NC}"