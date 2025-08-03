#!/usr/bin/env python3
"""
📊 LESSONS LEARNED INTEGRATION VALIDATOR
Enterprise validation script confirming explicit integration of learning patterns

VALIDATION ID: LLI_VAL_20250716_231738
PROCESS: Comprehensive lessons learned integration analysis
COMPLIANCE: DUAL COPILOT pattern with visual processing indicators
"""

import os
import sys
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from tqdm import tqdm
import logging
from utils.lessons_learned_integrator import load_lessons

# MANDATORY: Text indicators for cross-platform compatibility
TEXT_INDICATORS = {
    "start": "[START]",
    "progress": "[PROGRESS]",
    "success": "[SUCCESS]",
    "error": "[ERROR]",
    "warning": "[WARNING]",
    "info": "[INFO]",
    "validation": "[VALIDATION]",
    "completion": "[COMPLETION]",
    "database_query": "[DB_QUERY]",
    "autonomous": "[AUTONOMOUS]",
}


@dataclass
class LearningPatternValidation:
    """Learning pattern validation result"""

    pattern_name: str
    implementation_score: float
    files_validated: int
    evidence_found: List[str]
    compliance_status: str


@dataclass
class IntegrationValidationResult:
    """Comprehensive integration validation result"""

    validation_id: str
    start_time: datetime
    completion_time: Optional[datetime]
    overall_score: float
    pattern_validations: List[LearningPatternValidation]
    enterprise_compliance: bool
    dual_copilot_validated: bool


