# 📊 Examples

Real-world Build Detective usage examples and success stories.

## Example Analysis Results

### Java Version Mismatch
**Scenario**: GitHub Actions using Java 11, pom.xml configured for Java 17

**Command**: `"BD investigate maven compilation failure"`

**BD Response**:
```json
{
  "confidence": 9,
  "error_type": "java_version",
  "build_step": "compile",
  "primary_error": "release version 17 not supported",
  "suggested_action": "Update GitHub Actions setup-java to version 17 or change pom.xml target to 11",
  "pattern_matched": "java_version_mismatch_ci"
}
```

**Outcome**: ✅ **Correct** - Solution implemented in 2 minutes

### Docker COPY Missing File
**Scenario**: Docker build failing on COPY instruction

**Command**: `"BD docker build COPY instruction failure"`

**BD Response**:
```json
{
  "confidence": 10,
  "error_type": "docker_build",
  "build_step": "package",
  "primary_error": "COPY failed: file not found: target/app.jar",
  "suggested_action": "Run 'mvn package' before docker build or use multi-stage build",
  "pattern_matched": "docker_copy_missing_artifact"
}
```

**Outcome**: ✅ **Correct** - Added maven build stage to Dockerfile

### Git Submodule Configuration Error
**Scenario**: CI failing during git checkout with submodule error

**Command**: `"BD git submodule initialization failure"`

**BD Response**:
```json
{
  "confidence": 8,
  "error_type": "git_submodule",
  "build_step": "setup",
  "primary_error": "fatal: No url found for submodule path 'lib/external' in .gitmodules",
  "suggested_action": "Add submodule URL to .gitmodules or remove submodule reference",
  "pattern_matched": "git_submodule_missing_url"
}
```

**Outcome**: ✅ **Correct** - Fixed .gitmodules configuration

## Bulk Analysis Examples

### Pattern Identification Across 10 Builds
**Command**: `"BD analyze last 10 CI failures for recurring patterns"`

**BD Response**:
```json
{
  "analysis_type": "bulk_pattern",
  "total_failures": 10,
  "patterns_identified": [
    {
      "pattern": "maven_dependency_timeout",
      "frequency": 6,
      "confidence": 9,
      "root_cause": "External repository unavailable",
      "suggested_action": "Add backup repository or cache dependencies"
    },
    {
      "pattern": "test_flakiness",
      "frequency": 3,
      "confidence": 7,
      "root_cause": "Timing-dependent test assertions",
      "suggested_action": "Review test stability and add wait conditions"
    }
  ]
}
```

**Outcome**: ✅ **Valuable insights** - Team addressed repository caching and test flakiness systematically

## Quality Control Examples

### Low Confidence Escalation
**Scenario**: Complex multi-module Maven build failure

**Command**: `"BD analyze complex maven reactor build failure"`

**BD Response**:
```json
{
  "confidence": 5,
  "error_type": "complex_multi_system",
  "primary_error": "Multiple interconnected failures across modules",
  "suggested_action": "Manual analysis required - complex dependency chain issue",
  "escalation_required": true
}
```

**Outcome**: ✅ **Correct escalation** - Sonnet provided detailed multi-module analysis

### Technology Mismatch Detection
**Scenario**: BD incorrectly identifying Java error in Python project

**Validation Trigger**:
```python
if bd_result["error_type"] == "java" and not project.has_java_files():
    escalate_to_sonnet("Technology stack mismatch detected")
```

**Outcome**: ✅ **Validation caught error** - Prevented misleading analysis

## Advanced Usage Examples

### Cross-Repository Analysis
**Command**: `"BD compare failure patterns between microservice-a and microservice-b repositories"`

**Use Case**: Identifying common infrastructure issues across related services

**Result**: Discovered shared Docker base image causing memory issues in both services

### Historical Trend Analysis
**Command**: `"BD analyze CI failure trends over past month for systematic issues"`

**Use Case**: Sprint retrospective analysis

**Result**: Identified that 60% of failures were related to test environment instability

### Pre-Release Pipeline Analysis
**Command**: `"BD investigate all failures in release/v2.0 branch builds"`

**Use Case**: Release readiness assessment

**Result**: Found 3 blocking issues that needed resolution before release

## Team Workflow Integration Examples

### Pull Request Analysis
```markdown
## PR Review Checklist
- [ ] Code review completed
- [ ] Tests passing locally
- [ ] **BD analysis**: `"BD check CI failures in this PR"`
- [ ] No new architectural concerns
```

### Incident Response
```markdown
## Production Deployment Failed

**Step 1**: `"BD analyze deployment pipeline failure"`
**Result**: Docker registry authentication timeout
**Resolution**: Updated registry credentials
**Time to resolution**: 8 minutes (vs previous 45+ minutes)
```

### Onboarding New Developers
```markdown
## Build Failure Training

**Scenario**: Show new developer common CI failure
**Command**: `"BD explain this maven compilation error for learning purposes"`
**Result**: Clear explanation of Java classpath issues with actionable solution
```

## Performance Metrics

### Token Usage Comparison
```
Traditional Analysis (Sonnet):
- Average tokens: 3,200
- Time: 3-5 minutes
- Cost: High

Build Detective + Validation:
- Average tokens: 650
- Time: 45 seconds
- Cost: 80% reduction
```

### Accuracy by Pattern Type
```
High Confidence Patterns (8-10):
- Docker build issues: 94% accuracy
- Java version conflicts: 92% accuracy
- Maven plugin failures: 89% accuracy

Medium Confidence (6-7):
- Dependency conflicts: 83% accuracy (with validation)
- Test failures: 81% accuracy (with validation)
```

### Team Adoption Metrics
```
6-Month Usage Statistics:
- BD analyses performed: 847
- Accepted without review: 76%
- Escalated to Sonnet: 18%
- User-reported errors: 6%
- Average resolution time: 3.2 minutes (down from 18 minutes)
```

## Common Success Patterns

### ✅ **Quick Wins** (90%+ success rate)
- Standard Maven/Gradle build errors
- Docker COPY/ADD instruction failures
- GitHub Actions timeout issues
- Git submodule configuration problems

### ✅ **Good Coverage** (80-85% success rate)
- Dependency version conflicts
- Test execution failures
- Authentication/permission issues
- Memory allocation problems

### ⚠️ **Requires Validation** (escalated)
- Complex multi-system integration failures
- First-time custom build configurations
- Performance-related build issues
- Security/permission edge cases

## Anti-Patterns and Lessons Learned

### ❌ **What Doesn't Work Well**
- Expecting BD to handle novel, never-seen error patterns
- Using BD for architectural design decisions
- Trusting low-confidence (<7) analysis without validation
- Applying BD to highly custom build systems

### 📚 **Lessons Learned**
1. **Confidence scores matter** - Always check before accepting analysis
2. **Technology alignment** - Ensure BD understands your project stack
3. **Pattern evolution** - BD gets better with usage and feedback
4. **Team training** - Developers need to understand when to escalate

---

*These examples show Build Detective in action - fast, accurate, and continuously improving through real-world usage.* 📊