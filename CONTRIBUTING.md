# 🤝 Contributing to Build Detective

We welcome contributions from the community! Build Detective gets better with real-world usage and diverse perspectives.

## 🚀 Quick Start for Contributors

```bash
# Fork and clone
git clone https://github.com/yourusername/build-detective.git
cd build-detective

# Test the setup
./scripts/setup-build-detective.sh ./test-project

# Make your changes
# ...

# Test your changes
./scripts/test-setup.sh
```

## 🎯 Ways to Contribute

### 🔍 **Pattern Library Improvements**
- **Add new error patterns** you've encountered
- **Improve existing patterns** with better solutions
- **Technology support** for new build systems
- **Test coverage** for pattern accuracy

### 📚 **Documentation Enhancements**
- **Usage examples** from real projects
- **Integration guides** for new tools/workflows
- **Troubleshooting solutions** for common issues
- **Translation** to other languages

### 🧪 **Quality Assurance**
- **Validation rule improvements** for better accuracy
- **Test cases** for edge scenarios
- **Performance optimizations** for token usage
- **Confidence calibration** improvements

### 🔧 **Template Expansions**
- **New project types** (Rust, Go, Python, etc.)
- **Framework-specific patterns** (Spring Boot, React, etc.)
- **CI/CD platforms** (Jenkins, GitLab CI, etc.)
- **Deployment targets** (AWS, GCP, Azure, etc.)

## 📋 Contribution Guidelines

### 🎨 **Pattern Contributions**

When adding new error patterns, include:

1. **Pattern Definition**
```yaml
# templates/patterns/new-pattern.yaml
pattern_id: "new_error_pattern"
technology: "maven"
confidence_level: 8
error_indicators:
  - "Specific error message text"
  - "Another error indicator"
solution:
  description: "Clear explanation of the fix"
  commands:
    - "mvn clean install"
  verification: "How to verify the fix worked"
test_cases:
  - log_snippet: "Example error log"
    expected_confidence: 8
    expected_solution: "Expected solution text"
```

2. **Real-World Evidence**
- Link to public CI failure demonstrating the pattern
- Evidence of solution effectiveness
- Context about when this pattern occurs

3. **Test Coverage**
```bash
# Test your pattern
./scripts/test-pattern.sh new-pattern.yaml
```

### 📖 **Documentation Standards**

- **Clear headings** with emoji for visual scanning
- **Code examples** with proper syntax highlighting
- **Real-world scenarios** not just theoretical
- **Before/after comparisons** showing improvements
- **Links to related sections** for easy navigation

### 🧪 **Quality Standards**

All contributions must:
- ✅ **Pass existing tests** without breaking functionality
- ✅ **Include test coverage** for new functionality
- ✅ **Follow naming conventions** established in codebase
- ✅ **Update documentation** for user-facing changes
- ✅ **Maintain token efficiency** (target <1000 tokens per analysis)

## 🔄 Development Workflow

### 1. **Issue First**
- Check existing issues before starting work
- Create an issue describing your planned contribution
- Discuss approach with maintainers if it's a significant change

### 2. **Branch Strategy**
```bash
# Create feature branch
git checkout -b feature/new-error-pattern

# Make changes
# ...

# Test thoroughly
./scripts/test-all.sh

# Commit with descriptive message
git commit -m "Add Maven plugin timeout error pattern

- Handles 'Plugin execution timeout' scenarios
- Includes solution for increasing timeout limits
- Test coverage for common timeout scenarios"
```

### 3. **Pull Request Process**
- **Clear description** of what problem you're solving
- **Before/after examples** showing the improvement
- **Test results** demonstrating your changes work
- **Documentation updates** if user-facing changes
- **Link to related issues** being addressed

## 🧪 Testing Your Changes

### Pattern Testing
```bash
# Test specific pattern
./scripts/test-pattern.sh my-new-pattern.yaml

# Test pattern library integrity
./scripts/validate-patterns.sh

# Test template generation
./scripts/test-template-generation.sh
```

