#!/usr/bin/env python3
"""
Build Detective CI Analysis Specialist Agent

Domain expert for CI/CD pattern recognition and failure analysis.
Implements deep pattern matching for Maven, Docker, Python, and other build systems.
"""

import json
import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ErrorPattern:
    """Represents a known CI/CD error pattern"""
    name: str
    description: str
    indicators: List[str]  # Text patterns that indicate this error
    error_type: str
    confidence_boost: int  # How much this pattern increases confidence
    solutions: List[str]   # Suggested fix commands
    verification_steps: List[str]

class CISpecialistAgent:
    """
    CI Analysis Specialist - Deep pattern recognition for build failures
    
    This agent implements Build Detective's core pattern matching capabilities
    with technology-specific expertise for common CI/CD failure scenarios.
    """
    
    def __init__(self):
        self.agent_name = "build-detective-ci-specialist"
        self.error_patterns = self._initialize_error_patterns()
        self.technology_detectors = self._initialize_tech_detectors()
    
    def _initialize_error_patterns(self) -> Dict[str, List[ErrorPattern]]:
        """Initialize comprehensive error pattern database"""
        
        patterns = {
            "maven": [
                ErrorPattern(
                    name="surefire_reports_missing",
                    description="Maven Surefire plugin failed to generate test reports",
                    indicators=[
                        "No tests were executed!",
                        "surefire-reports",
                        "There are test failures",
                        "BUILD FAILURE.*Tests run:"
                    ],
                    error_type="maven_test",
                    confidence_boost=3,
                    solutions=[
                        "mvn clean test -Dtest=FailingTestClass", 
                        "mvn surefire:test",
                        "Check test dependencies in pom.xml"
                    ],
                    verification_steps=[
                        "Check target/surefire-reports/ directory",
                        "Verify test classes are in correct src/test/java path"
                    ]
                ),
                ErrorPattern(
                    name="dependency_resolution_conflict", 
                    description="Maven dependency resolution conflicts or missing artifacts",
                    indicators=[
                        "Could not resolve dependencies",
                        "Failed to collect dependencies", 
                        "ArtifactResolutionException",
                        "Non-resolvable parent POM"
                    ],
                    error_type="maven_dependency",
                    confidence_boost=4,
                    solutions=[
                        "mvn dependency:resolve-sources",
                        "mvn clean install -U",  # Force update snapshots
                        "Check repository configuration in pom.xml"
                    ],
                    verification_steps=[
                        "Run mvn dependency:tree to check conflicts",
                        "Verify repository URLs are accessible"
                    ]
                ),
                ErrorPattern(
                    name="jdk_version_mismatch",
                    description="JDK version compatibility issues in multi-version builds",
                    indicators=[
                        "invalid target release:",
                        "class file version",
                        "UnsupportedClassVersionError",
                        "JAVA_HOME.*not found"
                    ],
                    error_type="maven_jdk",
                    confidence_boost=4,
                    solutions=[
                        "Check maven.compiler.source and maven.compiler.target",
                        "Verify JAVA_HOME points to correct JDK version",
                        "Update maven-compiler-plugin configuration"
                    ],
                    verification_steps=[
                        "Run java -version and mvn -version",
                        "Check pom.xml compiler plugin configuration"
                    ]
                )
            ],
            
            "python": [
                ErrorPattern(
                    name="pytest_not_found",
                    description="pytest executable not available or not installed",
                    indicators=[
                        "pytest: command not found",
                        "No module named 'pytest'",
                        "ModuleNotFoundError.*pytest"
                    ],
                    error_type="python_test",
                    confidence_boost=4,
                    solutions=[
                        "pip install pytest",
                        "pip install --extra dev",  # For UV-based projects
                        "python -m pytest instead of pytest command"
                    ],
                    verification_steps=[
                        "Run pip list | grep pytest",
                        "Check requirements.txt or pyproject.toml for test dependencies"
                    ]
                ),
                ErrorPattern(
                    name="uv_extra_dev_needed",
                    description="UV project missing --extra dev flag for development dependencies",
                    indicators=[
                        "No module named.*in test file",
                        "ImportError.*test",
                        "uv.*--extra"
                    ],
                    error_type="python_dependency",
                    confidence_boost=3,
                    solutions=[
                        "uv pip install --extra dev",
                        "uv sync --extra dev", 
                        "Add dev dependencies to pyproject.toml [project.optional-dependencies]"
                    ],
                    verification_steps=[
                        "Check pyproject.toml for [project.optional-dependencies.dev]",
                        "Run uv pip list to see installed packages"
                    ]
                ),
                ErrorPattern(
                    name="import_resolution_error",
                    description="Python module import path resolution issues",
                    indicators=[
                        "ModuleNotFoundError",
                        "ImportError.*No module named",
                        "relative import with no known parent package"
                    ],
                    error_type="python_import",
                    confidence_boost=2,
                    solutions=[
                        "Add __init__.py files to package directories",
                        "Update PYTHONPATH or use pip install -e .",
                        "Check import paths are relative to project root"
                    ],
                    verification_steps=[
                        "Verify package structure has __init__.py files",
                        "Run python -c 'import package_name' to test imports"
                    ]
                )
            ],
            
            "docker": [
                ErrorPattern(
                    name="malformed_version_specifiers",
                    description="Docker build fails due to malformed version specifiers in UV commands",
                    indicators=[
                        "=1.0.0",
                        "=1.9.3", 
                        "Invalid requirement.*=",
                        "ERROR.*parsing.*version"
                    ],
                    error_type="docker_build",
                    confidence_boost=4,
                    solutions=[
                        "Quote version specifiers: '==1.0.0' not =1.0.0",
                        "Use proper pip syntax for version pinning",
                        "Add cache-busting layer: RUN touch /tmp/cache_bust"
                    ],
                    verification_steps=[
                        "Check Dockerfile for unquoted version specifiers",
                        "Test docker build locally with --no-cache"
                    ]
                ),
                ErrorPattern(
                    name="layer_cache_invalidation",
                    description="Docker build fails due to layer caching issues",
                    indicators=[
                        "COPY failed",
                        "ADD failed", 
                        "No such file or directory.*COPY",
                        "cache.*invalidated"
                    ],
                    error_type="docker_cache",
                    confidence_boost=3,
                    solutions=[
                        "docker build --no-cache",
                        "Reorder Dockerfile to optimize layer caching",
                        "Use .dockerignore to exclude changing files"
                    ],
                    verification_steps=[
                        "Check .dockerignore file exists and is properly configured",
                        "Verify COPY/ADD paths are correct relative to build context"
                    ]
                )
            ],
            
            "workflow": [
                ErrorPattern(
                    name="semantic_version_workflow_failure",
                    description="Semantic versioning automation workflow issues",
                    indicators=[
                        "semantic-release",
                        "conventional commits",
                        "version calculation failed",
                        "tag creation failed"
                    ],
                    error_type="workflow_versioning",
                    confidence_boost=3,
                    solutions=[
                        "Check commit message follows conventional commit format",
                        "Verify semantic-release configuration",
                        "Ensure proper GitHub permissions for tagging"
                    ],
                    verification_steps=[
                        "Review recent commit messages for format compliance",
                        "Check semantic-release logs for specific error details"
                    ]
                ),
                ErrorPattern(
                    name="github_actions_matrix_failure",
                    description="Matrix build failures across multiple versions/platforms",
                    indicators=[
                        "matrix.*failed",
                        "strategy.*matrix",
                        "Multiple job failures"
                    ],
                    error_type="workflow_matrix",
                    confidence_boost=2,
                    solutions=[
                        "Review matrix configuration for version compatibility",
                        "Add fail-fast: false to continue other matrix jobs",
                        "Check for platform-specific issues"
                    ],
                    verification_steps=[
                        "Review individual matrix job logs",
                        "Test locally with different versions/platforms"
                    ]
                )
            ],
            
            "integration": [
                ErrorPattern(
                    name="aws_integration_failure",
                    description="AWS service integration test failures",
                    indicators=[
                        "AWS.*authentication",
                        "S3.*403",
                        "DynamoDB.*AccessDenied",
                        "Integration Tests with AWS.*failed"
                    ],
                    error_type="integration_aws",
                    confidence_boost=4,
                    solutions=[
                        "Check AWS credentials are properly configured",
                        "Verify IAM permissions for test resources", 
                        "Ensure test environment AWS configuration is correct"
                    ],
                    verification_steps=[
                        "Run aws sts get-caller-identity to verify credentials",
                        "Check IAM policy for required service permissions"
                    ]
                )
            ]
        }
        
        return patterns
    
    def _initialize_tech_detectors(self) -> Dict[str, List[str]]:
        """Initialize technology detection patterns"""
        return {
            "maven": ["pom.xml", "mvn", "Maven", "Surefire"],
            "python": ["pip", "pytest", "python", "uv", ".py"],
            "docker": ["Dockerfile", "docker build", "COPY", "FROM"],
            "node": ["npm", "yarn", "package.json", "node"],
            "workflow": [".github", "actions", "workflow", "jobs"]
        }
    
    async def analyze_ci_failure(self, github_url: str, failure_data: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Main analysis method - deep CI/CD failure pattern recognition
        
        Args:
            github_url: GitHub Actions/PR URL
            failure_data: Raw failure information (job names, logs, etc.)
            context: Additional context from other agents
            
        Returns:
            Structured analysis with patterns matched and solutions
        """
        logger.info(f"🔍 CI Specialist analyzing: {github_url}")
        
        try:
            # Step 1: Extract failure details and logs
            enriched_failures = await self._enrich_failure_data(github_url, failure_data)
            
            # Step 2: Detect primary technologies involved
            tech_stack = self._detect_technologies(enriched_failures)
            
            # Step 3: Pattern matching against known failure patterns
            matched_patterns = self._match_error_patterns(enriched_failures, tech_stack)
            
            # Step 4: Analyze pattern confidence and primary error
            analysis = self._analyze_patterns(matched_patterns, enriched_failures)
            
            # Step 5: Generate actionable solutions
            solutions = self._generate_solutions(analysis, matched_patterns, tech_stack)
            
            # Step 6: Create structured response
            result = self._create_analysis_response(analysis, solutions, matched_patterns, tech_stack)
            
            logger.info(f"✅ CI Specialist analysis complete: {result['confidence']}/10 confidence")
            return result
            
        except Exception as e:
            logger.error(f"❌ CI Specialist analysis failed: {e}")
            return self._error_response(str(e))
    
    async def _enrich_failure_data(self, github_url: str, failure_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich basic failure data with additional context and logs"""
        
        # In real implementation, this would fetch logs via GitHub CLI
        # For now, simulate with the provided failure data
        enriched = {
            "url": github_url,
            "raw_failures": failure_data,
            "job_names": [],
            "error_logs": [],
            "workflow_context": {}
        }
        
        # Extract job names from different possible formats
        if "jobs" in failure_data:
            enriched["job_names"] = [job.get("name", "") for job in failure_data["jobs"]]
        elif "failed_jobs" in failure_data:
            enriched["job_names"] = failure_data["failed_jobs"]
        elif isinstance(failure_data, list):
            enriched["job_names"] = [item.get("job_name", "") for item in failure_data]
        
        return enriched
    
    def _detect_technologies(self, failure_data: Dict[str, Any]) -> List[str]:
        """Detect which technologies are involved based on job names and context"""
        
        detected = set()
        text_to_analyze = " ".join([
            " ".join(failure_data.get("job_names", [])),
            str(failure_data.get("raw_failures", "")),
            str(failure_data.get("error_logs", ""))
        ]).lower()
        
        for tech, indicators in self.technology_detectors.items():
            for indicator in indicators:
                if indicator.lower() in text_to_analyze:
                    detected.add(tech)
                    break
        
        return list(detected)
    
    def _match_error_patterns(self, failure_data: Dict[str, Any], tech_stack: List[str]) -> List[Tuple[ErrorPattern, int]]:
        """Match failure data against known error patterns"""
        
        matched_patterns = []
        
        # Combine all text for pattern matching
        failure_text = " ".join([
            " ".join(failure_data.get("job_names", [])),
            str(failure_data.get("error_logs", "")),
            str(failure_data.get("raw_failures", ""))
        ]).lower()
        
        # Check patterns for detected technologies
        for tech in tech_stack:
            if tech in self.error_patterns:
                for pattern in self.error_patterns[tech]:
                    match_score = self._calculate_pattern_match_score(pattern, failure_text)
                    if match_score > 0:
                        matched_patterns.append((pattern, match_score))
        
        # Sort by match score (highest first)
        matched_patterns.sort(key=lambda x: x[1], reverse=True)
        
        return matched_patterns
    
    def _calculate_pattern_match_score(self, pattern: ErrorPattern, failure_text: str) -> int:
        """Calculate how well a pattern matches the failure text"""
        score = 0
        
        for indicator in pattern.indicators:
            if indicator.lower() in failure_text:
                score += 1
            # Check for regex patterns
            elif self._is_regex_pattern(indicator) and re.search(indicator, failure_text, re.IGNORECASE):
                score += 2  # Regex matches are more specific
        
        return score
    
    def _is_regex_pattern(self, pattern: str) -> bool:
        """Check if a pattern contains regex metacharacters"""
        return any(char in pattern for char in ['.*', '+', '?', '\\d', '\\w', '\\s', '[', ']', '(', ')'])
    
    def _analyze_patterns(self, matched_patterns: List[Tuple[ErrorPattern, int]], failure_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze matched patterns to determine primary error and confidence"""
        
        if not matched_patterns:
            return {
                "primary_error": "Unable to match against known patterns",
                "error_type": "unknown",
                "confidence": 3,
                "pattern_matches": 0
            }
        
        # Primary pattern is the highest scoring match
        primary_pattern, primary_score = matched_patterns[0]
        
        # Calculate overall confidence
        base_confidence = 5  # Base confidence
        pattern_boost = min(primary_pattern.confidence_boost, 4)  # Cap boost at 4
        multiple_patterns_boost = min(len(matched_patterns) - 1, 2)  # Extra patterns add confidence
        
        confidence = min(10, base_confidence + pattern_boost + multiple_patterns_boost)
        
        return {
            "primary_error": primary_pattern.description,
            "error_type": primary_pattern.error_type,
            "confidence": confidence,
            "pattern_matches": len(matched_patterns),
            "primary_pattern": primary_pattern.name,
            "match_score": primary_score
        }
    
    def _generate_solutions(self, analysis: Dict[str, Any], matched_patterns: List[Tuple[ErrorPattern, int]], tech_stack: List[str]) -> Dict[str, Any]:
        """Generate actionable solutions based on matched patterns"""
        
        if not matched_patterns:
            return {
                "suggested_actions": ["Manual log review required"],
                "verification_steps": ["Check individual job logs"],
                "estimated_fix_time": "30+ minutes"
            }
        
        primary_pattern = matched_patterns[0][0]
        
        # Combine solutions from all matched patterns (top 3)
        all_actions = []
        all_verifications = []
        
        for pattern, _ in matched_patterns[:3]:
            all_actions.extend(pattern.solutions)
            all_verifications.extend(pattern.verification_steps)
        
        # Remove duplicates while preserving order
        unique_actions = list(dict.fromkeys(all_actions))
        unique_verifications = list(dict.fromkeys(all_verifications))
        
        # Estimate fix time based on error type
        time_estimates = {
            "maven_test": "5-10 minutes",
            "maven_dependency": "10-15 minutes", 
            "python_test": "5 minutes",
            "docker_build": "10-20 minutes",
            "workflow_versioning": "5 minutes",
            "integration_aws": "15-30 minutes"
        }
        
        return {
            "suggested_actions": unique_actions,
            "verification_steps": unique_verifications,
            "estimated_fix_time": time_estimates.get(analysis["error_type"], "10-15 minutes")
        }
    
    def _create_analysis_response(self, analysis: Dict[str, Any], solutions: Dict[str, Any], matched_patterns: List[Tuple[ErrorPattern, int]], tech_stack: List[str]) -> Dict[str, Any]:
        """Create structured response for other agents and end users"""
        
        return {
            "agent": self.agent_name,
            "status": "FAILURE" if analysis["confidence"] >= 6 else "PARTIAL",
            "primary_error": analysis["primary_error"],
            "error_type": analysis["error_type"],
            "confidence": analysis["confidence"],
            "blocking": analysis["confidence"] >= 6,  # High confidence errors are likely blocking
            "technology_stack": tech_stack,
            "patterns_analysis": {
                "patterns_matched": len(matched_patterns),
                "primary_pattern": analysis.get("primary_pattern", "unknown"),
                "match_quality": analysis.get("match_score", 0)
            },
            "solutions": {
                "suggested_actions": solutions["suggested_actions"],
                "verification_steps": solutions["verification_steps"],
                "estimated_fix_time": solutions["estimated_fix_time"]
            },
            "specialist_notes": {
                "analysis_depth": "pattern_matched" if matched_patterns else "fallback",
                "confidence_factors": [
                    f"Matched {len(matched_patterns)} known patterns",
                    f"Primary pattern confidence: {analysis.get('match_score', 0)}/10",
                    f"Technology stack identified: {', '.join(tech_stack)}"
                ]
            },
            "github_commands": self._generate_github_commands(analysis),
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_github_commands(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate relevant GitHub CLI commands for further investigation"""
        
        base_commands = ["gh run view --log"]
        
        if analysis["error_type"].startswith("maven"):
            base_commands.extend([
                "gh run view --log | grep -A5 -B5 'BUILD FAILURE'",
                "gh run view --log | grep 'Tests run:'"
            ])
        elif analysis["error_type"].startswith("python"):
            base_commands.extend([
                "gh run view --log | grep -A3 -B3 'ModuleNotFoundError'",
                "gh run view --log | grep 'pytest'"
            ])
        elif analysis["error_type"].startswith("docker"):
            base_commands.extend([
                "gh run view --log | grep -A5 'ERROR'",
                "gh run view --log | grep 'COPY\\|ADD'"
            ])
        
        return base_commands
    
    def _error_response(self, error_msg: str) -> Dict[str, Any]:
        """Generate error response when analysis fails"""
        return {
            "agent": self.agent_name,
            "status": "ERROR",
            "primary_error": f"CI Specialist analysis failed: {error_msg}",
            "error_type": "agent_error",
            "confidence": 1,
            "blocking": True,
            "suggested_actions": ["Manual analysis required", "Check agent logs"],
            "timestamp": datetime.now().isoformat()
        }

# CLI interface for testing
async def main():
    """CLI entry point for testing CI Specialist Agent"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python ci_specialist_agent.py <github_url> [job_names...]")
        print("Example: python ci_specialist_agent.py https://github.com/repo/actions/runs/123 'Integration Tests with AWS'")
        return 1
    
    agent = CISpecialistAgent()
    github_url = sys.argv[1]
    
    # Mock failure data from command line arguments
    failure_data = {
        "failed_jobs": sys.argv[2:] if len(sys.argv) > 2 else ["Test Job", "Build Job"],
        "error_logs": "Sample error logs would go here"
    }
    
    try:
        result = await agent.analyze_ci_failure(github_url, failure_data)
        print(json.dumps(result, indent=2))
        return 0
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return 1

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())