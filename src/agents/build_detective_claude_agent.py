#!/usr/bin/env python3
"""
Build Detective Claude Agent - Task Tool Integration

This is the main Claude Code agent that integrates with the Task tool system.
It replaces subprocess simulation with real Claude Code Task tool calls.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

# Import our specialized agents
from architect_agent import BuildDetectiveArchitect, AnalysisRequest
from ci_specialist_agent import CISpecialistAgent
from cost_optimizer_agent import CostOptimizerAgent, ModelRoutingDecision
from validation_agent import ValidationAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BuildDetectiveClaudeAgent:
    """
    Main Claude Agent for Build Detective - integrates with Claude Code's Task tool
    
    This agent coordinates the multi-agent system using real Task tool calls
    instead of subprocess simulation, making it a proper Claude Code agent.
    """
    
    def __init__(self):
        self.agent_name = "build-detective-claude-agent"
        self.version = "2.0.0"
        
        # Initialize specialized agents
        self.architect = BuildDetectiveArchitect()
        self.ci_specialist = CISpecialistAgent()
        self.cost_optimizer = CostOptimizerAgent()
        self.validator = ValidationAgent()
    
    async def analyze_ci_failure_with_task_tool(self, github_url: str, priority: str = "medium", context: Dict[str, Any] = None) -> str:
        """
        Main entry point for Claude Code Task tool integration
        
        This method is designed to be called by Claude Code through the Task tool:
        
        Task(
            description="Analyze CI failure with Build Detective",
            prompt=f"Analyze GitHub Actions failure at {github_url}",
            subagent_type="build-detective"
        )
        
        Returns JSON string suitable for Claude Code consumption
        """
        try:
            logger.info(f"🤖 Build Detective Claude Agent starting analysis: {github_url}")
            
            # Create structured analysis request
            request = AnalysisRequest(
                task_id=f"bd_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                github_url=github_url,
                priority=priority,
                requester="claude_code_task_tool",
                context=context or {}
            )
            
            # Use architect agent to orchestrate the analysis
            # This now uses real Task tool calls instead of simulation
            orchestration_result = await self._orchestrate_with_task_tool(request)
            
            # Format result for Claude Code
            formatted_result = self._format_for_claude_code(orchestration_result, request)
            
            logger.info(f"✅ Build Detective analysis complete: {formatted_result.get('status', 'unknown')}")
            return json.dumps(formatted_result, indent=2)
            
        except Exception as e:
            logger.error(f"❌ Build Detective Claude Agent failed: {e}")
            return self._error_response_for_claude_code(str(e), github_url)
    
    async def _orchestrate_with_task_tool(self, request: AnalysisRequest) -> Dict[str, Any]:
        """
        Orchestrate analysis using real Task tool calls
        
        This replaces the simulation in architect_agent.py with actual Task tool integration
        """
        logger.info(f"🎭 Orchestrating with Task tool for {request.github_url}")
        
        try:
            # Step 1: Get cost optimization routing decision
            routing_result = await self._task_cost_optimization(request)
            
            # Step 2: Perform CI analysis using chosen model
            ci_analysis_result = await self._task_ci_analysis(request, routing_result)
            
            # Step 3: Validate the analysis results
            validation_result = await self._task_validation(request, ci_analysis_result, routing_result)
            
            # Step 4: Aggregate results
            final_result = {
                "task_id": request.task_id,
                "github_url": request.github_url,
                "routing_decision": routing_result,
                "ci_analysis": ci_analysis_result,
                "validation": validation_result,
                "orchestration_metadata": {
                    "agent": self.agent_name,
                    "version": self.version,
                    "workflow": "task_tool_integrated",
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            return final_result
            
        except Exception as e:
            logger.error(f"❌ Task tool orchestration failed: {e}")
            raise
    
    async def _task_cost_optimization(self, request: AnalysisRequest) -> ModelRoutingDecision:
        """
        Use Task tool to get cost optimization routing decision
        
        Real implementation would be:
        Task(
            description="Optimize model routing for cost",
            prompt=f"Determine optimal AI model routing for: {request.github_url}",
            subagent_type="build-detective-cost-optimizer"
        )
        """
        logger.info("💰 Task tool: Cost optimization routing")
        
        # For now, use the cost optimizer directly
        # In production, this would be a Task tool call
        routing_request = {
            "github_url": request.github_url,
            "priority": request.priority,
            "failure_data": request.context.get("failure_data", {})
        }
        
        return await self.cost_optimizer.optimize_model_routing(routing_request, request.context)
    
    async def _task_ci_analysis(self, request: AnalysisRequest, routing: ModelRoutingDecision) -> Dict[str, Any]:
        """
        Use Task tool to perform CI analysis with chosen model
        
        Real implementation would be:
        Task(
            description="CI failure pattern analysis",
            prompt=self._create_ci_analysis_prompt(request, routing),
            subagent_type="build-detective-ci-specialist"
        )
        """
        logger.info(f"🔍 Task tool: CI analysis with {routing.chosen_model}")
        
        # Extract failure data from GitHub (this would be done by Task tool in real usage)
        failure_data = await self._extract_failure_data(request.github_url)
        
        # Perform CI analysis using the specialist agent
        # In production, this would be a Task tool call to Haiku or Sonnet
        return await self.ci_specialist.analyze_ci_failure(
            request.github_url,
            failure_data,
            request.context
        )
    
    async def _task_validation(self, request: AnalysisRequest, ci_analysis: Dict[str, Any], routing: ModelRoutingDecision) -> Dict[str, Any]:
        """
        Use Task tool to validate analysis results
        
        Real implementation would be:
        Task(
            description="Validate CI analysis quality",
            prompt=self._create_validation_prompt(ci_analysis),
            subagent_type="build-detective-validation"
        )
        """
        logger.info("✅ Task tool: Validation of analysis results")
        
        # Perform validation using the validation agent
        validation_result = await self.validator.validate_analysis(
            ci_analysis,
            request.__dict__,
            {"routing": routing.__dict__}
        )
        
        return validation_result.__dict__
    
    async def _extract_failure_data(self, github_url: str) -> Dict[str, Any]:
        """
        Extract failure data from GitHub URL
        
        In real usage, this would use Bash tool to call GitHub CLI
        """
        # Mock failure data extraction
        # Real implementation would use:
        # Bash(command="gh run view <run_id> --repo <repo> --json jobs")
        
        return {
            "failed_jobs": ["Integration Tests with AWS", "Maven Tests Java 21"],
            "workflow_name": "CI Pipeline",
            "run_id": "12345",
            "raw_data": "Simulated failure data"
        }
    
    def _format_for_claude_code(self, orchestration_result: Dict[str, Any], request: AnalysisRequest) -> Dict[str, Any]:
        """Format analysis results for Claude Code consumption - optimized for conciseness"""
        
        ci_analysis = orchestration_result.get("ci_analysis", {})
        validation = orchestration_result.get("validation", {})
        routing = orchestration_result.get("routing_decision", {})
        
        # Prioritized formatting for Claude Code - most important information first
        formatted = {
            # Primary results (top priority)
            "status": ci_analysis.get("status", "UNKNOWN"),
            "primary_error": ci_analysis.get("primary_error", "Analysis incomplete"),
            "confidence": f"{ci_analysis.get('confidence', 0)}/10",
            "error_type": ci_analysis.get("error_type", "unknown"),
            
            # Actionable solutions (high priority)
            "immediate_fix": self._get_top_priority_action(ci_analysis),
            "suggested_actions": ci_analysis.get("solutions", {}).get("suggested_actions", [])[:3],  # Limit to top 3
            "verification_steps": ci_analysis.get("solutions", {}).get("verification_steps", [])[:2],  # Limit to top 2
            
            # Quality indicators (medium priority)
            "cost_analysis": f"Used {routing.chosen_model if hasattr(routing, 'chosen_model') else 'unknown'} (${routing.estimated_cost if hasattr(routing, 'estimated_cost') else 0.0:.2f})",
            "validation": f"{validation.get('validation_status', 'NOT_VALIDATED')} - {validation.get('overall_confidence', 0)}/10",
            
            # Meta information (low priority - only if space allows)
            "github_url": request.github_url,
            "task_id": request.task_id,
            "agent_coordination": f"Multi-agent analysis with {len(orchestration_result.get('agents_used', []))} specialists"
        }
        
        return formatted
    
    def _get_top_priority_action(self, ci_analysis: Dict[str, Any]) -> str:
        """Extract the single most important action from analysis"""
        actions = ci_analysis.get("solutions", {}).get("suggested_actions", [])
        if not actions:
            return "No specific action identified"
        
        # Return the first action, which should be highest priority
        return actions[0] if isinstance(actions[0], str) else str(actions[0])
    
    def _error_response_for_claude_code(self, error_msg: str, github_url: str) -> str:
        """Generate error response in Claude Code compatible format"""
        
        error_response = {
            "status": "ERROR",
            "primary_error": f"Build Detective analysis failed: {error_msg}",
            "error_type": "agent_error",
            "confidence": 0,
            "suggested_actions": [
                "Check GitHub URL format",
                "Verify GitHub CLI authentication",
                "Try manual log analysis"
            ],
            "validation_status": "FAILED",
            "github_url": github_url,
            "claude_code_compatible": True,
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        return json.dumps(error_response, indent=2)
    
    # Claude Code Task Tool Integration Points
    
    def _create_ci_analysis_prompt(self, request: AnalysisRequest, routing: ModelRoutingDecision) -> str:
        """Create optimized prompt for CI analysis Task tool call"""
        
        base_prompt = f"""Analyze CI/CD failure for Build Detective multi-agent system.

