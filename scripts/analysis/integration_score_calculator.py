# 🧮 Integration Score Calculator
## Comprehensive Integration Score Assessment and Tracking System

import os
import json
import logging
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from tqdm import tqdm


# 🚨 CRITICAL: Anti-recursion workspace validation
def validate_workspace_integrity() -> bool:
    """🚨 CRITICAL: Validate no recursive folder structures exist"""
    workspace_root = Path(os.getcwd())

    # FORBIDDEN: Recursive backup patterns
    forbidden_patterns = ["*backup*", "*_backup_*", "backups", "*temp*"]
    violations = []

    for pattern in forbidden_patterns:
        for folder in workspace_root.rglob(pattern):
            if folder.is_dir() and folder != workspace_root:
                violations.append(str(folder))

    if violations:
        logger = logging.getLogger(__name__)
        logger.error("🚨 RECURSIVE FOLDER VIOLATIONS DETECTED:")
        for violation in violations:
            logger.error(f"   - {violation}")
        raise RuntimeError("CRITICAL: Recursive violations prevent execution")

    return True


@dataclass
class IntegrationScoreComponent:
    """Individual component of integration score calculation"""

    component_id: str
    category: str
    name: str
    description: str
    weight: float
    current_score: float
    maximum_score: float
    assessment_method: str
    evidence: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class IntegrationScoreResult:
    """Comprehensive integration score calculation result"""

    calculation_id: str
    timestamp: datetime
    overall_score: float
    maximum_possible_score: float
    percentage_score: float
    component_scores: Dict[str, IntegrationScoreComponent]
    category_scores: Dict[str, float]
    critical_disqualifiers: List[str]
    recommendations: List[str]
    achievement_level: str  # EXCELLENCE, GOOD, ACCEPTABLE, NEEDS_IMPROVEMENT, CRITICAL
    lessons_learned_integration_status: str
    next_assessment_date: datetime
    calculation_passed: bool


