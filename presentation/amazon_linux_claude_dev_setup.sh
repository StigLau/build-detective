#!/bin/bash
# setup-dev.sh
# Setup script for Claude code dev environment on Amazon Linux 2023
# Includes: Git, Java 24 (Corretto), Maven, Python3, pip, Claude CLI
set -euxo pipefail

echo ">>> Updating system packages..."
dnf -y upgrade --refresh || true

# Check if curl-minimal exists and if full curl is needed
if rpm -q curl-minimal >/dev/null 2>&1 && ! rpm -q curl >/dev/null 2>&1; then
  echo ">>> Installing full curl alongside curl-minimal..."
  # Install full curl - this will coexist with curl-minimal
  dnf -y install curl --allowerasing || {
    echo ">>> Warning: Could not install full curl, proceeding with curl-minimal"
  }
else
  echo ">>> Curl package already available"
fi

echo ">>> Installing base developer tools..."
dnf -y install \
  git \
  wget \
  unzip \
  tar \
  gzip \
  which \
  jq \
  nano \
  python3 \
  python3-pip \
  --allowerasing

echo ">>> Installing Amazon Corretto 24 (Java)..."
rpm --import https://apt.corretto.aws/corretto.key
curl -fsSL https://yum.corretto.aws/corretto.repo -o /etc/yum.repos.d/corretto.repo
dnf -y install java-24-amazon-corretto-devel

echo ">>> Installing Apache Maven..."
MAVEN_VERSION=3.9.11
MAVEN_DIR=/opt/apache-maven-${MAVEN_VERSION}
if [ ! -d "$MAVEN_DIR" ]; then
  curl -fsSL https://downloads.apache.org/maven/maven-3/${MAVEN_VERSION}/binaries/apache-maven-${MAVEN_VERSION}-bin.tar.gz \
    | tar -xz -C /opt
  ln -sfn "$MAVEN_DIR" /opt/maven
fi

# Create Maven environment setup
cat >/etc/profile.d/maven.sh <<'EOF'
export M2_HOME=/opt/maven
export PATH=$M2_HOME/bin:$PATH
EOF
chmod +x /etc/profile.d/maven.sh

# Source the Maven environment for current session
source /etc/profile.d/maven.sh

echo ">>> Installing/upgrading pip..."
python3 -m pip install --upgrade pip

echo ">>> Installing GitHub CLI..."
if ! command -v gh >/dev/null 2>&1; then
  GH_VERSION="2.64.0"
  ARCH=$(uname -m)
  case $ARCH in
    x86_64) GH_ARCH="linux_amd64" ;;
    aarch64) GH_ARCH="linux_arm64" ;;
    *) echo "Warning: Unsupported architecture for GitHub CLI: $ARCH" ;;
  esac
  
  if [ -n "${GH_ARCH:-}" ]; then
    echo ">>> Downloading GitHub CLI v${GH_VERSION}..."
    curl -fsSL "https://github.com/cli/cli/releases/download/v${GH_VERSION}/gh_${GH_VERSION}_${GH_ARCH}.tar.gz" | tar -xz
    mv "gh_${GH_VERSION}_${GH_ARCH}/bin/gh" /usr/local/bin/
    chmod +x /usr/local/bin/gh
    rm -rf "gh_${GH_VERSION}_${GH_ARCH}"
    echo ">>> GitHub CLI installed successfully"
  fi
fi

echo ">>> Installing Claude CLI..."
if ! command -v claude >/dev/null 2>&1; then
  # Download and run Claude CLI installer
  curl -fsSL https://claude.ai/install.sh | bash || {
    echo ">>> Warning: Claude CLI installation may have failed"
  }
  
  # Try to add Claude to PATH for current session if installed
  if [ -f "$HOME/.local/bin/claude" ]; then
    export PATH="$HOME/.local/bin:$PATH"
  elif [ -f "/usr/local/bin/claude" ]; then
    export PATH="/usr/local/bin:$PATH"
  fi
fi

echo ">>> Development environment setup complete!"
echo ">>> Installed versions:"
git --version
java -version 2>&1 | head -1
javac -version 2>&1 | head -1
mvn -version | head -1
python3 --version
pip --version
if command -v gh >/dev/null 2>&1; then
  gh --version
else
  echo "GitHub CLI installation pending"
fi
if command -v claude >/dev/null 2>&1; then
  claude --version || echo "Claude CLI installed (version check may require restart)"
else
  echo "Claude CLI installation pending (may require shell restart)"
fi

echo ""
echo ">>> Next steps:"
echo "1. Restart your shell or run: source ~/.bashrc"
echo "2. Authenticate GitHub CLI: gh auth login"
echo "3. Verify GitHub CLI: gh repo list --limit 5"
echo "4. Configure Claude CLI: claude configure"
echo "5. Test Build Detective: python src/main.py --repo owner/repo"