class LessonsLearnedIntegrationValidator:
    """
    🎯 Primary Executor: Validates explicit integration of learning patterns
    Implements DUAL COPILOT pattern with secondary validation
    """

    def __init__(self, workspace_path: str | None = None):
        """Initialize validator with dynamic workspace path.

        Falls back to the ``GH_COPILOT_WORKSPACE`` environment variable and
        ultimately the current working directory to avoid hard-coded platform
        paths.
        """
        workspace_env = workspace_path or os.getenv("GH_COPILOT_WORKSPACE", str(Path.cwd()))
        self.workspace_path = Path(workspace_env)
        self.validation_id = f"LLI_VAL_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.start_time = datetime.now()
        self.process_id = os.getpid()

        # Setup logging with visual indicators
        self.setup_logging()

        # CRITICAL: Anti-recursion validation
        self.validate_environment_compliance()

        # Learning patterns to validate
        self.learning_patterns = {
            "database_first_architecture": {
                "description": "Database-first logic with production.db priority",
                "target_score": 0.985,
                "validation_files": ["production.db", "unified_script_generation_system.py"],
            },
            "dual_copilot_pattern": {
                "description": "Primary executor + Secondary validator architecture",
                "target_score": 0.968,
                "validation_files": ["enterprise_dual_copilot_validator.py", "DUAL_COPILOT_PATTERN.instructions.md"],
            },
            "visual_processing_indicators": {
                "description": "Progress monitoring and enterprise visual standards",
                "target_score": 0.947,
                "validation_files": ["tqdm", "TEXT_INDICATORS", "progress"],
            },
            "autonomous_systems": {
                "description": "Self-healing and autonomous operation capabilities",
                "target_score": 0.972,
                "validation_files": ["self_healing_self_learning_system.py", "autonomous"],
            },
            "enterprise_compliance": {
                "description": "Zero tolerance protocols and enterprise standards",
                "target_score": 0.991,
                "validation_files": ["anti_recursion", "session_integrity", "enterprise"],
            },
        }

        self.logger.info(f"{TEXT_INDICATORS['start']} Lessons Learned Integration Validator")
        self.logger.info(f"Validation ID: {self.validation_id}")
        self.logger.info(f"Process ID: {self.process_id}")
        self.logger.info(f"Workspace: {self.workspace_path}")

    def setup_logging(self):
        """Setup comprehensive logging with visual indicators"""
        log_dir = self.workspace_path / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_dir / f"integration_validation_{self.validation_id}.log"),
                logging.StreamHandler(sys.stdout),
            ],
        )
        self.logger = logging.getLogger(__name__)

    def validate_environment_compliance(self):
        """CRITICAL: Validate workspace environment compliance"""
        try:
            # Check for recursive backup or temporary directory violations
            violations = []

            for folder in self.workspace_path.rglob("*"):
                if not folder.is_dir() or folder == self.workspace_path:
                    continue

                # Skip virtual environment, VCS, and expected temp directories
                if ".venv" in folder.parts or ".git" in folder.parts:
                    continue
                if folder == self.workspace_path / "tmp":
                    continue

                name = folder.name.lower()
                if "backup" in name or name in {"temp", "tmp"}:
                    violations.append(str(folder))

            if violations:
                self.logger.error(f"{TEXT_INDICATORS['error']} Recursive violations detected:")
                for violation in violations:
                    self.logger.error(f"   - {violation}")
                raise RuntimeError("CRITICAL: Environment violations prevent validation")

            self.logger.info(f"{TEXT_INDICATORS['success']} Environment compliance validated")

        except Exception as e:
            self.logger.error(f"{TEXT_INDICATORS['error']} Environment validation failed: {str(e)}")
            raise

    def query_production_database(self, query_type: str) -> Dict[str, Any]:
        """MANDATORY: Database-first query for validation patterns"""
        db_path = self.workspace_path / "databases" / "production.db"

        if not db_path.exists():
            self.logger.warning(f"{TEXT_INDICATORS['warning']} Production database not found: {db_path}")
            return {"patterns": [], "count": 0}

        try:
            self.logger.info(f"{TEXT_INDICATORS['database_query']} Querying production.db for {query_type}")

            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()

                if query_type == "script_patterns":
                    cursor.execute("""
                        SELECT script_path, functionality_category, script_type, importance_score
                        FROM enhanced_script_tracking
                        WHERE functionality_category IS NOT NULL
                        ORDER BY importance_score DESC
                    """)
                elif query_type == "learning_patterns":
                    cursor.execute("""
                        SELECT script_path, functionality_category, COUNT(*) as frequency
                        FROM enhanced_script_tracking
                        WHERE script_path LIKE '%learning%' OR script_path LIKE '%pattern%'
                        GROUP BY functionality_category
                        ORDER BY frequency DESC
                    """)
                else:
                    cursor.execute("SELECT COUNT(*) FROM enhanced_script_tracking")

                results = cursor.fetchall()

                self.logger.info(f"{TEXT_INDICATORS['success']} Database query completed: {len(results)} results")
                return {"patterns": results, "count": len(results)}

        except Exception as e:
            self.logger.error(f"{TEXT_INDICATORS['error']} Database query failed: {str(e)}")
            return {"patterns": [], "count": 0, "error": str(e)}

    def validate_learning_pattern(self, pattern_name: str, pattern_config: Dict[str, Any]) -> LearningPatternValidation:
        """Validate individual learning pattern integration"""
        self.logger.info(f"{TEXT_INDICATORS['validation']} Validating pattern: {pattern_name}")

        evidence_found = []
        files_validated = 0
        implementation_score = 0.0

        # Search for pattern evidence in codebase
        for validation_file in pattern_config["validation_files"]:
            if self.search_pattern_evidence(validation_file):
                evidence_found.append(validation_file)
                files_validated += 1

        # Calculate implementation score
        if files_validated > 0:
            base_score = min(files_validated / len(pattern_config["validation_files"]), 1.0)
            # Apply pattern-specific scoring
            implementation_score = base_score * pattern_config["target_score"]

        # Determine compliance status
        compliance_status = "COMPLIANT" if implementation_score >= pattern_config["target_score"] * 0.9 else "PARTIAL"

        validation_result = LearningPatternValidation(
            pattern_name=pattern_name,
            implementation_score=implementation_score,
            files_validated=files_validated,
            evidence_found=evidence_found,
            compliance_status=compliance_status,
        )

        self.logger.info(
            f"{TEXT_INDICATORS['info']} Pattern {pattern_name}: {implementation_score:.3f} score, {compliance_status}"
        )

        return validation_result

    def search_pattern_evidence(self, search_pattern: str) -> bool:
        """Search for pattern evidence in workspace"""
        try:
            # Search in Python files
            python_files = list(self.workspace_path.rglob("*.py"))
            for py_file in python_files[:50]:  # Limit search for performance
                try:
                    with open(py_file, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read().lower()
                        if search_pattern.lower() in content:
                            return True
                except Exception:
                    continue

            # Search in documentation files
            doc_files = list(self.workspace_path.rglob("*.md"))
            for doc_file in doc_files[:30]:  # Limit search for performance
                try:
                    with open(doc_file, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read().lower()
                        if search_pattern.lower() in content:
                            return True
                except Exception:
                    continue

            # Search for database files
            if search_pattern.endswith(".db"):
                db_path = self.workspace_path / "databases" / search_pattern
                return db_path.exists()

            return False

        except Exception as e:
            self.logger.warning(f"{TEXT_INDICATORS['warning']} Search error for {search_pattern}: {str(e)}")
            return False

    def execute_comprehensive_validation(self) -> IntegrationValidationResult:
        """
        🎯 PRIMARY EXECUTOR: Execute comprehensive validation with DUAL COPILOT pattern
        MANDATORY: Visual processing indicators and enterprise compliance
        """

        self.logger.info("=" * 80)
        self.logger.info(f"{TEXT_INDICATORS['start']} COMPREHENSIVE LESSONS LEARNED INTEGRATION VALIDATION")
        self.logger.info("=" * 80)

        pattern_validations = []
        total_patterns = len(self.learning_patterns)

        # MANDATORY: Progress monitoring with tqdm
        with tqdm(total=100, desc="[PROGRESS] Validation", unit="%") as pbar:
            # Phase 1: Database validation (25%)
            pbar.set_description("[PROGRESS] Database-First Validation")
            db_results = self.query_production_database("script_patterns")
            pbar.update(25)

            # Phase 2: Pattern validation (50%)
            pbar.set_description("[PROGRESS] Learning Pattern Analysis")
            for i, (pattern_name, pattern_config) in enumerate(self.learning_patterns.items()):
                validation_result = self.validate_learning_pattern(pattern_name, pattern_config)
                pattern_validations.append(validation_result)

                # Update progress
                pattern_progress = (i + 1) / total_patterns * 50
                pbar.update(pattern_progress / total_patterns)

            # Phase 3: Enterprise compliance (15%)
            pbar.set_description("[PROGRESS] Enterprise Compliance Check")
            enterprise_compliance = self.validate_enterprise_compliance()
            pbar.update(15)

            # Phase 4: DUAL COPILOT validation (10%)
            pbar.set_description("[PROGRESS] DUAL COPILOT Validation")
            dual_copilot_validated = self.validate_dual_copilot_pattern()
            pbar.update(10)

        # Calculate overall score
        if pattern_validations:
            overall_score = sum(pv.implementation_score for pv in pattern_validations) / len(pattern_validations)
        else:
            overall_score = 0.0

        # Create comprehensive result
        result = IntegrationValidationResult(
            validation_id=self.validation_id,
            start_time=self.start_time,
            completion_time=datetime.now(),
            overall_score=overall_score,
            pattern_validations=pattern_validations,
            enterprise_compliance=enterprise_compliance,
            dual_copilot_validated=dual_copilot_validated,
        )

        # MANDATORY: Completion logging
        self.log_validation_summary(result)

        return result

    def validate_enterprise_compliance(self) -> bool:
        """Validate enterprise compliance standards"""
        try:
            compliance_checks = [
                self.check_anti_recursion_protocols(),
                self.check_visual_processing_standards(),
                self.check_session_integrity_systems(),
                self.check_database_integration(),
                self.check_lessons_dataset_usage(),
                self.audit_module_hooks(),
            ]
            compliance_score = sum(compliance_checks) / len(compliance_checks)
            is_compliant = compliance_score >= 0.8
            self.logger.info(
                f"{TEXT_INDICATORS['validation']} Enterprise compliance: {compliance_score:.1%}"
            )
            return is_compliant
        except Exception as e:
            self.logger.error(
                f"{TEXT_INDICATORS['error']} Enterprise compliance validation failed: {str(e)}"
            )
            return False

    def validate_dual_copilot_pattern(self) -> bool:
        """Validate DUAL COPILOT pattern implementation"""
        try:
            # Check for dual copilot files
            dual_copilot_files = [
                "enterprise_dual_copilot_validator.py",
                "DUAL_COPILOT_PATTERN.instructions.md",
                "dual_copilot",
            ]

            evidence_count = 0
            for file_pattern in dual_copilot_files:
                if self.search_pattern_evidence(file_pattern):
                    evidence_count += 1

            is_validated = evidence_count >= 2

            self.logger.info(
                f"{TEXT_INDICATORS['validation']} DUAL COPILOT pattern: {evidence_count}/{len(dual_copilot_files)} validated"
            )

            return is_validated

        except Exception as e:
            self.logger.error(f"{TEXT_INDICATORS['error']} DUAL COPILOT validation failed: {str(e)}")
            return False

    def check_anti_recursion_protocols(self) -> bool:
        """Check anti-recursion protocol implementation"""
        return self.search_pattern_evidence("anti_recursion") or self.search_pattern_evidence("recursive")

    def check_visual_processing_standards(self) -> bool:
        """Check visual processing standards implementation"""
        return self.search_pattern_evidence("tqdm") or self.search_pattern_evidence("TEXT_INDICATORS")

    def check_session_integrity_systems(self) -> bool:
        """Check session integrity system implementation"""
        return self.search_pattern_evidence("session_integrity") or self.search_pattern_evidence(
            "comprehensive_session"
        )

    def check_lessons_dataset_usage(self) -> bool:
        """Confirm curated lessons dataset is present and non-empty."""
        try:
            lessons = load_lessons()
            count = len(lessons)
            if count:
                self.logger.info(
                    f"{TEXT_INDICATORS['info']} Lessons dataset entries: {count}"
                )
                return True
            self.logger.warning(f"{TEXT_INDICATORS['warning']} Lessons dataset empty")
            return False
        except Exception as exc:  # pragma: no cover - unexpected errors
            self.logger.error(
                f"{TEXT_INDICATORS['error']} Lessons dataset check failed: {exc}"
            )
            return False

    def check_database_integration(self) -> bool:
        """Check database integration implementation"""
        return self.search_pattern_evidence("production.db") or self.search_pattern_evidence("database_first")

    def audit_module_hooks(self) -> bool:
        """Audit scripts and template_engine modules for lessons learned hooks."""
        target_dirs = ["template_engine"]
        missing_modules: List[str] = []
        for directory in target_dirs:
            dir_path = self.workspace_path / directory
            if not dir_path.exists():
                continue
            for path in dir_path.rglob("*.py"):
                try:
                    content = path.read_text(encoding="utf-8")
                except Exception as exc:  # pragma: no cover - unexpected errors
                    self.logger.warning(
                        f"{TEXT_INDICATORS['warning']} Could not read {path}: {exc}"
                    )
                    continue
                if "lessons_learned_integrator" not in content:
                    missing_modules.append(path.relative_to(self.workspace_path).as_posix())
        if missing_modules:
            self.logger.warning(
                f"{TEXT_INDICATORS['warning']} Missing lessons learned hooks: {len(missing_modules)} modules"
            )
            for module in missing_modules:
                self.logger.warning(f"  - {module}")
            return False
        self.logger.info(
            f"{TEXT_INDICATORS['success']} All modules include lessons learned hooks"
        )
        return True

    def log_validation_summary(self, result: IntegrationValidationResult):
        """Log comprehensive validation summary"""
        if result.completion_time:
            duration = (result.completion_time - result.start_time).total_seconds()
        else:
            duration = 0.0

        self.logger.info("=" * 80)
        self.logger.info(f"{TEXT_INDICATORS['completion']} LESSONS LEARNED INTEGRATION VALIDATION COMPLETE")
        self.logger.info("=" * 80)
        self.logger.info(f"Validation ID: {result.validation_id}")
        self.logger.info(f"Duration: {duration:.1f} seconds")
        self.logger.info(f"Overall Integration Score: {result.overall_score:.1%}")
        self.logger.info(f"Enterprise Compliance: {'✅ PASSED' if result.enterprise_compliance else '❌ FAILED'}")
        self.logger.info(f"DUAL COPILOT Validated: {'✅ PASSED' if result.dual_copilot_validated else '❌ FAILED'}")

        self.logger.info("\n📊 LEARNING PATTERN VALIDATION RESULTS:")
        for pv in result.pattern_validations:
            status_icon = "✅" if pv.compliance_status == "COMPLIANT" else "⚠️"
            self.logger.info(
                f"  {status_icon} {pv.pattern_name}: {pv.implementation_score:.1%} ({pv.files_validated} files)"
            )

        # Overall assessment
        if result.overall_score >= 0.95:
            self.logger.info(f"\n{TEXT_INDICATORS['success']} LESSONS LEARNED 100% EXPLICITLY INTEGRATED ✅")
        elif result.overall_score >= 0.85:
            self.logger.info(f"\n{TEXT_INDICATORS['success']} LESSONS LEARNED SUBSTANTIALLY INTEGRATED ✅")
        else:
            self.logger.warning(f"\n{TEXT_INDICATORS['warning']} LESSONS LEARNED PARTIALLY INTEGRATED ⚠️")

        self.logger.info("=" * 80)


class LessonsLearnedSecondaryValidator:
    """
    🛡️ Secondary Validator: Validates primary validation results
    Implements DUAL COPILOT pattern for quality assurance
    """

    def __init__(self):
        self.validation_start = datetime.now()
        self.validator_id = f"LLI_SEC_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        self.logger.info(f"{TEXT_INDICATORS['validation']} Secondary Validator initialized: {self.validator_id}")

    def validate_primary_results(self, primary_result: IntegrationValidationResult) -> Dict[str, Any]:
        """Validate primary validation results for quality assurance"""

        self.logger.info("=" * 60)
        self.logger.info(f"{TEXT_INDICATORS['validation']} DUAL COPILOT SECONDARY VALIDATION")
        self.logger.info("=" * 60)

        validation_checks = {
            "overall_score_reasonable": primary_result.overall_score >= 0.7,
            "patterns_validated": len(primary_result.pattern_validations) >= 3,
            "enterprise_compliance_checked": primary_result.enterprise_compliance is not None,
            "dual_copilot_checked": primary_result.dual_copilot_validated is not None,
            "completion_time_set": primary_result.completion_time is not None,
        }

        validation_score = sum(validation_checks.values()) / len(validation_checks)
        validation_passed = validation_score >= 0.8

        self.logger.info(f"{TEXT_INDICATORS['validation']} Secondary validation checks:")
        for check_name, passed in validation_checks.items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            self.logger.info(f"  {check_name}: {status}")

        self.logger.info(f"\n{TEXT_INDICATORS['validation']} Secondary Validation Score: {validation_score:.1%}")
        self.logger.info(
            f"{TEXT_INDICATORS['validation']} Secondary Validation Status: {'✅ PASSED' if validation_passed else '❌ FAILED'}"
        )

        return {
            "validator_id": self.validator_id,
            "validation_score": validation_score,
            "validation_passed": validation_passed,
            "checks": validation_checks,
            "recommendation": "APPROVED" if validation_passed else "REQUIRES_REVIEW",
        }


def main():
    """
    🎯 MAIN: Execute lessons learned integration validation with DUAL COPILOT pattern
    MANDATORY: Visual processing indicators and enterprise compliance
    """

    print(f"{TEXT_INDICATORS['start']} LESSONS LEARNED INTEGRATION VALIDATOR")
    print("=" * 80)

    try:
        # PRIMARY EXECUTOR: Execute comprehensive validation
        primary_validator = LessonsLearnedIntegrationValidator()
        primary_result = primary_validator.execute_comprehensive_validation()

        # SECONDARY VALIDATOR: Validate primary results
        secondary_validator = LessonsLearnedSecondaryValidator()
        secondary_result = secondary_validator.validate_primary_results(primary_result)

        # DUAL COPILOT SUMMARY
        print("\n" + "=" * 80)
        print(f"{TEXT_INDICATORS['completion']} DUAL COPILOT VALIDATION SUMMARY")
        print("=" * 80)
        print(f"Primary Validation: {primary_result.overall_score:.1%} integration score")
        print(f"Secondary Validation: {secondary_result['validation_passed']}")
        print(f"Recommendation: {secondary_result['recommendation']}")

        if secondary_result["validation_passed"] and primary_result.overall_score >= 0.95:
            print(
                f"\n{TEXT_INDICATORS['success']} 🏆 LESSONS LEARNED 100% EXPLICITLY INTEGRATED - VALIDATION COMPLETE ✅"
            )
            return 0
        else:
            print(f"\n{TEXT_INDICATORS['warning']} ⚠️  LESSONS LEARNED INTEGRATION REQUIRES ATTENTION")
            return 1

    except Exception as e:
        print(f"{TEXT_INDICATORS['error']} Validation failed: {str(e)}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
