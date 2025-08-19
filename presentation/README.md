# Build Detective 🔍

A Claude Code agent for automated CI/CD failure analysis and reporting.

## Overview

Build Detective is an intelligent agent that monitors GitHub repositories, identifies failed CI tests, analyzes root causes, and provides actionable insights with confidence scores. Built for efficiency using Claude Haiku for analysis tasks and Claude Sonnet for orchestration.

## Architecture

```
build-detective/
├── README.md
├── ARCHITECTURE.md
├── AGENT_INSTRUCTIONS.md
├── .gitignore
├── config/
│   ├── settings.yaml
│   └── github_repos.yaml
├── src/
│   ├── main.py
│   ├── orchestrator/
│   │   ├── __init__.py
│   │   ├── supervisor.py
│   │   └── task_delegator.py
│   ├── github_integration/
│   │   ├── __init__.py
│   │   ├── client.py
│   │   ├── ci_parser.py
│   │   └── webhook_handler.py
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── failure_analyzer.py
│   │   ├── pattern_matcher.py
│   │   └── confidence_scorer.py
│   ├── issue_tracker/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   ├── deduplicator.py
│   │   └── solution_cache.py
│   ├── reporting/
│   │   ├── __init__.py
│   │   ├── report_generator.py
│   │   └── templates/
│   └── utils/
│       ├── __init__.py
│       ├── logger.py
│       └── token_optimizer.py
├── tests/
├── data/
│   ├── issues.db
│   └── cache/
└── logs/
```

## Key Features

- **GitHub Integration**: Seamless connection with GitHub Actions, CircleCI, Jenkins, Travis CI
- **Smart Analysis**: Pattern recognition for common failure types
- **Issue Tracking**: SQLite-based deduplication and solution caching
- **Cost Optimization**: Token usage monitoring and batching strategies
- **Confidence Scoring**: ML-based confidence assessment for root cause analysis
- **Version Control**: Git-based tracking of agent improvements

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/build-detective.git
cd build-detective

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Linux/macOS

# Install dependencies
pip install -r requirements.txt

# Configure GitHub access
export GITHUB_TOKEN="your-token-here"
export ANTHROPIC_API_KEY="your-api-key"

# Initialize the issue tracker database
python src/issue_tracker/database.py --init
```

## Configuration

Edit `config/settings.yaml`:

```yaml
claude:
  orchestrator_model: "claude-3-5-sonnet-20241022"
  analyzer_model: "claude-3-haiku-20240307"
  max_tokens_per_request: 1000
  temperature: 0.2

github:
  poll_interval: 300  # seconds
  max_repos: 10
  webhook_port: 8080

analysis:
  confidence_threshold: 0.7
  max_retries: 3
  cache_ttl: 3600  # seconds

reporting:
  format: "markdown"
  include_suggestions: true
  max_issues_per_report: 20
```

## Usage

### Running the Agent

```bash
# Start the Build Detective agent
python src/main.py --mode continuous

# Run once for specific repository
python src/main.py --repo owner/repo --mode single

# Generate report for recent failures
python src/main.py --report --days 7
```

### Claude Code Integration

When using with Claude Code:

```bash
# Let Claude Code manage the agent
claude-code "Monitor my GitHub repos and analyze any CI failures"

# Claude Code will automatically:
# 1. Start the Build Detective agent
# 2. Delegate analysis tasks to Haiku
# 3. Review and QC results
# 4. Suggest improvements
```

## Token Optimization Strategies

1. **Batching**: Group similar failures for analysis
2. **Caching**: Store analyzed patterns for 1 hour
3. **Compression**: Minimize log data sent to Claude
4. **Selective Analysis**: Only analyze new failure patterns
5. **Incremental Updates**: Delta-based reporting

## Issue Tracker Schema

```sql
CREATE TABLE issues (
    id INTEGER PRIMARY KEY,
    repo TEXT NOT NULL,
    build_id TEXT NOT NULL,
    test_name TEXT,
    error_signature TEXT,
    root_cause TEXT,
    confidence REAL,
    solution TEXT,
    first_seen TIMESTAMP,
    last_seen TIMESTAMP,
    occurrence_count INTEGER,
    resolved BOOLEAN
);

CREATE TABLE solutions (
    id INTEGER PRIMARY KEY,
    error_pattern TEXT UNIQUE,
    solution TEXT,
    success_rate REAL,
    usage_count INTEGER
);
```

## Development

### Adding New CI Providers

1. Create parser in `src/github_integration/ci_parser.py`
2. Add configuration mapping
3. Update webhook handler
4. Test with sample data

### Improving Analysis Accuracy

1. Collect false positive/negative feedback
2. Update pattern matching rules
3. Retrain confidence scorer
4. Version control changes with Git

## Performance Metrics

- Average analysis time: < 5 seconds per failure
- Token usage: ~500 tokens per analysis (Haiku)
- Cache hit rate target: > 60%
- Confidence accuracy: > 80%

## License

MIT
