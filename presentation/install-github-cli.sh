#!/bin/bash
# GitHub CLI setup for Amazon Linux 2023
set -euo pipefail

echo ">>> Installing GitHub CLI on Amazon Linux 2023..."

# Method 1: Direct binary download (recommended for Amazon Linux)
GH_VERSION="2.64.0"  # Use latest stable version
ARCH=$(uname -m)

# Map architecture
case $ARCH in
  x86_64) GH_ARCH="linux_amd64" ;;
  aarch64) GH_ARCH="linux_arm64" ;;
  *) echo "Unsupported architecture: $ARCH"; exit 1 ;;
esac

echo ">>> Downloading GitHub CLI v${GH_VERSION} for ${GH_ARCH}..."
wget -q "https://github.com/cli/cli/releases/download/v${GH_VERSION}/gh_${GH_VERSION}_${GH_ARCH}.tar.gz" -O gh.tar.gz

echo ">>> Installing GitHub CLI..."
tar -xzf gh.tar.gz
sudo mv "gh_${GH_VERSION}_${GH_ARCH}/bin/gh" /usr/local/bin/
sudo chmod +x /usr/local/bin/gh

# Clean up
rm -rf gh.tar.gz "gh_${GH_VERSION}_${GH_ARCH}"

echo ">>> Verifying installation..."
gh --version

echo ">>> GitHub CLI installed successfully!"
echo ">>> Next steps:"
echo "1. Authenticate: gh auth login"
echo "2. Test: gh repo list --limit 5"
echo "3. Use in Build Detective: python src/main.py --repo owner/repo"