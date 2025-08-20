"""Build Detective - AI-powered CI/CD failure analysis system"""

__version__ = "2.1.0"
__author__ = "Build Detective Team"

from .bd_claude_agent import BuildDetectiveAgent
from .agents.build_detective_claude_agent import BuildDetectiveClaudeAgent

__all__ = ['BuildDetectiveAgent', 'BuildDetectiveClaudeAgent']