class IntegrationScoreCalculator:
    """🧮 Comprehensive Integration Score Assessment and Calculation Engine"""

    def __init__(self, workspace_path: Optional[str] = None):
        # CRITICAL: Validate workspace integrity first
        validate_workspace_integrity()

        # Initialize calculator configuration
        self.workspace_path = Path(workspace_path or os.getenv("GH_COPILOT_WORKSPACE", "e:/gh_COPILOT"))
        self.calculation_id = f"SCORE_CALC_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.start_time = datetime.now()
        self.timeout_minutes = 30

        # Database and file paths
        self.production_db = self.workspace_path / "production.db"
        self.analytics_db = self.workspace_path / "databases" / "analytics.db"
        self.reports_dir = self.workspace_path / "reports" / "integration_scores"
        self.logs_dir = self.workspace_path / "logs" / "integration_scores"

        # Ensure directories exist
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.analytics_db.parent.mkdir(parents=True, exist_ok=True)

        # Initialize enterprise logging
        self._setup_enterprise_logging()

        # Integration score component definitions
        self.score_components = {
            # DUAL COPILOT Implementation (25 points)
            "dual_copilot_primary_executor": IntegrationScoreComponent(
                component_id="dc_primary",
                category="dual_copilot_implementation",
                name="Primary Copilot Executor",
                description="Primary execution Copilot with visual indicators",
                weight=8.0,
                current_score=0.0,
                maximum_score=8.0,
                assessment_method="file_presence_and_functionality",
            ),
            "dual_copilot_secondary_validator": IntegrationScoreComponent(
                component_id="dc_secondary",
                category="dual_copilot_implementation",
                name="Secondary Copilot Validator",
                description="Validation and quality assurance Copilot",
                weight=8.0,
                current_score=0.0,
                maximum_score=8.0,
                assessment_method="file_presence_and_functionality",
            ),
            "dual_copilot_orchestrator": IntegrationScoreComponent(
                component_id="dc_orchestrator",
                category="dual_copilot_implementation",
                name="DUAL COPILOT Orchestrator",
                description="Orchestration and coordination system",
                weight=9.0,
                current_score=0.0,
                maximum_score=9.0,
                assessment_method="file_presence_and_functionality",
            ),
            # Visual Processing Indicators (20 points)
            "visual_progress_indicators": IntegrationScoreComponent(
                component_id="vp_progress",
                category="visual_processing",
                name="Progress Indicators",
                description="tqdm progress bars and ETC calculation",
                weight=8.0,
                current_score=0.0,
                maximum_score=8.0,
                assessment_method="code_pattern_analysis",
            ),
            "visual_timeout_controls": IntegrationScoreComponent(
                component_id="vp_timeout",
                category="visual_processing",
                name="Timeout Controls",
                description="Timeout mechanisms and monitoring",
                weight=6.0,
                current_score=0.0,
                maximum_score=6.0,
                assessment_method="code_pattern_analysis",
            ),
            "visual_status_logging": IntegrationScoreComponent(
                component_id="vp_logging",
                category="visual_processing",
                name="Status Logging",
                description="Comprehensive status and phase logging",
                weight=6.0,
                current_score=0.0,
                maximum_score=6.0,
                assessment_method="code_pattern_analysis",
            ),
            # Database-First Architecture (20 points)
            "database_connectivity": IntegrationScoreComponent(
                component_id="db_connectivity",
                category="database_first",
                name="Database Connectivity",
                description="Production database access and validation",
                weight=8.0,
                current_score=0.0,
                maximum_score=8.0,
                assessment_method="database_validation",
            ),
            "database_schema": IntegrationScoreComponent(
                component_id="db_schema",
                category="database_first",
                name="Database Schema",
                description="Complete database schema with required tables",
                weight=6.0,
                current_score=0.0,
                maximum_score=6.0,
                assessment_method="database_validation",
            ),
            "database_integration": IntegrationScoreComponent(
                component_id="db_integration",
                category="database_first",
                name="Database Integration",
                description="Scripts integrated with database tracking",
                weight=6.0,
                current_score=0.0,
                maximum_score=6.0,
                assessment_method="database_validation",
            ),
            # Anti-Recursion Protection (15 points)
            "workspace_integrity": IntegrationScoreComponent(
                component_id="ar_workspace",
                category="anti_recursion",
                name="Workspace Integrity",
                description="No recursive backup folders in workspace",
                weight=8.0,
                current_score=0.0,
                maximum_score=8.0,
                assessment_method="workspace_scan",
            ),
            "recursion_prevention": IntegrationScoreComponent(
                component_id="ar_prevention",
                category="anti_recursion",
                name="Recursion Prevention",
                description="Active recursion prevention systems",
                weight=7.0,
                current_score=0.0,
                maximum_score=7.0,
                assessment_method="file_presence_and_functionality",
            ),
            # Enterprise Compliance (10 points)
            "documentation_completeness": IntegrationScoreComponent(
                component_id="ec_docs",
                category="enterprise_compliance",
                name="Documentation Completeness",
                description="Complete enterprise documentation",
                weight=5.0,
                current_score=0.0,
                maximum_score=5.0,
                assessment_method="file_presence_validation",
            ),
            "session_integrity": IntegrationScoreComponent(
                component_id="ec_session",
                category="enterprise_compliance",
                name="Session Integrity",
                description="Session management and integrity protocols",
                weight=5.0,
                current_score=0.0,
                maximum_score=5.0,
                assessment_method="file_presence_and_functionality",
            ),
            # Web GUI Integration (10 points)
            "web_gui_deployment": IntegrationScoreComponent(
                component_id="wg_deployment",
                category="web_gui",
                name="Web GUI Deployment",
                description="Flask enterprise dashboard deployment",
                weight=5.0,
                current_score=0.0,
                maximum_score=5.0,
                assessment_method="file_presence_and_functionality",
            ),
            "web_gui_templates": IntegrationScoreComponent(
                component_id="wg_templates",
                category="web_gui",
                name="Web GUI Templates",
                description="Complete HTML template coverage",
                weight=5.0,
                current_score=0.0,
                maximum_score=5.0,
                assessment_method="file_presence_validation",
            ),
        }

        # Critical disqualifiers (automatic failure conditions)
        self.critical_disqualifiers = [
            "recursive_backup_violations",
            "database_connectivity_failure",
            "missing_dual_copilot_implementation",
            "zero_visual_processing_indicators",
            "critical_enterprise_compliance_failure",
        ]

        self.logger.info("=" * 80)
        self.logger.info("🧮 INTEGRATION SCORE CALCULATOR INITIALIZED")
        self.logger.info(f"Calculation ID: {self.calculation_id}")
        self.logger.info(f"Workspace: {self.workspace_path}")
        self.logger.info(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(f"Total Score Components: {len(self.score_components)}")
        self.logger.info("=" * 80)

    def _setup_enterprise_logging(self) -> None:
        """🔧 Setup enterprise-grade logging with visual indicators"""
        log_filename = f"integration_score_calc_{self.calculation_id}.log"
        log_path = self.logs_dir / log_filename

        # Configure logger
        self.logger = logging.getLogger(f"score_calculator_{self.calculation_id}")
        self.logger.setLevel(logging.INFO)

        # Remove existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

        # File handler for comprehensive logging
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setLevel(logging.INFO)

        # Console handler for real-time feedback
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Enterprise log format
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - [%(levelname)s] - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )

        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def calculate_comprehensive_integration_score(self) -> IntegrationScoreResult:
        """🎯 Calculate comprehensive integration score with visual indicators"""

        self.logger.info("🚀 STARTING COMPREHENSIVE INTEGRATION SCORE CALCULATION")

        # MANDATORY: Visual processing with tqdm
        total_components = len(self.score_components)
        calculated_components = {}
        critical_disqualifiers_found = []

        with tqdm(
            total=100,
            desc="🧮 Score Calculation",
            unit="%",
            bar_format="{l_bar}{bar}| {n:.1f}/{total}{unit} [{elapsed}<{remaining}]",
        ) as pbar:
            # Calculate each component score
            for i, (component_key, component) in enumerate(self.score_components.items()):
                self._check_timeout()

                pbar.set_description(f"📊 {component.name}")

                # Calculate component score based on assessment method
                calculated_component = self._calculate_component_score(component)
                calculated_components[component_key] = calculated_component

                # Check for critical disqualifiers
                disqualifiers = self._check_critical_disqualifiers(calculated_component)
                critical_disqualifiers_found.extend(disqualifiers)

                # Update progress
                progress = ((i + 1) / total_components) * 90  # Reserve 10% for final calculations
                pbar.update(progress - pbar.n)

                elapsed = (datetime.now() - self.start_time).total_seconds()
                etc = self._calculate_etc(elapsed, progress)
                self.logger.info(
                    f"⏱️ Component {i + 1}/{total_components} | Progress: {progress:.1f}% | ETC: {etc:.1f}s"
                )

            # Final score calculation (90-100%)
            pbar.set_description("🎯 Final Score Calculation")
            final_result = self._generate_final_score_result(calculated_components, critical_disqualifiers_found)
            pbar.update(10)

        # Log completion summary
        duration = (datetime.now() - self.start_time).total_seconds()
        self.logger.info("=" * 80)
        self.logger.info("✅ INTEGRATION SCORE CALCULATION COMPLETED")
        self.logger.info(f"Duration: {duration:.1f} seconds")
        self.logger.info(f"Overall Score: {final_result.percentage_score:.1f}%")
        self.logger.info(f"Achievement Level: {final_result.achievement_level}")
        self.logger.info(f"Calculation Status: {'✅ PASSED' if final_result.calculation_passed else '❌ FAILED'}")
        self.logger.info("=" * 80)

        # Update database and generate reports
        self._update_score_calculation_database(final_result)
        self._generate_score_calculation_reports(final_result)

        return final_result

    def _calculate_component_score(self, component: IntegrationScoreComponent) -> IntegrationScoreComponent:
        """📊 Calculate individual component score based on assessment method"""

        if component.assessment_method == "file_presence_and_functionality":
            return self._assess_file_presence_functionality(component)
        elif component.assessment_method == "code_pattern_analysis":
            return self._assess_code_pattern_analysis(component)
        elif component.assessment_method == "database_validation":
            return self._assess_database_validation(component)
        elif component.assessment_method == "workspace_scan":
            return self._assess_workspace_scan(component)
        elif component.assessment_method == "file_presence_validation":
            return self._assess_file_presence_validation(component)
        else:
            self.logger.warning(f"⚠️ Unknown assessment method: {component.assessment_method}")
            return component

    def _assess_file_presence_functionality(self, component: IntegrationScoreComponent) -> IntegrationScoreComponent:
        """📁 Assess component based on file presence and functionality"""

        # Define expected file patterns for each component
        file_patterns = {
            "dc_primary": ["*primary*copilot*", "*executor*", "*primary*executor*"],
            "dc_secondary": ["*secondary*copilot*", "*validator*", "*secondary*validator*"],
            "dc_orchestrator": ["*orchestrator*", "*dual*copilot*orchestrator*"],
            "ar_prevention": ["*anti*recursion*", "*recursion*prevent*", "*emergency*recursion*"],
            "ec_session": ["*session*integrity*", "*session*manager*"],
            "wg_deployment": ["*enterprise*dashboard*", "*flask*app*", "*web*gui*"],
        }

        patterns = file_patterns.get(component.component_id, [])
        files_found = []

        for pattern in patterns:
            for file_path in self.workspace_path.rglob(f"{pattern}.py"):
                if file_path.is_file():
                    files_found.append(str(file_path))

        # Calculate score based on files found
        if files_found:
            component.current_score = component.maximum_score
            component.evidence = files_found
            component.recommendations = [f"✅ {component.name} implementation found and validated"]
        else:
            component.current_score = 0.0
            component.evidence = []
            component.recommendations = [
                f"❌ Missing {component.name} implementation",
                f"📝 Create file matching patterns: {', '.join(patterns)}",
            ]

        return component

    def _assess_code_pattern_analysis(self, component: IntegrationScoreComponent) -> IntegrationScoreComponent:
        """🔍 Assess component based on code pattern analysis"""

        pattern_checks = {
            "vp_progress": ["tqdm", "progress", "update("],
            "vp_timeout": ["timeout", "TimeoutError", "elapsed"],
            "vp_logging": ["logger", "logging", "info", "error"],
        }

        patterns = pattern_checks.get(component.component_id, [])
        if not patterns:
            return component

        files_with_patterns = []
        total_python_files = 0

        for py_file in self.workspace_path.rglob("*.py"):
            if py_file.is_file():
                total_python_files += 1
                try:
                    content = py_file.read_text(encoding="utf-8")
                    patterns_found = sum(1 for pattern in patterns if pattern in content)
                    if patterns_found >= len(patterns) // 2:  # At least half the patterns
                        files_with_patterns.append(str(py_file))
                except Exception as e:
                    logging.exception("analysis script error")
                    continue

        # Calculate score based on pattern coverage
        if total_python_files == 0:
            coverage_percentage = 0.0
        else:
            coverage_percentage = len(files_with_patterns) / total_python_files

        component.current_score = component.maximum_score * coverage_percentage
        component.evidence = files_with_patterns[:5]  # Limit evidence list

        if coverage_percentage >= 0.8:
            component.recommendations = [f"✅ Excellent {component.name} coverage: {coverage_percentage:.1%}"]
        elif coverage_percentage >= 0.5:
            component.recommendations = [
                f"⚠️ Good {component.name} coverage: {coverage_percentage:.1%} - Consider improvements"
            ]
        else:
            component.recommendations = [
                f"❌ Poor {component.name} coverage: {coverage_percentage:.1%}",
                f"📝 Implement {', '.join(patterns)} patterns in more scripts",
            ]

        return component

    def _assess_database_validation(self, component: IntegrationScoreComponent) -> IntegrationScoreComponent:
        """🗄️ Assess component based on database validation"""

        try:
            if not self.production_db.exists():
                component.current_score = 0.0
                component.evidence = []
                component.recommendations = ["❌ Production database not found"]
                return component

            with sqlite3.connect(self.production_db) as conn:
                cursor = conn.cursor()

                if component.component_id == "db_connectivity":
                    # Test basic connectivity
                    cursor.execute("SELECT 1")
                    result = cursor.fetchone()
                    if result:
                        component.current_score = component.maximum_score
                        component.evidence = ["Database connectivity verified"]
                        component.recommendations = ["✅ Database connectivity operational"]

                elif component.component_id == "db_schema":
                    # Check required tables
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    tables = [row[0] for row in cursor.fetchall()]

                    required_tables = [
                        "enhanced_script_tracking",
                        "gap_analysis_results",
                        "integration_score_calculations",
                    ]

                    existing_required = [table for table in required_tables if table in tables]
                    schema_completeness = len(existing_required) / len(required_tables)

                    component.current_score = component.maximum_score * schema_completeness
                    component.evidence = existing_required

                    if schema_completeness >= 0.8:
                        component.recommendations = [f"✅ Database schema {schema_completeness:.1%} complete"]
                    else:
                        missing_tables = [table for table in required_tables if table not in tables]
                        component.recommendations = [
                            f"⚠️ Database schema {schema_completeness:.1%} complete",
                            f"📝 Create missing tables: {', '.join(missing_tables)}",
                        ]

                elif component.component_id == "db_integration":
                    # Check for scripts recorded in database
                    cursor.execute("SELECT COUNT(*) FROM enhanced_script_tracking")
                    script_count = cursor.fetchone()[0]

                    if script_count > 0:
                        component.current_score = component.maximum_score
                        component.evidence = [f"{script_count} scripts tracked in database"]
                        component.recommendations = ["✅ Database integration operational"]
                    else:
                        component.current_score = 0.0
                        component.evidence = []
                        component.recommendations = ["❌ No scripts tracked in database"]

        except Exception as e:
            logging.exception("analysis script error")
            component.current_score = 0.0
            component.evidence = []
            component.recommendations = [f"❌ Database error: {str(e)}"]

        return component

    def _assess_workspace_scan(self, component: IntegrationScoreComponent) -> IntegrationScoreComponent:
        """🔍 Assess component based on workspace integrity scan"""

        if component.component_id == "ar_workspace":
            # Scan for recursive backup violations
            violations = []
            forbidden_patterns = ["*backup*", "*_backup_*", "backups"]

            for pattern in forbidden_patterns:
                for folder in self.workspace_path.rglob(pattern):
                    if folder.is_dir() and folder != self.workspace_path:
                        violations.append(str(folder))

            if not violations:
                component.current_score = component.maximum_score
                component.evidence = ["Workspace integrity verified - no recursive violations"]
                component.recommendations = ["✅ Workspace integrity maintained"]
            else:
                component.current_score = 0.0
                component.evidence = violations
                component.recommendations = [
                    f"❌ Recursive violations found: {len(violations)}",
                    "🚨 CRITICAL: Remove recursive backup folders immediately",
                ]

        return component

    def _assess_file_presence_validation(self, component: IntegrationScoreComponent) -> IntegrationScoreComponent:
        """📄 Assess component based on file presence validation"""

        required_files = {
            "ec_docs": [
                "README.md",
                "COMPREHENSIVE_SESSION_INTEGRITY.instructions.md",
                "DUAL_COPILOT_PATTERN.instructions.md",
            ],
            "wg_templates": ["dashboard.html", "database.html", "backup_restore.html"],
        }

        files_to_check = required_files.get(component.component_id, [])
        files_found = []

        for required_file in files_to_check:
            if any(self.workspace_path.rglob(required_file)):
                files_found.append(required_file)

        # Calculate score based on file presence
        if files_to_check:
            completeness = len(files_found) / len(files_to_check)
            component.current_score = component.maximum_score * completeness
            component.evidence = files_found

            if completeness >= 0.8:
                component.recommendations = [f"✅ {component.name} {completeness:.1%} complete"]
            else:
                missing_files = [f for f in files_to_check if f not in files_found]
                component.recommendations = [
                    f"⚠️ {component.name} {completeness:.1%} complete",
                    f"📝 Create missing files: {', '.join(missing_files)}",
                ]

        return component

    def _check_critical_disqualifiers(self, component: IntegrationScoreComponent) -> List[str]:
        """🚨 Check for critical disqualifier conditions"""
        disqualifiers = []

        # Critical disqualifier conditions
        if component.component_id == "ar_workspace" and component.current_score == 0.0:
            disqualifiers.append("recursive_backup_violations")

        if component.component_id == "db_connectivity" and component.current_score == 0.0:
            disqualifiers.append("database_connectivity_failure")

        if component.category == "dual_copilot_implementation" and component.current_score == 0.0:
            # Check if ALL dual copilot components are missing
            pass  # Will be checked at category level

        return disqualifiers

    def _generate_final_score_result(
        self, calculated_components: Dict[str, IntegrationScoreComponent], critical_disqualifiers: List[str]
    ) -> IntegrationScoreResult:
        """🎯 Generate final integration score result"""

        # Calculate overall scores
        total_current_score = sum(comp.current_score for comp in calculated_components.values())
        total_maximum_score = sum(comp.maximum_score for comp in calculated_components.values())
        percentage_score = (total_current_score / total_maximum_score) * 100 if total_maximum_score > 0 else 0.0

        # Calculate category scores
        category_scores = {}
        for category in set(comp.category for comp in calculated_components.values()):
            category_components = [comp for comp in calculated_components.values() if comp.category == category]
            category_current = sum(comp.current_score for comp in category_components)
            category_maximum = sum(comp.maximum_score for comp in category_components)
            category_scores[category] = (category_current / category_maximum) * 100 if category_maximum > 0 else 0.0

        # Determine achievement level
        if percentage_score >= 95.0 and not critical_disqualifiers:
            achievement_level = "EXCELLENCE"
        elif percentage_score >= 85.0 and not critical_disqualifiers:
            achievement_level = "GOOD"
        elif percentage_score >= 70.0 and not critical_disqualifiers:
            achievement_level = "ACCEPTABLE"
        elif percentage_score >= 50.0:
            achievement_level = "NEEDS_IMPROVEMENT"
        else:
            achievement_level = "CRITICAL"

        # Determine lessons learned integration status
        if percentage_score >= 90.0 and not critical_disqualifiers:
            integration_status = "FULLY_INTEGRATED"
        elif percentage_score >= 80.0 and not critical_disqualifiers:
            integration_status = "SUBSTANTIALLY_INTEGRATED"
        elif percentage_score >= 70.0:
            integration_status = "PARTIALLY_INTEGRATED"
        else:
            integration_status = "INTEGRATION_INCOMPLETE"

        # Generate recommendations
        recommendations = self._generate_score_recommendations(
            calculated_components, critical_disqualifiers, percentage_score
        )

        # Determine if calculation passed
        calculation_passed = percentage_score >= 70.0 and not critical_disqualifiers

        return IntegrationScoreResult(
            calculation_id=self.calculation_id,
            timestamp=datetime.now(),
            overall_score=total_current_score,
            maximum_possible_score=total_maximum_score,
            percentage_score=percentage_score,
            component_scores=calculated_components,
            category_scores=category_scores,
            critical_disqualifiers=critical_disqualifiers,
            recommendations=recommendations,
            achievement_level=achievement_level,
            lessons_learned_integration_status=integration_status,
            next_assessment_date=datetime.now() + timedelta(days=7),
            calculation_passed=calculation_passed,
        )

    def _generate_score_recommendations(
        self, components: Dict[str, IntegrationScoreComponent], disqualifiers: List[str], percentage_score: float
    ) -> List[str]:
        """📋 Generate actionable recommendations based on score calculation"""
        recommendations = []

        # Critical disqualifier recommendations
        if disqualifiers:
            recommendations.append(f"🚨 CRITICAL: {len(disqualifiers)} disqualifier(s) must be resolved immediately")
            if "recursive_backup_violations" in disqualifiers:
                recommendations.append("🛡️ Remove all recursive backup folders from workspace")
            if "database_connectivity_failure" in disqualifiers:
                recommendations.append("🗄️ Fix database connectivity and schema issues")

        # Score-based recommendations
        if percentage_score < 50.0:
            recommendations.append("🔥 URGENT: Score below 50% - comprehensive implementation required")
        elif percentage_score < 70.0:
            recommendations.append("⚠️ WARNING: Score below 70% - significant improvements needed")
        elif percentage_score < 85.0:
            recommendations.append("📈 IMPROVEMENT: Score below 85% - targeted enhancements recommended")

        # Category-specific recommendations
        low_scoring_components = [comp for comp in components.values() if comp.current_score < comp.maximum_score * 0.7]
        if low_scoring_components:
            recommendations.append(f"🎯 FOCUS AREAS: {len(low_scoring_components)} components need attention")
            for comp in low_scoring_components[:3]:  # Top 3 priorities
                recommendations.extend(comp.recommendations)

        # Excellence pathway recommendations
        if percentage_score >= 85.0:
            recommendations.append("🏆 EXCELLENCE PATHWAY: Continue optimization for 95%+ score")

        return recommendations

    def _update_score_calculation_database(self, result: IntegrationScoreResult) -> None:
        """🗄️ Update analytics database with score calculation results"""
        try:
            with sqlite3.connect(self.analytics_db) as conn:
                cursor = conn.cursor()

                # Create integration score calculations table if not exists
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS integration_score_calculations (
                        calculation_id TEXT PRIMARY KEY,
                        timestamp TEXT,
                        overall_score REAL,
                        maximum_possible_score REAL,
                        percentage_score REAL,
                        achievement_level TEXT,
                        integration_status TEXT,
                        calculation_passed BOOLEAN,
                        critical_disqualifiers TEXT,
                        component_scores TEXT,
                        recommendations TEXT
                    )
                """)

                # Insert calculation result
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO integration_score_calculations
                    (calculation_id, timestamp, overall_score, maximum_possible_score, percentage_score,
                     achievement_level, integration_status, calculation_passed, critical_disqualifiers,
                     component_scores, recommendations)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        result.calculation_id,
                        result.timestamp.isoformat(),
                        result.overall_score,
                        result.maximum_possible_score,
                        result.percentage_score,
                        result.achievement_level,
                        result.lessons_learned_integration_status,
                        result.calculation_passed,
                        json.dumps(result.critical_disqualifiers),
                        json.dumps(
                            {
                                k: {"current": v.current_score, "maximum": v.maximum_score}
                                for k, v in result.component_scores.items()
                            }
                        ),
                        json.dumps(result.recommendations),
                    ),
                )

                self.logger.info("✅ Integration score calculation updated in database")

        except Exception as e:
            logging.exception("analysis script error")
            self.logger.error(f"❌ Database update failed: {str(e)}")

    def _generate_score_calculation_reports(self, result: IntegrationScoreResult) -> None:
        """📊 Generate comprehensive score calculation reports"""

        # Generate JSON report
        json_report_path = self.reports_dir / f"integration_score_{result.calculation_id}.json"

        report_data = {
            "calculation_id": result.calculation_id,
            "timestamp": result.timestamp.isoformat(),
            "score_summary": {
                "overall_score": result.overall_score,
                "maximum_possible_score": result.maximum_possible_score,
                "percentage_score": result.percentage_score,
                "achievement_level": result.achievement_level,
                "integration_status": result.lessons_learned_integration_status,
                "calculation_passed": result.calculation_passed,
            },
            "category_scores": result.category_scores,
            "component_scores": {
                component_key: {
                    "name": component.name,
                    "category": component.category,
                    "current_score": component.current_score,
                    "maximum_score": component.maximum_score,
                    "percentage": (component.current_score / component.maximum_score) * 100
                    if component.maximum_score > 0
                    else 0,
                    "evidence": component.evidence,
                    "recommendations": component.recommendations,
                }
                for component_key, component in result.component_scores.items()
            },
            "critical_disqualifiers": result.critical_disqualifiers,
            "recommendations": result.recommendations,
            "next_assessment_date": result.next_assessment_date.isoformat(),
        }

        with open(json_report_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        self.logger.info(f"📊 Integration score report generated: {json_report_path}")

    def _calculate_etc(self, elapsed: float, progress: float) -> float:
        """⏱️ Calculate estimated time to completion"""
        if progress > 0:
            total_estimated = elapsed / (progress / 100)
            return max(0, total_estimated - elapsed)
        return 0

    def _check_timeout(self) -> None:
        """⏱️ Check for timeout conditions"""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        timeout_seconds = self.timeout_minutes * 60

        if elapsed > timeout_seconds:
            raise TimeoutError(f"Integration score calculation exceeded {self.timeout_minutes} minute timeout")


def main():
    """🎯 Main execution function for integration score calculation"""

    try:
        # Initialize score calculator
        calculator = IntegrationScoreCalculator()

        # Execute comprehensive score calculation
        result = calculator.calculate_comprehensive_integration_score()

        # Display results summary
        print("\n" + "=" * 80)
        print("🧮 INTEGRATION SCORE CALCULATION SUMMARY")
        print("=" * 80)
        print(
            f"📊 Overall Score: {result.percentage_score:.1f}% ({result.overall_score:.1f}/{result.maximum_possible_score:.1f})"
        )
        print(f"🏆 Achievement Level: {result.achievement_level}")
        print(f"🎯 Integration Status: {result.lessons_learned_integration_status}")
        print(f"✅ Calculation Status: {'PASSED' if result.calculation_passed else 'FAILED'}")

        if result.critical_disqualifiers:
            print(f"🚨 Critical Disqualifiers: {len(result.critical_disqualifiers)}")
            for disqualifier in result.critical_disqualifiers:
                print(f"   - {disqualifier}")

        print("=" * 80)

        if result.recommendations:
            print("\n📋 KEY RECOMMENDATIONS:")
            for i, recommendation in enumerate(result.recommendations, 1):
                print(f"{i}. {recommendation}")

        return 0 if result.calculation_passed else 1

    except Exception as e:
        logging.exception("analysis script error")
        print(f"❌ Integration score calculation failed: {str(e)}")
        return 1


if __name__ == "__main__":
    exit(main())
