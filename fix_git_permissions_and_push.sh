#!/bin/bash

# Fix Git permissions and push botv3 branch
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🔧 Fixing Git permissions and pushing botv3 branch${NC}"

# Step 1: Fix Git permissions
echo -e "${YELLOW}🔒 Fixing Git repository permissions...${NC}"
sudo chown -R $(whoami) .git/
sudo chmod -R 755 .git/

# Step 2: Remove any existing lock files
echo -e "${YELLOW}🧹 Cleaning up any existing lock files...${NC}"
rm -f .git/index.lock
rm -f .git/refs/heads/*.lock
rm -f .git/config.lock

# Step 3: Reset Git index if needed
echo -e "${YELLOW}🔄 Resetting Git index...${NC}"
git reset

# Step 4: Check current branch
echo -e "${YELLOW}📍 Checking current branch...${NC}"
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "botv3" ]; then
    echo -e "${YELLOW}⚠️  Switching to botv3 branch...${NC}"
    git checkout botv3
fi

# Step 5: Handle uncommitted changes
echo -e "${YELLOW}💾 Handling uncommitted changes...${NC}"
if ! git diff-index --quiet HEAD -- 2>/dev/null; then
    echo -e "${YELLOW}📝 Staging and committing current changes...${NC}"
    git add .
    git commit -m "Final botv3 updates - $(date '+%Y-%m-%d %H:%M:%S')"
else
    echo -e "${GREEN}✅ No uncommitted changes found${NC}"
fi

# Step 6: Create README.md for the new repo
echo -e "${YELLOW}📄 Creating README.md for new repository...${NC}"
echo "# botv3" > README.md
git add README.md
git commit -m "Add README for botv3 repository" 2>/dev/null || echo "README already committed or no changes"

# Step 7: Setup remote
echo -e "${YELLOW}🔗 Setting up remote origin...${NC}"
if git remote get-url origin >/dev/null 2>&1; then
    git remote remove origin
fi
git remote add origin https://github.com/deepakchaudharigit/botv3.git

# Step 8: Push to new repository
echo -e "${YELLOW}🚀 Pushing botv3 branch to new repository as main...${NC}"
git push -u origin botv3:main

echo -e "${GREEN}✅ SUCCESS! botv3 branch has been pushed to https://github.com/deepakchaudharigit/botv3.git${NC}"
echo -e "${GREEN}🎯 Your botv3 branch is now available as 'main' branch in the new repository${NC}"