#!/usr/bin/env python3
"""
Build Detective Architect Agent - Master orchestrator for multi-agent CI analysis

This implements the master orchestrator following StigLau's multi-agent template patterns.
Routes analysis tasks to appropriate specialist agents and coordinates workflows.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AnalysisRequest:
    """Structured analysis request for agent coordination"""
    task_id: str
    github_url: str
    priority: str  # low, medium, high, critical
    requester: str
    context: Dict[str, Any]

@dataclass
class AgentResponse:
    """Standardized agent response format"""
    agent: str
    task_id: str
    status: str
    confidence: int
    result: Dict[str, Any]
    cost: float
    processing_time: float

class BuildDetectiveArchitect:
    """
    Master Orchestrator Agent for Build Detective
    
    Implements hierarchical agent coordination patterns:
    - Sequential: task → ci-specialist → validation → result
    - Parallel: task → {ci-specialist, cost-optimizer} → merge → result  
    - Conditional: analyze complexity → route to appropriate specialist(s)
    """
    
    def __init__(self):
        self.agent_name = "build-detective-architect"
        self.supported_workflows = ["sequential", "parallel", "conditional"]
        self.agent_registry = {
            "ci-specialist": "build-detective-ci-specialist",
            "cost-optimizer": "build-detective-cost-optimizer", 
            "validation": "build-detective-validation",
            "project-discovery": "build-detective-project-discovery"
        }
    
    async def orchestrate_analysis(self, request: AnalysisRequest) -> Dict[str, Any]:
        """
        Master orchestration method - analyzes request and coordinates agents
        
        This is the main entry point that Claude Code's Task tool would call.
        """
        logger.info(f"🎭 Architect Agent orchestrating analysis for {request.task_id}")
        
        try:
            # Step 1: Analyze request complexity and determine routing strategy
            routing_decision = await self._analyze_and_route(request)
            
            # Step 2: Execute chosen workflow pattern
            if routing_decision["workflow"] == "sequential":
                result = await self._execute_sequential_workflow(request, routing_decision)
            elif routing_decision["workflow"] == "parallel":
                result = await self._execute_parallel_workflow(request, routing_decision)
            elif routing_decision["workflow"] == "conditional":
                result = await self._execute_conditional_workflow(request, routing_decision)
            else:
                raise ValueError(f"Unsupported workflow: {routing_decision['workflow']}")
            
            # Step 3: Aggregate results and provide final analysis
            final_analysis = await self._aggregate_results(request, routing_decision, result)
            
            logger.info(f"✅ Architect orchestration complete for {request.task_id}")
            return final_analysis
            
        except Exception as e:
            logger.error(f"❌ Orchestration failed for {request.task_id}: {e}")
            return self._error_response(request, str(e))
    
    async def _analyze_and_route(self, request: AnalysisRequest) -> Dict[str, Any]:
        """
        Analyze request complexity and determine optimal agent routing strategy
        """
        logger.info(f"🧠 Analyzing complexity for {request.github_url}")
        
        # Extract basic info from GitHub URL
        url_analysis = self._parse_github_url(request.github_url)
        
        # Determine complexity factors
        complexity_factors = {
            "url_type": url_analysis["type"],  # pr, actions_run, repo
            "priority": request.priority,
            "has_context": bool(request.context),
            "multi_job_likely": "actions/runs/" in request.github_url
        }
        
        # Calculate complexity score (1-10)
        complexity_score = self._calculate_complexity_score(complexity_factors, request)
        
        # Determine routing strategy
        if complexity_score <= 4:
            # Simple: Direct to CI specialist with cost optimization
            workflow = "sequential"
            agents = ["cost-optimizer", "ci-specialist", "validation"]
        elif complexity_score <= 7:
            # Moderate: Parallel analysis with cost awareness
            workflow = "parallel" 
            agents = ["ci-specialist", "cost-optimizer"]
            post_agents = ["validation"]
        else:
            # Complex: Full multi-agent analysis with project discovery
            workflow = "conditional"
            agents = ["project-discovery", "ci-specialist", "cost-optimizer", "validation"]
        
        routing_decision = {
            "workflow": workflow,
            "agents": agents,
            "complexity_score": complexity_score,
            "complexity_factors": complexity_factors,
            "estimated_cost": self._estimate_workflow_cost(workflow, agents),
            "reasoning": self._explain_routing_decision(complexity_score, workflow)
        }
        
        logger.info(f"📊 Complexity: {complexity_score}/10, Workflow: {workflow}, Agents: {agents}")
        return routing_decision
    
    def _parse_github_url(self, url: str) -> Dict[str, str]:
        """Extract structured information from GitHub URL"""
        if "/pull/" in url:
            return {"type": "pr", "complexity_hint": "moderate"}
        elif "/actions/runs/" in url:
            return {"type": "actions_run", "complexity_hint": "variable"}
        elif "/issues/" in url:
            return {"type": "issue", "complexity_hint": "low"}
        else:
            return {"type": "repo", "complexity_hint": "high"}
    
    def _calculate_complexity_score(self, factors: Dict[str, Any], request: AnalysisRequest) -> int:
        """Calculate complexity score for routing decisions"""
        score = 5  # Base score
        
        # URL type complexity
        if factors["url_type"] == "actions_run":
            score += 2  # Actions runs can be complex multi-job failures
        elif factors["url_type"] == "pr":
            score += 1  # PRs usually moderate complexity
        
        # Priority adjustments
        priority_scores = {"low": -1, "medium": 0, "high": 1, "critical": 2}
        score += priority_scores.get(factors["priority"], 0)
        
        # Context and multi-job indicators
        if factors["has_context"]:
            score += 1
        if factors["multi_job_likely"]:
            score += 1
        
        # Clamp to 1-10 range
        return max(1, min(10, score))
    
    def _estimate_workflow_cost(self, workflow: str, agents: List[str]) -> float:
        """Estimate cost for workflow execution"""
        agent_costs = {
            "ci-specialist": 0.03,  # Haiku-powered analysis
            "cost-optimizer": 0.01,  # Lightweight routing
            "validation": 0.02,     # Verification logic
            "project-discovery": 0.04  # Structure analysis
        }
        
        base_cost = sum(agent_costs.get(agent, 0.02) for agent in agents)
        
        # Workflow overhead
        workflow_multipliers = {
            "sequential": 1.0,
            "parallel": 1.1,    # Slight overhead for coordination
            "conditional": 1.2  # More overhead for complex routing
        }
        
        return base_cost * workflow_multipliers.get(workflow, 1.0)
    
    def _explain_routing_decision(self, complexity_score: int, workflow: str) -> str:
        """Provide human-readable reasoning for routing decision"""
        if complexity_score <= 4:
            return f"Simple analysis (score {complexity_score}) → Sequential workflow for cost efficiency"
        elif complexity_score <= 7:
            return f"Moderate complexity (score {complexity_score}) → Parallel workflow for balanced speed/cost"
        else:
            return f"High complexity (score {complexity_score}) → Full multi-agent workflow for comprehensive analysis"
    
    async def _execute_sequential_workflow(self, request: AnalysisRequest, routing: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute sequential workflow: agent1 → agent2 → agent3 → result
        """
        logger.info(f"🔄 Executing sequential workflow: {' → '.join(routing['agents'])}")
        
        results = []
        context = request.context.copy()
        
        for agent_key in routing["agents"]:
            agent_name = self.agent_registry[agent_key]
            
            # This is where Task tool integration happens in real Claude Code usage:
            # Task(
            #     description=f"{agent_key} analysis",
            #     prompt=self._create_agent_prompt(agent_key, request, context),
            #     subagent_type=agent_name
            # )
            
            # For now, simulate agent responses
            agent_result = await self._simulate_agent_call(agent_key, request, context)
            results.append(agent_result)
            
            # Pass results as context to next agent
            context[f"{agent_key}_result"] = agent_result.result
        
        return {
            "workflow": "sequential",
            "agents_executed": routing["agents"],
            "results": results,
            "final_result": results[-1].result if results else {}
        }
    
    async def _execute_parallel_workflow(self, request: AnalysisRequest, routing: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute parallel workflow: {agent1, agent2} → merge → validation
        """
        logger.info(f"⚡ Executing parallel workflow: {routing['agents']}")
        
        # Execute main agents in parallel
        parallel_agents = routing["agents"]
        post_agents = routing.get("post_agents", [])
        
        # Simulate parallel execution (in real usage, multiple Task calls in one message)
        parallel_results = []
        for agent_key in parallel_agents:
            agent_result = await self._simulate_agent_call(agent_key, request, request.context)
            parallel_results.append(agent_result)
        
        # Merge parallel results
        merged_context = request.context.copy()
        for result in parallel_results:
            merged_context[f"{result.agent}_result"] = result.result
        
        # Execute post-processing agents (like validation)
        post_results = []
        for agent_key in post_agents:
            agent_result = await self._simulate_agent_call(agent_key, request, merged_context)
            post_results.append(agent_result)
        
        return {
            "workflow": "parallel",
            "parallel_agents": parallel_agents,
            "parallel_results": parallel_results,
            "post_agents": post_agents,
            "post_results": post_results,
            "final_result": post_results[-1].result if post_results else merged_context
        }
    
    async def _execute_conditional_workflow(self, request: AnalysisRequest, routing: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute conditional workflow: analyze → route_to_specialist → validate
        """
        logger.info(f"🔀 Executing conditional workflow based on analysis")
        
        # First, run project discovery to understand context
        discovery_result = await self._simulate_agent_call("project-discovery", request, request.context)
        
        # Based on discovery, decide on specialized routing
        specialized_agents = self._determine_specialized_agents(discovery_result.result)
        
        # Execute specialized agents
        specialized_results = []
        context = request.context.copy()
        context["project_discovery"] = discovery_result.result
        
        for agent_key in specialized_agents:
            agent_result = await self._simulate_agent_call(agent_key, request, context)
            specialized_results.append(agent_result)
            context[f"{agent_key}_result"] = agent_result.result
        
        # Final validation
        validation_result = await self._simulate_agent_call("validation", request, context)
        
        return {
            "workflow": "conditional", 
            "discovery_result": discovery_result,
            "specialized_agents": specialized_agents,
            "specialized_results": specialized_results,
            "validation_result": validation_result,
            "final_result": validation_result.result
        }
    
    def _determine_specialized_agents(self, project_discovery: Dict[str, Any]) -> List[str]:
        """Determine which specialized agents to use based on project discovery"""
        agents = ["ci-specialist"]  # Always include CI specialist
        
        # Add cost optimizer for complex projects
        complexity = project_discovery.get("complexity_score", 5)
        if complexity > 6:
            agents.append("cost-optimizer")
        
        return agents
    
    async def _simulate_agent_call(self, agent_key: str, request: AnalysisRequest, context: Dict[str, Any]) -> AgentResponse:
        """
        Simulate agent call - In real usage this would use Task tool
        
        Real implementation:
        Task(
            description=f"{agent_key} CI analysis", 
            prompt=self._create_agent_prompt(agent_key, request, context),
            subagent_type=self.agent_registry[agent_key]
        )
        """
        import asyncio
        await asyncio.sleep(0.1)  # Simulate processing time
        
        # Mock responses based on agent type
        mock_responses = {
            "ci-specialist": {
                "status": "FAILURE",
                "primary_error": "Maven Surefire test execution failed",
                "error_type": "maven",
                "confidence": 8,
                "suggested_actions": ["mvn clean test", "check surefire reports"]
            },
            "cost-optimizer": {
                "model_routed": "haiku",
                "estimated_cost": 0.02,
                "budget_status": "within_limits",
                "routing_reason": "Simple single-job Maven failure"
            },
            "validation": {
                "validation_status": "APPROVED",
                "overall_confidence": 8,
                "quality_gates_passed": True,
                "recommendations": ["Test in development environment"]
            },
            "project-discovery": {
                "project_type": "maven_multi_module",
                "complexity_score": 7,
                "primary_tech": "java_maven",
                "risk_areas": ["integration_tests"]
            }
        }
        
        return AgentResponse(
            agent=agent_key,
            task_id=request.task_id,
            status="completed",
            confidence=8,
            result=mock_responses.get(agent_key, {"status": "completed"}),
            cost=0.02,
            processing_time=0.5
        )
    
    async def _aggregate_results(self, request: AnalysisRequest, routing: Dict[str, Any], workflow_result: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate multi-agent results into final comprehensive analysis"""
        
        final_analysis = {
            "task_id": request.task_id,
            "github_url": request.github_url,
            "orchestration": {
                "architect_agent": self.agent_name,
                "workflow_used": routing["workflow"],
                "complexity_score": routing["complexity_score"],
                "routing_reasoning": routing["reasoning"],
                "estimated_cost": routing["estimated_cost"]
            },
            "analysis_results": workflow_result.get("final_result", {}),
            "agent_coordination": {
                "agents_used": routing["agents"],
                "execution_pattern": routing["workflow"],
                "total_cost": sum(r.cost for r in workflow_result.get("results", [])),
                "processing_time": sum(r.processing_time for r in workflow_result.get("results", []))
            },
            "quality_assurance": {
                "multi_agent_validated": True,
                "architect_approved": True,
                "confidence_aggregated": True
            },
            "timestamp": datetime.now().isoformat()
        }
        
        return final_analysis
    
    def _error_response(self, request: AnalysisRequest, error_msg: str) -> Dict[str, Any]:
        """Generate error response for failed orchestration"""
        return {
            "task_id": request.task_id,
            "status": "ERROR",
            "error": error_msg,
            "orchestration_failed": True,
            "architect_agent": self.agent_name,
            "timestamp": datetime.now().isoformat()
        }

# CLI interface for testing
async def main():
    """CLI entry point for testing Architect Agent"""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python architect_agent.py <github_url>")
        print("Example: python architect_agent.py https://github.com/StigLau/vdvil/actions/runs/17024829354")
        return 1
    
    architect = BuildDetectiveArchitect()
    
    # Create test request
    request = AnalysisRequest(
        task_id="test_001",
        github_url=sys.argv[1],
        priority="medium",
        requester="cli_test",
        context={}
    )
    
    try:
        result = await architect.orchestrate_analysis(request)
        print(json.dumps(result, indent=2))
        return 0
    except Exception as e:
        print(f"❌ Orchestration failed: {e}")
        return 1

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())