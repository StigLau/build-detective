#!/usr/bin/env python3
"""
Java/Maven Build Detective - Specialized analyzer for Apache Camel and other Maven projects
Focuses on Maven Surefire, JUnit, dependency resolution, and compilation issues.
"""

import json
import subprocess
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JavaMavenAnalyzer:
    """Specialized analyzer for Java/Maven projects like Apache Camel"""
    
    def __init__(self):
        self.maven_patterns = {
            "surefire_failure": {
                "indicators": [
                    "Tests run:",
                    "Failures:",
                    "Errors:",
                    "BUILD FAILURE",
                    "Failed to execute goal.*surefire",
                    "There are test failures"
                ],
                "solutions": [
                    "mvn test -Dtest=FailingTestClass",
                    "mvn clean test",
                    "Check target/surefire-reports/ for details"
                ],
                "confidence": 8
            },
            "compilation_error": {
                "indicators": [
                    "COMPILATION ERROR",
                    "Failed to execute goal.*compiler",
                    "package does not exist",
                    "cannot find symbol"
                ],
                "solutions": [
                    "mvn clean compile",
                    "Check imports and dependencies",
                    "Verify Java version compatibility"
                ],
                "confidence": 9
            },
            "dependency_resolution": {
                "indicators": [
                    "Could not resolve dependencies",
                    "Failed to collect dependencies",
                    "ArtifactResolutionException",
                    "Non-resolvable parent POM"
                ],
                "solutions": [
                    "mvn clean install -U",
                    "mvn dependency:resolve-sources",
                    "Check repository configuration"
                ],
                "confidence": 7
            },
            "memory_issues": {
                "indicators": [
                    "OutOfMemoryError",
                    "Java heap space",
                    "PermGen space",
                    "Metaspace"
                ],
                "solutions": [
                    "Increase Maven memory: export MAVEN_OPTS='-Xmx2048m'",
                    "Check for memory leaks in tests",
                    "Use parallel execution carefully"
                ],
                "confidence": 6
            },
            "timeout_issues": {
                "indicators": [
                    "timeout",
                    "timed out",
                    "Process finished with exit code 143"
                ],
                "solutions": [
                    "Increase test timeout configuration",
                    "Check for infinite loops in tests",
                    "Review slow-running test cases"
                ],
                "confidence": 5
            }
        }
    
    def analyze_apache_camel_failure(self, run_url: str) -> Dict[str, Any]:
        """Analyze Apache Camel CI failure"""
        logger.info(f"🐪 Analyzing Apache Camel failure: {run_url}")
        
        # Extract run info
        parts = run_url.replace('https://github.com/', '').split('/')
        repo = f"{parts[0]}/{parts[1]}"
        run_id = parts[4]
        
        # Get failure details
        try:
            cmd = ['gh', 'run', 'view', run_id, '--repo', repo, '--json', 'jobs,conclusion,name']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            
            failed_jobs = []
            for job in data.get('jobs', []):
                if job.get('conclusion') == 'failure':
                    failed_jobs.append(job['name'])
            
            # Get logs for analysis
            log_content = self._get_failure_logs(repo, run_id)
            
            # Apply Maven pattern analysis
            analysis = self._analyze_maven_patterns(log_content, failed_jobs)
            
            # Apache Camel specific adjustments
            if "camel" in repo.lower():
                analysis = self._apply_camel_specific_patterns(analysis, log_content)
            
            analysis.update({
                "repository": repo,
                "run_id": run_id,
                "failed_jobs": failed_jobs,
                "analysis_timestamp": datetime.now().isoformat(),
                "analyzer": "java_maven_specialized"
            })
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Analysis failed: {e}")
            return self._error_response(str(e))
    
    def _get_failure_logs(self, repo: str, run_id: str) -> str:
        """Get detailed failure logs"""
        try:
            cmd = ['gh', 'run', 'view', run_id, '--repo', repo, '--log']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return result.stdout
        except Exception as e:
            logger.warning(f"Could not get logs: {e}")
            return ""
    
    def _analyze_maven_patterns(self, logs: str, failed_jobs: List[str]) -> Dict[str, Any]:
        """Apply Maven-specific pattern analysis"""
        
        if not logs:
            return {
                "status": "PARTIAL",
                "primary_error": f"Failed job: {', '.join(failed_jobs) if failed_jobs else 'Unknown'}",
                "error_type": "maven_test",
                "confidence": 4,
                "suggested_actions": ["Get detailed logs with: gh run view --log"],
                "pattern_matched": "no_logs_available"
            }
        
        # Analyze log content for patterns
        logs_lower = logs.lower()
        matched_patterns = []
        
        for pattern_name, pattern_info in self.maven_patterns.items():
            for indicator in pattern_info["indicators"]:
                if indicator.lower() in logs_lower:
                    matched_patterns.append((pattern_name, pattern_info))
                    break
        
        if not matched_patterns:
            return self._generic_maven_analysis(failed_jobs, logs)
        
        # Use the highest confidence pattern
        primary_pattern = max(matched_patterns, key=lambda x: x[1]["confidence"])
        pattern_name, pattern_info = primary_pattern
        
        # Extract specific error details
        error_details = self._extract_error_details(logs, pattern_name)
        
        return {
            "status": "FAILURE",
            "primary_error": error_details or f"Maven {pattern_name.replace('_', ' ')} detected",
            "error_type": f"maven_{pattern_name}",
            "confidence": pattern_info["confidence"],
            "pattern_matched": pattern_name,
            "patterns_found": len(matched_patterns),
            "suggested_actions": pattern_info["solutions"],
            "verification_steps": [
                "Run locally to reproduce the issue",
                "Check Maven and Java versions match CI environment",
                "Review relevant log sections for specific details"
            ],
            "github_commands": [
                f"gh run view --log | grep -A5 -B5 'BUILD FAILURE'",
                f"gh run view --log | grep -A10 'Tests run:'"
            ]
        }
    
    def _extract_error_details(self, logs: str, pattern_name: str) -> Optional[str]:
        """Extract specific error details based on pattern"""
        
        if pattern_name == "surefire_failure":
            # Look for test failure summaries
            test_failure_match = re.search(r'Tests run: (\d+), Failures: (\d+), Errors: (\d+)', logs)
            if test_failure_match:
                runs, failures, errors = test_failure_match.groups()
                return f"Maven Surefire: {runs} tests run, {failures} failures, {errors} errors"
        
        elif pattern_name == "compilation_error":
            # Look for compilation error details
            comp_error = re.search(r'COMPILATION ERROR.*?(?=\n\n|\nINFO|\nERROR)', logs, re.DOTALL)
            if comp_error:
                return f"Compilation error: {comp_error.group(0)[:100]}..."
        
        elif pattern_name == "dependency_resolution":
            # Look for dependency issues
            dep_error = re.search(r'Could not resolve dependencies.*?(?=\n\n|\nINFO)', logs, re.DOTALL)
            if dep_error:
                return f"Dependency resolution: {dep_error.group(0)[:100]}..."
        
        return None
    
    def _apply_camel_specific_patterns(self, analysis: Dict[str, Any], logs: str) -> Dict[str, Any]:
        """Apply Apache Camel specific pattern adjustments"""
        
        # Camel component test failures
        if "component test" in logs.lower():
            analysis["error_type"] = "camel_component_test"
            analysis["suggested_actions"].insert(0, 
                "Check Camel component integration tests for specific failures")
        
        # Camel Spring context issues  
        if "spring" in logs.lower() and "context" in logs.lower():
            analysis["suggested_actions"].append(
                "Verify Spring context configuration in Camel routes")
        
        # Camel route compilation issues
        if "route" in logs.lower() and ("compile" in logs.lower() or "build" in logs.lower()):
            analysis["suggested_actions"].append(
                "Check Camel route definitions and DSL syntax")
        
        return analysis
    
    def _generic_maven_analysis(self, failed_jobs: List[str], logs: str) -> Dict[str, Any]:
        """Generic analysis when no specific patterns match"""
        
        # Analyze job names for clues
        job_analysis = []
        for job in failed_jobs:
            if "test" in job.lower():
                job_analysis.append("Test execution failure")
            elif "component" in job.lower():
                job_analysis.append("Component test failure")  
            elif "build" in job.lower():
                job_analysis.append("Build process failure")
        
        primary_error = f"Maven job failure: {', '.join(failed_jobs)}"
        if job_analysis:
            primary_error += f" - {', '.join(job_analysis)}"
        
        return {
            "status": "PARTIAL", 
            "primary_error": primary_error,
            "error_type": "maven_generic",
            "confidence": 5,
            "pattern_matched": "generic_maven",
            "suggested_actions": [
                "Review detailed logs for specific error messages",
                "Check Maven and JDK versions",
                "Verify test configuration and dependencies"
            ],
            "verification_steps": [
                "Run mvn clean test locally",
                "Check for environment-specific issues"
            ]
        }
    
    def _error_response(self, error_msg: str) -> Dict[str, Any]:
        """Generate error response"""
        return {
            "status": "ERROR",
            "primary_error": f"Analysis failed: {error_msg}",
            "error_type": "analyzer_error", 
            "confidence": 1,
            "suggested_actions": ["Manual log review required"],
            "analyzer": "java_maven_specialized"
        }

def main():
    """CLI entry point"""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python3 java_maven_analyzer.py <github_actions_url>")
        print("Example: python3 java_maven_analyzer.py https://github.com/apache/camel/actions/runs/17094086851")
        return 1
    
    analyzer = JavaMavenAnalyzer()
    result = analyzer.analyze_apache_camel_failure(sys.argv[1])
    
    print("🐪 Apache Camel Maven Analysis")
    print("=" * 50)
    print(json.dumps(result, indent=2))
    
    return 0

if __name__ == "__main__":
    exit(main())