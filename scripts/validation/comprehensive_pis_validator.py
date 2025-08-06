# 🔄 Comprehensive PIS Validation Engine
## Plan Issued Statement Validation and Execution Tracking System

import os
import json
import logging
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from tqdm import tqdm
import re


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
class PISValidationComponent:
    """Individual PIS validation component"""

    component_id: str
    category: str
    name: str
    description: str
    validation_method: str
    expected_criteria: List[str]
    validation_status: str  # PENDING, PASSED, FAILED, WARNING
    evidence: List[str] = field(default_factory=list)
    findings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    validation_score: float = 0.0
    maximum_score: float = 100.0
    last_validated: datetime = field(default_factory=datetime.now)


@dataclass
class PISValidationResult:
    """Comprehensive PIS validation result"""

    validation_id: str
    timestamp: datetime
    pis_document_path: str
    validation_summary: Dict[str, str]
    component_validations: Dict[str, PISValidationComponent]
    overall_validation_score: float
    execution_readiness: str  # READY, PARTIAL, NOT_READY
    critical_blockers: List[str]
    warning_issues: List[str]
    success_criteria_met: List[str]
    execution_timeline_validated: bool
    resource_requirements_met: bool
    validation_passed: bool
    next_validation_date: datetime


class ComprehensivePISValidator:
    """🔄 Comprehensive Plan Issued Statement Validation Engine"""

    def __init__(self, workspace_path: Optional[str] = None):
        # CRITICAL: Validate workspace integrity first
        validate_workspace_integrity()

        # Initialize validator configuration
        self.workspace_path = Path(workspace_path or os.getenv("GH_COPILOT_WORKSPACE", "e:/gh_COPILOT"))
        self.validation_id = f"PIS_VAL_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.start_time = datetime.now()
        self.timeout_minutes = 45

        # Database and file paths
        self.production_db = self.workspace_path / "production.db"
        self.reports_dir = self.workspace_path / "reports" / "pis_validation"
        self.logs_dir = self.workspace_path / "logs" / "pis_validation"

        # Ensure directories exist
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        # Initialize enterprise logging
        self._setup_enterprise_logging()

        # PIS validation components
        self.validation_components = {
            # Objective Definition Validation
            "objective_clarity": PISValidationComponent(
                component_id="obj_clarity",
                category="objective_definition",
                name="Objective Clarity",
                description="Clear, specific, and measurable objective definition",
                validation_method="content_analysis",
                expected_criteria=[
                    "Specific objective statement present",
                    "Success criteria defined",
                    "Timeline specified",
                    "Measurable outcomes identified",
                ],
                validation_status="PENDING",
            ),
            "success_criteria": PISValidationComponent(
                component_id="obj_success",
                category="objective_definition",
                name="Success Criteria",
                description="Comprehensive success criteria and metrics",
                validation_method="criteria_validation",
                expected_criteria=[
                    "Quantitative success metrics",
                    "Quality gates defined",
                    "Acceptance criteria listed",
                    "Completion validation method",
                ],
                validation_status="PENDING",
            ),
            # Database-First Analysis Validation
            "database_query_validation": PISValidationComponent(
                component_id="db_query",
                category="database_first_analysis",
                name="Database Query Validation",
                description="Production database query methodology",
                validation_method="database_validation",
                expected_criteria=[
                    "Production.db query strategy",
                    "Existing solution analysis",
                    "Pattern matching approach",
                    "Template intelligence utilization",
                ],
                validation_status="PENDING",
            ),
            "pattern_matching": PISValidationComponent(
                component_id="db_pattern",
                category="database_first_analysis",
                name="Pattern Matching Strategy",
                description="Template pattern matching and reuse strategy",
                validation_method="pattern_analysis",
                expected_criteria=[
                    "Pattern identification methodology",
                    "Template reuse strategy",
                    "Gap analysis approach",
                    "Integration readiness assessment",
                ],
                validation_status="PENDING",
            ),
            # Implementation Strategy Validation
            "implementation_phases": PISValidationComponent(
                component_id="impl_phases",
                category="implementation_strategy",
                name="Implementation Phases",
                description="Clear implementation phases and milestones",
                validation_method="phase_validation",
                expected_criteria=[
                    "Phase breakdown defined",
                    "Dependencies identified",
                    "Resource allocation specified",
                    "Timeline for each phase",
                ],
                validation_status="PENDING",
            ),
            "resource_requirements": PISValidationComponent(
                component_id="impl_resources",
                category="implementation_strategy",
                name="Resource Requirements",
                description="Comprehensive resource requirement analysis",
                validation_method="resource_analysis",
                expected_criteria=[
                    "Human resource requirements",
                    "Technical resource needs",
                    "Database and system access",
                    "Tool and infrastructure requirements",
                ],
                validation_status="PENDING",
            ),
            # Risk Assessment Validation
            "risk_identification": PISValidationComponent(
                component_id="risk_id",
                category="risk_assessment",
                name="Risk Identification",
                description="Comprehensive risk identification and categorization",
                validation_method="risk_analysis",
                expected_criteria=[
                    "Technical risks identified",
                    "Operational risks assessed",
                    "Timeline risks evaluated",
                    "Resource availability risks",
                ],
                validation_status="PENDING",
            ),
            "mitigation_strategies": PISValidationComponent(
                component_id="risk_mit",
                category="risk_assessment",
                name="Mitigation Strategies",
                description="Risk mitigation and contingency planning",
                validation_method="mitigation_validation",
                expected_criteria=[
                    "Mitigation plans for each risk",
                    "Contingency procedures",
                    "Fallback options defined",
                    "Emergency response protocols",
                ],
                validation_status="PENDING",
            ),
            # Compliance and Quality Validation
            "enterprise_compliance": PISValidationComponent(
                component_id="comp_enterprise",
                category="compliance_quality",
                name="Enterprise Compliance",
                description="Enterprise standards and protocol compliance",
                validation_method="compliance_check",
                expected_criteria=[
                    "DUAL COPILOT pattern compliance",
                    "Visual processing requirements",
                    "Anti-recursion protection",
                    "Database-first methodology",
                ],
                validation_status="PENDING",
            ),
            "quality_assurance": PISValidationComponent(
                component_id="comp_quality",
                category="compliance_quality",
                name="Quality Assurance",
                description="Quality gates and validation procedures",
                validation_method="quality_validation",
                expected_criteria=[
                    "Quality validation checkpoints",
                    "Testing and validation procedures",
                    "Documentation requirements",
                    "Review and approval processes",
                ],
                validation_status="PENDING",
            ),
        }

        self.logger.info("=" * 80)
        self.logger.info("🔄 COMPREHENSIVE PIS VALIDATOR INITIALIZED")
        self.logger.info(f"Validation ID: {self.validation_id}")
        self.logger.info(f"Workspace: {self.workspace_path}")
        self.logger.info(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(f"Validation Components: {len(self.validation_components)}")
        self.logger.info("=" * 80)

    def _setup_enterprise_logging(self) -> None:
        """🔧 Setup enterprise-grade logging with visual indicators"""
        log_filename = f"pis_validation_{self.validation_id}.log"
        log_path = self.logs_dir / log_filename

        # Configure logger
        self.logger = logging.getLogger(f"pis_validator_{self.validation_id}")
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

    def validate_pis_document(self, pis_document_path: str) -> PISValidationResult:
        """🎯 Validate comprehensive PIS document with visual indicators"""

        self.logger.info("🚀 STARTING COMPREHENSIVE PIS VALIDATION")
        self.logger.info(f"PIS Document: {pis_document_path}")

        # Validate PIS document exists
        pis_path = Path(pis_document_path)
        if not pis_path.exists():
            raise FileNotFoundError(f"PIS document not found: {pis_document_path}")

        # Read PIS document content
        try:
            pis_content = pis_path.read_text(encoding="utf-8")
            self.logger.info(f"📄 PIS document loaded: {len(pis_content)} characters")
        except Exception as e:
            raise ValueError(f"Failed to read PIS document: {str(e)}")

        # MANDATORY: Visual processing with tqdm
        total_components = len(self.validation_components)
        validated_components = {}
        critical_blockers = []
        warning_issues = []

        with tqdm(
            total=100,
            desc="🔄 PIS Validation",
            unit="%",
            bar_format="{l_bar}{bar}| {n:.1f}/{total}{unit} [{elapsed}<{remaining}]",
        ) as pbar:
            # Validate each component
            for i, (component_key, component) in enumerate(self.validation_components.items()):
                self._check_timeout()

                pbar.set_description(f"📋 {component.name}")

                # Validate component based on method
                validated_component = self._validate_component(component, pis_content)
                validated_components[component_key] = validated_component

                # Collect issues
                if validated_component.validation_status == "FAILED":
                    critical_blockers.extend(validated_component.findings)
                elif validated_component.validation_status == "WARNING":
                    warning_issues.extend(validated_component.findings)

                # Update progress
                progress = ((i + 1) / total_components) * 90  # Reserve 10% for final calculations
                pbar.update(progress - pbar.n)

                elapsed = (datetime.now() - self.start_time).total_seconds()
                etc = self._calculate_etc(elapsed, progress)
                self.logger.info(
                    f"⏱️ Component {i + 1}/{total_components} | Progress: {progress:.1f}% | ETC: {etc:.1f}s"
                )

            # Final validation analysis (90-100%)
            pbar.set_description("🎯 Final Validation Analysis")
            final_result = self._generate_final_validation_result(
                pis_document_path, validated_components, critical_blockers, warning_issues
            )
            pbar.update(10)

        # Log completion summary
        duration = (datetime.now() - self.start_time).total_seconds()
        self.logger.info("=" * 80)
        self.logger.info("✅ PIS VALIDATION COMPLETED")
        self.logger.info(f"Duration: {duration:.1f} seconds")
        self.logger.info(f"Overall Score: {final_result.overall_validation_score:.1f}%")
        self.logger.info(f"Execution Readiness: {final_result.execution_readiness}")
        self.logger.info(f"Validation Status: {'✅ PASSED' if final_result.validation_passed else '❌ FAILED'}")
        self.logger.info("=" * 80)

        # Update database and generate reports
        self._update_pis_validation_database(final_result)
        self._generate_pis_validation_reports(final_result)

        return final_result

    def _validate_component(self, component: PISValidationComponent, pis_content: str) -> PISValidationComponent:
        """📋 Validate individual PIS component"""

        if component.validation_method == "content_analysis":
            return self._validate_content_analysis(component, pis_content)
        elif component.validation_method == "criteria_validation":
            return self._validate_criteria_validation(component, pis_content)
        elif component.validation_method == "database_validation":
            return self._validate_database_validation(component, pis_content)
        elif component.validation_method == "pattern_analysis":
            return self._validate_pattern_analysis(component, pis_content)
        elif component.validation_method == "phase_validation":
            return self._validate_phase_validation(component, pis_content)
        elif component.validation_method == "resource_analysis":
            return self._validate_resource_analysis(component, pis_content)
        elif component.validation_method == "risk_analysis":
            return self._validate_risk_analysis(component, pis_content)
        elif component.validation_method == "mitigation_validation":
            return self._validate_mitigation_validation(component, pis_content)
        elif component.validation_method == "compliance_check":
            return self._validate_compliance_check(component, pis_content)
        elif component.validation_method == "quality_validation":
            return self._validate_quality_validation(component, pis_content)
        else:
            self.logger.warning(f"⚠️ Unknown validation method: {component.validation_method}")
            component.validation_status = "WARNING"
            component.findings = [f"Unknown validation method: {component.validation_method}"]
            return component

    def _validate_content_analysis(self, component: PISValidationComponent, content: str) -> PISValidationComponent:
        """📝 Validate content analysis components"""

        criteria_patterns = {
            "Specific objective statement present": [
                r"objective[s]?\s*[:]\s*.+",
                r"goal[s]?\s*[:]\s*.+",
                r"purpose\s*[:]\s*.+",
            ],
            "Success criteria defined": [r"success\s+criteria", r"completion\s+criteria", r"acceptance\s+criteria"],
            "Timeline specified": [r"\d+\s+days?", r"\d+\s+weeks?", r"\d+\s+months?", r"timeline", r"schedule"],
            "Measurable outcomes identified": [r"\d+%", r"metric[s]?", r"measurable", r"quantifiable"],
        }

        criteria_met = []
        evidence_found = []

        for criterion in component.expected_criteria:
            patterns = criteria_patterns.get(criterion, [])
            found = False

            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    found = True
                    evidence_found.append(f"Found: {pattern}")
                    break

            if found:
                criteria_met.append(criterion)

        # Calculate validation score
        score = (len(criteria_met) / len(component.expected_criteria)) * 100
        component.validation_score = score
        component.evidence = evidence_found

        if score >= 80:
            component.validation_status = "PASSED"
            component.findings = [f"✅ {len(criteria_met)}/{len(component.expected_criteria)} criteria met"]
        elif score >= 60:
            component.validation_status = "WARNING"
            component.findings = [
                f"⚠️ {len(criteria_met)}/{len(component.expected_criteria)} criteria met - improvements needed"
            ]
        else:
            component.validation_status = "FAILED"
            component.findings = [
                f"❌ {len(criteria_met)}/{len(component.expected_criteria)} criteria met - critical gaps"
            ]

        missing_criteria = [c for c in component.expected_criteria if c not in criteria_met]
        if missing_criteria:
            component.recommendations = [f"📝 Add missing criteria: {', '.join(missing_criteria)}"]

        return component

    def _validate_database_validation(self, component: PISValidationComponent, content: str) -> PISValidationComponent:
        """🗄️ Validate database-related components"""

        database_patterns = [
            r"production\.db",
            r"database.first",
            r"query.*database",
            r"enhanced_script_tracking",
            r"16[,.]?500\+?\s*(?:scripts?|patterns?|entries?)",
        ]

        evidence_found = []
        pattern_count = 0

        for pattern in database_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                pattern_count += 1
                evidence_found.append(f"Database reference: {pattern}")

        # Check if actual database exists
        if self.production_db.exists():
            pattern_count += 2  # Bonus for actual database presence
            evidence_found.append("✅ Production database file exists")

        score = min((pattern_count / len(database_patterns)) * 100, 100)
        component.validation_score = score
        component.evidence = evidence_found

        if score >= 80:
            component.validation_status = "PASSED"
            component.findings = ["✅ Strong database-first approach documented"]
        elif score >= 60:
            component.validation_status = "WARNING"
            component.findings = ["⚠️ Some database references found - enhance database-first methodology"]
        else:
            component.validation_status = "FAILED"
            component.findings = ["❌ Insufficient database-first approach - critical enhancement needed"]
            component.recommendations = ["📝 Enhance database-first methodology documentation"]

        return component

    def _validate_phase_validation(self, component: PISValidationComponent, content: str) -> PISValidationComponent:
        """📅 Validate implementation phase components"""

        phase_patterns = [
            r"phase\s+\d+",
            r"step\s+\d+",
            r"milestone",
            r"timeline",
            r"dependencies?",
            r"deliverable[s]?",
        ]

        evidence_found = []
        pattern_count = 0

        for pattern in phase_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                pattern_count += len(matches)
                evidence_found.append(f"Phase reference: {pattern} ({len(matches)} instances)")

        score = min((pattern_count / 10) * 100, 100)  # Expect at least 10 phase-related references
        component.validation_score = score
        component.evidence = evidence_found

        if score >= 80:
            component.validation_status = "PASSED"
            component.findings = ["✅ Comprehensive implementation phases documented"]
        elif score >= 60:
            component.validation_status = "WARNING"
            component.findings = ["⚠️ Basic phases documented - consider more detailed breakdown"]
        else:
            component.validation_status = "FAILED"
            component.findings = ["❌ Insufficient phase documentation - detailed implementation plan needed"]
            component.recommendations = ["📝 Add detailed phase breakdown with timelines and dependencies"]

        return component

    def _validate_risk_analysis(self, component: PISValidationComponent, content: str) -> PISValidationComponent:
        """⚠️ Validate risk analysis components"""

        risk_patterns = [
            r"risk[s]?",
            r"mitigation",
            r"contingency",
            r"fallback",
            r"challenge[s]?",
            r"obstacle[s]?",
            r"blocker[s]?",
        ]

        evidence_found = []
        pattern_count = 0

        for pattern in risk_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                pattern_count += len(matches)
                evidence_found.append(f"Risk reference: {pattern} ({len(matches)} instances)")

        score = min((pattern_count / 8) * 100, 100)  # Expect at least 8 risk-related references
        component.validation_score = score
        component.evidence = evidence_found

        if score >= 80:
            component.validation_status = "PASSED"
            component.findings = ["✅ Comprehensive risk analysis documented"]
        elif score >= 60:
            component.validation_status = "WARNING"
            component.findings = ["⚠️ Basic risk analysis present - enhance with specific mitigation plans"]
        else:
            component.validation_status = "FAILED"
            component.findings = ["❌ Insufficient risk analysis - comprehensive risk assessment needed"]
            component.recommendations = ["📝 Conduct detailed risk analysis with mitigation strategies"]

        return component

    def _validate_compliance_check(self, component: PISValidationComponent, content: str) -> PISValidationComponent:
        """🛡️ Validate enterprise compliance components"""

        compliance_patterns = [
            r"dual\s+copilot",
            r"visual\s+processing",
            r"anti[- ]?recursion",
            r"database[- ]?first",
            r"enterprise\s+compliance",
            r"quality\s+gates?",
            r"validation\s+procedures?",
        ]

        evidence_found = []
        pattern_count = 0

        for pattern in compliance_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                pattern_count += 1
                evidence_found.append(f"Compliance reference: {pattern}")

        score = (pattern_count / len(compliance_patterns)) * 100
        component.validation_score = score
        component.evidence = evidence_found

        if score >= 80:
            component.validation_status = "PASSED"
            component.findings = ["✅ Strong enterprise compliance documented"]
        elif score >= 60:
            component.validation_status = "WARNING"
            component.findings = ["⚠️ Some compliance requirements documented - enhance coverage"]
        else:
            component.validation_status = "FAILED"
            component.findings = ["❌ Insufficient compliance documentation - critical enhancement needed"]
            component.recommendations = ["📝 Document all enterprise compliance requirements"]

        return component

    def _validate_criteria_validation(self, component: PISValidationComponent, content: str) -> PISValidationComponent:
        """✅ Validate criteria validation components"""
        return self._validate_content_analysis(component, content)  # Similar logic

    def _validate_pattern_analysis(self, component: PISValidationComponent, content: str) -> PISValidationComponent:
        """🔍 Validate pattern analysis components"""
        return self._validate_database_validation(component, content)  # Similar logic

    def _validate_resource_analysis(self, component: PISValidationComponent, content: str) -> PISValidationComponent:
        """🛠️ Validate resource analysis components"""
        return self._validate_phase_validation(component, content)  # Similar logic

    def _validate_mitigation_validation(
        self, component: PISValidationComponent, content: str
    ) -> PISValidationComponent:
        """🛡️ Validate mitigation validation components"""
        return self._validate_risk_analysis(component, content)  # Similar logic

    def _validate_quality_validation(self, component: PISValidationComponent, content: str) -> PISValidationComponent:
        """🏆 Validate quality validation components"""
        return self._validate_compliance_check(component, content)  # Similar logic

    def _generate_final_validation_result(
        self,
        pis_path: str,
        components: Dict[str, PISValidationComponent],
        critical_blockers: List[str],
        warning_issues: List[str],
    ) -> PISValidationResult:
        """🎯 Generate final PIS validation result"""

        # Calculate overall validation score
        total_score = sum(comp.validation_score for comp in components.values())
        average_score = total_score / len(components) if components else 0.0

        # Determine execution readiness
        passed_components = sum(1 for comp in components.values() if comp.validation_status == "PASSED")
        failed_components = sum(1 for comp in components.values() if comp.validation_status == "FAILED")

        if failed_components == 0 and average_score >= 85:
            execution_readiness = "READY"
        elif failed_components <= 2 and average_score >= 70:
            execution_readiness = "PARTIAL"
        else:
            execution_readiness = "NOT_READY"

        # Generate validation summary
        validation_summary = {
            "total_components": len(components),
            "passed_components": passed_components,
            "failed_components": failed_components,
            "warning_components": len(components) - passed_components - failed_components,
            "average_score": average_score,
            "critical_blockers": len(critical_blockers),
            "warning_issues": len(warning_issues),
        }

        # Collect success criteria met
        success_criteria_met = []
        for comp in components.values():
            if comp.validation_status == "PASSED":
                success_criteria_met.extend(comp.evidence)

        # Determine validation pass/fail
        validation_passed = execution_readiness in ["READY", "PARTIAL"] and failed_components <= 2

        return PISValidationResult(
            validation_id=self.validation_id,
            timestamp=datetime.now(),
            pis_document_path=pis_path,
            validation_summary=validation_summary,
            component_validations=components,
            overall_validation_score=average_score,
            execution_readiness=execution_readiness,
            critical_blockers=critical_blockers,
            warning_issues=warning_issues,
            success_criteria_met=success_criteria_met,
            execution_timeline_validated=(average_score >= 70),
            resource_requirements_met=(average_score >= 75),
            validation_passed=validation_passed,
            next_validation_date=datetime.now() + timedelta(days=3),
        )

    def _update_pis_validation_database(self, result: PISValidationResult) -> None:
        """🗄️ Update database with PIS validation results"""
        try:
            with sqlite3.connect(self.production_db) as conn:
                cursor = conn.cursor()

                # Create PIS validation table if not exists
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS pis_validations (
                        validation_id TEXT PRIMARY KEY,
                        timestamp TEXT,
                        pis_document_path TEXT,
                        overall_score REAL,
                        execution_readiness TEXT,
                        validation_passed BOOLEAN,
                        critical_blockers INTEGER,
                        warning_issues INTEGER,
                        component_validations TEXT,
                        validation_summary TEXT
                    )
                """)

                # Insert validation result
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO pis_validations
                    (validation_id, timestamp, pis_document_path, overall_score, execution_readiness,
                     validation_passed, critical_blockers, warning_issues, component_validations, validation_summary)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        result.validation_id,
                        result.timestamp.isoformat(),
                        result.pis_document_path,
                        result.overall_validation_score,
                        result.execution_readiness,
                        result.validation_passed,
                        len(result.critical_blockers),
                        len(result.warning_issues),
                        json.dumps(
                            {
                                k: {"status": v.validation_status, "score": v.validation_score}
                                for k, v in result.component_validations.items()
                            }
                        ),
                        json.dumps(result.validation_summary),
                    ),
                )

                self.logger.info("✅ PIS validation results updated in database")

        except Exception as e:
            self.logger.error(f"❌ Database update failed: {str(e)}")

    def _generate_pis_validation_reports(self, result: PISValidationResult) -> None:
        """📊 Generate comprehensive PIS validation reports"""

        # Generate JSON report
        json_report_path = self.reports_dir / f"pis_validation_{result.validation_id}.json"

        report_data = {
            "validation_id": result.validation_id,
            "timestamp": result.timestamp.isoformat(),
            "pis_document_path": result.pis_document_path,
            "validation_summary": result.validation_summary,
            "overall_validation_score": result.overall_validation_score,
            "execution_readiness": result.execution_readiness,
            "validation_passed": result.validation_passed,
            "component_validations": {
                component_key: {
                    "name": component.name,
                    "category": component.category,
                    "validation_status": component.validation_status,
                    "validation_score": component.validation_score,
                    "evidence": component.evidence,
                    "findings": component.findings,
                    "recommendations": component.recommendations,
                }
                for component_key, component in result.component_validations.items()
            },
            "critical_blockers": result.critical_blockers,
            "warning_issues": result.warning_issues,
            "success_criteria_met": result.success_criteria_met,
            "next_validation_date": result.next_validation_date.isoformat(),
        }

        with open(json_report_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        self.logger.info(f"📊 PIS validation report generated: {json_report_path}")

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
            raise TimeoutError(f"PIS validation exceeded {self.timeout_minutes} minute timeout")


def main():
    """🎯 Main execution function for PIS validation"""

    import argparse

    parser = argparse.ArgumentParser(description="Comprehensive PIS Validation Engine")
    parser.add_argument("pis_document", help="Path to PIS document to validate")
    parser.add_argument("--workspace", help="Workspace path", default=None)
    parser.add_argument("--timeout", type=int, help="Timeout in minutes", default=45)

    args = parser.parse_args()

    try:
        # Initialize PIS validator
        validator = ComprehensivePISValidator(workspace_path=args.workspace)
        validator.timeout_minutes = args.timeout

        # Execute comprehensive PIS validation
        result = validator.validate_pis_document(args.pis_document)

        # Display results summary
        print("\n" + "=" * 80)
        print("🔄 PIS VALIDATION SUMMARY")
        print("=" * 80)
        print(f"📄 PIS Document: {result.pis_document_path}")
        print(f"📊 Overall Score: {result.overall_validation_score:.1f}%")
        print(f"🎯 Execution Readiness: {result.execution_readiness}")
        print(f"✅ Validation Status: {'PASSED' if result.validation_passed else 'FAILED'}")

        if result.critical_blockers:
            print(f"🚨 Critical Blockers: {len(result.critical_blockers)}")
            for blocker in result.critical_blockers:
                print(f"   - {blocker}")

        if result.warning_issues:
            print(f"⚠️ Warning Issues: {len(result.warning_issues)}")
            for warning in result.warning_issues[:3]:  # Show top 3
                print(f"   - {warning}")

        print("=" * 80)

        return 0 if result.validation_passed else 1

    except Exception as e:
        print(f"❌ PIS validation failed: {str(e)}")
        return 1


if __name__ == "__main__":
    exit(main())
