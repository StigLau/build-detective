"""
GitHub client for CI failure detection and log retrieval
"""
import json
import subprocess
import asyncio
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime

from utils.logger import setup_logger

logger = setup_logger(__name__)

@dataclass
class CIFailure:
    """CI failure information"""
    id: str
    job_name: str
    workflow_name: str
    run_id: Optional[str]
    conclusion: str
    logs: Optional[str] = None
    error: Optional[str] = None
    repo: Optional[str] = None

class GitHubClient:
    """Handles GitHub API interactions with rate limiting"""
    
    def __init__(self):
        self._verify_gh_cli()
        
    def _verify_gh_cli(self):
        """Verify GitHub CLI is available and authenticated"""
        try:
            result = subprocess.run(['gh', 'auth', 'status'], 
                                  capture_output=True, text=True, check=True)
            logger.info("✅ GitHub CLI authenticated")
        except subprocess.CalledProcessError:
            logger.warning("⚠️ GitHub CLI not authenticated - some features may not work")
        except FileNotFoundError:
            logger.error("❌ GitHub CLI not found - install with 'brew install gh'")
    
    async def get_recent_failures(self, repo: str, limit: int = 10) -> List[CIFailure]:
        """
        Get recent CI failures for a repository
        
        Args:
            repo: Repository in format 'owner/repo'
            limit: Maximum number of failures to return
            
        Returns:
            List of CI failures
        """
        logger.info(f"🔍 Getting recent failures for {repo}")
        
        try:
            # Get recent workflow runs that failed
            cmd = [
                'gh', 'run', 'list', 
                '--repo', repo,
                '--status', 'failure',
                '--limit', str(limit),
                '--json', 'databaseId,name,conclusion,workflowName,createdAt'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            runs_data = json.loads(result.stdout)
            
            failures = []
            for run in runs_data:
                # Get job details for each failed run
                run_failures = await self._get_run_failures(repo, str(run['databaseId']))
                failures.extend(run_failures)
            
            logger.info(f"📊 Found {len(failures)} recent failures")
            return failures[:limit]
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ GitHub CLI error: {e}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON parsing error: {e}")
            return []
    
    async def get_pr_failures(self, repo: str, pr_number: str) -> List[CIFailure]:
        """
        Get CI failures for a specific PR
        
        Args:
            repo: Repository in format 'owner/repo'
            pr_number: PR number
            
        Returns:
            List of CI failures for the PR
        """
        logger.info(f"🔍 Getting PR#{pr_number} failures for {repo}")
        
        try:
            # Get PR status checks
            cmd = ['gh', 'pr', 'view', pr_number, '--repo', repo, '--json', 'statusCheckRollup']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            data = json.loads(result.stdout)
            failures = []
            
            for check in data.get('statusCheckRollup', []):
                if check.get('conclusion') == 'FAILURE':
                    # Extract run ID from details URL if available
                    run_id = None
                    if 'detailsUrl' in check and '/runs/' in check['detailsUrl']:
                        run_id = check['detailsUrl'].split('/runs/')[1].split('/')[0]
                    
                    failure = CIFailure(
                        id=f"{repo}-{pr_number}-{check['name']}",
                        job_name=check['name'],
                        workflow_name=check.get('workflowName', 'Unknown'),
                        run_id=run_id,
                        conclusion='FAILURE',
                        repo=repo
                    )
                    
                    # Try to get logs if we have run_id
                    if run_id:
                        failure.logs = await self._get_job_logs(repo, run_id, check['name'])
                    
                    failures.append(failure)
            
            logger.info(f"📊 Found {len(failures)} PR failures")
            return failures
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ GitHub CLI error for PR: {e}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON parsing error for PR: {e}")
            return []
    
    async def _get_run_failures(self, repo: str, run_id: str) -> List[CIFailure]:
        """Get failed jobs for a specific workflow run"""
        try:
            # Get jobs for the run
            cmd = ['gh', 'run', 'view', run_id, '--repo', repo, '--json', 'jobs']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                logger.warning(f"⚠️ Failed to get jobs for run {run_id}")
                return []
            
            data = json.loads(result.stdout)
            failures = []
            
            for job in data.get('jobs', []):
                if job.get('conclusion') == 'failure':
                    failure = CIFailure(
                        id=f"{repo}-{run_id}-{job['name']}",
                        job_name=job['name'],
                        workflow_name=job.get('workflowName', 'Unknown'),
                        run_id=run_id,
                        conclusion='failure',
                        repo=repo
                    )
                    
                    # Get logs for failed job
                    failure.logs = await self._get_job_logs(repo, run_id, job['name'])
                    failures.append(failure)
            
            return failures
            
        except (subprocess.TimeoutExpired, json.JSONDecodeError) as e:
            logger.warning(f"⚠️ Error getting run failures for {run_id}: {e}")
            return []
    
    async def _get_job_logs(self, repo: str, run_id: str, job_name: str) -> Optional[str]:
        """
        Get logs for a specific job
        
        Args:
            repo: Repository name
            run_id: Workflow run ID
            job_name: Job name
            
        Returns:
            Job logs as string, or None if not available
        """
        try:
            # Get full run logs
            cmd = ['gh', 'run', 'view', run_id, '--repo', repo, '--log']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                logger.warning(f"⚠️ Failed to get logs for run {run_id}")
                return None
            
            # Extract logs for specific job
            logs = result.stdout
            job_logs = self._extract_job_logs(logs, job_name)
            
            # Compress logs to essential error information
            from utils.token_optimizer import TokenOptimizer
            optimizer = TokenOptimizer()
            compressed_logs = optimizer.compress_logs(job_logs, max_tokens=500)
            
            return compressed_logs
            
        except subprocess.TimeoutExpired:
            logger.warning(f"⚠️ Timeout getting logs for {run_id}")
            return None
        except Exception as e:
            logger.warning(f"⚠️ Error getting logs for {run_id}: {e}")
            return None
    
    def _extract_job_logs(self, full_logs: str, job_name: str) -> str:
        """Extract logs for a specific job from full workflow logs"""
        lines = full_logs.split('\n')
        job_lines = []
        in_job_section = False
        
        for line in lines:
            # Look for job section markers
            if job_name in line and ('==' in line or '--' in line):
                in_job_section = True
                job_lines.append(line)
            elif in_job_section:
                # Stop at next job section or end
                if ('==' in line or '--' in line) and job_name not in line:
                    break
                job_lines.append(line)
        
        # If no specific section found, return relevant error lines
        if not job_lines:
            error_lines = [line for line in lines if any(
                keyword in line.lower() for keyword in 
                ['error', 'failed', 'exception', 'fatal', 'exit code']
            )]
            return '\n'.join(error_lines[-50:])  # Last 50 error lines
        
        return '\n'.join(job_lines)
    
    async def get_pull_request_context(self, repo: str, pr_number: int) -> Dict[str, Any]:
        """Get PR context for failure analysis"""
        try:
            cmd = ['gh', 'pr', 'view', str(pr_number), '--repo', repo, '--json', 
                   'title,body,headRefName,baseRefName,changedFiles']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            return json.loads(result.stdout)
            
        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            logger.warning(f"⚠️ Failed to get PR context: {e}")
            return {}
    
    async def post_comment(self, repo: str, issue_number: int, analysis: str) -> bool:
        """Post analysis comment to GitHub issue/PR"""
        try:
            cmd = ['gh', 'pr', 'comment', str(issue_number), '--repo', repo, '--body', analysis]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            logger.info(f"✅ Posted analysis comment to {repo}#{issue_number}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to post comment: {e}")
            return False