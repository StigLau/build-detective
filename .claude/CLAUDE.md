# Build Detective Multi-Agent Architecture

This project implements a hierarchical multi-agent system for CI/CD failure analysis following patterns from StigLau's LLM sub-agents template.

## Agent Hierarchy

```
Architect Agent (Master Orchestrator)
├── CI Analysis Specialist Agent
├── Cost Optimization Agent  
├── Validation Agent
└── Project Discovery Agent
```

## Agent Coordination Patterns

### Sequential Chain Analysis
```
task → architect-agent → ci-specialist-agent → validation-agent → result
```

### Parallel Execution
```
architect-agent → {ci-specialist, cost-optimizer} → integration → validation
```

### Conditional Routing
```
architect-agent → analyzes_complexity → routes_to_appropriate_specialist(s)
```

## Core Agents

### 1. Architect Agent
**Role**: Master orchestrator and decision router
**Responsibilities**:
- Analyze incoming CI failure requests
- Route to appropriate specialist agents
- Coordinate multi-agent workflows
- Aggregate results and provide final analysis

### 2. CI Analysis Specialist Agent  
**Role**: Domain expert for CI/CD pattern recognition
**Responsibilities**:
- Deep analysis of build failures
- Pattern matching against known CI/CD issues
- Technology-specific diagnostics (Maven, Docker, Python, etc.)
- Log parsing and error extraction

### 3. Cost Optimization Agent
**Role**: AI cost management and routing
**Responsibilities**:
- Route analysis to Haiku vs Claude based on complexity
- Track daily/monthly AI usage costs
- Optimize prompt engineering for cost efficiency
- Budget enforcement and alerting

### 4. Validation Agent
**Role**: Solution verification and testing
**Responsibilities**:
- Verify suggested fixes make sense
- Cross-reference solutions against project context
- Confidence scoring for recommendations
- Post-analysis validation

### 5. Project Discovery Agent
**Role**: Adaptive project structure understanding
**Responsibilities**:
- Analyze project structure and technologies
- Identify testing frameworks and build systems
- Adapt analysis patterns to project context
- Learn from project-specific patterns

## Agent Communication Protocol

Agents communicate via structured JSON messages:

```json
{
  "agent": "architect",
  "task_id": "bd_analysis_001",
  "request_type": "analyze_ci_failure",
  "data": {
    "github_actions_url": "...",
    "priority": "high",
    "context": {}
  },
  "routing": {
    "target_agents": ["ci-specialist", "cost-optimizer"],
    "execution_mode": "parallel"
  }
}
```

## Build Detective Integration

The multi-agent system enhances Build Detective's core capabilities:

1. **Intelligent Routing**: Complex failures → Claude Sonnet, Simple patterns → Haiku
2. **Context Awareness**: Project-specific pattern learning and adaptation  
3. **Cost Optimization**: AI usage tracking and budget management
4. **Quality Assurance**: Multi-agent validation and confidence scoring
5. **Scalability**: Parallel analysis for multi-repository scenarios

## Usage Patterns

### Standard CI Analysis
```python
# Via Task tool
Task(
    description="Analyze GitHub Actions failure",
    prompt="Analyze failure at https://github.com/repo/actions/runs/123",
    subagent_type="build-detective-architect"
)
```

### Advanced Multi-Agent Analysis  
```python
# Complex multi-step analysis
Task(
    description="Deep analysis with validation",
    prompt="Analyze and validate solutions for repo-wide CI failures",
    subagent_type="build-detective-architect",
    options={"mode": "comprehensive", "validate": True}
)
```

## Agent Development

Each agent follows the template pattern:
- **Isolated contexts**: No shared state between agents
- **Clear interfaces**: Structured input/output contracts
- **Autonomous operation**: Can function independently
- **Composable workflows**: Easy to chain and parallelize

## External Integration

- **GitHub CLI**: Repository and CI data access
- **Anthropic API**: Haiku/Claude routing based on complexity
- **Build Systems**: Maven, Docker, UV, etc. integration
- **Monitoring**: Cost tracking and performance metrics