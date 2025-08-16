# 🎯 Command Patterns Guide

Master the art of communicating with Build Detective for maximum effectiveness.

## Basic Command Structure

### Formal Analysis Request
```bash
"Use build-detective to investigate this build failure: <URL>"
```

### Shorthand Commands
```bash
"BD <error-type> <context>"
```

## Command Categories

### 🔍 Single Failure Analysis

#### GitHub Actions Failures
```bash
"Use build-detective to investigate this GitHub Actions failure: 
https://github.com/user/repo/actions/runs/12345"

"BD github actions timeout"
"BD github actions artifact missing"
"BD github actions setup failure"
```

#### Technology-Specific Errors
```bash
# Java/Maven
"BD maven compilation error"
"BD maven dependency conflict"
"BD java version mismatch"
"BD junit test failures"

# Docker
"BD docker build COPY missing file"
"BD dockerfile missing dependencies"
"BD docker compose startup failure"

# Git
"BD git submodule error"
"BD git clone authentication failure"
"BD git merge conflict in CI"
```

### 📊 Bulk Analysis Commands

#### Pattern Identification
```bash
"BD analyze last 10 CI failures for recurring patterns"
"BD check failure trends over past week"
"BD identify common issues across multiple builds"
```

#### Historical Analysis
```bash
"BD compare failure patterns between staging and production"
"BD analyze CI failures since last release"
"BD find systematic issues in build pipeline"
```

### 🎨 Context-Specific Commands

#### Project Phase Analysis
```bash
"BD investigate compilation phase failures"
"BD analyze test execution problems"
"BD check deployment pipeline issues"
"BD examine setup/initialization errors"
```

#### Technology Stack Focus
```bash
"BD maven plugin execution failures"
"BD docker multi-stage build issues"
"BD spring boot test configuration problems"
"BD github packages authentication errors"
```

## Command Modifiers

### Confidence Control
```bash
"BD analyze but flag if confidence < 8"
"BD investigate but escalate if technology mismatch detected"
"BD provide analysis with confidence assessment"
```

### Quality Assurance
```bash
"BD analyze this complex build failure but escalate if uncertain"
"BD investigate but verify against project constraints"
"BD provide quick analysis then Sonnet validate if needed"
```

### Scope Modifiers
```bash
"BD analyze recent failures in this repository only"
"BD investigate failures across all related microservices"
"BD focus on main branch failures excluding feature branches"
```

## Response Interpretation

### High Confidence (8-10)
```json
{
  "confidence": 9,
  "primary_error": "Docker COPY failed: file not found",
  "suggested_action": "Add Dockerfile to .dockerignore or verify file path"
}
```
**Action**: Trust and implement the solution

### Medium Confidence (6-7)
```json
{
  "confidence": 7,
  "primary_error": "Maven compilation failed with multiple errors",
  "suggested_action": "Check Java version compatibility and dependency conflicts"
}
```
**Action**: Consider the suggestion but verify against project context

### Low Confidence (<6)
```json
{
  "confidence": 5,
  "primary_error": "Complex multi-system failure",
  "suggested_action": "Manual review required for root cause analysis"
}
```
**Action**: Escalate to full Sonnet analysis

## Advanced Usage Patterns

### Multi-Step Investigations
```bash
# Step 1: Quick pattern check
"BD quick analysis of this CI failure for obvious patterns"

# Step 2: Deep dive if needed
"BD detailed analysis with full log examination"

# Step 3: Cross-reference
"BD compare this failure with similar historical issues"
```

### Workflow Integration
```bash
# Pre-commit analysis
"BD analyze local build failure before pushing"

# Code review support
"BD check if CI failures in this PR are code-related"

# Release pipeline
"BD investigate deployment failures blocking production release"
```

### Team Collaboration
```bash
# Handoff documentation
"BD analyze and document this failure for team knowledge base"

# Pattern sharing
"BD identify if this failure pattern exists in other team projects"

# Training scenarios
"BD explain this build failure for new team member learning"
```

## Quality Control Commands

### Validation Requests
```bash
"BD analyze but Sonnet verify the technology stack alignment"
"BD investigate with automatic escalation if solution seems generic"
"BD provide analysis with quality confidence assessment"
```

### Error Prevention
```bash
"BD check if this solution conflicts with our project constraints"
"BD verify suggested fix doesn't introduce new dependencies"
"BD assess if this is recurring issue needing systematic fix"
```

## Troubleshooting Commands

### When BD Analysis Seems Wrong
```bash
"Sonnet review this BD analysis - confidence seems too high for complexity"
"Manual analysis needed - BD suggestion doesn't match project context"
"Escalate to human review - BD technology classification appears incorrect"
```

### Quality Recovery
```bash
"Override BD analysis and provide correct solution"
"Document BD error pattern for future improvement"
"Add escalation trigger for similar scenarios"
```

## Best Practices

### ✅ Effective Commands
- **Be specific**: "BD maven compiler plugin failure" vs "BD build error"
- **Include context**: "BD docker build failure in GitHub Actions"
- **Use technology names**: "BD spring boot test configuration"
- **Request confidence**: "BD analyze with confidence assessment"

### ❌ Avoid These Patterns
- **Too vague**: "BD fix my build"
- **Wrong scope**: "BD analyze all failures ever"
- **No context**: "BD error"
- **Blind trust**: Accepting low-confidence analysis without verification

### 🎯 Optimization Tips
- **Batch analysis**: Group related failures for pattern recognition
- **Technology focus**: Match commands to your project's tech stack
- **Quality gates**: Always check confidence scores
- **Learning loop**: Document patterns for team knowledge

## Command Cheat Sheet

| Error Type | Command Pattern | Example |
|------------|----------------|---------|
| Maven | `BD maven <specific-error>` | `BD maven dependency conflict` |
| Docker | `BD docker <build-phase>` | `BD docker COPY missing file` |
| Git | `BD git <operation>` | `BD git submodule initialization` |
| GitHub Actions | `BD github actions <step>` | `BD github actions artifact timeout` |
| Java | `BD java <version/compilation>` | `BD java version mismatch` |
| Tests | `BD test <framework>` | `BD junit test execution failure` |

---

*Master these patterns and Build Detective becomes your most reliable CI debugging partner.* 🕵️‍♀️