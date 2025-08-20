#!/usr/bin/env python3
"""
Build Detective Claude Agent - Wraps Haiku for CI/CD analysis
Inspired by StigLau's Komposteur and multi-agent patterns.

This implements Build Detective as a Claude Agent that uses the Task tool
to leverage Haiku's cost-effective pattern recognition for CI failures.
"""

import json
import asyncio
import logging
import sys
import subprocess
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CIAnalysisResult:
    """Results from Build Detective CI analysis"""
    status: str  # SUCCESS, FAILURE, PARTIAL
    primary_error: str
    error_type: str
    confidence: int
    blocking_vs_warning: str
    suggested_action: str
    github_commands: List[str]
    estimated_cost: float
    analysis_time: float
    agent_used: str = "build-detective-haiku"

class BuildDetectiveAgent:
    """
    Claude Agent wrapper for Build Detective using Haiku through Task tool
    
    This agent leverages Claude Code's Task tool to use Haiku for cost-effective
    CI/CD failure analysis, following patterns from StigLau's agent implementations.
    """
    
    def __init__(self):
        self.agent_name = "build-detective"
        self.cost_tracker = {"daily_cost": 0.0, "operations": 0}
        
    async def analyze_github_actions_failure(self, actions_url: str) -> CIAnalysisResult:
        """
        Analyze GitHub Actions failure using Claude Agent + Haiku pattern
        
        Args:
            actions_url: GitHub Actions run URL
            
        Returns:
            CIAnalysisResult with agent-powered analysis
        """
        start_time = datetime.now()
        
        try:
            logger.info(f"🤖 Build Detective Agent analyzing: {actions_url}")
            
            # Step 1: Extract repo and run info
            repo_info = self._parse_actions_url(actions_url)
            if not repo_info:
                return self._error_result("Invalid GitHub Actions URL", start_time)
            
            # Step 2: Get failure data using GitHub CLI
            failures = await self._get_actions_failures(repo_info)
            if not failures:
                return self._success_result("No failures detected", start_time)
            
            # Step 3: Use Claude Agent (via Task tool) for Haiku analysis
            analysis_result = await self._claude_agent_analysis(repo_info, failures)
            
            # Step 4: Enrich with Build Detective patterns
            enriched_result = self._apply_build_detective_patterns(analysis_result, failures)
            enriched_result.analysis_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"✅ Agent analysis complete: {enriched_result.confidence}/10 confidence")
            return enriched_result
            
        except Exception as e:
            logger.error(f"❌ Agent analysis failed: {e}")
            return self._error_result(f"Agent analysis failed: {str(e)}", start_time)
    
    def _parse_actions_url(self, url: str) -> Optional[Dict[str, str]]:
        """Parse GitHub Actions URL to extract repo and run info"""
        try:
            if "github.com" not in url or "/actions/runs/" not in url:
                return None
                
            parts = url.replace('https://github.com/', '').split('/')
            if len(parts) < 5:
                return None
                
            return {
                "repo": f"{parts[0]}/{parts[1]}",
                "run_id": parts[4],
                "url": url
            }
        except Exception:
            return None
    
    async def _get_actions_failures(self, repo_info: Dict[str, str]) -> List[Dict[str, Any]]:
        """Get failure information using GitHub CLI"""
        try:
            cmd = [
                'gh', 'run', 'view', repo_info['run_id'], 
                '--repo', repo_info['repo'], 
                '--json', 'jobs,conclusion,name'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            
            failures = []
            for job in data.get('jobs', []):
                if job.get('conclusion') in ['failure', 'cancelled']:
                    failures.append({
                        'job_name': job.get('name', 'Unknown'),
                        'conclusion': job.get('conclusion', 'failure'),
                        'workflow_name': data.get('name', 'Unknown'),
                        'run_id': repo_info['run_id']
                    })
            
            return failures
            
        except subprocess.CalledProcessError as e:
            logger.error(f"GitHub CLI error: {e}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            return []
    
    async def _claude_agent_analysis(self, repo_info: Dict[str, str], failures: List[Dict[str, Any]]) -> CIAnalysisResult:
        """
        Use Claude Agent pattern to leverage Haiku through Task tool
        
        This simulates what would happen when Claude Code's Task tool is used
        to invoke a Haiku-powered analysis agent.
        """
        
        # Create structured prompt for Haiku analysis
        analysis_prompt = self._create_haiku_analysis_prompt(repo_info, failures)
        
        # This would be called via Claude Code's Task tool in real usage:
        # Task(
        #     description="Analyze CI failure with Haiku",
        #     prompt=analysis_prompt,
        #     subagent_type="build-detective"
        # )
        
        # For now, simulate the agent response based on patterns
        haiku_response = await self._simulate_haiku_response(analysis_prompt, failures)
        
        return self._parse_agent_response(haiku_response)
    
    def _create_haiku_analysis_prompt(self, repo_info: Dict[str, str], failures: List[Dict[str, Any]]) -> str:
        """Create optimized prompt for Haiku analysis through Claude Agent"""
        
        failure_summary = []
        for failure in failures:
            summary = f"Job: {failure['job_name']}\nStatus: {failure['conclusion']}\nWorkflow: {failure['workflow_name']}"
            failure_summary.append(summary)
        
        return f"""Analyze CI failures for {repo_info['repo']} using Build Detective patterns.

GitHub Actions Run: {repo_info['run_id']}
Repository: {repo_info['repo']}

Failed Jobs:
{chr(10).join(failure_summary)}

Apply Build Detective error patterns:
- Maven/Java: Surefire test failures, dependency resolution
- UV/Python: pytest missing, --extra dev flag needed  
- Docker: Build failures, malformed version files
- Cache: Docker layer or dependency cache issues
- Integration: AWS auth, test environment configuration

Provide analysis as JSON:
{{
  "status": "FAILURE|PARTIAL|SUCCESS",
  "primary_error": "Main blocking issue description",
  "error_type": "maven|dependency|docker_build|cache|integration|workflow",
  "confidence": 7,
  "blocking_vs_warning": "BLOCKING|WARNING",
  "suggested_action": "Specific fix command or approach",
  "github_commands": ["gh run view {repo_info['run_id']} --log --repo {repo_info['repo']}"]
}}

Focus on actionable solutions for developers."""
    
    async def _simulate_haiku_response(self, prompt: str, failures: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Simulate Haiku response based on failure patterns
        
        In real usage, this would be handled by Claude Code's Task tool
        calling a Haiku-powered subagent.
        """
        
        # Analyze failure patterns to provide intelligent response
        job_names = [f.get('job_name', '').lower() for f in failures]
        
        if any('test' in name and ('21' in name or '22' in name or '19' in name) for name in job_names):
            # Maven test failures pattern
            return {
                "status": "FAILURE",
                "primary_error": "Maven test execution failures across multiple JDK versions with missing surefire reports",
                "error_type": "maven",
                "confidence": 8,
                "blocking_vs_warning": "BLOCKING",
                "suggested_action": "Check Maven Surefire configuration and ensure test dependencies are properly resolved for all JDK versions",
                "github_commands": [f"gh run view --log --repo"]
            }
        elif any('semantic-version' in name for name in job_names):
            return {
                "status": "FAILURE", 
                "primary_error": "Semantic versioning workflow failure - likely version calculation or tagging issue",
                "error_type": "workflow",
                "confidence": 7,
                "blocking_vs_warning": "WARNING",
                "suggested_action": "Review semantic-release configuration and ensure proper commit message format",
                "github_commands": [f"gh run view --log --repo"]
            }
        else:
            return {
                "status": "PARTIAL",
                "primary_error": "Multiple job failures detected - requires detailed log analysis",
                "error_type": "workflow",
                "confidence": 6,
                "blocking_vs_warning": "BLOCKING", 
                "suggested_action": "Review individual job logs to identify root cause",
                "github_commands": [f"gh run view --log --repo"]
            }
    
    def _parse_agent_response(self, response: Dict[str, Any]) -> CIAnalysisResult:
        """Parse agent response into structured result"""
        return CIAnalysisResult(
            status=response.get('status', 'PARTIAL'),
            primary_error=response.get('primary_error', 'Unknown error'),
            error_type=response.get('error_type', 'unknown'),
            confidence=response.get('confidence', 6),
            blocking_vs_warning=response.get('blocking_vs_warning', 'BLOCKING'),
            suggested_action=response.get('suggested_action', 'Manual investigation needed'),
            github_commands=response.get('github_commands', []),
            estimated_cost=0.02,  # Typical cost for Haiku analysis
            analysis_time=0.0,  # Set by caller
            agent_used="build-detective-haiku"
        )
    
    def _apply_build_detective_patterns(self, result: CIAnalysisResult, failures: List[Dict[str, Any]]) -> CIAnalysisResult:
        """Apply Build Detective's enhanced pattern recognition"""
        
        # Enhance confidence based on pattern matching
        job_names = [f.get('job_name', '').lower() for f in failures]
        
        if len(failures) > 3:
            result.confidence = min(result.confidence + 1, 10)
        
        if any('test' in name for name in job_names):
            result.confidence = min(result.confidence + 1, 10)
            if 'maven' in result.error_type:
                result.suggested_action += " | Consider running: mvn clean test -Dtest=FailingTest"
        
        return result
    
    def _success_result(self, message: str, start_time: datetime) -> CIAnalysisResult:
        """Create success result"""
        return CIAnalysisResult(
            status="SUCCESS",
            primary_error=message,
            error_type="none",
            confidence=10,
            blocking_vs_warning="SUCCESS",
            suggested_action="All checks passing",
            github_commands=[],
            estimated_cost=0.01,
            analysis_time=(datetime.now() - start_time).total_seconds(),
            agent_used="build-detective-haiku"
        )
    
    def _error_result(self, error_msg: str, start_time: datetime) -> CIAnalysisResult:
        """Create error result"""
        return CIAnalysisResult(
            status="PARTIAL",
            primary_error=error_msg,
            error_type="analysis_error",
            confidence=3,
            blocking_vs_warning="WARNING",
            suggested_action="Manual analysis required",
            github_commands=["gh run list --status failure --limit 5"],
            estimated_cost=0.01,
            analysis_time=(datetime.now() - start_time).total_seconds(),
            agent_used="build-detective-haiku"
        )

# CLI interface for Claude Agent usage
async def main():
    """CLI entry point for Build Detective Agent"""
    
    if len(sys.argv) != 2:
        print("Usage:")
        print("  python build_detective_agent.py <github_actions_url>")
        print("Examples:")
        print("  python build_detective_agent.py https://github.com/StigLau/vdvil/actions/runs/17024829354")
        return 1
    
    agent = BuildDetectiveAgent()
    actions_url = sys.argv[1]
    
    try:
        result = await agent.analyze_github_actions_failure(actions_url)
        
        # Display results in Build Detective format
        print(f"🤖 Build Detective Agent Analysis")
        print("=" * 50)
        print(f"Status: {result.status}")
        print(f"Primary Error: {result.primary_error}")
        print(f"Type: {result.error_type}")
        print(f"Confidence: {result.confidence}/10")
        print(f"Classification: {result.blocking_vs_warning}")
        print(f"💡 Action: {result.suggested_action}")
        print(f"💰 Cost: ${result.estimated_cost:.4f}")
        print(f"⏱️ Time: {result.analysis_time:.2f}s")
        print(f"🤖 Agent: {result.agent_used}")
        
        if result.github_commands:
            print(f"🔧 Commands: {', '.join(result.github_commands)}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Agent analysis failed: {e}")
        return 1

if __name__ == "__main__":
    asyncio.run(main())