#!/bin/bash

# Script to push only botv3 branch to a new repository
# Usage: ./push_botv3_to_new_repo.sh <new-repo-url>

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Push botv3 Branch to New Repository ===${NC}"

# Check if new repo URL is provided
if [ $# -eq 0 ]; then
    echo -e "${RED}Error: Please provide the new repository URL${NC}"
    echo "Usage: $0 <new-repo-url>"
    echo "Example: $0 https://github.com/yourusername/your-new-repo.git"
    exit 1
fi

NEW_REPO_URL=$1

# Verify we're on botv3 branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "botv3" ]; then
    echo -e "${YELLOW}Warning: You're not on botv3 branch. Current branch: $CURRENT_BRANCH${NC}"
    echo "Switching to botv3 branch..."
    git checkout botv3
fi

echo -e "${GREEN}✓ Currently on botv3 branch${NC}"

# Check if there are uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo -e "${YELLOW}Warning: You have uncommitted changes.${NC}"
    echo "Do you want to commit them first? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo "Enter commit message:"
        read -r commit_message
        git add .
        git commit -m "$commit_message"
        echo -e "${GREEN}✓ Changes committed${NC}"
    else
        echo -e "${YELLOW}Proceeding with uncommitted changes...${NC}"
    fi
fi

# Add new remote (if it doesn't exist)
if git remote get-url new-repo >/dev/null 2>&1; then
    echo -e "${YELLOW}Remote 'new-repo' already exists. Updating URL...${NC}"
    git remote set-url new-repo "$NEW_REPO_URL"
else
    echo "Adding new remote repository..."
    git remote add new-repo "$NEW_REPO_URL"
fi

echo -e "${GREEN}✓ New remote added: $NEW_REPO_URL${NC}"

# Push only botv3 branch to new repository
echo "Pushing botv3 branch to new repository..."
git push new-repo botv3:main

echo -e "${GREEN}✓ Successfully pushed botv3 branch to new repository as 'main' branch${NC}"

# Optional: Set up new repo as default upstream for botv3
echo "Do you want to set the new repository as upstream for botv3 branch? (y/n)"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    git push --set-upstream new-repo botv3:main
    echo -e "${GREEN}✓ Upstream set for botv3 branch${NC}"
fi

echo -e "${GREEN}=== Process Complete ===${NC}"
echo "Your botv3 branch has been pushed to: $NEW_REPO_URL"
echo "The branch has been pushed as 'main' in the new repository."
echo ""
echo "Next steps:"
echo "1. Visit your new repository to verify the code"
echo "2. Update any documentation or README files as needed"
echo "3. Set up any necessary CI/CD pipelines"
echo ""
echo "To work with the new repository:"
echo "  git clone $NEW_REPO_URL"