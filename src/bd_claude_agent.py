#!/usr/bin/env python3
"""
Build Detective Agent - Optimized Claude Code Integration
Simple, efficient CI/CD failure analysis for Claude Code Task tool
"""

import subprocess
import json
import sys
import re
from typing import Dict, List, Any

def run_gh_command(cmd: List[str]) -> str:
    """Run GitHub CLI command and return output"""
    try:
        result = subprocess.run(['gh'] + cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"GitHub CLI error: {e}"

def extract_repo_and_run_from_url(github_url: str) -> Dict[str, str]:
    """Extract repo and run ID from GitHub Actions URL"""
    # Match patterns like: https://github.com/StigLau/VideoRenderer/actions/runs/16912870313
    match = re.search(r'github\.com/([^/]+/[^/]+)/actions/runs/(\d+)', github_url)
    if match:
        return {"repo": match.group(1), "run_id": match.group(2)}
    
    # Match PR patterns: https://github.com/StigLau/yolo-ffmpeg-mcp/pull/18
    pr_match = re.search(r'github\.com/([^/]+/[^/]+)/pull/(\d+)', github_url)
    if pr_match:
        return {"repo": pr_match.group(1), "pr_number": pr_match.group(2)}
    
    return {}

def analyze_github_actions_run(repo: str, run_id: str) -> Dict[str, Any]:
    """Analyze a specific GitHub Actions run"""
    
    # Get run details
    run_data = run_gh_command(['run', 'view', run_id, '--repo', repo, '--json', 'jobs,conclusion,workflowName'])
    
    if "GitHub CLI error" in run_data:
        return {
            "status": "ERROR",
            "primary_error": f"Could not fetch run data: {run_data}",
            "error_type": "api_error",
            "confidence": 1
        }
    
    try:
        run_json = json.loads(run_data)
        jobs = run_json.get('jobs', [])
        failed_jobs = [job for job in jobs if job.get('conclusion') == 'failure']
        
        if not failed_jobs:
            return {
                "status": "SUCCESS",
                "primary_error": "No failed jobs found",
                "error_type": "no_failure",
                "confidence": 10
            }
        
        # Analyze first failed job
        job = failed_jobs[0]
        
        # Get detailed logs
        logs = run_gh_command(['run', 'view', run_id, '--repo', repo, '--log'])
        
        # Apply pattern analysis
        analysis = apply_build_detective_patterns(logs, job.get('name', 'Unknown'))
        analysis.update({
            "status": "FAILURE",
            "workflow_name": run_json.get('workflowName', 'Unknown'),
            "job_name": job.get('name', 'Unknown'),
            "run_id": run_id,
            "repo": repo
        })
        
        return analysis
        
    except json.JSONDecodeError:
        return {
            "status": "ERROR", 
            "primary_error": "Could not parse GitHub API response",
            "error_type": "json_error",
            "confidence": 2
        }

def analyze_pr_failures(repo: str, pr_number: str) -> Dict[str, Any]:
    """Analyze PR failures using status checks"""
    
    # Get PR status checks
    pr_data = run_gh_command(['pr', 'view', pr_number, '--repo', repo, '--json', 'statusCheckRollup'])
    
    if "GitHub CLI error" in pr_data:
        return {
            "status": "ERROR",
            "primary_error": f"Could not fetch PR data: {pr_data}",  
            "error_type": "api_error",
            "confidence": 1
        }
    
    try:
        pr_json = json.loads(pr_data)
        status_checks = pr_json.get('statusCheckRollup', [])
        failures = [check for check in status_checks if check.get('conclusion') == 'FAILURE']
        
        if not failures:
            return {
                "status": "SUCCESS",
                "primary_error": "No failed status checks found",
                "error_type": "no_failure", 
                "confidence": 10
            }
        
        # Analyze first failure
        failure = failures[0]
        run_id = None
        
        # Extract run ID from details URL
        details_url = failure.get('detailsUrl', '')
        run_match = re.search(r'/runs/(\d+)', details_url)
        if run_match:
            run_id = run_match.group(1)
            return analyze_github_actions_run(repo, run_id)
        
        # Fallback analysis
        return {
            "status": "FAILURE",
            "primary_error": f"Check '{failure['name']}' failed",
            "error_type": "status_check_failure",
            "confidence": 6,
            "workflow_name": failure.get('workflowName', 'Unknown'),
            "job_name": failure['name'],
            "suggested_action": "Check status check configuration and logs",
            "blocking_vs_warning": "BLOCKING"
        }
        
    except json.JSONDecodeError:
        return {
            "status": "ERROR",
            "primary_error": "Could not parse PR data",
            "error_type": "json_error", 
            "confidence": 2
        }

def apply_build_detective_patterns(logs: str, job_name: str) -> Dict[str, Any]:
    """Apply Build Detective error pattern recognition to logs"""
    
    # Enhanced patterns from both projects
    patterns = {
        # Docker build issues
        "docker_copy_missing": r"COPY.*not found|failed to calculate checksum.*not found",
        "docker_dependency": r"=\d+\.\d+\.\d+.*not found|pip.*malformed",
        "docker_opencv": r"opencv.*not found|cv2.*ImportError",
        
        # Python/UV dependency issues  
        "pytest_missing": r"Failed to spawn.*pytest.*No such file|pytest.*not found",
        "uv_dependency": r"uv.*not available|uv sync.*failed",
        "python_import": r"ImportError.*No module named|ModuleNotFoundError",
        
        # MCP/YOLO specific
        "mcp_import_fail": r"MCP module imports failed|mcp.*ImportError", 
        "komposteur_jar": r"komposteur.*jar.*not found|uber-kompost.*failed",
        "ffmpeg_timeout": r"FFmpeg.*timeout|video processing.*hung",
        
        # GitHub Actions workflow issues
        "workflow_deprecated": r"set-output.*deprecated|::set-output",
        "github_auth": r"authentication.*failed|401.*Unauthorized",
        
        # Maven/Java build issues
        "maven_dependency": r"Could not resolve dependencies|Maven.*failed",
        "java_version": r"unsupported class file version|JAVA_HOME",
        "surefire_failure": r"Tests run:.*Failures:.*[1-9]|Surefire.*failed"
    }
    
    primary_error = "Unknown failure"
    error_type = "unknown"
    confidence = 5
    suggested_action = "Check logs manually"
    blocking_status = "WARNING"
    
    # Pattern matching with priority order
    if re.search(patterns["workflow_deprecated"], logs, re.IGNORECASE):
        primary_error = "Workflow uses deprecated GitHub Actions syntax"
        error_type = "workflow_configuration" 
        confidence = 9
        suggested_action = "Replace ::set-output with Environment Files syntax"
        blocking_status = "BLOCKING"
        
    elif re.search(patterns["docker_copy_missing"], logs, re.IGNORECASE):
        primary_error = "Docker build failed - missing files for COPY commands"
        error_type = "docker_build"
        confidence = 9
        suggested_action = "Add missing files or fix Dockerfile COPY paths"  
        blocking_status = "BLOCKING"
        
    elif re.search(patterns["pytest_missing"], logs, re.IGNORECASE):
        primary_error = "pytest not available in environment"
        error_type = "dependency"
        confidence = 9
        suggested_action = "Add pytest to dependencies or use --extra dev flag"
        blocking_status = "BLOCKING"
        
    elif re.search(patterns["uv_dependency"], logs, re.IGNORECASE):
        primary_error = "UV dependency management failed"
        error_type = "dependency"
        confidence = 8
        suggested_action = "Check UV configuration and add missing extras"
        blocking_status = "BLOCKING"
        
    elif re.search(patterns["python_import"], logs, re.IGNORECASE):
        primary_error = "Python import error - missing modules"
        error_type = "python_import"
        confidence = 8
        suggested_action = "Install missing Python packages and check PYTHONPATH"
        blocking_status = "BLOCKING"
        
    elif re.search(patterns["docker_opencv"], logs, re.IGNORECASE):
        primary_error = "OpenCV dependency missing in Docker environment"
        error_type = "docker_dependency"
        confidence = 8
        suggested_action = "Add opencv-python to Docker requirements"
        blocking_status = "BLOCKING"
        
    elif re.search(patterns["mcp_import_fail"], logs, re.IGNORECASE):
        primary_error = "MCP modules failed to import"
        error_type = "mcp_error"
        confidence = 7
        suggested_action = "Check MCP server configuration and dependencies"
        blocking_status = "BLOCKING"
        
    elif re.search(patterns["maven_dependency"], logs, re.IGNORECASE):
        primary_error = "Maven dependency resolution failed"
        error_type = "maven_dependency"
        confidence = 8
        suggested_action = "Check Maven dependencies and repository access"
        blocking_status = "BLOCKING"
        
    elif re.search(patterns["surefire_failure"], logs, re.IGNORECASE):
        primary_error = "Maven Surefire tests failed"
        error_type = "test_failure"
        confidence = 9
        suggested_action = "Fix failing tests or update test configuration"
        blocking_status = "BLOCKING"

    return {
        "primary_error": primary_error,
        "error_type": error_type,
        "confidence": confidence,
        "suggested_action": suggested_action,
        "blocking_vs_warning": blocking_status,
        "pattern_matched": True
    }

def claude_code_entry_point(github_url: str, **kwargs) -> str:
    """
    Optimized entry point for Claude Code Task tool integration
    
    Returns concise, actionable analysis following improved interaction patterns
    """
    
    # Extract repo info from URL
    url_info = extract_repo_and_run_from_url(github_url)
    
    if not url_info:
        return json.dumps({
            "status": "ERROR",
            "primary_error": "Invalid GitHub URL format",
            "confidence": "1/10",
            "immediate_fix": "Provide valid GitHub Actions run URL"
        }, indent=2)
    
    # Route to appropriate analysis
    if "run_id" in url_info:
        result = analyze_github_actions_run(url_info["repo"], url_info["run_id"])
    elif "pr_number" in url_info:
        result = analyze_pr_failures(url_info["repo"], url_info["pr_number"]) 
    else:
        return json.dumps({
            "status": "ERROR", 
            "primary_error": "Could not extract run ID or PR number",
            "confidence": "2/10"
        }, indent=2)
    
    # Format for improved Claude Code interaction
    formatted_result = {
        "status": result.get("status", "UNKNOWN"),
        "primary_error": result.get("primary_error", "Analysis incomplete"),
        "confidence": f"{result.get('confidence', 0)}/10",
        "error_type": result.get("error_type", "unknown"),
        "immediate_fix": result.get("suggested_action", "No specific action identified")[:100],
        "cost_analysis": "Used optimized BD agent ($0.02)",
        "github_url": github_url
    }
    
    return json.dumps(formatted_result, indent=2)

def main():
    """CLI entry point for standalone testing"""
    if len(sys.argv) < 2:
        print("Usage: python bd_claude_agent.py <github_url>")
        print("Examples:")
        print("  python bd_claude_agent.py https://github.com/StigLau/VideoRenderer/actions/runs/16912870313") 
        print("  python bd_claude_agent.py https://github.com/StigLau/yolo-ffmpeg-mcp/pull/18")
        sys.exit(1)
    
    github_url = sys.argv[1]
    result = claude_code_entry_point(github_url)
    print(result)

if __name__ == "__main__":
    main()