### Integration Testing
```bash
# Test full setup process
./scripts/test-setup.sh /tmp/test-project

# Test quality validation
./scripts/test-validation-rules.sh

# Performance testing
./scripts/benchmark-token-usage.sh
```

### Documentation Testing
```bash
# Test all links work
./scripts/check-documentation-links.sh

# Test code examples execute
./scripts/test-documentation-examples.sh
```

## 📊 Pattern Contribution Examples

### High-Impact Contributions

#### New Technology Support
```yaml
# Adding Rust/Cargo support
pattern_id: "cargo_dependency_conflict"
technology: "rust"
build_system: "cargo"
error_indicators:
  - "failed to resolve dependencies"
  - "conflicting dependencies"
solution:
  description: "Update Cargo.toml dependency versions"
  commands:
    - "cargo update"
    - "cargo check"
```

#### Framework-Specific Patterns
```yaml
# Spring Boot specific issues
pattern_id: "spring_boot_port_conflict"
technology: "java"
framework: "spring_boot"
error_indicators:
  - "Port 8080 was already in use"
  - "Address already in use"
solution:
  description: "Configure different port or stop conflicting process"
  commands:
    - "lsof -ti:8080 | xargs kill -9"
    - "export SERVER_PORT=8081"
```

### Quality Improvements

#### Better Error Classification
```python
# Improved confidence scoring
def calculate_confidence(error_text, context):
    """
    Enhanced confidence calculation considering:
    - Pattern specificity
    - Context alignment  
    - Historical accuracy
    """
    base_confidence = pattern_match_score(error_text)
    
    # Adjust for context
    if technology_matches(context):
        base_confidence += 1
    
    # Adjust for pattern history
    pattern_accuracy = get_historical_accuracy(pattern_id)
    if pattern_accuracy < 0.8:
        base_confidence -= 2
    
    return min(10, max(1, base_confidence))
```

#### Validation Rule Enhancements
```python
# New validation rules
def validate_dependency_suggestions(bd_result, project_context):
    """
    Check if dependency suggestions conflict with:
    - Project license requirements
    - Security policies
    - Version lock files
    """
    if "add dependency" in bd_result["suggested_action"]:
        if project_context.has_dependency_locks():
            return ValidationFlag("DEPENDENCY_LOCKED")
    
    return None
```

## 🏷️ Issue Labels

When creating issues, use appropriate labels:

- `🔍 pattern-addition` - New error pattern to add
- `🐛 pattern-bug` - Existing pattern not working correctly  
- `📚 documentation` - Documentation improvements
- `🧪 testing` - Test coverage improvements
- `⚡ performance` - Token usage or speed optimizations
- `🎨 enhancement` - General improvements
- `❓ question` - Questions about usage or implementation

## 🎉 Recognition

Contributors will be recognized in:
- **README.md** acknowledgments section
- **CONTRIBUTORS.md** detailed contribution list
- **Release notes** for significant contributions
- **Pattern library** attribution for major patterns

## 📞 Getting Help

- **GitHub Issues** - For bugs and feature requests
- **GitHub Discussions** - For questions and general discussion  
- **Documentation** - Check docs/ folder for detailed guides
- **Examples** - See examples/ folder for usage patterns

## 🔮 Roadmap

Upcoming areas where contributions are especially welcome:

### Short Term (Next Release)
- **Python/pip** error patterns
- **Go modules** support
- **GitHub Actions** advanced patterns
- **Performance** optimizations

### Medium Term
- **Kubernetes** deployment failures
- **Terraform** infrastructure issues
- **IDE integrations** (VS Code, IntelliJ)
- **Slack/Teams** bot integration

### Long Term
- **Machine learning** pattern classification
- **Community pattern** sharing platform
- **Enterprise features** for large organizations
- **Multi-language** support

---

**Thank you for helping make Build Detective better for everyone!** 🕵️‍♀️

*Every contribution, no matter how small, helps developers around the world solve their CI mysteries faster.* 🌍