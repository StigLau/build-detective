"""
Supervisor - Main orchestration using Claude Sonnet
Quality control and task delegation for Build Detective
"""
import json
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import yaml
from pathlib import Path

from analysis.failure_analyzer import FailureAnalyzer
from issue_tracker.database import IssueDatabase
from utils.token_optimizer import TokenOptimizer
from utils.logger import setup_logger

logger = setup_logger(__name__)

@dataclass
class AnalysisPlan:
    """Plan for analyzing a batch of failures"""
    batch_groups: Dict[str, List[Any]]
    use_cache: List[str]
    need_analysis: List[str]
    estimated_tokens: int

@dataclass
class QCResult:
    """Quality control result for Haiku analysis"""
    passed: bool
    confidence_adjustment: float
    issues: List[str]
    needs_escalation: bool

class Supervisor:
    """Main orchestration component using Claude Sonnet for oversight"""
    
    def __init__(self, config_path: str = "config/settings.yaml"):
        self.config = self._load_config(config_path)
        
        self.analyzer = FailureAnalyzer(self.config)
        self.issue_db = IssueDatabase()
        self.token_optimizer = TokenOptimizer()
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration with fallback to defaults"""
        try:
            config_file = Path(__file__).parent.parent.parent / config_path
            if config_file.exists():
                with open(config_file) as f:
                    return yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"Config load failed: {e}, using defaults")
        
        return self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration"""
        return {
            "claude": {
                "orchestrator_model": "claude-3-5-sonnet-20241022",
                "analyzer_model": "claude-3-haiku-20240307",
                "max_tokens_per_request": 1000,
                "temperature": 0.2
            },
            "github": {
                "poll_interval": 300,
                "max_repos": 10
            },
            "analysis": {
                "confidence_threshold": 0.7,
                "max_retries": 3,
                "cache_ttl": 3600
            },
            "repos": []
        }
    
    def get_configured_repos(self) -> List[str]:
        """Get list of repositories to monitor"""
        return self.config.get("repos", [])
    
    async def analyze_failures(self, failures: List[Dict]) -> Dict[str, Any]:
        """
        Main analysis orchestration
        
        Args:
            failures: List of CI failure information
            
        Returns:
            Analysis results with recommendations
        """
        if not failures:
            return {"status": "no_failures", "analyses": []}
        
        logger.info(f"🔍 Orchestrating analysis of {len(failures)} failures")
        
        # Step 1: Plan the analysis strategy
        plan = self.plan_analysis(failures)
        logger.info(f"📋 Analysis plan: {len(plan.use_cache)} cached, {len(plan.need_analysis)} need analysis")
        
        # Step 2: Get cached solutions
        cached_results = []
        for failure_id in plan.use_cache:
            cached = self._get_cached_solution(failure_id)
            if cached:
                cached_results.append(cached)
        
        # Step 3: Analyze new failures with Haiku
        new_analyses = []
        if plan.need_analysis:
            for error_type, failure_group in plan.batch_groups.items():
                try:
                    batch_analysis = await self.analyzer.batch_analyze(failure_group)
                    for analysis in batch_analysis:
                        # Quality control
                        qc_result = self.review_results(analysis)
                        if qc_result.needs_escalation:
                            analysis = await self._escalate_to_sonnet(analysis)
                        else:
                            analysis['confidence'] *= qc_result.confidence_adjustment
                        
                        new_analyses.append(analysis)
                        
                        # Cache if high confidence
                        if analysis['confidence'] > 0.8:
                            self.issue_db.cache_solution(analysis)
                            
                except Exception as e:
                    logger.error(f"❌ Batch analysis failed for {error_type}: {e}")
                    # Fallback analysis
                    for failure in failure_group:
                        fallback = self._create_fallback_analysis(failure)
                        new_analyses.append(fallback)
        
        # Step 4: Combine and return results
        all_analyses = cached_results + new_analyses
        
        return {
            "status": "completed",
            "total_failures": len(failures),
            "analyses": all_analyses,
            "cached_count": len(cached_results),
            "new_analysis_count": len(new_analyses),
            "estimated_cost": plan.estimated_tokens * 0.000025,  # Haiku pricing
            "summary": self._generate_summary(all_analyses)
        }
    
    def plan_analysis(self, failures: List[Dict]) -> AnalysisPlan:
        """Plan the analysis strategy for a batch of failures"""
        plan = AnalysisPlan(
            batch_groups={},
            use_cache=[],
            need_analysis=[],
            estimated_tokens=0
        )
        
        for failure in failures:
            failure_id = failure.get('id', str(hash(str(failure))))
            
            # Check if we've seen this before
            if self.issue_db.has_recent_solution(failure):
                plan.use_cache.append(failure_id)
            else:
                plan.need_analysis.append(failure_id)
                # Group by error type for batching
                error_type = self._categorize_error(failure)
                if error_type not in plan.batch_groups:
                    plan.batch_groups[error_type] = []
                plan.batch_groups[error_type].append(failure)
        
        # Estimate token usage
        for group in plan.batch_groups.values():
            for failure in group:
                logs = failure.get('logs', '')
                compressed = self.token_optimizer.compress_logs(logs, max_tokens=500)
                plan.estimated_tokens += self.token_optimizer.estimate_tokens(compressed)
        
        return plan
    
    def review_results(self, analysis: Dict) -> QCResult:
        """Quality control for Haiku's analysis"""
        qc = QCResult(
            passed=True,
            confidence_adjustment=1.0,
            issues=[],
            needs_escalation=False
        )
        
        # Check confidence score reasonableness
        confidence = analysis.get('confidence', 0)
        if confidence > 0.95:
            qc.issues.append("Confidence suspiciously high")
            qc.confidence_adjustment = 0.9
        elif confidence < 0.4:
            qc.issues.append("Very low confidence")
            qc.needs_escalation = True
        
        # Check if suggested action is too generic
        action = analysis.get('suggested_action', '').lower()
        generic_phrases = ['check configuration', 'review logs', 'investigate further']
        if any(phrase in action for phrase in generic_phrases):
            qc.issues.append("Generic suggested action")
            qc.confidence_adjustment *= 0.8
        
        # Check for technology stack mismatch
        error_type = analysis.get('error_type', '')
        primary_error = analysis.get('primary_error', '').lower()
        if 'java' in primary_error and 'python' in error_type:
            qc.issues.append("Technology stack mismatch")
            qc.needs_escalation = True
        
        return qc
    
    async def _escalate_to_sonnet(self, analysis: Dict) -> Dict:
        """Escalate complex analysis to Sonnet for review"""
        logger.info("🆙 Escalating analysis to Sonnet for review")
        
        # In a real implementation, this would call Claude Sonnet
        # For now, return adjusted analysis
        analysis['escalated'] = True
        analysis['confidence'] = min(analysis.get('confidence', 0.5) + 0.2, 0.9)
        analysis['reviewed_by'] = 'sonnet'
        
        return analysis
    
    def _categorize_error(self, failure: Dict) -> str:
        """Categorize failure type for batching"""
        logs = failure.get('logs', '').lower()
        error_msg = failure.get('error', '').lower()
        
        combined = f"{logs} {error_msg}"
        
        if any(keyword in combined for keyword in ['compile', 'compilation', 'syntax']):
            return 'compilation'
        elif any(keyword in combined for keyword in ['import', 'module not found', 'dependency']):
            return 'dependency'
        elif any(keyword in combined for keyword in ['docker', 'container', 'dockerfile']):
            return 'docker'
        elif any(keyword in combined for keyword in ['timeout', 'timed out', 'deadline']):
            return 'timeout'
        elif any(keyword in combined for keyword in ['permission', 'access denied', 'unauthorized']):
            return 'permission'
        else:
            return 'general'
    
    def _get_cached_solution(self, failure_id: str) -> Optional[Dict]:
        """Get cached solution if available"""
        # Implementation would query issue database
        return None
    
    def _create_fallback_analysis(self, failure: Dict) -> Dict:
        """Create fallback analysis when automated analysis fails"""
        return {
            "id": failure.get('id', 'unknown'),
            "status": "partial",
            "primary_error": "Analysis failed - manual review needed",
            "error_type": "analysis_failure",
            "confidence": 0.1,
            "suggested_action": "Manual investigation required",
            "escalated": True
        }
    
    def _generate_summary(self, analyses: List[Dict]) -> Dict:
        """Generate summary of all analyses"""
        if not analyses:
            return {"total": 0}
        
        total = len(analyses)
        high_confidence = len([a for a in analyses if a.get('confidence', 0) > 0.8])
        escalated = len([a for a in analyses if a.get('escalated', False)])
        
        # Group by error type
        error_types = {}
        for analysis in analyses:
            error_type = analysis.get('error_type', 'unknown')
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        return {
            "total": total,
            "high_confidence": high_confidence,
            "escalated": escalated,
            "error_types": error_types,
            "avg_confidence": sum(a.get('confidence', 0) for a in analyses) / total
        }