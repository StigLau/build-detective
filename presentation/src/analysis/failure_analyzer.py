"""
Failure Analyzer - Core analysis engine using Claude Haiku
Optimized for token efficiency and cost-effective pattern recognition
"""
import json
import asyncio
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from utils.logger import setup_logger
from utils.token_optimizer import TokenOptimizer

logger = setup_logger(__name__)

@dataclass
class AnalysisResult:
    """Results from failure analysis"""
    id: str
    status: str  # SUCCESS, FAILURE, PARTIAL
    primary_error: str
    error_type: str
    confidence: float
    blocking_vs_warning: str
    suggested_action: str
    github_commands: List[str]
    estimated_cost: float

class FailureAnalyzer:
    """Core analysis engine using Claude Haiku for cost-effective pattern recognition"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.token_optimizer = TokenOptimizer()
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        
        # Pattern library for quick recognition
        self.known_patterns = {
            'docker_uv_malformed': {
                'pattern': r'=\d+\.\d+\.\d+',
                'error_type': 'docker_build',
                'confidence': 0.9,
                'action': 'Quote version specifiers in Dockerfile UV commands'
            },
            'pytest_missing': {
                'pattern': r'pytest.*not available|--extra dev',
                'error_type': 'dependency',
                'confidence': 0.85,
                'action': 'Add --extra dev flag to UV install command'
            },
            'python_import': {
                'pattern': r'ImportError|ModuleNotFoundError|cannot import',
                'error_type': 'python_import',
                'confidence': 0.8,
                'action': 'Check module installation and PYTHONPATH'
            },
            'docker_copy': {
                'pattern': r'COPY.*no such file|cannot stat',
                'error_type': 'docker_build',
                'confidence': 0.9,
                'action': 'Verify file paths in COPY instruction'
            },
            'git_submodule': {
                'pattern': r'submodule.*failed|git submodule',
                'error_type': 'git',
                'confidence': 0.85,
                'action': 'Initialize git submodules or check .gitmodules'
            }
        }
    
    async def analyze_failure(self, failure: Dict) -> AnalysisResult:
        """
        Analyze a single CI failure
        
        Args:
            failure: Failure information including logs
            
        Returns:
            Analysis result with recommendations
        """
        failure_id = failure.get('id', 'unknown')
        logs = failure.get('logs', '')
        
        logger.info(f"🔍 Analyzing failure: {failure_id}")
        
        # Step 1: Quick pattern matching (no API cost)
        pattern_result = self._check_known_patterns(logs)
        if pattern_result and pattern_result.confidence > 0.8:
            logger.info(f"✅ Pattern match found: {pattern_result.error_type}")
            return pattern_result
        
        # Step 2: Use Haiku for deeper analysis
        if self.anthropic_api_key:
            haiku_result = await self._analyze_with_haiku(failure)
            if haiku_result:
                return haiku_result
        
        # Step 3: Fallback analysis
        logger.warning(f"⚠️ Using fallback analysis for {failure_id}")
        return self._create_fallback_analysis(failure)
    
    async def batch_analyze(self, failures: List[Dict]) -> List[AnalysisResult]:
        """
        Analyze multiple failures efficiently
        
        Args:
            failures: List of failure information
            
        Returns:
            List of analysis results
        """
        if not failures:
            return []
        
        logger.info(f"🔍 Batch analyzing {len(failures)} failures")
        
        # Quick pattern matching for all failures
        results = []
        needs_haiku = []
        
        for failure in failures:
            pattern_result = self._check_known_patterns(failure.get('logs', ''))
            if pattern_result and pattern_result.confidence > 0.8:
                results.append(pattern_result)
            else:
                needs_haiku.append(failure)
        
        # Batch Haiku analysis for remaining failures
        if needs_haiku and self.anthropic_api_key:
            haiku_results = await self._batch_analyze_with_haiku(needs_haiku)
            results.extend(haiku_results)
        else:
            # Fallback for remaining
            for failure in needs_haiku:
                results.append(self._create_fallback_analysis(failure))
        
        logger.info(f"✅ Completed batch analysis: {len(results)} results")
        return results
    
    def _check_known_patterns(self, logs: str) -> Optional[AnalysisResult]:
        """Check against known failure patterns for instant recognition"""
        if not logs:
            return None
        
        import re
        
        for pattern_name, pattern_info in self.known_patterns.items():
            if re.search(pattern_info['pattern'], logs, re.IGNORECASE):
                logger.info(f"🎯 Pattern match: {pattern_name}")
                
                return AnalysisResult(
                    id=f"pattern-{pattern_name}",
                    status="FAILURE",
                    primary_error=f"Detected {pattern_name.replace('_', ' ')} pattern",
                    error_type=pattern_info['error_type'],
                    confidence=pattern_info['confidence'],
                    blocking_vs_warning="BLOCKING",
                    suggested_action=pattern_info['action'],
                    github_commands=[],
                    estimated_cost=0.0  # No API cost for pattern matching
                )
        
        return None
    
    async def _analyze_with_haiku(self, failure: Dict) -> Optional[AnalysisResult]:
        """Use Claude Haiku for detailed analysis"""
        try:
            # Prepare optimized prompt
            prompt = self._create_analysis_prompt(failure)
            
            # Simulate Haiku API call (in production, use real Anthropic client)
            logger.info("🤖 Calling Haiku API for analysis...")
            await asyncio.sleep(0.5)  # Simulate API latency
            
            # Mock response (in production, parse actual Haiku response)
            response = await self._mock_haiku_response(failure)
            
            return self._parse_haiku_response(response, failure)
            
        except Exception as e:
            logger.error(f"❌ Haiku analysis failed: {e}")
            return None
    
    async def _batch_analyze_with_haiku(self, failures: List[Dict]) -> List[AnalysisResult]:
        """Batch analyze multiple failures with Haiku"""
        results = []
        
        # Process in smaller batches for efficiency
        batch_size = 3  # Optimize for token limits
        for i in range(0, len(failures), batch_size):
            batch = failures[i:i + batch_size]
            
            try:
                batch_prompt = self._create_batch_analysis_prompt(batch)
                
                logger.info(f"🤖 Batch Haiku analysis for {len(batch)} failures...")
                await asyncio.sleep(0.8)  # Simulate API call
                
                # Mock batch response
                batch_response = await self._mock_batch_haiku_response(batch)
                batch_results = self._parse_batch_haiku_response(batch_response, batch)
                
                results.extend(batch_results)
                
            except Exception as e:
                logger.error(f"❌ Batch Haiku analysis failed: {e}")
                # Fallback for this batch
                for failure in batch:
                    results.append(self._create_fallback_analysis(failure))
        
        return results
    
    def _create_analysis_prompt(self, failure: Dict) -> str:
        """Create optimized prompt for Haiku analysis"""
        logs = failure.get('logs', '')
        job_name = failure.get('job_name', 'Unknown')
        
        # Compress logs for cost efficiency
        compressed_logs = self.token_optimizer.compress_logs(logs, max_tokens=400)
        
        return f"""Analyze CI failure and provide structured response:

