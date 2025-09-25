# Manual Commands to Push botv3 Branch to New Repository

If you prefer to run commands manually instead of using the script, here are the exact commands:

## Prerequisites
1. Create a new repository on GitHub/GitLab (don't initialize with files)
2. Copy the repository URL (e.g., `https://github.com/yourusername/your-new-repo.git`)

## Commands to Run

### 1. Ensure you're on botv3 branch
```bash
git branch --show-current
# Should show: botv3

# If not on botv3, switch to it:
git checkout botv3
```

### 2. Commit any uncommitted changes (if needed)
```bash
# Check for uncommitted changes
git status

# If there are changes, commit them:
git add .
git commit -m "Final changes before pushing to new repo"
```

### 3. Add new repository as remote
```bash
# Replace YOUR_NEW_REPO_URL with your actual repository URL
git remote add new-repo YOUR_NEW_REPO_URL

# Verify the remote was added
git remote -v
```

### 4. Push only botv3 branch to new repository
```bash
# Push botv3 branch as 'main' branch in new repo
git push new-repo botv3:main

# Or if you want to keep the same branch name:
git push new-repo botv3:botv3
```

### 5. (Optional) Set upstream for future pushes
```bash
# If you pushed as 'main':
git push --set-upstream new-repo botv3:main

# If you kept the same branch name:
git push --set-upstream new-repo botv3:botv3
```

## Verification
After pushing, visit your new repository URL to verify that:
- ✅ Only the botv3 branch content is present
- ✅ All your files and commit history are there
- ✅ No other branches were copied

## Important Notes
- This method pushes ONLY the botv3 branch, not any other branches
- The commit history of botv3 will be preserved
- Other branches from the original repository will NOT be included
- You can safely work on the new repository without affecting the original

## If You Want to Clone the New Repository Later
```bash
git clone YOUR_NEW_REPO_URL
cd your-new-repo-name
```

## Troubleshooting
If you get authentication errors:
- Make sure you're logged into your Git provider (GitHub/GitLab)
- Use personal access tokens if required
- Check that the repository URL is correct