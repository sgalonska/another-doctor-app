#!/bin/bash

# Another Doctor - GitHub Push Script
# This script helps you push the repository to GitHub

echo "🚀 Another Doctor - GitHub Setup"
echo "=================================="
echo ""

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Error: Not in a git repository"
    exit 1
fi

# Check if there are uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo "📝 You have uncommitted changes. Committing them now..."
    git add .
    git commit -m "docs: add GitHub push script"
fi

echo "📋 Before pushing to GitHub, you need to:"
echo "1. Create a new repository on GitHub.com"
echo "2. Set the repository name to: another-doctor"
echo "3. DO NOT initialize with README, .gitignore, or license"
echo ""

# Get GitHub username
read -p "Enter your GitHub username: " GITHUB_USERNAME

if [ -z "$GITHUB_USERNAME" ]; then
    echo "❌ Error: GitHub username is required"
    exit 1
fi

# Check if remote already exists
if git remote get-url origin > /dev/null 2>&1; then
    echo "🔗 Remote 'origin' already exists:"
    git remote get-url origin
    read -p "Do you want to update it? (y/n): " UPDATE_REMOTE
    if [ "$UPDATE_REMOTE" = "y" ]; then
        git remote set-url origin https://github.com/$GITHUB_USERNAME/another-doctor.git
        echo "✅ Updated remote origin"
    fi
else
    # Add remote
    echo "🔗 Adding GitHub remote..."
    git remote add origin https://github.com/$GITHUB_USERNAME/another-doctor.git
    echo "✅ Added remote: https://github.com/$GITHUB_USERNAME/another-doctor.git"
fi

echo ""
echo "📤 Ready to push! Choose your authentication method:"
echo "1. HTTPS (requires GitHub token or username/password)"
echo "2. SSH (requires SSH key setup)"
echo ""

read -p "Choose method (1 or 2): " AUTH_METHOD

if [ "$AUTH_METHOD" = "2" ]; then
    # Update remote to SSH
    git remote set-url origin git@github.com:$GITHUB_USERNAME/another-doctor.git
    echo "🔑 Switched to SSH authentication"
fi

echo ""
echo "🚀 Pushing to GitHub..."
echo "Running: git push -u origin main"
echo ""

# Attempt to push
if git push -u origin main; then
    echo ""
    echo "🎉 SUCCESS! Your repository has been pushed to GitHub!"
    echo ""
    echo "📍 Repository URL: https://github.com/$GITHUB_USERNAME/another-doctor"
    echo ""
    echo "📋 Next steps:"
    echo "1. Visit your repository on GitHub"
    echo "2. Set up branch protection rules"
    echo "3. Configure GitHub Actions secrets for deployment"
    echo "4. Create your first release (v0.1.0)"
    echo ""
    echo "📚 See SETUP_GITHUB.md for detailed next steps"
else
    echo ""
    echo "❌ Push failed. Common solutions:"
    echo ""
    echo "🔐 Authentication Issues:"
    echo "   - Make sure you have GitHub access (SSH key or personal access token)"
    echo "   - For HTTPS: git config --global credential.helper store"
    echo "   - For SSH: ssh -T git@github.com (test SSH connection)"
    echo ""
    echo "📁 Repository Issues:"
    echo "   - Make sure the GitHub repository exists and is empty"
    echo "   - Repository should be named 'another-doctor'"
    echo "   - Don't initialize with README/license on GitHub"
    echo ""
    echo "🔧 Manual commands to try:"
    echo "   git remote -v                    (check remotes)"
    echo "   git push -u origin main --force  (force push if needed)"
    echo ""
    exit 1
fi