Job: {job_name}
Error Logs:
{compressed_logs}

Apply Build Detective patterns:
- UV dependency: pytest missing, --extra dev needed
- Docker malformed: =X.X.X version files  
- Python imports: module resolution failures
- Git submodules: initialization problems

Return JSON only:
{{
  "status": "FAILURE|PARTIAL|SUCCESS",
  "primary_error": "Main blocking error",
  "error_type": "dependency|docker_build|python_import|git|compilation|timeout|permission|other",
  "confidence": 0.85,
  "blocking_vs_warning": "BLOCKING|WARNING",
  "suggested_action": "Specific fix command or approach"
}}

Be concise and actionable."""
    
    def _create_batch_analysis_prompt(self, failures: List[Dict]) -> str:
        """Create batch analysis prompt for multiple failures"""
        failure_summaries = []
        
        for i, failure in enumerate(failures):
            logs = failure.get('logs', '')
            compressed = self.token_optimizer.compress_logs(logs, max_tokens=200)
            
            summary = f"Failure {i+1}:\nJob: {failure.get('job_name', 'Unknown')}\nLogs:\n{compressed}\n"
            failure_summaries.append(summary)
        
        combined = "\n---\n".join(failure_summaries)
        
        return f"""Analyze {len(failures)} CI failures, return JSON array:

{combined}

For each failure, provide:
{{
  "failure_index": 1,
  "status": "FAILURE|PARTIAL",
  "primary_error": "Brief error description",
  "error_type": "dependency|docker_build|python_import|git|other",
  "confidence": 0.8,
  "suggested_action": "Specific fix"
}}