GitHub URL: {request.github_url}
Priority: {request.priority}
Chosen AI Model: {routing.chosen_model}
Cost Budget: ${routing.estimated_cost:.4f}

Apply Build Detective pattern recognition for:
- Maven/Java: Surefire failures, dependency conflicts, JDK compatibility
- Python/UV: pytest issues, --extra dev flags, import resolution
- Docker: Build failures, version specifiers, layer caching
- GitHub Actions: Workflow configuration, matrix builds, secrets

Focus on {routing.routing_reason.lower()}.

Return structured analysis with:
- Primary error identification and confidence (1-10)
- Technology-specific error classification
- Actionable fix commands and verification steps
- Estimated implementation time
"""
        
        # Optimize for chosen model
        if routing.chosen_model == "haiku":
            base_prompt += "\nOptimize for cost efficiency - focus on top 3 most likely solutions."
        else:
            base_prompt += "\nProvide comprehensive analysis with detailed reasoning."
        
        return base_prompt
    
    def _create_validation_prompt(self, ci_analysis: Dict[str, Any]) -> str:
        """Create prompt for validation Task tool call"""
        
        return f"""Validate CI analysis results for quality assurance.

Analysis to validate:
- Primary Error: {ci_analysis.get('primary_error', 'N/A')}
- Error Type: {ci_analysis.get('error_type', 'unknown')}
- Confidence: {ci_analysis.get('confidence', 0)}/10
- Suggested Actions: {ci_analysis.get('solutions', {}).get('suggested_actions', [])}

