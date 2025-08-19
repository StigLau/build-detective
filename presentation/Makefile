# Build Detective Makefile
# Simplified commands for development and presentation

.PHONY: help install test analyze clean setup

# Colors for output
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(GREEN)🕵️ Build Detective - Available Commands:$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}'
	@echo ""

setup: ## Initial setup - create directories and install dependencies
	@echo "$(GREEN)🔧 Setting up Build Detective...$(NC)"
	mkdir -p data logs config
	touch data/.gitkeep logs/.gitkeep
	@if [ ! -f .env ]; then \
		echo "# Build Detective Environment Variables" > .env; \
		echo "ANTHROPIC_API_KEY=your_api_key_here" >> .env; \
		echo "$(YELLOW)⚠️  Please update .env with your Anthropic API key$(NC)"; \
	fi
	@echo "$(GREEN)✅ Setup complete$(NC)"

install: setup ## Install Python dependencies
	@echo "$(GREEN)📦 Installing dependencies...$(NC)"
	pip install -r requirements.txt
	@echo "$(GREEN)✅ Dependencies installed$(NC)"

test-cli: ## Test CLI interface
	@echo "$(GREEN)🧪 Testing CLI interface...$(NC)"
	python src/main.py --help
	@echo "$(GREEN)✅ CLI test passed$(NC)"

analyze: ## Analyze a repository (usage: make analyze REPO=owner/repo)
	@if [ -z "$(REPO)" ]; then \
		echo "$(RED)❌ Usage: make analyze REPO=owner/repo$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)🔍 Analyzing $(REPO)...$(NC)"
	cd src && python main.py --repo $(REPO) --mode single

analyze-pr: ## Analyze a specific PR (usage: make analyze-pr REPO=owner/repo PR=123)
	@if [ -z "$(REPO)" ] || [ -z "$(PR)" ]; then \
		echo "$(RED)❌ Usage: make analyze-pr REPO=owner/repo PR=123$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)🔍 Analyzing $(REPO) PR#$(PR)...$(NC)"
	cd src && python main.py --repo $(REPO) --pr $(PR)

monitor: ## Start continuous monitoring mode
	@echo "$(GREEN)👁️ Starting continuous monitoring...$(NC)"
	cd src && python main.py --mode continuous

report: ## Generate failure report for last 7 days
	@echo "$(GREEN)📊 Generating failure report...$(NC)"
	cd src && python main.py --report --days 7

check-gh: ## Check if GitHub CLI is installed and authenticated
	@echo "$(GREEN)🔍 Checking GitHub CLI...$(NC)"
	@if command -v gh >/dev/null 2>&1; then \
		echo "$(GREEN)✅ GitHub CLI found$(NC)"; \
		if gh auth status >/dev/null 2>&1; then \
			echo "$(GREEN)✅ GitHub CLI authenticated$(NC)"; \
		else \
			echo "$(YELLOW)⚠️  GitHub CLI not authenticated. Run: gh auth login$(NC)"; \
		fi \
	else \
		echo "$(RED)❌ GitHub CLI not found. Install with: brew install gh$(NC)"; \
	fi

demo: ## Run demo analysis on yolo-ffmpeg-mcp repository
	@echo "$(GREEN)🎬 Running Build Detective demo...$(NC)"
	$(MAKE) check-gh
	$(MAKE) analyze REPO=StigLau/yolo-ffmpeg-mcp

demo-pr: ## Run demo PR analysis on yolo-ffmpeg-mcp PR#16
	@echo "$(GREEN)🎬 Running Build Detective PR demo...$(NC)"
	$(MAKE) check-gh
	$(MAKE) analyze-pr REPO=StigLau/yolo-ffmpeg-mcp PR=16

stats: ## Show database statistics
	@echo "$(GREEN)📊 Database statistics:$(NC)"
	@python -c "import sys; sys.path.append('src'); from issue_tracker.database import IssueDatabase; db = IssueDatabase(); stats = db.get_statistics(); print(f'Total issues: {stats.get(\"total_issues\", 0)}'); print(f'Cached solutions: {stats.get(\"cached_solutions\", 0)}'); print(f'Recent activity: {stats.get(\"recent_issues\", 0)}')"

clean: ## Clean up generated files and cache
	@echo "$(GREEN)🧹 Cleaning up...$(NC)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache
	rm -f data/issues.db*
	@echo "$(GREEN)✅ Cleanup complete$(NC)"

lint: ## Run code linting (if available)
	@echo "$(GREEN)🔍 Running linting...$(NC)"
	@if command -v ruff >/dev/null 2>&1; then \
		ruff check src/; \
	elif command -v flake8 >/dev/null 2>&1; then \
		flake8 src/; \
	else \
		echo "$(YELLOW)⚠️  No linter found (install ruff or flake8)$(NC)"; \
	fi

dev: ## Development mode - install + test + demo
	$(MAKE) install
	$(MAKE) test-cli
	$(MAKE) demo

# Quick commands for presentations
show: demo ## Alias for demo
quick: demo-pr ## Quick demo using PR analysis

# Documentation
docs: ## Show project structure
	@echo "$(GREEN)📁 Build Detective Project Structure:$(NC)"
	@tree -I '__pycache__|*.pyc|.git' . || find . -type d -name .git -prune -o -type f -print | head -20

version: ## Show version information
	@echo "$(GREEN)🕵️ Build Detective Presentation Version$(NC)"
	@echo "Python: $(shell python --version)"
	@echo "GitHub CLI: $(shell gh --version 2>/dev/null | head -1 || echo 'Not installed')"
	@echo "Project: Build Detective Presentation Implementation"