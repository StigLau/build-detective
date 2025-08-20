#!/usr/bin/env python3
"""
Build Detective Project Discovery Agent

Adaptive project structure analysis and context learning for Build Detective.
Discovers project patterns and adapts analysis strategies accordingly.
"""

import json
import re
import logging
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import subprocess

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ProjectProfile:
    """Comprehensive project profile for adaptive analysis"""
    project_type: str
    primary_language: str
    build_system: str
    testing_framework: str
    complexity_score: int
    risk_areas: List[str]
    custom_patterns: Dict[str, Any]
    ci_characteristics: Dict[str, Any]

@dataclass
class TechnologyStack:
    """Technology stack detection results"""
    languages: Dict[str, float]  # Language -> confidence score
    frameworks: List[str]
    build_tools: List[str]
    testing_tools: List[str]
    deployment_tools: List[str]
    dependencies: Dict[str, List[str]]  # Tool -> list of dependencies

class ProjectDiscoveryAgent:
    """
    Project Discovery Agent - Adaptive project structure analysis
    
    Analyzes project structure to understand:
    1. Technology stack and architecture patterns
    2. Build system configuration and complexity
    3. Testing strategies and frameworks
    4. CI/CD integration patterns
    5. Risk areas and critical paths
    
    Uses this understanding to customize Build Detective analysis patterns.
    """
    
    def __init__(self):
        self.agent_name = "build-detective-project-discovery"
        self.file_analyzers = self._initialize_file_analyzers()
        self.pattern_extractors = self._initialize_pattern_extractors()
        self.complexity_factors = self._initialize_complexity_factors()
    
    def _initialize_file_analyzers(self) -> Dict[str, Dict[str, Any]]:
        """Initialize file pattern analyzers for different technologies"""
        return {
            "java_maven": {
                "indicators": ["pom.xml", "src/main/java", "src/test/java"],
                "config_files": ["pom.xml", "maven.xml", "settings.xml"],
                "patterns": {
                    "multi_module": r"<modules>\s*<module>",
                    "spring_boot": r"spring-boot-starter",
                    "junit5": r"junit-jupiter",
                    "integration_tests": r"failsafe|integration-test"
                }
            },
            "python": {
                "indicators": ["requirements.txt", "pyproject.toml", "setup.py", "*.py"],
                "config_files": ["pyproject.toml", "requirements.txt", "setup.cfg", "tox.ini"],
                "patterns": {
                    "poetry": r"\[tool\.poetry\]",
                    "pytest": r"pytest|conftest\.py",
                    "django": r"django|manage\.py",
                    "flask": r"from flask import|app = Flask",
                    "uv": r"uv\.lock|tool\.uv"
                }
            },
            "node": {
                "indicators": ["package.json", "node_modules", "*.js", "*.ts"],
                "config_files": ["package.json", "tsconfig.json", "webpack.config.js"],
                "patterns": {
                    "typescript": r"\.ts$|tsconfig\.json",
                    "react": r"react|jsx",
                    "vue": r"\.vue$|vue",
                    "jest": r"jest|\.test\.[jt]s",
                    "npm_workspace": r"workspaces"
                }
            },
            "docker": {
                "indicators": ["Dockerfile", "docker-compose.yml", ".dockerignore"],
                "config_files": ["Dockerfile", "docker-compose.yml", "docker-compose.yaml"],
                "patterns": {
                    "multi_stage": r"FROM.*AS\s+\w+",
                    "alpine": r"FROM.*alpine",
                    "node_docker": r"FROM node:|node:",
                    "java_docker": r"FROM openjdk:|FROM eclipse-temurin:"
                }
            },
            "github_actions": {
                "indicators": [".github/workflows/*.yml", ".github/workflows/*.yaml"],
                "config_files": [".github/workflows/*.yml"],
                "patterns": {
                    "matrix_builds": r"strategy:\s*matrix:",
                    "cron_schedules": r"schedule:\s*-\s*cron:",
                    "pull_request_triggers": r"on:.*pull_request",
                    "multiple_jobs": r"jobs:\s*\w+:.*\w+:"
                }
            }
        }
    
    def _initialize_pattern_extractors(self) -> Dict[str, callable]:
        """Initialize pattern extraction functions"""
        return {
            "dependency_analysis": self._analyze_dependencies,
            "build_complexity": self._analyze_build_complexity,
            "test_structure": self._analyze_test_structure,
            "ci_integration": self._analyze_ci_integration,
            "deployment_patterns": self._analyze_deployment_patterns
        }
    
    def _initialize_complexity_factors(self) -> Dict[str, Dict[str, int]]:
        """Initialize complexity scoring factors"""
        return {
            "project_structure": {
                "single_module": 2,
                "multi_module": 5,
                "microservices": 8,
                "monorepo": 9
            },
            "technology_diversity": {
                "single_tech": 1,
                "multi_language": 3,
                "polyglot": 6,
                "full_stack": 8
            },
            "build_complexity": {
                "simple_build": 1,
                "custom_scripts": 3,
                "complex_pipeline": 6,
                "multi_stage_docker": 4
            },
            "testing_complexity": {
                "unit_tests_only": 1,
                "integration_tests": 3,
                "end_to_end_tests": 5,
                "performance_tests": 4
            }
        }
    
    async def discover_project_profile(self, github_url: str, context: Dict[str, Any] = None) -> ProjectProfile:
        """
        Main discovery method - analyzes project to create comprehensive profile
        
        Args:
            github_url: GitHub repository or Actions URL
            context: Additional context from other agents
            
        Returns:
            ProjectProfile with discovered characteristics
        """
        logger.info(f"🔍 Project Discovery analyzing: {github_url}")
        
        try:
            # Step 1: Extract repository information
            repo_info = self._extract_repo_info(github_url)
            
            # Step 2: Analyze project structure (would use GitHub API in production)
            structure_analysis = await self._analyze_project_structure(repo_info)
            
            # Step 3: Detect technology stack
            tech_stack = await self._detect_technology_stack(structure_analysis)
            
            # Step 4: Analyze build system complexity
            build_analysis = await self._analyze_build_system(structure_analysis, tech_stack)
            
            # Step 5: Examine CI/CD patterns
            ci_patterns = await self._analyze_ci_patterns(repo_info, context)
            
            # Step 6: Calculate complexity score
            complexity_score = self._calculate_complexity_score(structure_analysis, tech_stack, build_analysis, ci_patterns)
            
            # Step 7: Identify risk areas
            risk_areas = self._identify_risk_areas(structure_analysis, tech_stack, ci_patterns)
            
            # Step 8: Generate custom patterns
            custom_patterns = self._generate_custom_patterns(tech_stack, build_analysis, ci_patterns)
            
            # Step 9: Create comprehensive profile
            profile = ProjectProfile(
                project_type=self._determine_project_type(structure_analysis, tech_stack),
                primary_language=self._determine_primary_language(tech_stack),
                build_system=self._determine_build_system(tech_stack, build_analysis),
                testing_framework=self._determine_testing_framework(tech_stack),
                complexity_score=complexity_score,
                risk_areas=risk_areas,
                custom_patterns=custom_patterns,
                ci_characteristics=ci_patterns
            )
            
            logger.info(f"✅ Project profile: {profile.project_type} ({profile.primary_language}, complexity {complexity_score}/10)")
            return profile
            
        except Exception as e:
            logger.error(f"❌ Project discovery failed: {e}")
            return self._fallback_project_profile(github_url)
    
    def _extract_repo_info(self, github_url: str) -> Dict[str, str]:
        """Extract repository information from GitHub URL"""
        
        # Parse different GitHub URL formats
        if "github.com" in github_url:
            if "/actions/runs/" in github_url:
                # Extract from Actions URL: https://github.com/owner/repo/actions/runs/123
                parts = github_url.replace('https://github.com/', '').split('/')
                return {
                    "owner": parts[0],
                    "repo": parts[1], 
                    "full_name": f"{parts[0]}/{parts[1]}",
                    "type": "actions_run",
                    "run_id": parts[4] if len(parts) > 4 else None
                }
            elif "/pull/" in github_url:
                # Extract from PR URL: https://github.com/owner/repo/pull/123
                parts = github_url.replace('https://github.com/', '').split('/')
                return {
                    "owner": parts[0],
                    "repo": parts[1],
                    "full_name": f"{parts[0]}/{parts[1]}",
                    "type": "pull_request",
                    "pr_number": parts[3] if len(parts) > 3 else None
                }
            else:
                # Regular repo URL: https://github.com/owner/repo
                parts = github_url.replace('https://github.com/', '').split('/')
                return {
                    "owner": parts[0],
                    "repo": parts[1] if len(parts) > 1 else parts[0],
                    "full_name": f"{parts[0]}/{parts[1]}" if len(parts) > 1 else parts[0],
                    "type": "repository"
                }
        
        # Fallback for non-GitHub URLs or malformed URLs
        return {
            "owner": "unknown",
            "repo": "unknown", 
            "full_name": "unknown/unknown",
            "type": "unknown"
        }
    
    async def _analyze_project_structure(self, repo_info: Dict[str, str]) -> Dict[str, Any]:
        """
        Analyze project structure (in production would use GitHub API)
        
        For now, simulate based on known repository patterns
        """
        
        # In production, this would call GitHub API:
        # GET /repos/{owner}/{repo}/contents to get file structure
        
        # Simulate structure analysis based on repository name patterns
        repo_name = repo_info.get("repo", "").lower()
        
        if "vdvil" in repo_name:
            # StigLau's VDVIL project patterns
            return {
                "structure_type": "maven_multi_module",
                "modules": ["vdvil-core", "vdvil-web", "vdvil-integration"],
                "depth": 3,
                "file_count_estimate": 150,
                "has_docker": True,
                "has_tests": True,
                "config_files": ["pom.xml", "Dockerfile", ".github/workflows"]
            }
        elif "komposteur" in repo_name:
            # Another StigLau project
            return {
                "structure_type": "maven_single_module", 
                "modules": ["main"],
                "depth": 2,
                "file_count_estimate": 75,
                "has_docker": True,
                "has_tests": True,
                "config_files": ["pom.xml", "Dockerfile"]
            }
        else:
            # Generic structure for unknown repositories
            return {
                "structure_type": "unknown",
                "modules": ["main"],
                "depth": 2,
                "file_count_estimate": 50,
                "has_docker": False,
                "has_tests": True,
                "config_files": ["unknown"]
            }
    
    async def _detect_technology_stack(self, structure: Dict[str, Any]) -> TechnologyStack:
        """Detect technology stack from project structure"""
        
        structure_type = structure.get("structure_type", "unknown")
        
        if "maven" in structure_type:
            return TechnologyStack(
                languages={"java": 0.9, "xml": 0.6},
                frameworks=["Spring Boot", "JUnit"],
                build_tools=["Maven"],
                testing_tools=["JUnit", "Surefire", "Failsafe"],
                deployment_tools=["Docker"],
                dependencies={
                    "maven": ["spring-boot-starter", "junit-jupiter"],
                    "docker": ["openjdk", "alpine"]
                }
            )
        elif structure_type == "python":
            return TechnologyStack(
                languages={"python": 0.9},
                frameworks=["FastAPI", "pytest"],
                build_tools=["pip", "uv"],
                testing_tools=["pytest"],
                deployment_tools=["Docker"],
                dependencies={
                    "python": ["fastapi", "pytest", "uvicorn"],
                    "uv": ["dev-dependencies"]
                }
            )
        else:
            # Generic/unknown technology stack
            return TechnologyStack(
                languages={"unknown": 0.5},
                frameworks=["Unknown"],
                build_tools=["Unknown"],
                testing_tools=["Unknown"],
                deployment_tools=[],
                dependencies={}
            )
    
    async def _analyze_build_system(self, structure: Dict[str, Any], tech_stack: TechnologyStack) -> Dict[str, Any]:
        """Analyze build system complexity and characteristics"""
        
        primary_build_tool = tech_stack.build_tools[0] if tech_stack.build_tools else "unknown"
        
        build_analysis = {
            "primary_tool": primary_build_tool,
            "complexity": "moderate",
            "custom_scripts": False,
            "multi_stage": False,
            "build_time_estimate": "5-10 minutes"
        }
        
        if primary_build_tool == "Maven":
            build_analysis.update({
                "complexity": "moderate" if "multi_module" in structure.get("structure_type", "") else "simple",
                "custom_scripts": structure.get("depth", 1) > 2,
                "build_phases": ["compile", "test", "package", "verify"],
                "test_integration": "surefire" in [t.lower() for t in tech_stack.testing_tools]
            })
        elif primary_build_tool in ["pip", "uv"]:
            build_analysis.update({
                "complexity": "simple",
                "dependency_management": primary_build_tool,
                "virtual_environments": True,
                "build_phases": ["install", "test"]
            })
        
        # Docker build complexity
        if structure.get("has_docker"):
            build_analysis.update({
                "docker_builds": True,
                "multi_stage": "multi_module" in structure.get("structure_type", ""),
                "complexity": "complex" if build_analysis["complexity"] == "moderate" else build_analysis["complexity"]
            })
        
        return build_analysis
    
    async def _analyze_ci_patterns(self, repo_info: Dict[str, str], context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze CI/CD patterns from context and repository info"""
        
        ci_patterns = {
            "platform": "github_actions",  # Assume GitHub Actions based on URL
            "matrix_builds": False,
            "integration_tests": False,
            "deployment_automation": False,
            "failure_patterns": []
        }
        
        # Analyze from context (failure data from other agents)
        if context:
            failure_data = context.get("failure_data", {})
            failed_jobs = failure_data.get("job_names", [])
            
            # Detect matrix builds
            if any("java" in job.lower() and any(version in job for version in ["11", "17", "21"]) for job in failed_jobs):
                ci_patterns["matrix_builds"] = True
                ci_patterns["matrix_type"] = "jdk_versions"
            
            # Detect integration tests
            if any("integration" in job.lower() for job in failed_jobs):
                ci_patterns["integration_tests"] = True
            
            # Detect AWS integration
            if any("aws" in job.lower() for job in failed_jobs):
                ci_patterns["aws_integration"] = True
                ci_patterns["cloud_services"] = ["AWS"]
            
            # Extract failure patterns
            ci_patterns["failure_patterns"] = [
                job for job in failed_jobs 
                if any(keyword in job.lower() for keyword in ["test", "build", "integration"])
            ]
        
        return ci_patterns
    
    def _calculate_complexity_score(self, structure: Dict[str, Any], tech_stack: TechnologyStack, build_analysis: Dict[str, Any], ci_patterns: Dict[str, Any]) -> int:
        """Calculate overall project complexity score (1-10)"""
        
        score = 3  # Base score
        
        # Structure complexity
        structure_type = structure.get("structure_type", "unknown")
        if "multi_module" in structure_type:
            score += 3
        elif "single_module" in structure_type:
            score += 1
        
        # Technology diversity
        language_count = len([lang for lang, conf in tech_stack.languages.items() if conf > 0.5])
        score += min(language_count, 3)  # Max 3 points for languages
        
        # Build complexity
        build_complexity = build_analysis.get("complexity", "simple")
        complexity_scores = {"simple": 1, "moderate": 2, "complex": 4}
        score += complexity_scores.get(build_complexity, 1)
        
        # CI complexity
        if ci_patterns.get("matrix_builds"):
            score += 2
        if ci_patterns.get("integration_tests"):
            score += 1
        if ci_patterns.get("aws_integration"):
            score += 2
        
        # Docker adds complexity
        if structure.get("has_docker"):
            score += 1
        
        return max(1, min(10, score))
    
    def _identify_risk_areas(self, structure: Dict[str, Any], tech_stack: TechnologyStack, ci_patterns: Dict[str, Any]) -> List[str]:
        """Identify potential risk areas for CI failures"""
        
        risks = []
        
        # Multi-module risks
        if "multi_module" in structure.get("structure_type", ""):
            risks.append("inter_module_dependencies")
            risks.append("build_order_dependencies")
        
        # Technology-specific risks
        primary_language = max(tech_stack.languages.items(), key=lambda x: x[1])[0] if tech_stack.languages else "unknown"
        
        if primary_language == "java":
            risks.extend(["jdk_version_compatibility", "maven_dependency_conflicts"])
            
            if ci_patterns.get("matrix_builds"):
                risks.append("matrix_build_inconsistencies")
        
        elif primary_language == "python":
            risks.extend(["dependency_resolution", "import_path_issues"])
            
            if "uv" in tech_stack.build_tools:
                risks.append("uv_extra_dev_dependencies")
        
        # Docker-specific risks
        if structure.get("has_docker"):
            risks.extend(["docker_build_context", "layer_caching_issues"])
        
        # Integration test risks
        if ci_patterns.get("integration_tests"):
            risks.append("integration_test_environment")
        
        if ci_patterns.get("aws_integration"):
            risks.extend(["aws_authentication", "aws_resource_availability"])
        
        return list(set(risks))  # Remove duplicates
    
    def _generate_custom_patterns(self, tech_stack: TechnologyStack, build_analysis: Dict[str, Any], ci_patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Generate custom error patterns specific to this project"""
        
        custom_patterns = {}
        
        # Maven-specific patterns
        if "Maven" in tech_stack.build_tools:
            if build_analysis.get("multi_stage"):
                custom_patterns["maven_multi_module_failure"] = {
                    "indicators": ["Failed to execute goal.*on project", "modules"],
                    "solutions": ["mvn clean install -pl specific-module", "Check module dependencies"],
                    "confidence_boost": 2
                }
            
            if ci_patterns.get("matrix_builds"):
                custom_patterns["maven_jdk_matrix_failure"] = {
                    "indicators": ["java.*version", "BUILD FAILURE", "Tests run:"],
                    "solutions": ["Check maven.compiler.source", "Verify test compatibility"],
                    "confidence_boost": 3
                }
        
        # Python UV-specific patterns
        if "uv" in tech_stack.build_tools:
            custom_patterns["uv_dev_dependencies_missing"] = {
                "indicators": ["No module named.*test", "pytest.*not found"],
                "solutions": ["uv pip install --extra dev", "uv sync --extra dev"],
                "confidence_boost": 4
            }
        
        # Docker + integration patterns
        if ci_patterns.get("aws_integration") and build_analysis.get("docker_builds"):
            custom_patterns["docker_aws_integration_failure"] = {
                "indicators": ["Integration Tests with AWS", "docker.*build", "403"],
                "solutions": ["Check AWS credentials in Docker", "Verify IAM permissions"],
                "confidence_boost": 3
            }
        
        return custom_patterns
    
    def _determine_project_type(self, structure: Dict[str, Any], tech_stack: TechnologyStack) -> str:
        """Determine high-level project type"""
        
        structure_type = structure.get("structure_type", "unknown")
        
        if "maven" in structure_type and "multi" in structure_type:
            return "maven_multi_module"
        elif "maven" in structure_type:
            return "maven_single_module"
        elif any(lang in tech_stack.languages for lang in ["python"]):
            return "python_application"
        elif any(lang in tech_stack.languages for lang in ["javascript", "typescript"]):
            return "node_application"
        else:
            return "unknown_application"
    
    def _determine_primary_language(self, tech_stack: TechnologyStack) -> str:
        """Determine primary programming language"""
        if not tech_stack.languages:
            return "unknown"
        
        return max(tech_stack.languages.items(), key=lambda x: x[1])[0]
    
    def _determine_build_system(self, tech_stack: TechnologyStack, build_analysis: Dict[str, Any]) -> str:
        """Determine primary build system"""
        return build_analysis.get("primary_tool", "unknown")
    
    def _determine_testing_framework(self, tech_stack: TechnologyStack) -> str:
        """Determine primary testing framework"""
        if not tech_stack.testing_tools:
            return "unknown"
        return tech_stack.testing_tools[0]
    
    def _fallback_project_profile(self, github_url: str) -> ProjectProfile:
        """Fallback profile when discovery fails"""
        return ProjectProfile(
            project_type="unknown_application",
            primary_language="unknown",
            build_system="unknown",
            testing_framework="unknown",
            complexity_score=5,
            risk_areas=["unknown_patterns"],
            custom_patterns={},
            ci_characteristics={"platform": "github_actions"}
        )
    
    # Additional analysis methods referenced in pattern extractors
    
    async def _analyze_dependencies(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze project dependencies and potential conflicts"""
        # Would analyze pom.xml, package.json, requirements.txt etc.
        return {"analysis": "dependency_analysis_placeholder"}
    
    async def _analyze_build_complexity(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze build process complexity"""
        # Would analyze build scripts, custom configurations
        return {"analysis": "build_complexity_placeholder"}
    
    async def _analyze_test_structure(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze test organization and patterns"""
        # Would analyze test directory structure, test configurations
        return {"analysis": "test_structure_placeholder"}
    
    async def _analyze_ci_integration(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze CI/CD integration patterns"""
        # Would analyze .github/workflows, CI configurations
        return {"analysis": "ci_integration_placeholder"}
    
    async def _analyze_deployment_patterns(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze deployment and release patterns"""
        # Would analyze deployment scripts, Docker configurations
        return {"analysis": "deployment_patterns_placeholder"}

# CLI interface for testing
async def main():
    """CLI entry point for testing Project Discovery Agent"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python project_discovery_agent.py <github_url>")
        print("Example: python project_discovery_agent.py https://github.com/StigLau/vdvil/actions/runs/17024829354")
        return 1
    
    agent = ProjectDiscoveryAgent()
    github_url = sys.argv[1]
    
    # Mock context for testing
    context = {
        "failure_data": {
            "job_names": ["Integration Tests with AWS", "Maven Tests Java 21", "Maven Tests Java 17"],
        }
    }
    
    try:
        profile = await agent.discover_project_profile(github_url, context)
        
        print(json.dumps({
            "project_type": profile.project_type,
            "primary_language": profile.primary_language,
            "build_system": profile.build_system,
            "testing_framework": profile.testing_framework,
            "complexity_score": profile.complexity_score,
            "risk_areas": profile.risk_areas,
            "custom_patterns": profile.custom_patterns,
            "ci_characteristics": profile.ci_characteristics
        }, indent=2))
        
        return 0
        
    except Exception as e:
        print(f"❌ Project discovery failed: {e}")
        return 1

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())