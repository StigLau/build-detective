# 🚀 Quick Start Guide

Get Build Detective up and running in your project in 5 minutes.

## Prerequisites

- **Claude Code** with subagent support
- **GitHub CLI** (`gh`) installed and authenticated
- **Git repository** (recommended but not required)

## Installation

### 1. Install Build Detective

```bash
# Clone Build Detective
git clone https://github.com/StigLau/build-detective.git

# Install to your project
cd build-detective
./scripts/setup-build-detective.sh /path/to/your/project
```

### 2. Configure Your Project

The setup script will prompt for:
- **Project name** and primary language
- **Build system** (Maven, Gradle, npm)
- **Key dependencies** and deployment targets
- **Common issues** and typical solutions

Example configuration:
```
Project name: MyApp
Primary language: Java
Build system: Maven
Key dependencies: Spring Boot, JUnit
Deployment target: AWS
```

### 3. Integrate with Claude Code

Add to your project's `CLAUDE.md`:

```markdown
### Subagent Delegation Strategy
**CRITICAL**: Automatically delegate tasks to specialized subagents:

- **CI/Build Analysis**: Use `build-detective` subagent for:
  - GitHub Actions failures
  - Maven/Gradle build errors
  - Docker build failures
  - Compilation errors
  - Test failures
  - Dependency conflicts
```

## First Analysis

### Test with a Real Failure

```bash
# Find a recent CI failure
gh run list --status failure --limit 5

# Analyze with Build Detective
"Use build-detective to investigate this build failure: 
https://github.com/user/repo/actions/runs/12345"
```

### Expected Response

Build Detective will return structured JSON:

```json
{
  "confidence": 8,
  "error_type": "compilation",
  "build_step": "compile",
  "primary_error": "cannot find symbol: class Example",
  "suggested_action": "Add missing import for Example class",
  "pattern_matched": "missing_import_java"
}
```

## Common Usage Patterns

### Single Failure Analysis
```bash
"BD investigate Maven compilation error"
"BD docker build COPY file missing"
"BD github actions timeout issue"
```

### Bulk Pattern Analysis
```bash
"BD analyze last 10 CI failures for patterns"
"BD check recurring issues in recent builds"
```

### Technology-Specific
```bash
"BD maven dependency conflict resolution"
"BD git submodule configuration error"
"BD java version mismatch in CI"
```

## Verification

### Check Installation
```bash
# Verify Build Detective file exists
ls -la /path/to/project/.claude/agents/build-detective.md

# Test GitHub CLI integration
gh auth status
gh run list --repo owner/repo --status failure --limit 3
```

### Quality Check
Use Build Detective on a known failure and verify:
- ✅ Confidence score makes sense (8+ for clear patterns)
- ✅ Technology stack matches your project  
- ✅ Suggested solution is actionable
- ✅ No obvious contradictions

## Troubleshooting

### BD Not Available
```bash
# Re-run setup if needed
./scripts/setup-build-detective.sh /path/to/project

# Check CLAUDE.md integration
grep "build-detective" /path/to/project/CLAUDE.md
```

### GitHub CLI Issues
```bash
# Install and authenticate
brew install gh  # macOS
gh auth login --scopes "repo,read:org"

# Test access
gh repo view owner/repo
```

### Low Quality Analysis
If Build Detective gives generic responses:
1. Check confidence score (should be 7+)
2. Verify project template matches technology stack
3. Consider escalating to Sonnet for complex scenarios

## Next Steps

- 📚 [Integration Guide](INTEGRATION.md) - Team workflow integration
- 🔧 [Command Patterns](../guides/COMMAND_PATTERNS.md) - Advanced usage
- 🛡️ [Quality Control](../guides/QUALITY_CONTROL.md) - Understanding validation
- 🌐 [Multi-Project Setup](../guides/MULTI_PROJECT.md) - Organization deployment

## Success Indicators

You'll know Build Detective is working well when:
- ⚡ **Fast response**: Analysis completes in 10-30 seconds
- 🎯 **Actionable results**: Specific solutions, not generic advice
- 💰 **Cost effective**: 85% token reduction vs full Sonnet analysis
- 🔧 **Team adoption**: Developers use BD for routine CI failures

---

*Ready to solve your first build mystery? Happy investigating! 🕵️*