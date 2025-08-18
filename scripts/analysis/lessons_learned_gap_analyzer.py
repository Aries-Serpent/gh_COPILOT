# 📊 Lessons Learned Gap Analyzer
# Intelligent Gap Detection and Remediation Framework
#
# 🎯 LESSONS LEARNED GAP ANALYZER MANDATE
#
# ABSOLUTE DATABASE-FIRST GAP ANALYSIS: This script provides systematic analysis
# of lessons learned integration gaps, leveraging production.db for intelligent
# gap detection and automated remediation recommendations.

import os
import json
import logging
import sqlite3
from datetime import datetime
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from tqdm import tqdm
import uuid

from template_engine.learning_templates import (
    get_lesson_templates,
    get_dataset_sources,
)
from utils.lessons_learned_integrator import store_lesson


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
class LessonsLearnedGap:
    """Data structure for lessons learned gaps"""

    gap_id: str
    category: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    description: str
    current_status: str
    target_status: str
    remediation_actions: List[str] = field(default_factory=list)
    integration_score_impact: float = 0.0
    priority_score: int = 0
    estimated_effort_hours: float = 0.0


@dataclass
class GapAnalysisResult:
    """Comprehensive gap analysis result container"""

    analysis_id: str
    timestamp: datetime
    total_gaps_found: int
    critical_gaps: int
    high_priority_gaps: int
    medium_priority_gaps: int
    low_priority_gaps: int
    overall_integration_score_impact: float
    gaps_by_category: Dict[str, List[LessonsLearnedGap]]
    remediation_roadmap: List[Dict[str, Any]]
    dataset_coverage_ok: bool
    analysis_passed: bool
    recommendations: List[str] = field(default_factory=list)


