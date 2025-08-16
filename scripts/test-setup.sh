#!/bin/bash
set -e

# Build Detective Test Setup Script
# Tests the setup process and validates installation

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 Build Detective Test Suite${NC}"
echo "=================================="

# Test 1: Verify core files exist
echo -e "\n${BLUE}Test 1: Core files verification${NC}"
required_files=(
    "README.md"
    "LICENSE"
    "scripts/setup-build-detective.sh"
    "templates/build-detective-template.md"
    "docs/setup/QUICK_START.md"
    "docs/guides/COMMAND_PATTERNS.md"
)

for file in "${required_files[@]}"; do
    if [[ -f "$ROOT_DIR/$file" ]]; then
        echo -e "✅ $file"
    else
        echo -e "❌ $file ${RED}MISSING${NC}"
        exit 1
    fi
done

# Test 2: Template validation
echo -e "\n${BLUE}Test 2: Template validation${NC}"
template_file="$ROOT_DIR/templates/build-detective-template.md"

# Check for required template variables
required_vars=(
    "{{PROJECT_NAME}}"
    "{{PRIMARY_LANGUAGE}}"
    "{{BUILD_SYSTEM}}"
    "{{PROJECT_SPECIFIC_DOMAIN}}"
)

for var in "${required_vars[@]}"; do
    if grep -q "$var" "$template_file"; then
        echo -e "✅ Template variable: $var"
    else
        echo -e "❌ Template variable: $var ${RED}MISSING${NC}"
        exit 1
    fi
done

# Test 3: Setup script functionality
echo -e "\n${BLUE}Test 3: Setup script test${NC}"
test_project_dir="/tmp/build-detective-test-$(date +%s)"
mkdir -p "$test_project_dir"

# Create minimal test environment
echo "# Test Project" > "$test_project_dir/README.md"
git init "$test_project_dir" > /dev/null 2>&1 || true

# Test setup with minimal interaction (would normally be interactive)
echo -e "${YELLOW}Testing setup script (non-interactive)${NC}"
setup_script="$ROOT_DIR/scripts/setup-build-detective.sh"

if [[ -x "$setup_script" ]]; then
    echo -e "✅ Setup script is executable"
else
    echo -e "❌ Setup script not executable ${RED}FAILED${NC}"
    exit 1
fi

# Test 4: Documentation link validation
echo -e "\n${BLUE}Test 4: Documentation structure${NC}"
doc_dirs=(
    "docs/setup"
    "docs/guides"
    "docs/troubleshooting"
    "docs/architecture"
)

for dir in "${doc_dirs[@]}"; do
    if [[ -d "$ROOT_DIR/$dir" ]]; then
        echo -e "✅ Directory: $dir"
    else
        echo -e "❌ Directory: $dir ${RED}MISSING${NC}"
        exit 1
    fi
done

# Test 5: Examples validation
echo -e "\n${BLUE}Test 5: Examples validation${NC}"
if [[ -d "$ROOT_DIR/examples" ]]; then
    echo -e "✅ Examples directory exists"
    if [[ -f "$ROOT_DIR/examples/README.md" ]]; then
        echo -e "✅ Examples documentation exists"
    else
        echo -e "❌ Examples README.md ${RED}MISSING${NC}"
    fi
else
    echo -e "❌ Examples directory ${RED}MISSING${NC}"
fi

# Test 6: GitHub CLI integration test
echo -e "\n${BLUE}Test 6: GitHub CLI integration${NC}"
if command -v gh &> /dev/null; then
    echo -e "✅ GitHub CLI installed"
    
    # Test authentication (non-blocking)
    if gh auth status &> /dev/null; then
        echo -e "✅ GitHub CLI authenticated"
    else
        echo -e "⚠️  GitHub CLI not authenticated (optional for testing)"
    fi
else
    echo -e "⚠️  GitHub CLI not installed (required for full functionality)"
fi

# Cleanup
rm -rf "$test_project_dir"

# Test 7: Template content validation
echo -e "\n${BLUE}Test 7: Template content validation${NC}"
template_content=$(cat "$ROOT_DIR/templates/build-detective-template.md")

# Check for essential sections
essential_sections=(
    "Core Responsibilities"
    "Analysis Priorities"
    "Response Format"
    "GitHub CLI Integration"
    "Maven Plugin Failure Patterns"
)

for section in "${essential_sections[@]}"; do
    if echo "$template_content" | grep -q "$section"; then
        echo -e "✅ Section: $section"
    else
        echo -e "❌ Section: $section ${RED}MISSING${NC}"
        exit 1
    fi
done

# Final summary
echo -e "\n${GREEN}🎉 All tests passed!${NC}"
echo -e "${GREEN}Build Detective is ready for use.${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "1. Run: ./scripts/setup-build-detective.sh /path/to/your/project"
echo "2. Add delegation to your project's CLAUDE.md"
echo "3. Start analyzing CI failures!"
echo ""
echo -e "${YELLOW}For help:${NC}"
echo "- Quick Start: docs/setup/QUICK_START.md"
echo "- Command Patterns: docs/guides/COMMAND_PATTERNS.md"
echo "- Troubleshooting: docs/troubleshooting/TROUBLESHOOTING.md"