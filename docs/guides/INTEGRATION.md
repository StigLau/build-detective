# Build Detective Integration Examples

## CLAUDE.md Integration Patterns

### Basic Delegation Strategy
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

### Advanced Delegation with Quality Control
```markdown
### Build Detective Integration Pattern
**CRITICAL**: Use Build Detective with Sonnet oversight:

1. **Delegate to build-detective** for CI failures, build errors
2. **Sonnet validates** BD analysis using quality checks:
   - Confidence score vs complexity alignment
   - Technology stack match verification
   - Solution feasibility assessment
3. **Escalate to manual** if BD confidence < 7 or context mismatch detected
4. **Document lessons** learned for BD pattern improvement

### Build Detective Quality Checklist
Before accepting BD analysis, verify:
- [ ] BD confidence aligns with error complexity
- [ ] Technology stack matches project reality
- [ ] Suggested solution is project-feasible
- [ ] Error classification matches actual build phase
- [ ] No obvious context contradictions present
```

### Project-Specific Customization
```markdown
### Project Context for Build Detective
**Technology Stack**: Java 21, Maven 3.9, Spring Boot 3.1, Docker
**Common Issues**: 
- Maven plugin version conflicts with Java 21
- Docker multi-stage build layer caching issues
- Spring Boot test slice configuration problems
**Deployment Target**: AWS ECS with GitHub Actions CI/CD
**Dependencies**: PostgreSQL, Redis, OpenAPI codegen
```

## Team Workflow Integration

### Pull Request Template Addition
```markdown
## CI Failure Checklist
If CI is failing:
1. Use Build Detective: `"BD analyze GitHub Actions failure in this PR"`
2. If BD confidence < 7, escalate to manual review
3. Apply suggested fixes and re-run CI
4. Document any new patterns discovered for future reference
```

### Code Review Guidelines
```markdown
### CI Failure Review Process
1. **Quick Analysis**: Reviewer uses BD to identify obvious issues
2. **Confidence Check**: Accept BD analysis only if confidence ≥ 7
3. **Context Validation**: Verify BD solution matches project constraints
4. **Escalation**: If BD analysis seems wrong, perform manual review
5. **Learning**: Document any BD mistakes for pattern improvement
```

## Development Environment Setup

### VS Code Integration
```json
{
  "tasks": [
    {
      "label": "Analyze Build Failure with BD",
      "type": "shell",
      "command": "echo 'Use build-detective to investigate build failure in current branch'",
      "group": "build",
      "presentation": {
        "echo": true,
        "reveal": "always"
      }
    }
  ]
}
```

### Git Hooks Integration
```bash
#!/bin/bash
# pre-push hook
if [ "$(git status --porcelain)" ]; then
  echo "Running local build check with BD patterns..."
  # Add BD pattern checking logic here
fi
```

## CI/CD Pipeline Integration

### GitHub Actions Workflow
```yaml
name: CI with Build Detective Analysis
on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up build environment
      # ... build steps ...
    
    - name: Analyze Failures with BD on Failure
      if: failure()
      run: |
        echo "Build failed - BD analysis patterns:"
        echo "- Check for common Maven plugin conflicts"
        echo "- Verify Java version compatibility"
        echo "- Review Docker layer caching issues"
        # Could integrate with actual BD analysis here
```

### Jenkins Pipeline Integration
```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                script {
                    try {
                        sh 'mvn clean compile'
                    } catch (Exception e) {
                        echo "Build failed - Apply BD analysis patterns:"
                        echo "- Maven dependency conflicts"
                        echo "- Java version mismatches"
                        echo "- Plugin execution failures"
                        throw e
                    }
                }
            }
        }
    }
}
```

## Multi-Project Deployment

### Template Deployment Script
```bash
#!/bin/bash
# deploy-bd-to-all-projects.sh

PROJECTS=(
    "/projects/backend-api"
    "/projects/frontend-app" 
    "/projects/data-pipeline"
    "/projects/mobile-backend"
)

for project in "${PROJECTS[@]}"; do
    echo "Setting up Build Detective for $project"
    ./setup-build-detective.sh "$project"
    
    # Add project-specific customization
    if [[ "$project" == *"backend"* ]]; then
        echo "Applying backend-specific BD patterns..."
    elif [[ "$project" == *"frontend"* ]]; then
        echo "Applying frontend-specific BD patterns..."
    fi
done
```

### Organization-Wide Rollout
```markdown
### Build Detective Rollout Plan

**Phase 1**: Pilot Projects (Week 1-2)
- Deploy to 2-3 high-activity repositories
- Gather feedback on analysis accuracy
- Refine patterns based on real usage

**Phase 2**: Core Services (Week 3-4)  
- Deploy to critical service repositories
- Train team leads on BD usage and validation
- Establish escalation procedures

**Phase 3**: All Repositories (Week 5-6)
- Organization-wide deployment
- Create shared pattern library
- Implement feedback collection system

**Success Metrics**:
- BD analysis acceptance rate > 80%
- Average time to CI issue resolution < 10 minutes
- False positive rate < 10%
```

## Troubleshooting Integration Issues

### Common Setup Problems
```markdown
### BD Not Working Checklist

1. **Template File Missing**
   ```bash
   ls -la .claude/agents/build-detective.md
   # If missing, re-run setup script
   ```

2. **GitHub CLI Not Authenticated**
   ```bash
   gh auth status
   gh auth login
   ```

3. **Wrong Template Path in Script**
   - Check script points to correct template directory
   - Verify template file exists and is readable

4. **CLAUDE.md Integration Missing**
   - Add delegation strategy to project CLAUDE.md
   - Ensure subagent name matches template exactly
```

### Quality Issues
```markdown
### When BD Analysis Seems Wrong

**Immediate Actions**:
1. Check BD confidence score (< 7 = unreliable)
2. Verify technology stack matches project
3. Review solution against project constraints
4. Escalate to manual Sonnet analysis

**Documentation**:
1. Record what BD got wrong
2. Identify pattern improvement needed
3. Update team knowledge base
4. Consider adding escalation trigger
```

## Advanced Usage Patterns

### Bulk Historical Analysis
```markdown
# Team retrospective using BD
"BD analyze all CI failures from last sprint to identify recurring issues"

# Pattern trend analysis
"BD review CI failure patterns over last month for systemic issues"

# Cross-repository comparison
"BD compare failure patterns between microservices to find common root causes"
```

### Custom Pattern Development
```markdown
### Adding Project-Specific Patterns

1. **Identify Recurring Issues**
   - Collect failed build logs
   - Extract common error patterns
   - Document typical solutions

2. **Enhance BD Template**
   - Add patterns to `{{COMMON_ISSUE_X}}` sections
   - Include project-specific dependencies
   - Update technology stack information

3. **Test and Validate**
   - Apply to historical failures
   - Verify accuracy with team
   - Refine based on feedback

4. **Share with Team**
   - Update team documentation
   - Train team on new patterns
   - Establish feedback loop for improvements
```