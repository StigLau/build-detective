#!/usr/bin/env python3
"""
Build Detective Cost Optimization Agent

Intelligent AI model routing and budget management for cost-effective CI analysis.
Routes between Haiku (cheap, fast) and Claude Sonnet (expensive, powerful) based on complexity.
"""

import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, date
import os
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CostTracking:
    """Track AI usage costs and budget status"""
    daily_spend: float = 0.0
    monthly_spend: float = 0.0
    operations_today: int = 0
    daily_limit: float = 10.0
    monthly_limit: float = 200.0
    last_reset: str = ""

@dataclass
class ModelRoutingDecision:
    """Represents a model routing decision with reasoning"""
    chosen_model: str  # "haiku" or "sonnet" 
    estimated_cost: float
    routing_reason: str
    confidence: int  # How confident we are in this routing decision
    budget_impact: float  # Percentage of daily budget this represents
    alternative_model: str
    alternative_cost: float

class CostOptimizerAgent:
    """
    Cost Optimization Agent - Intelligent AI model routing and budget management
    
    Routes analysis requests to optimal models based on:
    1. Request complexity (simple → Haiku, complex → Sonnet)
    2. Current budget status (approaching limits → cheaper models)
    3. Priority level (production critical → best model regardless)
    4. Historical success rates (learning from past routing decisions)
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.agent_name = "build-detective-cost-optimizer"
        self.config_path = config_path or os.path.expanduser("~/.build-detective/cost-tracking.json")
        self.cost_tracking = self._load_cost_tracking()
        
        # Model pricing (per 1K input tokens + per 1K output tokens)
        self.model_costs = {
            "haiku": {"input": 0.00025, "output": 0.00125, "avg_analysis": 0.02},
            "sonnet": {"input": 0.003, "output": 0.015, "avg_analysis": 0.15}
        }
        
        # Routing rules and thresholds
        self.complexity_thresholds = {
            "simple": 4,      # Score 1-4 → Haiku
            "moderate": 7,    # Score 5-7 → Context dependent 
            "complex": 10     # Score 8-10 → Sonnet
        }
        
        self.budget_thresholds = {
            "green": 0.5,     # <50% of daily budget → Normal routing
            "yellow": 0.8,    # 50-80% → Prefer cheaper models
            "red": 0.95       # >80% → Force cheap models only
        }
    
    def _load_cost_tracking(self) -> CostTracking:
        """Load cost tracking data from persistent storage"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                    tracking = CostTracking(**data)
                    
                    # Reset daily counters if new day
                    if tracking.last_reset != str(date.today()):
                        tracking.daily_spend = 0.0
                        tracking.operations_today = 0
                        tracking.last_reset = str(date.today())
                        self._save_cost_tracking(tracking)
                    
                    return tracking
        except Exception as e:
            logger.warning(f"Failed to load cost tracking: {e}")
        
        # Return default tracking
        return CostTracking(last_reset=str(date.today()))
    
    def _save_cost_tracking(self, tracking: CostTracking) -> None:
        """Save cost tracking data to persistent storage"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(tracking.__dict__, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save cost tracking: {e}")
    
    async def optimize_model_routing(self, analysis_request: Dict[str, Any], context: Dict[str, Any] = None) -> ModelRoutingDecision:
        """
        Main optimization method - determines best model for analysis request
        
        Args:
            analysis_request: Contains github_url, priority, failure_data
            context: Additional context from other agents (project discovery, etc.)
            
        Returns:
            ModelRoutingDecision with chosen model and reasoning
        """
        logger.info(f"💰 Cost Optimizer analyzing request for optimal routing")
        
        try:
            # Step 1: Analyze request complexity
            complexity_analysis = self._analyze_request_complexity(analysis_request, context)
            
            # Step 2: Check current budget status  
            budget_status = self._check_budget_status()
            
            # Step 3: Apply routing decision matrix
            routing_decision = self._make_routing_decision(complexity_analysis, budget_status, analysis_request)
            
            # Step 4: Validate decision against constraints
            validated_decision = self._validate_routing_decision(routing_decision, budget_status)
            
            # Step 5: Record decision for learning
            self._record_routing_decision(validated_decision, analysis_request)
            
            logger.info(f"💰 Routing decision: {validated_decision.chosen_model} (${validated_decision.estimated_cost:.4f}) - {validated_decision.routing_reason}")
            return validated_decision
            
        except Exception as e:
            logger.error(f"❌ Cost optimization failed: {e}")
            return self._fallback_routing_decision()
    
    def _analyze_request_complexity(self, request: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze request complexity for routing decisions"""
        
        complexity_score = 5  # Base complexity
        factors = []
        
        # URL-based complexity analysis
        github_url = request.get("github_url", "")
        
        if "/actions/runs/" in github_url:
            complexity_score += 1
            factors.append("GitHub Actions run analysis")
            
        if "/pull/" in github_url:
            complexity_score += 0  # PRs are standard complexity
            factors.append("PR failure analysis")
        
        # Priority-based adjustments
        priority = request.get("priority", "medium").lower()
        priority_adjustments = {
            "low": -1,
            "medium": 0,
            "high": 1,
            "critical": 2
        }
        complexity_score += priority_adjustments.get(priority, 0)
        factors.append(f"Priority: {priority}")
        
        # Context-based complexity (from project discovery agent)
        if context:
            project_complexity = context.get("project_discovery", {}).get("complexity_score", 5)
            if project_complexity > 7:
                complexity_score += 1
                factors.append("High project complexity detected")
                
            # Multiple failed jobs increase complexity
            failed_jobs = context.get("failed_jobs", 1)
            if failed_jobs > 3:
                complexity_score += 2
                factors.append(f"Multiple job failures ({failed_jobs})")
            elif failed_jobs > 1:
                complexity_score += 1
                factors.append(f"Multi-job failure ({failed_jobs})")
        
        # Failure data complexity analysis
        failure_data = request.get("failure_data", {})
        if failure_data:
            # Check for integration test patterns (more complex)
            if any("integration" in str(job).lower() for job in failure_data.get("job_names", [])):
                complexity_score += 1
                factors.append("Integration test failures detected")
                
            # Check for unknown error patterns (requires deeper analysis)
            if failure_data.get("unknown_patterns", False):
                complexity_score += 2
                factors.append("Unknown error patterns require deep analysis")
        
        # Clamp to 1-10 range
        final_score = max(1, min(10, complexity_score))
        
        return {
            "complexity_score": final_score,
            "complexity_level": self._score_to_level(final_score),
            "factors": factors,
            "token_estimate": self._estimate_token_usage(final_score)
        }
    
    def _score_to_level(self, score: int) -> str:
        """Convert numeric complexity score to level"""
        if score <= self.complexity_thresholds["simple"]:
            return "simple"
        elif score <= self.complexity_thresholds["moderate"]:
            return "moderate"
        else:
            return "complex"
    
    def _estimate_token_usage(self, complexity_score: int) -> Dict[str, int]:
        """Estimate token usage based on complexity"""
        base_tokens = {
            "input": 1000,   # Base prompt size
            "output": 500    # Base response size
        }
        
        # Scale with complexity
        multiplier = 1.0 + (complexity_score - 5) * 0.2  # Each point above 5 adds 20%
        
        return {
            "input_tokens": int(base_tokens["input"] * multiplier),
            "output_tokens": int(base_tokens["output"] * multiplier),
            "total_tokens": int((base_tokens["input"] + base_tokens["output"]) * multiplier)
        }
    
    def _check_budget_status(self) -> Dict[str, Any]:
        """Check current budget usage and constraints"""
        
        daily_usage_percent = self.cost_tracking.daily_spend / self.cost_tracking.daily_limit
        monthly_usage_percent = self.cost_tracking.monthly_spend / self.cost_tracking.monthly_limit
        
        # Determine budget status color
        max_usage = max(daily_usage_percent, monthly_usage_percent)
        
        if max_usage >= self.budget_thresholds["red"]:
            status = "red"
        elif max_usage >= self.budget_thresholds["yellow"]:
            status = "yellow"
        else:
            status = "green"
        
        return {
            "status": status,
            "daily_spend": self.cost_tracking.daily_spend,
            "daily_limit": self.cost_tracking.daily_limit,
            "daily_usage_percent": daily_usage_percent,
            "monthly_spend": self.cost_tracking.monthly_spend,
            "monthly_limit": self.cost_tracking.monthly_limit,
            "monthly_usage_percent": monthly_usage_percent,
            "operations_today": self.cost_tracking.operations_today,
            "remaining_daily_budget": self.cost_tracking.daily_limit - self.cost_tracking.daily_spend
        }
    
    def _make_routing_decision(self, complexity: Dict[str, Any], budget: Dict[str, Any], request: Dict[str, Any]) -> ModelRoutingDecision:
        """Apply routing decision matrix to choose optimal model"""
        
        complexity_level = complexity["complexity_level"]
        budget_status = budget["status"]
        priority = request.get("priority", "medium").lower()
        
        # Decision matrix logic
        chosen_model = "haiku"  # Default to cheaper model
        routing_reason = "Default routing"
        
        # Priority overrides (critical always gets best model)
        if priority == "critical":
            chosen_model = "sonnet"
            routing_reason = "Critical priority requires highest quality analysis"
            
        # Budget constraints (red status forces cheap models)
        elif budget_status == "red" and priority != "critical":
            chosen_model = "haiku"
            routing_reason = "Budget constraints require cost-effective routing"
            
        # Complexity-based routing for normal budget status
        elif budget_status == "green":
            if complexity_level == "simple":
                chosen_model = "haiku"
                routing_reason = "Simple analysis suitable for cost-effective model"
            elif complexity_level == "moderate":
                chosen_model = "haiku"  # Prefer cheaper for moderate complexity
                routing_reason = "Moderate complexity, choosing cost-effective option"
            else:  # complex
                chosen_model = "sonnet"
                routing_reason = "Complex analysis requires advanced reasoning capabilities"
                
        # Yellow budget status (cautious routing)
        elif budget_status == "yellow":
            if complexity_level == "complex" and priority in ["high", "critical"]:
                chosen_model = "sonnet" 
                routing_reason = "Complex high-priority analysis justifies higher cost"
            else:
                chosen_model = "haiku"
                routing_reason = "Budget caution with acceptable complexity for Haiku"
        
        # Calculate costs
        estimated_cost = self.model_costs[chosen_model]["avg_analysis"]
        alternative_model = "sonnet" if chosen_model == "haiku" else "haiku"
        alternative_cost = self.model_costs[alternative_model]["avg_analysis"]
        
        # Budget impact calculation
        budget_impact = (estimated_cost / budget["remaining_daily_budget"]) * 100 if budget["remaining_daily_budget"] > 0 else 100
        
        return ModelRoutingDecision(
            chosen_model=chosen_model,
            estimated_cost=estimated_cost,
            routing_reason=routing_reason,
            confidence=8,  # High confidence in matrix-based decisions
            budget_impact=budget_impact,
            alternative_model=alternative_model,
            alternative_cost=alternative_cost
        )
    
    def _validate_routing_decision(self, decision: ModelRoutingDecision, budget: Dict[str, Any]) -> ModelRoutingDecision:
        """Validate routing decision against hard constraints"""
        
        # Check if we have enough budget for the chosen model
        remaining_budget = budget["remaining_daily_budget"]
        
        if decision.estimated_cost > remaining_budget:
            # Force downgrade to cheaper model
            if decision.chosen_model == "sonnet":
                logger.warning(f"Insufficient budget for Sonnet (${decision.estimated_cost:.4f} > ${remaining_budget:.4f}), downgrading to Haiku")
                decision.chosen_model = "haiku"
                decision.estimated_cost = self.model_costs["haiku"]["avg_analysis"] 
                decision.routing_reason = f"Budget constraint forced downgrade from Sonnet: {decision.routing_reason}"
                decision.confidence = 6  # Lower confidence for forced decisions
            else:
                # Even Haiku is too expensive - this is unusual
                logger.error(f"Insufficient budget even for Haiku: ${decision.estimated_cost:.4f} > ${remaining_budget:.4f}")
                decision.routing_reason = f"BUDGET CRISIS: {decision.routing_reason}"
                decision.confidence = 3
        
        return decision
    
    def _record_routing_decision(self, decision: ModelRoutingDecision, request: Dict[str, Any]) -> None:
        """Record routing decision for cost tracking and learning"""
        
        # Update cost tracking
        self.cost_tracking.daily_spend += decision.estimated_cost
        self.cost_tracking.monthly_spend += decision.estimated_cost
        self.cost_tracking.operations_today += 1
        
        # Save updated tracking
        self._save_cost_tracking(self.cost_tracking)
        
        # Log decision for analysis
        logger.info(f"📊 Cost tracking updated: Daily ${self.cost_tracking.daily_spend:.4f}/{self.cost_tracking.daily_limit:.2f}, Operations: {self.cost_tracking.operations_today}")
    
    def _fallback_routing_decision(self) -> ModelRoutingDecision:
        """Fallback routing decision when optimization fails"""
        return ModelRoutingDecision(
            chosen_model="haiku",
            estimated_cost=self.model_costs["haiku"]["avg_analysis"],
            routing_reason="Fallback to cost-effective option due to optimization error",
            confidence=3,
            budget_impact=5.0,
            alternative_model="sonnet", 
            alternative_cost=self.model_costs["sonnet"]["avg_analysis"]
        )
    
    async def get_budget_status(self) -> Dict[str, Any]:
        """Return current budget status for other agents"""
        return self._check_budget_status()
    
    async def record_actual_cost(self, actual_cost: float, model_used: str) -> None:
        """Record actual cost after analysis completion for learning"""
        
        # Calculate variance from estimate
        estimated_cost = self.model_costs[model_used]["avg_analysis"]
        variance = actual_cost - estimated_cost
        
        # Update cost tracking with actual cost
        adjustment = actual_cost - estimated_cost
        self.cost_tracking.daily_spend += adjustment
        self.cost_tracking.monthly_spend += adjustment
        
        # Save updated tracking
        self._save_cost_tracking(self.cost_tracking)
        
        logger.info(f"💰 Actual cost recorded: ${actual_cost:.4f} (variance: ${variance:+.4f} from estimate)")
    
    async def optimize_prompt_for_cost(self, original_prompt: str, target_model: str) -> str:
        """Optimize prompt for cost efficiency while maintaining quality"""
        
        if target_model == "haiku":
            # For Haiku, focus on conciseness and structure
            optimized_sections = [
                "## Analysis Request (Optimized for Haiku)",
                "Focus on primary error identification and actionable solutions.",
                "Limit analysis to top 3 most likely causes.",
                original_prompt.replace("comprehensive analysis", "focused analysis"),
                "## Response Format",
                "Return structured JSON with: status, primary_error, confidence, suggested_actions"
            ]
            return "\n".join(optimized_sections)
            
        else:  # Sonnet
            # For Sonnet, maintain full detail but structure for efficiency
            return f"## Comprehensive Analysis Request\n{original_prompt}\n\n## Response Requirements\nProvide detailed analysis with reasoning for complex failure scenarios."

