#!/bin/bash

# Single command to push botv3 branch to new repository
# This script handles everything in one execution

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🚀 Pushing botv3 branch to https://github.com/deepakchaudharigit/botv3.git${NC}"

# Ensure we're on botv3 branch
echo -e "${YELLOW}📍 Checking current branch...${NC}"
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "botv3" ]; then
    echo -e "${YELLOW}⚠️  Switching to botv3 branch...${NC}"
    git checkout botv3
fi

# Commit any uncommitted changes
echo -e "${YELLOW}💾 Handling uncommitted changes...${NC}"
if ! git diff-index --quiet HEAD --; then
    echo -e "${YELLOW}📝 Committing current changes...${NC}"
    git add .
    git commit -m "Final botv3 updates - $(date '+%Y-%m-%d %H:%M:%S')"
fi

# Create README.md for the new repo (as per your commands)
echo -e "${YELLOW}📄 Creating README.md for new repository...${NC}"
echo "# botv3" > README.md
git add README.md
git commit -m "Add README for botv3 repository" || echo "README already exists or no changes"

# Add remote origin (remove if exists)
echo -e "${YELLOW}🔗 Setting up remote origin...${NC}"
if git remote get-url origin >/dev/null 2>&1; then
    git remote remove origin
fi
git remote add origin https://github.com/deepakchaudharigit/botv3.git

# Push botv3 branch as main to new repository
echo -e "${YELLOW}🚀 Pushing botv3 branch to new repository as main...${NC}"
git push -u origin botv3:main

echo -e "${GREEN}✅ SUCCESS! botv3 branch has been pushed to https://github.com/deepakchaudharigit/botv3.git${NC}"
echo -e "${GREEN}🎯 Your botv3 branch is now available as 'main' branch in the new repository${NC}"