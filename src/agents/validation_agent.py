#!/usr/bin/env python3
"""
Build Detective Validation Agent

Solution verification and quality assurance for CI/CD failure analysis.
Validates that suggested fixes are appropriate, safe, and likely to succeed.
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
class ValidationRule:
    """Represents a validation rule for solution quality"""
    name: str
    description: str
    check_function: str  # Name of the method to call
    weight: float       # How important this rule is (0.0-1.0)
    failure_penalty: int  # Points deducted if this rule fails

@dataclass
class ValidationResult:
    """Result of validation process"""
    validation_status: str  # APPROVED, APPROVED_WITH_CAUTION, REVISION_NEEDED, REJECTED
    overall_confidence: int
    validation_details: Dict[str, int]
    quality_gates: Dict[str, bool]
    recommendations: List[str]
    risk_factors: List[str]
    validation_time: str

class ValidationAgent:
    """
    Validation Agent - Solution verification and quality assurance
    
    Validates CI/CD analysis results against quality standards:
    1. Solution coherence and technical accuracy
    2. Context appropriateness for the project
    3. Risk assessment and safety verification
    4. Implementation clarity and actionability
    """
    
    def __init__(self):
        self.agent_name = "build-detective-validation"
        self.validation_rules = self._initialize_validation_rules()
        self.risk_patterns = self._initialize_risk_patterns()
        self.solution_templates = self._initialize_solution_templates()
    
    def _initialize_validation_rules(self) -> List[ValidationRule]:
        """Initialize validation rules for solution quality"""
        return [
            ValidationRule(
                name="error_identification_accuracy",
                description="How well was the root cause identified?",
                check_function="validate_error_identification",
                weight=0.25,
                failure_penalty=3
            ),
            ValidationRule(
                name="solution_appropriateness", 
                description="How well does the fix address the problem?",
                check_function="validate_solution_appropriateness",
                weight=0.25,
                failure_penalty=3
            ),
            ValidationRule(
                name="implementation_clarity",
                description="How clear and actionable are the instructions?",
                check_function="validate_implementation_clarity",
                weight=0.20,
                failure_penalty=2
            ),
            ValidationRule(
                name="risk_assessment",
                description="How safe is the fix implementation?",
                check_function="validate_risk_assessment",
                weight=0.15,
                failure_penalty=2
            ),
            ValidationRule(
                name="technical_accuracy",
                description="Are the technical recommendations correct?",
                check_function="validate_technical_accuracy",
                weight=0.15,
                failure_penalty=4
            )
        ]
    
    def _initialize_risk_patterns(self) -> Dict[str, List[str]]:
        """Initialize patterns that indicate risky solutions"""
        return {
            "high_risk": [
                "rm -rf",
                "sudo.*install",
                "chmod 777",
                "disable.*security",
                "production.*database"
            ],
            "medium_risk": [
                "mvn clean install",  # Can be time-consuming
                "docker.*--no-cache",  # Rebuilds everything
                "git reset --hard",    # Loses changes
                "npm.*global"         # Global installs
            ],
            "configuration_changes": [
                "pom.xml",
                "package.json", 
                "Dockerfile",
                "github.*workflows",
                "maven.*settings"
            ]
        }
    
    def _initialize_solution_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize templates for validating solution quality"""
        return {
            "maven": {
                "expected_commands": ["mvn", "java", "javac"],
                "safe_operations": ["clean", "test", "compile", "verify"],
                "risky_operations": ["install", "deploy", "release"],
                "required_context": ["pom.xml", "java version", "maven version"]
            },
            "python": {
                "expected_commands": ["pip", "python", "pytest", "uv"],
                "safe_operations": ["install", "test", "list", "show"],
                "risky_operations": ["uninstall", "freeze", "global"],
                "required_context": ["requirements.txt", "pyproject.toml", "python version"]
            },
            "docker": {
                "expected_commands": ["docker", "FROM", "RUN", "COPY"],
                "safe_operations": ["build", "run", "inspect"],
                "risky_operations": ["rm", "system prune", "--privileged"],
                "required_context": ["Dockerfile", "base image", "build context"]
            }
        }
    
    async def validate_analysis(self, analysis_result: Dict[str, Any], original_request: Dict[str, Any], context: Dict[str, Any] = None) -> ValidationResult:
        """
        Main validation method - validates analysis quality and solution appropriateness
        
        Args:
            analysis_result: Results from CI Specialist Agent
            original_request: Original analysis request 
            context: Additional context from other agents
            
        Returns:
            ValidationResult with approval status and detailed feedback
        """
        logger.info(f"🔍 Validation Agent reviewing analysis quality")
        
        try:
            # Step 1: Run all validation rules
            validation_scores = await self._run_validation_rules(analysis_result, original_request, context)
            
            # Step 2: Check quality gates
            quality_gates = self._check_quality_gates(analysis_result, validation_scores)
            
            # Step 3: Assess risks
            risk_assessment = self._assess_solution_risks(analysis_result)
            
            # Step 4: Calculate overall confidence
            overall_confidence = self._calculate_overall_confidence(validation_scores, quality_gates, risk_assessment)
            
            # Step 5: Determine validation status
            validation_status = self._determine_validation_status(overall_confidence, quality_gates, risk_assessment)
            
            # Step 6: Generate recommendations
            recommendations = self._generate_recommendations(analysis_result, validation_scores, risk_assessment)
            
            result = ValidationResult(
                validation_status=validation_status,
                overall_confidence=overall_confidence,
                validation_details=validation_scores,
                quality_gates=quality_gates,
                recommendations=recommendations,
                risk_factors=risk_assessment["risk_factors"],
                validation_time=datetime.now().isoformat()
            )
            
            logger.info(f"✅ Validation complete: {validation_status} with {overall_confidence}/10 confidence")
            return result
            
        except Exception as e:
            logger.error(f"❌ Validation failed: {e}")
            return self._error_validation_result(str(e))
    
    async def _run_validation_rules(self, analysis: Dict[str, Any], request: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, int]:
        """Run all validation rules and return scores"""
        
        scores = {}
        
        for rule in self.validation_rules:
            try:
                # Get the validation method
                validation_method = getattr(self, rule.check_function)
                score = await validation_method(analysis, request, context)
                scores[rule.name] = score
            except Exception as e:
                logger.warning(f"Validation rule {rule.name} failed: {e}")
                scores[rule.name] = 1  # Minimum score for failed validation
        
        return scores
    
    async def validate_error_identification(self, analysis: Dict[str, Any], request: Dict[str, Any], context: Dict[str, Any]) -> int:
        """Validate how well the error was identified (1-10 scale)"""
        
        score = 5  # Base score
        
        # Check if primary error is specific and actionable
        primary_error = analysis.get("primary_error", "")
        
        if not primary_error or primary_error.lower() in ["unknown", "generic", "manual analysis needed"]:
            score = 2  # Very low for generic errors
        elif len(primary_error) < 20:
            score = 3  # Too brief, likely not specific enough
        elif any(keyword in primary_error.lower() for keyword in ["specific", "version", "configuration", "dependency"]):
            score = 8  # Good specificity
        else:
            score = 6  # Reasonable identification
        
        # Check error type specificity
        error_type = analysis.get("error_type", "unknown")
        if error_type == "unknown":
            score -= 2
        elif "_" in error_type:  # Specific subtypes like "maven_test"
            score += 1
        
        # Check if confidence matches error specificity
        confidence = analysis.get("confidence", 5)
        error_specificity = len(primary_error.split())
        
        # If confidence is high but error description is vague, penalize
        if confidence >= 8 and error_specificity < 5:
            score -= 2
        
        # If confidence is low but error is well described, boost
        if confidence <= 4 and error_specificity >= 10:
            score += 1
        
        return max(1, min(10, score))
    
    async def validate_solution_appropriateness(self, analysis: Dict[str, Any], request: Dict[str, Any], context: Dict[str, Any]) -> int:
        """Validate how appropriate the suggested solutions are (1-10 scale)"""
        
        score = 5  # Base score
        
        suggested_actions = analysis.get("solutions", {}).get("suggested_actions", [])
        error_type = analysis.get("error_type", "unknown")
        
        if not suggested_actions:
            return 1  # No solutions provided
        
        # Check if solutions match error type
        if error_type.startswith("maven"):
            maven_commands = ["mvn", "java", "pom.xml"]
            if any(cmd in " ".join(suggested_actions).lower() for cmd in maven_commands):
                score += 2
            else:
                score -= 3  # Maven error but no Maven solutions
        
        elif error_type.startswith("python"):
            python_commands = ["pip", "python", "pytest", "uv"]
            if any(cmd in " ".join(suggested_actions).lower() for cmd in python_commands):
                score += 2
            else:
                score -= 3  # Python error but no Python solutions
        
        elif error_type.startswith("docker"):
            docker_commands = ["docker", "dockerfile"]
            if any(cmd in " ".join(suggested_actions).lower() for cmd in docker_commands):
                score += 2
            else:
                score -= 3  # Docker error but no Docker solutions
        
        # Check solution specificity
        generic_solutions = ["check logs", "manual review", "investigate", "debug"]
        specific_actions = 0
        generic_actions = 0
        
        for action in suggested_actions:
            action_lower = action.lower()
            if any(generic in action_lower for generic in generic_solutions):
                generic_actions += 1
            elif len(action.split()) >= 3:  # Reasonably detailed
                specific_actions += 1
        
        if generic_actions > specific_actions:
            score -= 2  # Too many generic solutions
        elif specific_actions > 0 and generic_actions == 0:
            score += 2  # All solutions are specific
        
        # Check for actionable commands
        command_patterns = [r'^\w+\s+\w+', r'\-\-\w+', r'\.xml$', r'\.json$']
        actionable_commands = 0
        
        for action in suggested_actions:
            if any(re.search(pattern, action) for pattern in command_patterns):
                actionable_commands += 1
        
        if actionable_commands >= len(suggested_actions) * 0.5:  # At least 50% actionable
            score += 1
        
        return max(1, min(10, score))
    
    async def validate_implementation_clarity(self, analysis: Dict[str, Any], request: Dict[str, Any], context: Dict[str, Any]) -> int:
        """Validate clarity and actionability of implementation steps (1-10 scale)"""
        
        score = 5  # Base score
        
        solutions = analysis.get("solutions", {})
        suggested_actions = solutions.get("suggested_actions", [])
        verification_steps = solutions.get("verification_steps", [])
        
        if not suggested_actions:
            return 1  # No implementation steps provided
        
        # Check for step-by-step clarity
        numbered_or_ordered = False
        for action in suggested_actions:
            if re.match(r'^\d+\.|\-\s|\*\s|Step\s\d+', action):
                numbered_or_ordered = True
                break
        
        if numbered_or_ordered:
            score += 2
        
        # Check for command specificity
        executable_commands = 0
        for action in suggested_actions:
            # Look for executable command patterns
            if re.match(r'^(mvn|pip|docker|gh|git|java|python)\s', action.strip()):
                executable_commands += 1
            elif any(flag in action for flag in ['--', '-']):  # Command line flags
                executable_commands += 1
        
        if executable_commands >= len(suggested_actions) * 0.7:  # 70% executable
            score += 2
        elif executable_commands >= len(suggested_actions) * 0.4:  # 40% executable
            score += 1
        
        # Check for verification steps
        if verification_steps:
            if len(verification_steps) >= 2:
                score += 2  # Good verification coverage
            else:
                score += 1  # Some verification
        else:
            score -= 1  # No verification provided
        
        # Check for context-specific instructions
        error_type = analysis.get("error_type", "")
        context_appropriate = False
        
        if error_type.startswith("maven") and any("pom.xml" in action for action in suggested_actions):
            context_appropriate = True
        elif error_type.startswith("python") and any("requirements.txt" in action or "pyproject.toml" in action for action in suggested_actions):
            context_appropriate = True
        elif error_type.startswith("docker") and any("Dockerfile" in action for action in suggested_actions):
            context_appropriate = True
        
        if context_appropriate:
            score += 1
        
        # Check for estimated time
        estimated_time = solutions.get("estimated_fix_time", "")
        if estimated_time and "minute" in estimated_time:
            score += 1  # Time estimates help with planning
        
        return max(1, min(10, score))
    
    async def validate_risk_assessment(self, analysis: Dict[str, Any], request: Dict[str, Any], context: Dict[str, Any]) -> int:
        """Validate risk level of suggested solutions (1-10 scale, higher = safer)"""
        
        score = 7  # Start with reasonably safe assumption
        
        suggested_actions = analysis.get("solutions", {}).get("suggested_actions", [])
        
        if not suggested_actions:
            return score
        
        # Check for high-risk patterns
        all_actions_text = " ".join(suggested_actions).lower()
        
        for risk_pattern in self.risk_patterns["high_risk"]:
            if risk_pattern.lower() in all_actions_text:
                score -= 4  # Major penalty for high risk
                logger.warning(f"High-risk pattern detected: {risk_pattern}")
        
        # Check for medium-risk patterns
        for risk_pattern in self.risk_patterns["medium_risk"]:
            if risk_pattern.lower() in all_actions_text:
                score -= 2  # Medium penalty
        
        # Check for configuration file changes (requires caution)
        config_changes = 0
        for config_pattern in self.risk_patterns["configuration_changes"]:
            if config_pattern.lower() in all_actions_text:
                config_changes += 1
        
        if config_changes > 2:
            score -= 2  # Multiple config changes increase risk
        elif config_changes > 0:
            score -= 1  # Some config changes
        
        # Check for destructive operations
        destructive_patterns = ["delete", "remove", "rm ", "drop", "truncate", "clear"]
        for pattern in destructive_patterns:
            if pattern in all_actions_text:
                score -= 3
                logger.warning(f"Potentially destructive operation detected: {pattern}")
        
        # Boost score for safe, reversible operations
        safe_patterns = ["test", "check", "verify", "validate", "dry-run", "--help"]
        safe_operations = sum(1 for pattern in safe_patterns if pattern in all_actions_text)
        if safe_operations >= 2:
            score += 1
        
        return max(1, min(10, score))
    
    async def validate_technical_accuracy(self, analysis: Dict[str, Any], request: Dict[str, Any], context: Dict[str, Any]) -> int:
        """Validate technical accuracy of recommendations (1-10 scale)"""
        
        score = 6  # Start with reasonable accuracy assumption
        
        error_type = analysis.get("error_type", "unknown")
        suggested_actions = analysis.get("solutions", {}).get("suggested_actions", [])
        
        if not suggested_actions:
            return 1
        
        # Check technology-specific accuracy
        if error_type.startswith("maven"):
            score += self._check_maven_accuracy(suggested_actions)
        elif error_type.startswith("python"):
            score += self._check_python_accuracy(suggested_actions)
        elif error_type.startswith("docker"):
            score += self._check_docker_accuracy(suggested_actions)
        
        # Check for command syntax validity (basic validation)
        syntax_errors = 0
        for action in suggested_actions:
            # Look for common syntax issues
            if re.search(r'[{}]\s*[{}]', action):  # Double brackets/braces
                syntax_errors += 1
            elif action.count('"') % 2 != 0:  # Unmatched quotes
                syntax_errors += 1
            elif action.count("'") % 2 != 0:  # Unmatched quotes
                syntax_errors += 1
        
        if syntax_errors > 0:
            score -= min(syntax_errors * 2, 4)  # Penalize syntax errors
        
        return max(1, min(10, score))
    
    def _check_maven_accuracy(self, actions: List[str]) -> int:
        """Check Maven-specific technical accuracy"""
        accuracy_boost = 0
        actions_text = " ".join(actions).lower()
        
        # Check for correct Maven syntax
        if "mvn clean" in actions_text:
            accuracy_boost += 1  # Standard practice
        if any(phase in actions_text for phase in ["test", "compile", "verify", "validate"]):
            accuracy_boost += 1  # Valid Maven phases
        if "surefire" in actions_text and "maven" in actions_text:
            accuracy_boost += 1  # Context-appropriate for Maven testing
        
        # Penalize incorrect patterns
        if "npm" in actions_text or "pip" in actions_text:
            accuracy_boost -= 2  # Wrong technology
        
        return accuracy_boost
    
    def _check_python_accuracy(self, actions: List[str]) -> int:
        """Check Python-specific technical accuracy"""
        accuracy_boost = 0
        actions_text = " ".join(actions).lower()
        
        # Check for correct Python patterns
        if any(cmd in actions_text for cmd in ["pip install", "python -m", "pytest"]):
            accuracy_boost += 1
        if "--extra" in actions_text and "uv" in actions_text:
            accuracy_boost += 1  # Correct UV usage
        if "requirements.txt" in actions_text or "pyproject.toml" in actions_text:
            accuracy_boost += 1  # Proper dependency files
        
        # Penalize incorrect patterns
        if "mvn" in actions_text or "java" in actions_text:
            accuracy_boost -= 2  # Wrong technology
        
        return accuracy_boost
    
    def _check_docker_accuracy(self, actions: List[str]) -> int:
        """Check Docker-specific technical accuracy"""
        accuracy_boost = 0
        actions_text = " ".join(actions).lower()
        
        # Check for correct Docker patterns
        if "docker build" in actions_text:
            accuracy_boost += 1
        if "--no-cache" in actions_text:
            accuracy_boost += 1  # Valid Docker flag
        if "dockerfile" in actions_text:
            accuracy_boost += 1  # Context-appropriate
        
        # Penalize incorrect patterns
        if any(wrong in actions_text for wrong in ["mvn", "pip install"]):
            accuracy_boost -= 1  # Mixed technologies
        
        return accuracy_boost
    
    def _check_quality_gates(self, analysis: Dict[str, Any], validation_scores: Dict[str, int]) -> Dict[str, bool]:
        """Check if analysis passes quality gates"""
        
        return {
            "primary_error_identified": len(analysis.get("primary_error", "")) > 10,
            "solution_actionable": len(analysis.get("solutions", {}).get("suggested_actions", [])) > 0,
            "technically_sound": validation_scores.get("technical_accuracy", 0) >= 6,
            "appropriate_confidence": 3 <= analysis.get("confidence", 0) <= 10,
            "reasonable_cost": True  # Assume cost is reasonable for now
        }
    
    def _assess_solution_risks(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall risk level of suggested solutions"""
        
        suggested_actions = analysis.get("solutions", {}).get("suggested_actions", [])
        all_actions_text = " ".join(suggested_actions).lower()
        
        risk_factors = []
        risk_level = "low"
        
        # Check for high-risk patterns
        for pattern in self.risk_patterns["high_risk"]:
            if pattern.lower() in all_actions_text:
                risk_factors.append(f"High-risk operation: {pattern}")
                risk_level = "high"
        
        # Check for configuration changes
        config_changes = []
        for pattern in self.risk_patterns["configuration_changes"]:
            if pattern.lower() in all_actions_text:
                config_changes.append(pattern)
        
        if config_changes:
            risk_factors.append(f"Configuration changes: {', '.join(config_changes)}")
            if risk_level == "low":
                risk_level = "medium"
        
        # Check for production environment implications
        if any(prod in all_actions_text for prod in ["production", "prod", "main branch", "master"]):
            risk_factors.append("May affect production environment")
            if risk_level == "low":
                risk_level = "medium"
        
        return {
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "requires_manual_review": risk_level == "high"
        }
    
    def _calculate_overall_confidence(self, validation_scores: Dict[str, int], quality_gates: Dict[str, bool], risk_assessment: Dict[str, Any]) -> int:
        """Calculate overall confidence score from validation results"""
        
        # Weighted average of validation scores
        total_score = 0
        total_weight = 0
        
        for rule in self.validation_rules:
            score = validation_scores.get(rule.name, 5)
            total_score += score * rule.weight
            total_weight += rule.weight
        
        weighted_average = total_score / total_weight if total_weight > 0 else 5
        
        # Adjust for quality gates
        gates_passed = sum(quality_gates.values())
        gate_adjustment = (gates_passed - 3) * 0.5  # Boost/penalty based on gates passed
        
        # Adjust for risk level
        risk_adjustments = {"low": 0, "medium": -1, "high": -2}
        risk_adjustment = risk_adjustments.get(risk_assessment["risk_level"], 0)
        
        final_confidence = weighted_average + gate_adjustment + risk_adjustment
        
        return max(1, min(10, int(round(final_confidence))))
    
    def _determine_validation_status(self, confidence: int, quality_gates: Dict[str, bool], risk_assessment: Dict[str, Any]) -> str:
        """Determine overall validation status"""
        
        gates_passed = sum(quality_gates.values())
        risk_level = risk_assessment["risk_level"]
        
        if confidence >= 8 and gates_passed >= 4 and risk_level == "low":
            return "APPROVED"
        elif confidence >= 6 and gates_passed >= 3 and risk_level in ["low", "medium"]:
            return "APPROVED_WITH_CAUTION"
        elif confidence >= 4 and gates_passed >= 2:
            return "REVISION_NEEDED"
        else:
            return "REJECTED"
    
    def _generate_recommendations(self, analysis: Dict[str, Any], validation_scores: Dict[str, int], risk_assessment: Dict[str, Any]) -> List[str]:
        """Generate recommendations for improving analysis quality"""
        
        recommendations = []
        
        # Recommendations based on validation scores
        if validation_scores.get("error_identification_accuracy", 5) < 6:
            recommendations.append("Improve error identification specificity")
        
        if validation_scores.get("solution_appropriateness", 5) < 6:
            recommendations.append("Ensure solutions directly address the identified problem")
        
        if validation_scores.get("implementation_clarity", 5) < 6:
            recommendations.append("Provide more specific, step-by-step implementation instructions")
        
        if validation_scores.get("technical_accuracy", 5) < 6:
            recommendations.append("Review technical recommendations for accuracy")
        
        # Risk-based recommendations
        if risk_assessment["risk_level"] == "high":
            recommendations.append("Test all changes in development environment first")
            recommendations.append("Consider having solutions reviewed by senior developer")
        elif risk_assessment["risk_level"] == "medium":
            recommendations.append("Test the solution in non-production environment")
        
        # Default recommendations if none specified
        if not recommendations:
            recommendations = ["Solution appears ready for implementation"]
        
        return recommendations
    
    def _error_validation_result(self, error_msg: str) -> ValidationResult:
        """Generate error result when validation fails"""
        return ValidationResult(
            validation_status="REJECTED",
            overall_confidence=1,
            validation_details={"validation_error": 1},
            quality_gates={gate: False for gate in ["primary_error_identified", "solution_actionable", "technically_sound", "appropriate_confidence", "reasonable_cost"]},
            recommendations=[f"Validation failed: {error_msg}"],
            risk_factors=["Validation process failed"],
            validation_time=datetime.now().isoformat()
        )

# CLI interface for testing
async def main():
    """CLI entry point for testing Validation Agent"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python validation_agent.py <analysis_result_json>")
        print("Example: python validation_agent.py '{\"primary_error\":\"Maven test failure\",\"confidence\":8}'")
        return 1
    
    validator = ValidationAgent()
    
    try:
        # Parse analysis result from command line
        analysis_result = json.loads(sys.argv[1])
        
        # Mock request data
        original_request = {
            "github_url": "https://github.com/example/repo/actions/runs/123",
            "priority": "medium"
        }
        
        # Run validation
        result = await validator.validate_analysis(analysis_result, original_request)
        
        # Output results
        print(json.dumps({
            "validation_status": result.validation_status,
            "overall_confidence": result.overall_confidence,
            "quality_gates": result.quality_gates,
            "recommendations": result.recommendations,
            "risk_factors": result.risk_factors
        }, indent=2))
        
        return 0
        
    except json.JSONDecodeError:
        print("❌ Invalid JSON in analysis result")
        return 1
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return 1

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())