# CLI interface for testing
async def main():
    """CLI entry point for testing Cost Optimizer Agent"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python cost_optimizer_agent.py <command> [args...]")
        print("Commands:")
        print("  route <github_url> [priority]  - Get routing recommendation")
        print("  budget                         - Check budget status")
        print("  cost <amount> <model>          - Record actual cost")
        return 1
    
    optimizer = CostOptimizerAgent()
    command = sys.argv[1]
    
    try:
        if command == "route":
            github_url = sys.argv[2] if len(sys.argv) > 2 else "https://github.com/example/repo/actions/runs/123"
            priority = sys.argv[3] if len(sys.argv) > 3 else "medium"
            
            request = {
                "github_url": github_url,
                "priority": priority,
                "failure_data": {"job_names": ["Test Job", "Build Job"]}
            }
            
            decision = await optimizer.optimize_model_routing(request)
            print(json.dumps(decision.__dict__, indent=2))
            
        elif command == "budget":
            status = await optimizer.get_budget_status()
            print(json.dumps(status, indent=2))
            
        elif command == "cost":
            if len(sys.argv) < 4:
                print("Usage: cost <amount> <model>")
                return 1
            amount = float(sys.argv[2])
            model = sys.argv[3]
            await optimizer.record_actual_cost(amount, model)
            print(f"✅ Recorded actual cost: ${amount:.4f} for {model}")
            
        else:
            print(f"Unknown command: {command}")
            return 1
            
        return 0
        
    except Exception as e:
        print(f"❌ Command failed: {e}")
        return 1

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())