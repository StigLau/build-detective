#!/usr/bin/env python3
"""
Build Detective - Main entry point
AI-powered CI/build failure analysis for development teams
"""
import argparse
import asyncio
import logging
import sys
from datetime import datetime, timedelta
from typing import Optional
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from orchestrator.supervisor import Supervisor
from github_integration.client import GitHubClient
from reporting.report_generator import ReportGenerator
from utils.logger import setup_logger

logger = setup_logger(__name__)

class BuildDetective:
    """Main Build Detective orchestrator"""
    
    def __init__(self, config_path: str = "config/settings.yaml"):
        self.supervisor = Supervisor(config_path)
        self.github_client = GitHubClient()
        self.report_generator = ReportGenerator()
        
    async def run_continuous(self):
        """Run in continuous monitoring mode"""
        logger.info("🕵️ Starting Build Detective in continuous mode")
        while True:
            try:
                await self.check_repositories()
                await asyncio.sleep(300)  # 5 minutes
            except KeyboardInterrupt:
                logger.info("🛑 Shutting down Build Detective")
                break
            except Exception as e:
                logger.error(f"❌ Error in continuous mode: {e}")
                await asyncio.sleep(60)
    
    async def run_single(self, repo: str):
        """Run analysis for a single repository"""
        logger.info(f"🔍 Analyzing repository: {repo}")
        failures = await self.github_client.get_recent_failures(repo)
        if failures:
            analysis = await self.supervisor.analyze_failures(failures)
            report = self.report_generator.generate(analysis)
            print(report)
        else:
            logger.info("✅ No recent failures found")
    
    async def analyze_pr(self, repo: str, pr_number: str):
        """Analyze specific PR failures"""
        logger.info(f"🔍 Analyzing PR#{pr_number} in {repo}")
        failures = await self.github_client.get_pr_failures(repo, pr_number)
        if failures:
            analysis = await self.supervisor.analyze_failures(failures)
            report = self.report_generator.generate(analysis)
            print(report)
            return analysis
        else:
            logger.info("✅ No PR failures found")
            return None
    
    async def check_repositories(self):
        """Check all configured repositories"""
        repos = self.supervisor.get_configured_repos()
        for repo in repos:
            try:
                await self.run_single(repo)
            except Exception as e:
                logger.error(f"❌ Error checking {repo}: {e}")

    async def generate_report(self, days: int = 7):
        """Generate failure report for recent days"""
        logger.info(f"📊 Generating {days}-day failure report")
        # Implementation would gather historical data
        print(f"Report for last {days} days would be generated here")

def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="🕵️ Build Detective - AI-powered CI/build failure analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --mode continuous                    # Monitor all configured repos
  %(prog)s --repo owner/repo --mode single     # Analyze one repo
  %(prog)s --repo owner/repo --pr 123          # Analyze specific PR
  %(prog)s --report --days 7                   # Generate weekly report
        """
    )
    
    parser.add_argument("--mode", choices=["continuous", "single"], 
                       default="single", help="Running mode")
    parser.add_argument("--repo", help="Repository to analyze (owner/repo format)")
    parser.add_argument("--pr", help="PR number to analyze")
    parser.add_argument("--report", action="store_true", 
                       help="Generate report for recent failures")
    parser.add_argument("--days", type=int, default=7, 
                       help="Days to look back for report")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    detective = BuildDetective()
    
    try:
        if args.report:
            # Generate report mode
            asyncio.run(detective.generate_report(args.days))
        elif args.pr:
            if not args.repo:
                parser.error("--repo required when analyzing PR")
            asyncio.run(detective.analyze_pr(args.repo, args.pr))
        elif args.mode == "single":
            if not args.repo:
                parser.error("--repo required for single mode")
            asyncio.run(detective.run_single(args.repo))
        else:
            asyncio.run(detective.run_continuous())
    except KeyboardInterrupt:
        logger.info("🛑 Build Detective stopped by user")
    except Exception as e:
        logger.error(f"❌ Build Detective failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()