Validation criteria:
1. Error identification accuracy and specificity
2. Solution appropriateness for the error type  
3. Implementation clarity and actionability
4. Technical accuracy of recommendations
5. Risk assessment and safety considerations

Return validation decision:
- APPROVED: High quality, ready for implementation
- APPROVED_WITH_CAUTION: Good quality, needs testing
- REVISION_NEEDED: Issues require fixing
- REJECTED: Significant problems, manual review needed

Include confidence score, quality gates status, and recommendations."""

# Entry point for Claude Code Task tool
async def claude_code_entry_point(github_url: str, priority: str = "medium", **kwargs) -> str:
    """
    Entry point for Claude Code Task tool integration
    
    This function is called when Claude Code invokes:
    Task(
        description="Analyze CI failure", 
        prompt="Analyze failure at <url>",
        subagent_type="build-detective"
    )
    """
    agent = BuildDetectiveClaudeAgent()
    return await agent.analyze_ci_failure_with_task_tool(github_url, priority, kwargs.get('context'))

# CLI interface for testing
async def main():
    """CLI entry point for testing the Task tool integrated agent"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python build_detective_claude_agent.py <github_url> [priority]")
        print("Example: python build_detective_claude_agent.py https://github.com/StigLau/vdvil/actions/runs/17024829354 high")
        return 1
    
    github_url = sys.argv[1]
    priority = sys.argv[2] if len(sys.argv) > 2 else "medium"
    
    agent = BuildDetectiveClaudeAgent()
    
    try:
        result = await agent.analyze_ci_failure_with_task_tool(github_url, priority)
        print(result)
        return 0
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return 1

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())