class LessonsLearnedGapAnalyzer:
    """🔍 Intelligent Lessons Learned Gap Detection and Analysis Engine"""

    def __init__(self, workspace_path: Optional[str] = None):
        # CRITICAL: Validate workspace integrity first
        validate_workspace_integrity()

        # Initialize analyzer configuration
        self.workspace_path = Path(workspace_path or os.getenv("GH_COPILOT_WORKSPACE", "e:/gh_COPILOT"))
        self.analysis_id = f"GAP_ANALYSIS_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.start_time = datetime.now()
        self.timeout_minutes = 30

        # Database and file paths
        self.production_db = self.workspace_path / "production.db"
        self.dataset_sources = get_dataset_sources(str(self.workspace_path))
        self.reports_dir = self.workspace_path / "reports" / "gap_analysis"
        self.logs_dir = self.workspace_path / "logs" / "gap_analysis"

        # Ensure directories exist
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        # Initialize enterprise logging
        self._setup_enterprise_logging()

        # Gap analysis configuration
        self.gap_categories = {
            "dual_copilot_implementation": {
                "weight": 25.0,
                "critical_files": [
                    "enterprise_dual_copilot_validator.py",
                    "comprehensive_dual_copilot_orchestrator.py",
                    "primary_copilot_executor.py",
                ],
            },
            "visual_processing_indicators": {
                "weight": 20.0,
                "critical_files": [
                    "enterprise_visual_processing_system.py",
                    "visual_indicator_compliance_checker.py",
                    "progress_monitoring_system.py",
                ],
            },
            "database_first_architecture": {
                "weight": 20.0,
                "critical_files": [
                    "production.db",
                    "database_first_query_engine.py",
                    "template_intelligence_platform.py",
                ],
            },
            "anti_recursion_protection": {
                "weight": 15.0,
                "critical_files": [
                    "anti_recursion_validator.py",
                    "workspace_integrity_monitor.py",
                    "emergency_recursion_prevention.py",
                ],
            },
            "enterprise_compliance": {
                "weight": 10.0,
                "critical_files": [
                    "enterprise_compliance_validator.py",
                    "session_integrity_manager.py",
                    "comprehensive_quality_assurance.py",
                ],
            },
            "web_gui_integration": {
                "weight": 10.0,
                "critical_files": [
                    "enterprise_dashboard.py",
                    "web_gui_deployment_manager.py",
                    "flask_enterprise_integration.py",
                ],
            },
        }

        self.logger.info("=" * 80)
        self.logger.info("🔍 LESSONS LEARNED GAP ANALYZER INITIALIZED")
        self.logger.info(f"Analysis ID: {self.analysis_id}")
        self.logger.info(f"Workspace: {self.workspace_path}")
        self.logger.info(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info("=" * 80)

    def _setup_enterprise_logging(self) -> None:
        """🔧 Setup enterprise-grade logging with visual indicators"""
        log_filename = f"gap_analysis_{self.analysis_id}.log"
        log_path = self.logs_dir / log_filename

        # Configure logger
        self.logger = logging.getLogger(f"gap_analyzer_{self.analysis_id}")
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

    def _dataset_lesson_keys(self) -> set[str]:
        """Collect lesson identifiers from available dataset sources."""
        lessons: set[str] = set()
        for db in self.dataset_sources:
            if not db.exists():
                continue
            try:
                with sqlite3.connect(db) as conn:
                    try:
                        cur = conn.execute(
                            "SELECT lesson_name FROM pattern_assets WHERE lesson_name IS NOT NULL"
                        )
                        lessons.update(row[0] for row in cur.fetchall())
                    except sqlite3.Error:
                        pass
                    try:
                        cur = conn.execute("SELECT lesson_key FROM lessons_learned")
                        lessons.update(row[0] for row in cur.fetchall())
                    except sqlite3.Error:
                        pass
            except sqlite3.Error:
                continue
        return lessons

    def validate_dataset_coverage(self) -> bool:
        """Verify all lesson templates are represented in the dataset."""
        expected = set(get_lesson_templates().keys())
        available = self._dataset_lesson_keys()
        missing = expected - available
        if missing:
            self.logger.warning("Missing lessons in dataset: %s", ", ".join(sorted(missing)))
            return False
        return True

    def execute_comprehensive_gap_analysis(self) -> GapAnalysisResult:
        """🎯 Execute comprehensive lessons learned gap analysis with visual indicators"""

        self.logger.info("🚀 STARTING COMPREHENSIVE GAP ANALYSIS")

        coverage_ok = self.validate_dataset_coverage()

        # MANDATORY: Visual processing with tqdm
        gaps_found = []

        with tqdm(
            total=100,
            desc="🔍 Gap Analysis",
            unit="%",
            bar_format="{l_bar}{bar}| {n:.1f}/{total}{unit} [{elapsed}<{remaining}]",
        ) as pbar:
            # Phase 1: Database connectivity validation (0-10%)
            pbar.set_description("🗄️ Database Connectivity")
            self._check_timeout()
            database_gaps = self._analyze_database_connectivity_gaps()
            gaps_found.extend(database_gaps)
            pbar.update(16.7)

            # Phase 2: DUAL COPILOT implementation analysis (10-35%)
            pbar.set_description("🤖 DUAL COPILOT Analysis")
            self._check_timeout()
            dual_copilot_gaps = self._analyze_dual_copilot_gaps()
            gaps_found.extend(dual_copilot_gaps)
            pbar.update(16.7)

            # Phase 3: Visual processing indicators (35-55%)
            pbar.set_description("🎬 Visual Processing")
            self._check_timeout()
            visual_gaps = self._analyze_visual_processing_gaps()
            gaps_found.extend(visual_gaps)
            pbar.update(16.7)

            # Phase 4: Anti-recursion protection (55-70%)
            pbar.set_description("🛡️ Anti-Recursion")
            self._check_timeout()
            recursion_gaps = self._analyze_anti_recursion_gaps()
            gaps_found.extend(recursion_gaps)
            pbar.update(16.7)

            # Phase 5: Enterprise compliance (70-85%)
            pbar.set_description("🏢 Enterprise Compliance")
            self._check_timeout()
            compliance_gaps = self._analyze_enterprise_compliance_gaps()
            gaps_found.extend(compliance_gaps)
            pbar.update(16.6)

            # Phase 6: Remediation roadmap generation (85-100%)
            pbar.set_description("🗺️ Remediation Roadmap")
            self._check_timeout()
            analysis_result = self._generate_comprehensive_analysis_result(gaps_found)
            analysis_result.dataset_coverage_ok = coverage_ok
            analysis_result.analysis_passed = analysis_result.analysis_passed and coverage_ok
            pbar.update(16.6)

        # Log completion summary
        duration = (datetime.now() - self.start_time).total_seconds()
        self.logger.info("=" * 80)
        self.logger.info("✅ GAP ANALYSIS COMPLETED")
        self.logger.info(f"Duration: {duration:.1f} seconds")
        self.logger.info(f"Total Gaps Found: {analysis_result.total_gaps_found}")
        self.logger.info(f"Critical Gaps: {analysis_result.critical_gaps}")
        self.logger.info(f"Analysis Status: {'✅ PASSED' if analysis_result.analysis_passed else '❌ FAILED'}")
        self.logger.info("=" * 80)

        # Update database and generate reports
        self._update_gap_analysis_database(analysis_result)
        self._generate_gap_analysis_reports(analysis_result)

        return analysis_result

    def _analyze_database_connectivity_gaps(self) -> List[LessonsLearnedGap]:
        """🗄️ Analyze database connectivity and integration gaps"""
        gaps = []

        # Check production database existence
        if not self.production_db.exists():
            gaps.append(
                LessonsLearnedGap(
                    gap_id=str(uuid.uuid4())[:8],
                    category="database_first_architecture",
                    severity="CRITICAL",
                    description="Production database (production.db) not found",
                    current_status="MISSING",
                    target_status="OPERATIONAL",
                    remediation_actions=[
                        "Create production.db with proper schema",
                        "Initialize database with enterprise tracking tables",
                        "Implement database connectivity validation",
                    ],
                    integration_score_impact=-15.0,
                    priority_score=100,
                    estimated_effort_hours=4.0,
                )
            )

        # Check database schema validation
        try:
            with sqlite3.connect(self.production_db) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()

                required_tables = ["enhanced_script_tracking", "gap_analysis_results", "lessons_learned_tracking"]

                existing_tables = [table[0] for table in tables]
                missing_tables = [table for table in required_tables if table not in existing_tables]

                if missing_tables:
                    gaps.append(
                        LessonsLearnedGap(
                            gap_id=str(uuid.uuid4())[:8],
                            category="database_first_architecture",
                            severity="HIGH",
                            description=f"Missing database tables: {', '.join(missing_tables)}",
                            current_status="INCOMPLETE_SCHEMA",
                            target_status="COMPLETE_SCHEMA",
                            remediation_actions=[f"Create missing table: {table}" for table in missing_tables],
                            integration_score_impact=-5.0,
                            priority_score=80,
                            estimated_effort_hours=2.0,
                        )
                    )

        except (sqlite3.Error, OSError):
            logging.exception("analysis script error")
            raise

        return gaps

    def _analyze_dual_copilot_gaps(self) -> List[LessonsLearnedGap]:
        """🤖 Analyze DUAL COPILOT implementation gaps"""
        gaps = []
        category = "dual_copilot_implementation"
        critical_files = self.gap_categories[category]["critical_files"]

        missing_files = []
        for file_pattern in critical_files:
            found = False
            for script_path in self.workspace_path.rglob(f"*{file_pattern}*"):
                if script_path.is_file():
                    found = True
                    break
            if not found:
                missing_files.append(file_pattern)

        if missing_files:
            gaps.append(
                LessonsLearnedGap(
                    gap_id=str(uuid.uuid4())[:8],
                    category=category,
                    severity="CRITICAL",
                    description=f"Missing DUAL COPILOT files: {', '.join(missing_files)}",
                    current_status="INCOMPLETE_IMPLEMENTATION",
                    target_status="COMPLETE_DUAL_COPILOT",
                    remediation_actions=[f"Implement {file}" for file in missing_files],
                    integration_score_impact=-12.0,
                    priority_score=95,
                    estimated_effort_hours=8.0,
                )
            )

        return gaps

    def _analyze_visual_processing_gaps(self) -> List[LessonsLearnedGap]:
        """🎬 Analyze visual processing indicators gaps"""
        gaps = []
        category = "visual_processing_indicators"

        # Check for visual processing compliance
        visual_indicators_found = False
        for script_path in self.workspace_path.rglob("*.py"):
            try:
                content = script_path.read_text(encoding="utf-8")
                if "tqdm" in content and "progress" in content.lower():
                    visual_indicators_found = True
                    break
            except (OSError, UnicodeDecodeError):
                logging.exception("analysis script error")
                continue

        if not visual_indicators_found:
            gaps.append(
                LessonsLearnedGap(
                    gap_id=str(uuid.uuid4())[:8],
                    category=category,
                    severity="HIGH",
                    description="Visual processing indicators not implemented across scripts",
                    current_status="NO_VISUAL_INDICATORS",
                    target_status="VISUAL_INDICATORS_ACTIVE",
                    remediation_actions=[
                        "Implement tqdm progress bars in all scripts",
                        "Add ETC calculation for all operations",
                        "Include timeout controls and status logging",
                    ],
                    integration_score_impact=-8.0,
                    priority_score=75,
                    estimated_effort_hours=6.0,
                )
            )

        return gaps

    def _analyze_anti_recursion_gaps(self) -> List[LessonsLearnedGap]:
        """🛡️ Analyze anti-recursion protection gaps"""
        gaps = []
        category = "anti_recursion_protection"

        # Check for backup folders in workspace (FORBIDDEN)
        workspace_violations = []
        for backup_pattern in ["*backup*", "*_backup_*", "backups"]:
            for violation in self.workspace_path.rglob(backup_pattern):
                if violation.is_dir() and violation != self.workspace_path:
                    workspace_violations.append(str(violation))

        if workspace_violations:
            gaps.append(
                LessonsLearnedGap(
                    gap_id=str(uuid.uuid4())[:8],
                    category=category,
                    severity="CRITICAL",
                    description=f"Recursive backup violations: {', '.join(workspace_violations)}",
                    current_status="RECURSIVE_VIOLATIONS",
                    target_status="CLEAN_WORKSPACE",
                    remediation_actions=[f"Remove recursive folder: {violation}" for violation in workspace_violations],
                    integration_score_impact=-20.0,
                    priority_score=100,
                    estimated_effort_hours=1.0,
                )
            )

        return gaps

    def _analyze_enterprise_compliance_gaps(self) -> List[LessonsLearnedGap]:
        """🏢 Analyze enterprise compliance gaps"""
        gaps = []
        category = "enterprise_compliance"

        # Check for enterprise documentation
        required_docs = [
            "README.md",
            "COMPREHENSIVE_SESSION_INTEGRITY.instructions.md",
            "DUAL_COPILOT_PATTERN.instructions.md",
        ]

        missing_docs = []
        for doc in required_docs:
            if not any(self.workspace_path.rglob(doc)):
                missing_docs.append(doc)

        if missing_docs:
            gaps.append(
                LessonsLearnedGap(
                    gap_id=str(uuid.uuid4())[:8],
                    category=category,
                    severity="MEDIUM",
                    description=f"Missing enterprise documentation: {', '.join(missing_docs)}",
                    current_status="INCOMPLETE_DOCUMENTATION",
                    target_status="COMPLETE_DOCUMENTATION",
                    remediation_actions=[f"Create documentation: {doc}" for doc in missing_docs],
                    integration_score_impact=-3.0,
                    priority_score=50,
                    estimated_effort_hours=4.0,
                )
            )

        return gaps

    def _generate_comprehensive_analysis_result(self, gaps: List[LessonsLearnedGap]) -> GapAnalysisResult:
        """📊 Generate comprehensive gap analysis result"""

        # Categorize gaps by severity
        critical_gaps = [gap for gap in gaps if gap.severity == "CRITICAL"]
        high_gaps = [gap for gap in gaps if gap.severity == "HIGH"]
        medium_gaps = [gap for gap in gaps if gap.severity == "MEDIUM"]
        low_gaps = [gap for gap in gaps if gap.severity == "LOW"]

        # Calculate overall integration score impact
        total_impact = sum(gap.integration_score_impact for gap in gaps)

        # Group gaps by category
        gaps_by_category = {}
        for gap in gaps:
            if gap.category not in gaps_by_category:
                gaps_by_category[gap.category] = []
            gaps_by_category[gap.category].append(gap)

        # Generate remediation roadmap
        remediation_roadmap = self._generate_remediation_roadmap(gaps)

        # Generate recommendations
        recommendations = self._generate_actionable_recommendations(gaps)

        # Determine if analysis passed (no critical gaps, minimal negative impact)
        analysis_passed = len(critical_gaps) == 0 and total_impact >= -10.0

        return GapAnalysisResult(
            analysis_id=self.analysis_id,
            timestamp=datetime.now(),
            total_gaps_found=len(gaps),
            critical_gaps=len(critical_gaps),
            high_priority_gaps=len(high_gaps),
            medium_priority_gaps=len(medium_gaps),
            low_priority_gaps=len(low_gaps),
            overall_integration_score_impact=total_impact,
            gaps_by_category=gaps_by_category,
            remediation_roadmap=remediation_roadmap,
            dataset_coverage_ok=True,
            analysis_passed=analysis_passed,
            recommendations=recommendations,
        )

    def _generate_remediation_roadmap(self, gaps: List[LessonsLearnedGap]) -> List[Dict[str, Any]]:
        """🗺️ Generate prioritized remediation roadmap"""
        # Sort gaps by priority score (descending)
        sorted_gaps = sorted(gaps, key=lambda g: g.priority_score, reverse=True)

        roadmap = []
        for i, gap in enumerate(sorted_gaps):
            roadmap.append(
                {
                    "phase": i + 1,
                    "gap_id": gap.gap_id,
                    "category": gap.category,
                    "severity": gap.severity,
                    "description": gap.description,
                    "actions": gap.remediation_actions,
                    "estimated_hours": gap.estimated_effort_hours,
                    "integration_impact": gap.integration_score_impact,
                    "priority": gap.priority_score,
                }
            )

        return roadmap

    def _generate_actionable_recommendations(self, gaps: List[LessonsLearnedGap]) -> List[str]:
        """📋 Generate actionable recommendations based on gap analysis"""
        recommendations = []

        critical_gaps = [gap for gap in gaps if gap.severity == "CRITICAL"]
        if critical_gaps:
            recommendations.append(
                f"🚨 IMMEDIATE ACTION REQUIRED: {len(critical_gaps)} critical gaps must be resolved immediately"
            )
            recommendations.append("🎯 Focus on DUAL COPILOT implementation and database connectivity first")

        high_gaps = [gap for gap in gaps if gap.severity == "HIGH"]
        if high_gaps:
            recommendations.append(
                f"⚠️ HIGH PRIORITY: {len(high_gaps)} high-priority gaps need attention within 24 hours"
            )

        total_impact = sum(gap.integration_score_impact for gap in gaps)
        if total_impact < -15.0:
            recommendations.append(
                f"📉 INTEGRATION SCORE RISK: {total_impact:.1f}% negative impact threatens integration success"
            )

        recommendations.append("📊 Implement continuous gap monitoring to prevent regression")

        return recommendations

    def _update_gap_analysis_database(self, result: GapAnalysisResult) -> None:
        """🗄️ Update database with gap analysis results"""
        try:
            with sqlite3.connect(self.production_db) as conn:
                cursor = conn.cursor()

                # Create gap analysis table if not exists
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS gap_analysis_results (
                        analysis_id TEXT PRIMARY KEY,
                        timestamp TEXT,
                        total_gaps_found INTEGER,
                        critical_gaps INTEGER,
                        high_priority_gaps INTEGER,
                        overall_score_impact REAL,
                        analysis_passed BOOLEAN,
                        analysis_details TEXT
                    )
                """)

                # Insert analysis result
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO gap_analysis_results
                    (analysis_id, timestamp, total_gaps_found, critical_gaps, 
                     high_priority_gaps, overall_score_impact, analysis_passed, analysis_details)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        result.analysis_id,
                        result.timestamp.isoformat(),
                        result.total_gaps_found,
                        result.critical_gaps,
                        result.high_priority_gaps,
                        result.overall_integration_score_impact,
                        result.analysis_passed,
                        json.dumps(
                            {
                                "gaps_by_category": {k: len(v) for k, v in result.gaps_by_category.items()},
                                "recommendations": result.recommendations,
                            }
                        ),
                    ),
                )

                self.logger.info("✅ Gap analysis results updated in database")

        except (sqlite3.Error, OSError):
            logging.exception("analysis script error")
            self.logger.error("❌ Database update failed")
            raise

    def _generate_gap_analysis_reports(self, result: GapAnalysisResult) -> None:
        """📊 Generate comprehensive gap analysis reports"""

        # Generate JSON report
        json_report_path = self.reports_dir / f"gap_analysis_{result.analysis_id}.json"

        report_data = {
            "analysis_id": result.analysis_id,
            "timestamp": result.timestamp.isoformat(),
            "summary": {
                "total_gaps": result.total_gaps_found,
                "critical_gaps": result.critical_gaps,
                "high_priority_gaps": result.high_priority_gaps,
                "medium_priority_gaps": result.medium_priority_gaps,
                "low_priority_gaps": result.low_priority_gaps,
                "integration_score_impact": result.overall_integration_score_impact,
                "analysis_passed": result.analysis_passed,
            },
            "gaps_by_category": {
                category: [
                    {
                        "gap_id": gap.gap_id,
                        "severity": gap.severity,
                        "description": gap.description,
                        "current_status": gap.current_status,
                        "target_status": gap.target_status,
                        "remediation_actions": gap.remediation_actions,
                        "integration_score_impact": gap.integration_score_impact,
                        "priority_score": gap.priority_score,
                        "estimated_effort_hours": gap.estimated_effort_hours,
                    }
                    for gap in gaps
                ]
                for category, gaps in result.gaps_by_category.items()
            },
            "remediation_roadmap": result.remediation_roadmap,
            "recommendations": result.recommendations,
        }

        with open(json_report_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        self.logger.info(f"📊 Gap analysis report generated: {json_report_path}")

    def _check_timeout(self) -> None:
        """⏱️ Check for timeout conditions"""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        timeout_seconds = self.timeout_minutes * 60

        if elapsed > timeout_seconds:
            raise TimeoutError(f"Gap analysis exceeded {self.timeout_minutes} minute timeout")


def main(argv: list[str] | None = None):
    """🎯 Main execution function for gap analysis"""

    parser = argparse.ArgumentParser(description="Run gap analysis or append a lesson")
    parser.add_argument("--lesson", help="Append a new lesson and exit")
    args = parser.parse_args(argv)

    if args.lesson:
        store_lesson(
            description=args.lesson,
            source="gap_analyzer",
            timestamp=datetime.utcnow().isoformat(),
            validation_status="pending",
            tags="gap",
        )
        print("Lesson stored")
        return 0

    analyzer = LessonsLearnedGapAnalyzer()
    result = analyzer.execute_comprehensive_gap_analysis()
    print("\n" + "=" * 80)
    print("🔍 LESSONS LEARNED GAP ANALYSIS SUMMARY")
    print("=" * 80)
    print(f"📊 Total Gaps Found: {result.total_gaps_found}")
    print(f"🚨 Critical Gaps: {result.critical_gaps}")
    print(f"⚠️ High Priority Gaps: {result.high_priority_gaps}")
    print(f"📉 Integration Score Impact: {result.overall_integration_score_impact:.1f}%")
    print(f"✅ Analysis Status: {'PASSED' if result.analysis_passed else 'FAILED'}")
    print("=" * 80)
    if result.recommendations:
        print("\n📋 KEY RECOMMENDATIONS:")
        for i, recommendation in enumerate(result.recommendations, 1):
            print(f"{i}. {recommendation}")
    return 0 if result.analysis_passed else 1


if __name__ == "__main__":
    exit(main())
