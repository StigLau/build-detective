# Build Detective Troubleshooting Guide

## Setup Issues

### BD Template Not Found
**Problem**: Setup script can't find template file
```bash
Error: Template file not found at 'templates/build-detective-template.md'
```

**Solutions**:
```bash
# Verify template exists
ls -la templates/build-detective-template.md

# If missing, check package integrity
ls -la templates/

# Re-download package if corrupted
```

### Permission Denied During Setup
**Problem**: Can't create .claude/agents directory
```bash
mkdir: cannot create directory '.claude/agents': Permission denied
```

**Solutions**:
```bash
# Check directory permissions
ls -la /path/to/target/project

# Fix permissions if needed
chmod 755 /path/to/target/project

# Try setup with sudo if necessary (not recommended)
sudo ./setup-build-detective.sh /path/to/project
```

### Git Repository Warning
**Problem**: Warning about non-git directory
```bash
Warning: '/path/to/project' is not a git repository
```

**Solutions**:
- **Continue anyway**: BD works in non-git directories
- **Initialize git**: `git init` in target directory
- **Point to git repository**: Use actual git repository path

## BD Analysis Issues

### BD Subagent Not Available
**Problem**: Claude doesn't recognize build-detective subagent
```
Error: Unknown subagent 'build-detective'
```

**Solutions**:
```bash
# Verify BD file exists
ls -la .claude/agents/build-detective.md

# Check file content
head -20 .claude/agents/build-detective.md

# Re-run setup if file missing
./setup-build-detective.sh .

# Check CLAUDE.md integration
grep -n "build-detective" CLAUDE.md
```

### GitHub CLI Integration Problems
**Problem**: BD can't access GitHub repositories
```bash
gh: not found
# or
gh auth status: not authenticated
```

**Solutions**:
```bash
# Install GitHub CLI
brew install gh  # macOS
# or
sudo apt install gh  # Ubuntu

# Authenticate
gh auth login

# Test access
gh repo view owner/repo
gh run list --repo owner/repo --status failure
```

### BD Analysis Quality Issues

#### Generic Solutions
**Problem**: BD provides vague solutions like "check configuration"
```json
{
  "suggested_action": "Check configuration and verify setup",
  "confidence": 6
}
```

**Diagnosis**: BD couldn't find specific pattern match
**Action**: Escalate to Sonnet for manual analysis

#### Technology Stack Mismatch
**Problem**: BD suggests Java solutions for Python project
```json
{
  "error_type": "java_version",
  "primary_error": "Maven compilation failed"
}
```

**Diagnosis**: BD applied wrong pattern library
**Action**: 
1. Check project template customization
2. Update `{{PRIMARY_LANGUAGE}}` in BD template
3. Re-run setup with correct language

#### Overconfident Analysis
**Problem**: BD shows confidence 10 for complex scenario
```json
{
  "confidence": 10,
  "primary_error": "Simple dependency issue"
}
```

**Diagnosis**: Perfect confidence suspicious for real CI failures
**Action**: Apply Sonnet validation patterns - verify accuracy

## Validation System Issues

### False Positive Detection
**Problem**: BD incorrectly identifies error pattern

**Validation Checks**:
```python
# Check if error matches project context
if bd_result["error_type"] == "maven" and not project.has_pom_xml():
    escalate_to_sonnet()

# Verify build phase logic  
if bd_result["build_step"] == "test" and "BUILD FAILURE" in log:
    escalate_to_sonnet()

# Check solution feasibility
if "update dependency" in solution and project.has_version_locks():
    escalate_to_sonnet()
```

**Actions**:
1. Document the false positive
2. Update BD pattern library
3. Add escalation trigger for similar cases
4. Test updated patterns against historical data

### Low Confidence Scenarios
**Problem**: BD consistently returns confidence < 7

**Common Causes**:
- Complex multi-system failures
- Custom build configurations
- Environmental issues
- First-time error patterns

**Actions**:
1. Use Sonnet for manual analysis
2. Document new patterns discovered
3. Update BD template with new patterns
4. Set appropriate escalation triggers

## Performance Issues

### Slow BD Analysis
**Problem**: BD takes longer than expected (>60 seconds)

**Diagnosis Steps**:
```bash
# Check if GitHub CLI is slow
time gh run view <run-id> --log

# Test BD template loading
time cat .claude/agents/build-detective.md

# Verify network connectivity
ping github.com
```