Focus on Build Detective patterns. Be concise."""
    
    async def _mock_haiku_response(self, failure: Dict) -> str:
        """Mock Haiku response for demonstration"""
        logs = failure.get('logs', '').lower()
        
        # Simulate intelligent pattern recognition
        if 'docker' in logs and ('=1.' in logs or '=0.' in logs):
            return '''{
                "status": "FAILURE",
                "primary_error": "Docker UV creates malformed version files (=1.0.0)",
                "error_type": "docker_build", 
                "confidence": 0.9,
                "blocking_vs_warning": "BLOCKING",
                "suggested_action": "Quote UV version specifiers in Dockerfile"
            }'''
        elif 'pytest' in logs and ('not available' in logs or 'extra dev' in logs):
            return '''{
                "status": "FAILURE",
                "primary_error": "Pytest not available - missing dev dependencies",
                "error_type": "dependency",
                "confidence": 0.85,
                "blocking_vs_warning": "BLOCKING", 
                "suggested_action": "Add --extra dev flag to UV install command"
            }'''
        else:
            return '''{
                "status": "PARTIAL",
                "primary_error": "General CI failure - needs investigation",
                "error_type": "other",
                "confidence": 0.6,
                "blocking_vs_warning": "BLOCKING",
                "suggested_action": "Review logs for specific error patterns"
            }'''
    
    async def _mock_batch_haiku_response(self, failures: List[Dict]) -> str:
        """Mock batch Haiku response"""
        results = []
        
        for i, failure in enumerate(failures):
            single_response = await self._mock_haiku_response(failure)
            response_data = json.loads(single_response)
            response_data['failure_index'] = i + 1
            results.append(response_data)
        
        return json.dumps(results)
    
    def _parse_haiku_response(self, response: str, failure: Dict) -> AnalysisResult:
        """Parse Haiku JSON response into AnalysisResult"""
        try:
            data = json.loads(response)
            
            return AnalysisResult(
                id=failure.get('id', 'unknown'),
                status=data.get('status', 'PARTIAL'),
                primary_error=data.get('primary_error', 'Unknown error'),
                error_type=data.get('error_type', 'other'),
                confidence=data.get('confidence', 0.5),
                blocking_vs_warning=data.get('blocking_vs_warning', 'BLOCKING'),
                suggested_action=data.get('suggested_action', 'Manual investigation needed'),
                github_commands=[],
                estimated_cost=0.03  # Typical Haiku cost
            )
            
        except json.JSONDecodeError:
            logger.warning("⚠️ Failed to parse Haiku response")
            return self._create_fallback_analysis(failure)
    
    def _parse_batch_haiku_response(self, response: str, failures: List[Dict]) -> List[AnalysisResult]:
        """Parse batch Haiku response"""
        try:
            data = json.loads(response)
            results = []
            
            for item in data:
                failure_index = item.get('failure_index', 1) - 1
                if 0 <= failure_index < len(failures):
                    failure = failures[failure_index]
                    
                    result = AnalysisResult(
                        id=failure.get('id', f'batch-{failure_index}'),
                        status=item.get('status', 'PARTIAL'),
                        primary_error=item.get('primary_error', 'Unknown error'),
                        error_type=item.get('error_type', 'other'),
                        confidence=item.get('confidence', 0.5),
                        blocking_vs_warning=item.get('blocking_vs_warning', 'BLOCKING'),
                        suggested_action=item.get('suggested_action', 'Manual investigation needed'),
                        github_commands=[],
                        estimated_cost=0.02  # Batch discount
                    )
                    results.append(result)
            
            return results
            
        except json.JSONDecodeError:
            logger.warning("⚠️ Failed to parse batch Haiku response")
            return [self._create_fallback_analysis(f) for f in failures]
    
    def _create_fallback_analysis(self, failure: Dict) -> AnalysisResult:
        """Create fallback analysis when AI analysis fails"""
        return AnalysisResult(
            id=failure.get('id', 'unknown'),
            status="PARTIAL",
            primary_error="Analysis failed - manual review needed",
            error_type="analysis_failure",
            confidence=0.1,
            blocking_vs_warning="WARNING",
            suggested_action="Manual investigation required - check logs manually",
            github_commands=[],
            estimated_cost=0.0
        )