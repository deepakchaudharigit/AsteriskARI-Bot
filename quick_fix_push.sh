#!/bin/bash

# Quick fix for Git permissions and push
set -e

echo "🔧 Quick fix for Git permissions issue..."

# Fix the .git directory permissions
echo "📝 Fixing .git directory permissions..."
chmod 755 .git/

# Remove any lock files
echo "🧹 Cleaning lock files..."
rm -f .git/index.lock 2>/dev/null || true

# Now try the push process
echo "🚀 Starting push process..."

# Ensure we're on botv3
git checkout botv3

# Add and commit changes
echo "💾 Adding and committing changes..."
git add .
git commit -m "Final botv3 commit - $(date)" || echo "Nothing to commit"

# Create README
echo "📄 Creating README..."
echo "# botv3" > README.md
git add README.md
git commit -m "Add README" || echo "README already exists"

# Setup remote
echo "🔗 Setting up remote..."
git remote remove origin 2>/dev/null || true
git remote add origin https://github.com/deepakchaudharigit/botv3.git

# Push
echo "🚀 Pushing to GitHub..."
git push -u origin botv3:main

echo "✅ Done! Check your repository at: https://github.com/deepakchaudharigit/botv3.git"