**Solutions**:
- Use cached analysis for repeated requests
- Optimize GitHub CLI queries
- Consider local log file analysis instead of remote

### Token Usage Higher Than Expected
**Problem**: BD using more tokens than 400-800 range

**Common Causes**:
- Large log files being analyzed
- Complex error scenarios
- Multiple pattern matching attempts

**Solutions**:
- Truncate log files to relevant sections
- Use log filtering for specific error types
- Implement pattern prioritization

## Integration Problems

### CLAUDE.md Delegation Not Working
**Problem**: Subagent delegation not triggering

**Check CLAUDE.md Integration**:
```markdown
# Verify delegation strategy exists
grep -A 5 -B 5 "build-detective" CLAUDE.md

# Check for typos in subagent name
grep -i "detective" CLAUDE.md

# Ensure proper formatting
```

**Correct Format**:
```markdown
### Subagent Delegation Strategy
- **CI/Build Analysis**: Use `build-detective` subagent for GitHub Actions failures
```

### Team Adoption Issues
**Problem**: Team not using BD consistently

**Common Barriers**:
- Lack of training on BD usage patterns
- Uncertainty about when to trust BD analysis
- No clear escalation procedures

**Solutions**:
1. Provide BD training session
2. Create quick reference cards
3. Establish clear escalation criteria
4. Document success stories and lessons learned

## Quality Assurance Problems

### Sonnet Validation Failures
**Problem**: Sonnet incorrectly overriding good BD analysis

**Debug Steps**:
```python
# Check validation trigger logic
def debug_validation_triggers(bd_result, context):
    print(f"Confidence: {bd_result['confidence']}")
    print(f"Error type: {bd_result['error_type']}")
    print(f"Project has Java: {context.has_java_files()}")
    print(f"Solution: {bd_result['suggested_action']}")
    
    # Check each validation rule
    if bd_result["confidence"] < 7:
        print("TRIGGER: Low confidence")
    
    if "java" in bd_result["error_type"] and not context.has_java_files():
        print("TRIGGER: Technology mismatch")
```

**Tuning Actions**:
1. Adjust confidence thresholds
2. Refine technology detection logic
3. Update context validation rules
4. Test validation against known good analyses

### Pattern Library Drift
**Problem**: BD patterns becoming less accurate over time

**Monitoring Metrics**:
- Pattern success rates
- User feedback scores
- False positive/negative rates
- Escalation frequency

**Maintenance Actions**:
1. Regular pattern accuracy review
2. Update patterns based on user feedback
3. Retire low-performing patterns
4. Add new patterns for emerging error types

## Emergency Procedures

### BD Completely Wrong Analysis
**Immediate Actions**:
1. Document the incorrect analysis
2. Use Sonnet for correct analysis
3. Apply manual fix
4. Record lesson learned

**Follow-up Actions**:
1. Analyze why BD failed
2. Update pattern library
3. Add escalation trigger
4. Test fix against similar scenarios

### System-Wide BD Failure
**Problem**: BD not working across multiple projects

**Diagnosis**:
```bash
# Check core components
ls -la templates/build-detective-template.md
./setup-build-detective.sh --test-mode
gh auth status

# Verify template integrity
md5sum templates/build-detective-template.md
```

**Recovery**:
1. Re-download BD package
2. Verify all files present
3. Re-run setup on affected projects
4. Test with known failure scenario

## Getting Help

### Self-Diagnosis Checklist
- [ ] BD template file exists and is readable
- [ ] GitHub CLI installed and authenticated
- [ ] CLAUDE.md delegation properly configured
- [ ] Project context matches BD template
- [ ] Confidence scores align with complexity

### Documentation Resources
1. **BUILD_DETECTIVE_COMPREHENSIVE_GUIDE.md** - Complete usage guide
2. **BUILD_DETECTIVE_QUALITY_ASSURANCE.md** - Quality control system
3. **BD_CONFIDENCE_VALIDATION_PATTERNS.md** - Technical validation details
4. **QUICK_REFERENCE.md** - Command patterns and confidence interpretation

### Community Support
- Review historical usage patterns in project
- Check team documentation for project-specific patterns
- Consult with team leads on escalation procedures
- Document new issues for future reference