#!/bin/bash
# Script to remove all git history (local and remote) and start fresh

set -e

echo "⚠️  WARNING: This will permanently delete all git history!"
echo "   - Local git history will be deleted"
echo "   - Remote git history will be overwritten"
echo ""
read -p "Are you sure you want to continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Aborted."
    exit 1
fi

# Get remote URL before deleting .git
REMOTE_URL=$(git remote get-url origin 2>/dev/null || echo "")

# Remove local git history
echo ""
echo "Step 1: Removing local git history..."
rm -rf .git

# Initialize new git repository
echo "Step 2: Initializing new git repository..."
git init

# Add all files
echo "Step 3: Adding all files..."
git add .

# Create initial commit
echo "Step 4: Creating initial commit..."
git commit -m "Initial commit: Portfolio website"

# Add remote if it existed
if [ -n "$REMOTE_URL" ]; then
    echo "Step 5: Adding remote repository..."
    git remote add origin "$REMOTE_URL"
    
    # Set default branch to main
    git branch -M main
    
    echo ""
    echo "Step 6: Force pushing to remote (this will overwrite remote history)..."
    echo "⚠️  This will permanently delete all history on the remote!"
    read -p "Continue with force push? (yes/no): " push_confirm
    
    if [ "$push_confirm" == "yes" ]; then
        git push -f origin main
        echo ""
        echo "✅ Success! Git history has been reset locally and remotely."
        echo "   Your repository now has a fresh start with a single initial commit."
    else
        echo ""
        echo "✅ Local git history has been reset."
        echo "   To push to remote later, run:"
        echo "   git push -f origin main"
    fi
else
    echo ""
    echo "✅ Local git history has been reset."
    echo "   No remote was configured, so only local history was removed."
fi

echo ""
echo "Done!"

