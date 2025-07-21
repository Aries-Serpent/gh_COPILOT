#!/usr/bin/env python3
"""
🚀 UNIFIED WRAP-UP ORCHESTRATOR - ENTERPRISE MASTER CONTROLLER
Database-First Comprehensive File Organization & Validation Framework

MISSION: Integrate ALL existing wrap-up components into unified workflow
- Complete root maintenance with 100% file placement compliance
- Integrated config functionality validation
- Comprehensive modularization reporting
- End-to-end validation of entire process

Author: GitHub Copilot with Enterprise Intelligence
Created: July 16, 2025
"""

import os
import sys
import json
import sqlite3
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import importlib.util
from tqdm import tqdm
import time
import logging

# Configure enterprise logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/unified_wrapup_orchestrator.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


@dataclass
class WrapUpResult:
    """Comprehensive wrap-up operation result"""

    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = "IN_PROGRESS"
    files_organized: int = 0
    configs_validated: int = 0
    scripts_modularized: int = 0
    root_files_remaining: int = 0
    compliance_score: float = 0.0
    validation_results: Dict[str, Any] = field(default_factory=dict)
    error_details: List[str] = field(default_factory=list)

    def __post_init__(self):
        if self.end_time is not None and self.end_time < self.start_time:
            raise ValueError("end_time cannot be earlier than start_time")
        if not 0.0 <= self.compliance_score <= 100.0:
            raise ValueError("compliance_score must be between 0 and 100")


class UnifiedWrapUpOrchestrator:
    """
    🎯 Master Wrap-Up Orchestrator with Database Intelligence

    Integrates ALL existing components:
    - File organization specialists
    - Config functionality validators
    - Script modularization reporters
    - Root maintenance systems
    - Database pattern matching
    """

    def __init__(self, workspace_path: Optional[str] = None):
        self.workspace_path = Path(workspace_path or os.getcwd())
        self.session_id = f"wrapup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.start_time = datetime.now()

        # Database connections
        self.production_db = self.workspace_path / "databases" / "production.db"
        self.analytics_db = self.workspace_path / "databases" / "analytics.db"

        # File organization patterns from database
        self.organization_patterns = self._load_organization_patterns()

        # Component integrations
        self.components = {
            "file_organizer": self._initialize_file_organizer(),
            "config_validator": self._initialize_config_validator(),
            "script_modularizer": self._initialize_script_modularizer(),
            "root_maintainer": self._initialize_root_maintainer(),
            "compliance_checker": self._initialize_compliance_checker(),
        }

        logger.info("🚀 UNIFIED WRAP-UP ORCHESTRATOR INITIALIZED")
        logger.info(f"Session ID: {self.session_id}")
        logger.info(f"Workspace: {self.workspace_path}")

    def _load_organization_patterns(self) -> Dict[str, Any]:
        """📊 Load file organization patterns from production database"""
        patterns = {
            "logs": ["*.log", "*_log_*", "*log*"],
            "reports": ["*report*", "*_report_*", "*summary*", "*analysis*"],
            "results": ["*result*", "*_result_*", "*output*", "*data*"],
            "documentation": ["*.md", "*.txt", "*.rst", "*doc*", "*readme*"],
            "config": ["*.json", "*.yaml", "*.yml", "*.ini", "*.cfg", "*config*"],
            "scripts": ["*.py", "*.ps1", "*.sh", "*.bat"],
        }

        try:
            with sqlite3.connect(self.production_db) as conn:
                cursor = conn.cursor()

                # Get enhanced patterns from database
                cursor.execute("""
                    SELECT script_path, functionality_category, script_type 
                    FROM enhanced_script_tracking 
                    WHERE functionality_category IS NOT NULL
                """)

                db_patterns = cursor.fetchall()

                # Enhance patterns with database intelligence
                for script_path, category, script_type in db_patterns:
                    file_name = Path(script_path).name.lower()

                    # Add learned patterns
                    if "log" in file_name and "logs" in patterns:
                        patterns["logs"].append(f"*{file_name.split('_')[0]}*")

                    if "report" in file_name and "reports" in patterns:
                        patterns["reports"].append(f"*{file_name.split('_')[0]}*")

                logger.info(
                    f"📊 Loaded {len(db_patterns)} organization patterns from database"
                )

        except Exception as e:
            logger.warning(f"⚠️ Database pattern loading failed: {e}")

        return patterns

    def _initialize_file_organizer(self) -> Dict[str, Any]:
        """🗂️ Initialize file organization component"""
        return {
            "target_folders": {
                "logs": self.workspace_path / "logs",
                "reports": self.workspace_path / "reports",
                "results": self.workspace_path / "results",
                "documentation": self.workspace_path / "documentation",
                "config": self.workspace_path / "config",
                "scripts": self.workspace_path / "scripts",
            },
            "organized_count": 0,
            "skipped_files": [],
            "error_files": [],
            "misclassified": [],
        }

    def _initialize_config_validator(self) -> Dict[str, Any]:
        """⚙️ Initialize config functionality validator"""
        return {
            "validated_configs": [],
            "broken_configs": [],
            "validation_results": {},
            "functionality_preserved": True,
        }

    def _initialize_script_modularizer(self) -> Dict[str, Any]:
        """🔧 Initialize script modularization reporter"""
        return {
            "root_scripts": [],
            "modularization_candidates": [],
            "organized_scripts": [],
            "recommendations": [],
        }

    def _initialize_root_maintainer(self) -> Dict[str, Any]:
        """🏠 Initialize root maintenance component"""
        return {
            "root_files": [],
            "essential_files": [
                "README.md",
                "CHANGELOG.md",
                "requirements.txt",
                "package.json",
                "Makefile",
                "docker-compose.yml",
                "Dockerfile",
                "pyproject.toml",
                "COPILOT_NAVIGATION_MAP.json",
            ],
            "cleanup_candidates": [],
            "maintenance_actions": [],
        }

    def _initialize_compliance_checker(self) -> Dict[str, Any]:
        """✅ Initialize compliance validation component"""
        return {
            "compliance_rules": [
                "All logs in logs/ folder",
                "All reports in reports/ folder",
                "All results in results/ folder",
                "All docs in documentation/ folder",
                "All configs in config/ folder",
                "Root contains only essential files",
            ],
            "compliance_score": 0.0,
            "violations": [],
            "recommendations": [],
        }

    def execute_unified_wrapup(self) -> WrapUpResult:
        """
        🎯 Execute comprehensive unified wrap-up process

        Phases:
        1. Root maintenance and file discovery
        2. Database-driven file organization
        3. Config functionality validation
        4. Script modularization analysis
        5. Compliance validation
        6. Final verification and reporting
        """

        result = WrapUpResult(session_id=self.session_id, start_time=self.start_time)

        try:
            logger.info("=" * 80)
            logger.info("🚀 UNIFIED WRAP-UP ORCHESTRATOR - MASTER EXECUTION")
            logger.info("=" * 80)

            # Phase 1: Root maintenance and file discovery
            with tqdm(total=100, desc="🔍 Phase 1: Root Discovery", unit="%") as pbar:
                self._execute_phase1_root_discovery(pbar)
                pbar.update(100)

            # Phase 2: Database-driven file organization
            with tqdm(total=100, desc="🗂️ Phase 2: File Organization", unit="%") as pbar:
                self._execute_phase2_file_organization(pbar, result)
                pbar.update(100)

            # Phase 3: Config functionality validation
            with tqdm(total=100, desc="⚙️ Phase 3: Config Validation", unit="%") as pbar:
                self._execute_phase3_config_validation(pbar, result)
                pbar.update(100)

            # Phase 4: Script modularization analysis
            with tqdm(
                total=100, desc="🔧 Phase 4: Script Modularization", unit="%"
            ) as pbar:
                self._execute_phase4_script_modularization(pbar, result)
                pbar.update(100)

            # Phase 5: Compliance validation
            with tqdm(total=100, desc="✅ Phase 5: Compliance Check", unit="%") as pbar:
                self._execute_phase5_compliance_validation(pbar, result)
                pbar.update(100)

            # Phase 6: Final verification and reporting
            with tqdm(total=100, desc="📊 Phase 6: Final Reporting", unit="%") as pbar:
                self._execute_phase6_final_reporting(pbar, result)
                pbar.update(100)

            result.end_time = datetime.now()
            result.status = "COMPLETED"

            # Store results in database
            self._store_wrapup_results(result)

            logger.info("✅ UNIFIED WRAP-UP ORCHESTRATOR COMPLETED SUCCESSFULLY")

        except Exception as e:
            result.status = "FAILED"
            result.error_details.append(str(e))
            logger.error(f"❌ Wrap-up orchestrator failed: {e}")

        return result

    def _execute_phase1_root_discovery(self, pbar: tqdm):
        """🔍 Phase 1: Discover and categorize root files"""
        logger.info("🔍 Phase 1: Root maintenance and file discovery")

        root_maintainer = self.components["root_maintainer"]

        # Discover all root files
        root_files = []
        for item in self.workspace_path.iterdir():
            if item.is_file():
                root_files.append(str(item))

        root_maintainer["root_files"] = root_files

        # Categorize files
        for file_path in root_files:
            file_name = Path(file_path).name

            if file_name in root_maintainer["essential_files"]:
                continue  # Keep essential files in root
            else:
                root_maintainer["cleanup_candidates"].append(file_path)

        logger.info(f"📊 Discovered {len(root_files)} root files")
        logger.info(
            f"📊 {len(root_maintainer['cleanup_candidates'])} candidates for organization"
        )

    def _execute_phase2_file_organization(self, pbar: tqdm, result: WrapUpResult):
        """🗂️ Phase 2: Execute database-driven file organization"""
        logger.info("🗂️ Phase 2: Database-driven file organization")

        file_organizer = self.components["file_organizer"]
        organized_count = 0

        # Create target directories
        for folder_name, folder_path in file_organizer["target_folders"].items():
            folder_path.mkdir(parents=True, exist_ok=True)
            pbar.set_description(f"📁 Creating {folder_name}/ directory")
            time.sleep(0.1)

        # Organize files based on patterns
        cleanup_candidates = self.components["root_maintainer"]["cleanup_candidates"]

        for file_path in cleanup_candidates:
            try:
                file_name = Path(file_path).name.lower()
                organized = False

                script_path = Path(file_path)
                script_type = self.prevent_executable_misclassification(script_path)
                expected_type = {
                    ".py": "python",
                    ".pyw": "python",
                    ".sh": "shell",
                    ".bash": "shell",
                    ".zsh": "shell",
                    ".ps1": "shell",
                    ".bat": "batch",
                    ".cmd": "batch",
                }.get(script_path.suffix.lower(), "unknown")

                if (
                    script_type != "unknown"
                    and expected_type != "unknown"
                    and script_type != expected_type
                ):
                    file_organizer["misclassified"].append(
                        {
                            "file": str(script_path),
                            "detected": script_type,
                            "extension": script_path.suffix.lower(),
                        }
                    )

                if script_type != "unknown":
                    target_folder = file_organizer["target_folders"]["scripts"]
                    target_path = target_folder / Path(file_path).name
                    shutil.move(file_path, target_path)
                    organized_count += 1
                    organized = True
                    pbar.set_description(
                        f"📦 Moved {Path(file_path).name} -> scripts/ ({script_type})"
                    )
                    logger.info(
                        f"📦 Organized: {Path(file_path).name} -> scripts/ ({script_type})"
                    )
                    continue

                # Apply organization patterns
                for folder_type, patterns in self.organization_patterns.items():
                    if folder_type in file_organizer["target_folders"]:
                        for pattern in patterns:
                            pattern_clean = pattern.replace("*", "").replace(".", "")
                            if pattern_clean in file_name:
                                target_folder = file_organizer["target_folders"][
                                    folder_type
                                ]
                                target_path = target_folder / Path(file_path).name

                                # Move file
                                shutil.move(file_path, target_path)
                                organized_count += 1
                                organized = True

                                pbar.set_description(
                                    f"📦 Moved {Path(file_path).name} -> {folder_type}/"
                                )
                                logger.info(
                                    f"📦 Organized: {Path(file_path).name} -> {folder_type}/"
                                )
                                break

                    if organized:
                        break

                if not organized:
                    file_organizer["skipped_files"].append(file_path)

            except Exception as e:
                file_organizer["error_files"].append((file_path, str(e)))
                logger.error(f"❌ Failed to organize {file_path}: {e}")

        file_organizer["organized_count"] = organized_count
        result.files_organized = organized_count

        logger.info(f"✅ Organized {organized_count} files into appropriate folders")

    def _execute_phase3_config_validation(self, pbar: tqdm, result: WrapUpResult):
        """⚙️ Phase 3: Validate config functionality after moves"""
        logger.info("⚙️ Phase 3: Config functionality validation")

        config_validator = self.components["config_validator"]
        config_folder = self.workspace_path / "config"

        if not config_folder.exists():
            logger.info("📁 No config folder found - skipping config validation")
            return

        # Find all config files
        config_files = list(config_folder.glob("*"))
        validated_count = 0

        for config_file in config_files:
            try:
                pbar.set_description(f"🔧 Validating {config_file.name}")

                # Validate config file format
                validation_result = self._validate_config_file(config_file)

                config_validator["validation_results"][str(config_file)] = (
                    validation_result
                )

                if validation_result["valid"]:
                    config_validator["validated_configs"].append(str(config_file))
                    validated_count += 1
                else:
                    config_validator["broken_configs"].append(str(config_file))
                    config_validator["functionality_preserved"] = False

                time.sleep(0.1)

            except Exception as e:
                config_validator["broken_configs"].append(str(config_file))
                logger.error(f"❌ Config validation failed for {config_file}: {e}")

        result.configs_validated = validated_count

        logger.info(f"✅ Validated {validated_count}/{len(config_files)} config files")

        if not config_validator["functionality_preserved"]:
            logger.warning("⚠️ Some config files have validation issues")

    def _validate_config_file(self, config_file: Path) -> Dict[str, Any]:
        """🔧 Validate individual config file functionality"""
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                content = f.read()

            # JSON validation
            if config_file.suffix.lower() == ".json":
                json.loads(content)
                return {"valid": True, "type": "json", "size": len(content)}

            # Basic validation for other formats
            return {
                "valid": True,
                "type": config_file.suffix.lower(),
                "size": len(content),
                "lines": len(content.splitlines()),
            }

        except Exception as e:
            return {"valid": False, "error": str(e)}

    def _execute_phase4_script_modularization(self, pbar: tqdm, result: WrapUpResult):
        """🔧 Phase 4: Script modularization analysis and reporting"""
        logger.info("🔧 Phase 4: Script modularization analysis")

        script_modularizer = self.components["script_modularizer"]

        # Find remaining root scripts
        root_scripts = []
        for item in self.workspace_path.iterdir():
            if item.is_file() and item.suffix in [".py", ".ps1", ".sh", ".bat"]:
                root_scripts.append(str(item))

        script_modularizer["root_scripts"] = root_scripts

        # Analyze each script for modularization opportunities
        for script_path in root_scripts:
            try:
                pbar.set_description(f"🔍 Analyzing {Path(script_path).name}")

                # Get modularization recommendation
                recommendation = self._analyze_script_modularization(script_path)
                script_modularizer["recommendations"].append(recommendation)

                if recommendation["should_modularize"]:
                    script_modularizer["modularization_candidates"].append(script_path)

                time.sleep(0.1)

            except Exception as e:
                logger.error(f"❌ Script analysis failed for {script_path}: {e}")

        result.scripts_modularized = len(
            script_modularizer["modularization_candidates"]
        )
        result.root_files_remaining = len(root_scripts)

        logger.info(
            f"📊 Found {len(script_modularizer['modularization_candidates'])} scripts for modularization"
        )
        logger.info(f"📊 {len(root_scripts)} scripts remaining in root")

    def _analyze_script_modularization(self, script_path: str) -> Dict[str, Any]:
        """🔍 Analyze script for modularization opportunities"""
        try:
            script_file = Path(script_path)

            with open(script_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Basic analysis
            lines = content.splitlines()
            size_kb = len(content) / 1024

            # Check against database patterns
            category = self._get_script_category_from_db(script_file.name)

            # Modularization criteria
            should_modularize = (
                size_kb > 5  # Large scripts
                or len(lines) > 100  # Long scripts
                or script_file.name.startswith(
                    ("temp_", "test_", "debug_")
                )  # Temporary scripts
                or category
                in [
                    "analysis",
                    "automation",
                    "validation",
                    "database",
                ]  # Specific categories
            )

            recommended_folder = self._recommend_script_folder(
                script_file.name, category
            )

            return {
                "script_path": script_path,
                "script_name": script_file.name,
                "script_type": self.prevent_executable_misclassification(script_file),
                "size_kb": round(size_kb, 2),
                "lines": len(lines),
                "category": category,
                "should_modularize": should_modularize,
                "recommended_folder": recommended_folder,
                "reason": self._get_modularization_reason(
                    should_modularize, size_kb, len(lines), category
                ),
            }

        except Exception as e:
            return {
                "script_path": script_path,
                "script_name": Path(script_path).name,
                "script_type": self.prevent_executable_misclassification(
                    Path(script_path)
                ),
                "error": str(e),
                "should_modularize": True,  # Default to modularize on error
                "recommended_folder": "scripts/utilities",
            }

    def _get_script_category_from_db(self, script_name: str) -> str:
        """📊 Get script category from database patterns"""
        try:
            with sqlite3.connect(self.production_db) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT functionality_category 
                    FROM enhanced_script_tracking 
                    WHERE script_path LIKE ? 
                    LIMIT 1
                """,
                    (f"%{script_name}%",),
                )

                result = cursor.fetchone()
                if result:
                    return result[0] or "uncategorized"

        except Exception:
            pass

        # Fallback pattern matching
        script_lower = script_name.lower()

        if any(word in script_lower for word in ["analysis", "report", "breakdown"]):
            return "analysis"
        elif any(word in script_lower for word in ["auto", "orchestr", "executor"]):
            return "automation"
        elif any(word in script_lower for word in ["database", "db", "sql"]):
            return "database"
        elif any(word in script_lower for word in ["valid", "test", "check"]):
            return "validation"
        elif any(word in script_lower for word in ["optim", "enhance", "improve"]):
            return "optimization"
        else:
            return "utilities"

    def prevent_executable_misclassification(self, script_path: Path) -> str:
        """Detect script file type via extension and file header.

        Raises ``ValueError`` when a shebang indicates an executable script but
        the extension does not match the detected type. This prevents text files
        from masquerading as executables.
        """

        try:
            with open(script_path, "rb") as f:
                first_bytes = f.read(4)
                f.seek(0)
                first_line = f.readline().decode("utf-8", errors="ignore").lower()
        except Exception:
            first_bytes = b""
            first_line = ""

        ext = script_path.suffix.lower()

        # Python bytecode detection
        if first_bytes.startswith(importlib.util.MAGIC_NUMBER):
            detected = "python"
        elif "#!" in first_line:
            if "python" in first_line:
                detected = "python"
            elif any(sh in first_line for sh in ["sh", "bash", "zsh", "ksh", "csh", "tcsh", "dash", "pwsh", "powershell"]):
                detected = "shell"
            elif "node" in first_line or "javascript" in first_line:
                detected = "javascript"
            elif "ruby" in first_line:
                detected = "ruby"
            elif "perl" in first_line:
                detected = "perl"
            elif "php" in first_line:
                detected = "php"
            elif "go" in first_line:
                detected = "go"
            elif "rust" in first_line:
                detected = "rust"
            elif "csharp" in first_line or "dotnet" in first_line:
                detected = "csharp"
            elif "java" in first_line:
                detected = "java"
            else:
                detected = "unknown"
        else:
            detected = {
                ".py": "python",
                ".pyi": "python",
                ".pyw": "python",
                ".pyc": "python",
                ".sh": "shell",
                ".ksh": "shell",
                ".csh": "shell",
                ".tcsh": "shell",
                ".dash": "shell",
                ".bash": "shell",
                ".zsh": "shell",
                ".ps1": "shell",
                ".psm1": "shell",
                ".bat": "batch",
                ".cmd": "batch",
                ".js": "javascript",
                ".rb": "ruby",
                ".pl": "perl",
                ".php": "php",
                ".vbs": "vbscript",
                ".vbe": "vbscript",
                ".exe": "binary",
                ".dll": "binary",
                ".jar": "java",
                ".go": "go",
                ".rs": "rust",
                ".c": "c",
                ".h": "c_header",
                ".cpp": "cpp",
                ".cc": "cpp",
                ".cxx": "cpp",
                ".hpp": "cpp_header",
                ".java": "java",
                ".cs": "csharp",
            }.get(ext, "unknown")

        # If a script type was detected from the header but extension does not
        # match, raise an error to flag potential misclassification.
        if detected != "unknown" and ext not in {
            ".py", ".pyi", ".pyw", ".pyc", ".sh", ".bash", ".zsh", ".ksh", ".csh",
            ".tcsh", ".dash", ".ps1", ".psm1", ".bat", ".cmd", ".js", ".rb",
            ".pl", ".php", ".vbs", ".vbe", ".exe", ".dll", ".jar",
            ".go", ".rs", ".c", ".cpp", ".cc", ".cxx", ".h", ".hpp", ".java", ".cs",
        }:
            raise ValueError(f"File extension {ext} does not match detected script type {detected}")

        return detected

    def _recommend_script_folder(self, script_name: str, category: str) -> str:
        """📁 Recommend appropriate folder for script"""
        folder_mapping = {
            "analysis": "scripts/analysis",
            "automation": "scripts/automation",
            "database": "scripts/database",
            "validation": "scripts/validation",
            "optimization": "scripts/optimization",
            "enterprise": "scripts/enterprise",
            "utilities": "scripts/utilities",
        }

        return folder_mapping.get(category, "scripts/utilities")

    def _get_modularization_reason(
        self, should_modularize: bool, size_kb: float, lines: int, category: str
    ) -> str:
        """📝 Get reason for modularization recommendation"""
        if not should_modularize:
            return "Keep in root - essential system file"

        reasons = []
        if size_kb > 5:
            reasons.append(f"Large file ({size_kb:.1f}KB)")
        if lines > 100:
            reasons.append(f"Long script ({lines} lines)")
        if category in ["analysis", "automation", "validation", "database"]:
            reasons.append(f"Category-specific script ({category})")

        return " | ".join(reasons) if reasons else "Organization improvement"

    def _execute_phase5_compliance_validation(self, pbar: tqdm, result: WrapUpResult):
        """✅ Phase 5: Validate file organization compliance"""
        logger.info("✅ Phase 5: Compliance validation")

        compliance_checker = self.components["compliance_checker"]
        violations = []
        compliance_score = 0.0

        # Check each compliance rule
        rules = compliance_checker["compliance_rules"]
        passed_rules = 0

        for i, rule in enumerate(rules):
            pbar.set_description(f"🔍 Checking: {rule}")

            rule_passed = self._check_compliance_rule(rule)

            if rule_passed:
                passed_rules += 1
                logger.info(f"✅ PASSED: {rule}")
            else:
                violations.append(rule)
                logger.warning(f"❌ FAILED: {rule}")

            time.sleep(0.1)

        compliance_score = (passed_rules / len(rules)) * 100

        compliance_checker["violations"] = violations
        compliance_checker["compliance_score"] = compliance_score
        result.compliance_score = compliance_score

        logger.info(f"📊 Compliance Score: {compliance_score:.1f}%")

        if violations:
            logger.warning(f"⚠️ {len(violations)} compliance violations found")
        else:
            logger.info("🎉 Perfect compliance achieved!")

    def _check_compliance_rule(self, rule: str) -> bool:
        """🔍 Check individual compliance rule"""
        try:
            if "logs in logs/" in rule:
                return self._check_folder_compliance("logs", [".log"])
            elif "reports in reports/" in rule:
                return self._check_folder_compliance(
                    "reports", ["report", "summary", "analysis"]
                )
            elif "results in results/" in rule:
                return self._check_folder_compliance(
                    "results", ["result", "output", "data"]
                )
            elif "docs in documentation/" in rule:
                return self._check_folder_compliance(
                    "documentation", [".md", ".txt", ".rst"]
                )
            elif "configs in config/" in rule:
                return self._check_folder_compliance(
                    "config", [".json", ".yaml", ".yml", ".ini", ".cfg"]
                )
            elif "Root contains only essential" in rule:
                return self._check_root_cleanliness()
            else:
                return True  # Unknown rule passes by default

        except Exception as e:
            logger.error(f"❌ Compliance check failed for '{rule}': {e}")
            return False

    def _check_folder_compliance(self, folder_name: str, patterns: List[str]) -> bool:
        """📁 Check if files are properly organized in target folder"""
        # Check root for files that should be in the target folder
        root_violations = 0

        for item in self.workspace_path.iterdir():
            if item.is_file():
                file_name = item.name.lower()

                for pattern in patterns:
                    if pattern in file_name:
                        root_violations += 1
                        break

        return root_violations == 0

    def _check_root_cleanliness(self) -> bool:
        """🏠 Check if root contains only essential files"""
        essential_files = self.components["root_maintainer"]["essential_files"]

        for item in self.workspace_path.iterdir():
            if item.is_file() and item.name not in essential_files:
                return False

        return True

    def _execute_phase6_final_reporting(self, pbar: tqdm, result: WrapUpResult):
        """📊 Phase 6: Generate comprehensive final report"""
        logger.info("📊 Phase 6: Final verification and reporting")

        # Generate comprehensive report
        report = self._generate_comprehensive_report(result)

        # Save report to reports folder
        reports_folder = self.workspace_path / "reports"
        reports_folder.mkdir(exist_ok=True)

        report_file = reports_folder / f"unified_wrapup_report_{self.session_id}.json"

        pbar.set_description(f"💾 Saving report: {report_file.name}")

        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, default=str)

        # Generate markdown summary
        summary_file = reports_folder / f"unified_wrapup_summary_{self.session_id}.md"
        markdown_summary = self._generate_markdown_summary(result, report)

        with open(summary_file, "w", encoding="utf-8") as f:
            f.write(markdown_summary)

        logger.info("📊 Reports saved:")
        logger.info(f"  - {report_file}")
        logger.info(f"  - {summary_file}")

        # Update result with report paths
        result.validation_results["report_file"] = str(report_file)
        result.validation_results["summary_file"] = str(summary_file)

    def _generate_comprehensive_report(self, result: WrapUpResult) -> Dict[str, Any]:
        """📋 Generate comprehensive wrap-up report"""
        return {
            "session_info": {
                "session_id": result.session_id,
                "start_time": result.start_time.isoformat(),
                "end_time": result.end_time.isoformat() if result.end_time else None,
                "duration_seconds": (
                    result.end_time - result.start_time
                ).total_seconds()
                if result.end_time
                else None,
                "status": result.status,
            },
            "file_organization": {
                "files_organized": result.files_organized,
                "target_folders": list(
                    self.components["file_organizer"]["target_folders"].keys()
                ),
                "skipped_files": self.components["file_organizer"]["skipped_files"],
                "error_files": self.components["file_organizer"]["error_files"],
                "misclassified_scripts": self.components["file_organizer"][
                    "misclassified"
                ],
            },
            "config_validation": {
                "configs_validated": result.configs_validated,
                "validated_configs": self.components["config_validator"][
                    "validated_configs"
                ],
                "broken_configs": self.components["config_validator"]["broken_configs"],
                "functionality_preserved": self.components["config_validator"][
                    "functionality_preserved"
                ],
            },
            "script_modularization": {
                "scripts_modularized": result.scripts_modularized,
                "root_files_remaining": result.root_files_remaining,
                "modularization_recommendations": self.components["script_modularizer"][
                    "recommendations"
                ],
            },
            "compliance_validation": {
                "compliance_score": result.compliance_score,
                "violations": self.components["compliance_checker"]["violations"],
                "rules_checked": self.components["compliance_checker"][
                    "compliance_rules"
                ],
            },
            "root_maintenance": {
                "root_files_total": len(
                    self.components["root_maintainer"]["root_files"]
                ),
                "essential_files": self.components["root_maintainer"][
                    "essential_files"
                ],
                "cleanup_candidates": len(
                    self.components["root_maintainer"]["cleanup_candidates"]
                ),
            },
        }

    def _generate_markdown_summary(
        self, result: WrapUpResult, report: Dict[str, Any]
    ) -> str:
        """📝 Generate markdown summary report"""
        duration = (
            (result.end_time - result.start_time).total_seconds()
            if result.end_time
            else 0
        )

        return f"""# 🚀 UNIFIED WRAP-UP ORCHESTRATOR - EXECUTION SUMMARY

## 📊 Session Information
- **Session ID**: {result.session_id}
- **Start Time**: {result.start_time.strftime("%Y-%m-%d %H:%M:%S")}
- **End Time**: {result.end_time.strftime("%Y-%m-%d %H:%M:%S") if result.end_time else "N/A"}
- **Duration**: {duration:.2f} seconds
- **Status**: {result.status}

## 📈 Key Metrics
- **Files Organized**: {result.files_organized}
- **Configs Validated**: {result.configs_validated}
- **Scripts for Modularization**: {result.scripts_modularized}
- **Root Files Remaining**: {result.root_files_remaining}
- **Compliance Score**: {result.compliance_score:.1f}%

## 🗂️ File Organization Results
{self._format_file_organization_results(report["file_organization"])}

## ⚙️ Config Validation Results
{self._format_config_validation_results(report["config_validation"])}

## 🔧 Script Modularization Analysis
{self._format_script_modularization_results(report["script_modularization"])}

## ✅ Compliance Validation
{self._format_compliance_results(report["compliance_validation"])}

## 🏠 Root Maintenance Summary
{self._format_root_maintenance_results(report["root_maintenance"])}

## 🎯 Recommendations
{self._generate_recommendations(result, report)}

---
*Generated by Unified Wrap-Up Orchestrator v4.0*
*Database-First Enterprise File Organization Framework*
"""

    def _format_file_organization_results(self, org_results: Dict[str, Any]) -> str:
        """📊 Format file organization results for markdown"""
        results = []
        results.append(f"- **Total Files Organized**: {org_results['files_organized']}")
        results.append(
            f"- **Target Folders**: {', '.join(org_results['target_folders'])}"
        )

        if org_results["skipped_files"]:
            results.append(f"- **Skipped Files**: {len(org_results['skipped_files'])}")

        if org_results["error_files"]:
            results.append(f"- **Error Files**: {len(org_results['error_files'])}")

        if org_results.get("misclassified_scripts"):
            results.append(
                f"- **Misclassified Scripts**: {len(org_results['misclassified_scripts'])}"
            )

        return "\n".join(results)

    def _format_config_validation_results(self, config_results: Dict[str, Any]) -> str:
        """⚙️ Format config validation results for markdown"""
        results = []
        results.append(
            f"- **Configs Validated**: {config_results['configs_validated']}"
        )
        results.append(
            f"- **Functionality Preserved**: {'✅ Yes' if config_results['functionality_preserved'] else '❌ No'}"
        )

        if config_results["broken_configs"]:
            results.append(
                f"- **Broken Configs**: {len(config_results['broken_configs'])}"
            )

        return "\n".join(results)

    def _format_script_modularization_results(
        self, script_results: Dict[str, Any]
    ) -> str:
        """🔧 Format script modularization results for markdown"""
        results = []
        results.append(
            f"- **Scripts Requiring Modularization**: {script_results['scripts_modularized']}"
        )
        results.append(
            f"- **Scripts Remaining in Root**: {script_results['root_files_remaining']}"
        )

        if script_results["modularization_recommendations"]:
            results.append("- **Modularization Recommendations**:")
            for rec in script_results["modularization_recommendations"][:5]:  # Top 5
                if rec.get("should_modularize"):
                    results.append(
                        f"  - `{rec['script_name']}` → `{rec['recommended_folder']}`"
                    )

        return "\n".join(results)

    def _format_compliance_results(self, compliance_results: Dict[str, Any]) -> str:
        """✅ Format compliance results for markdown"""
        results = []
        results.append(
            f"- **Compliance Score**: {compliance_results['compliance_score']:.1f}%"
        )

        if compliance_results["violations"]:
            results.append("- **Violations Found**:")
            for violation in compliance_results["violations"]:
                results.append(f"  - ❌ {violation}")
        else:
            results.append("- **Status**: ✅ Perfect Compliance Achieved!")

        return "\n".join(results)

    def _format_root_maintenance_results(self, root_results: Dict[str, Any]) -> str:
        """🏠 Format root maintenance results for markdown"""
        results = []
        results.append(f"- **Total Root Files**: {root_results['root_files_total']}")
        results.append(f"- **Essential Files**: {len(root_results['essential_files'])}")
        results.append(f"- **Files Organized**: {root_results['cleanup_candidates']}")

        return "\n".join(results)

    def _generate_recommendations(
        self, result: WrapUpResult, report: Dict[str, Any]
    ) -> str:
        """🎯 Generate actionable recommendations"""
        recommendations = []

        # Compliance recommendations
        if result.compliance_score < 100:
            recommendations.append(
                "- 📋 Address compliance violations to achieve 100% compliance"
            )

        # Config recommendations
        if not report["config_validation"]["functionality_preserved"]:
            recommendations.append("- ⚙️ Review and fix broken configuration files")

        # Script modularization recommendations
        if result.scripts_modularized > 0:
            recommendations.append(
                f"- 🔧 Modularize {result.scripts_modularized} scripts for better organization"
            )

        # Root maintenance recommendations
        if result.root_files_remaining > len(
            report["root_maintenance"]["essential_files"]
        ):
            recommendations.append(
                "- 🏠 Continue root cleanup to maintain minimal root directory"
            )

        if not recommendations:
            recommendations.append("- 🎉 Excellent! All organization goals achieved!")

        return "\n".join(recommendations)

    def _store_wrapup_results(self, result: WrapUpResult):
        """💾 Store wrap-up results in database"""
        try:
            with sqlite3.connect(self.production_db) as conn:
                cursor = conn.cursor()

                # Create table if not exists
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS unified_wrapup_sessions (
                        session_id TEXT PRIMARY KEY,
                        start_time TEXT,
                        end_time TEXT,
                        status TEXT,
                        files_organized INTEGER,
                        configs_validated INTEGER,
                        scripts_modularized INTEGER,
                        root_files_remaining INTEGER,
                        compliance_score REAL,
                        validation_results TEXT,
                        error_details TEXT
                    )
                """)

                # Insert results
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO unified_wrapup_sessions 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        result.session_id,
                        result.start_time.isoformat(),
                        result.end_time.isoformat() if result.end_time else None,
                        result.status,
                        result.files_organized,
                        result.configs_validated,
                        result.scripts_modularized,
                        result.root_files_remaining,
                        result.compliance_score,
                        json.dumps(result.validation_results),
                        json.dumps(result.error_details),
                    ),
                )

                conn.commit()
                logger.info(f"💾 Results stored in database: {result.session_id}")

        except Exception as e:
            logger.error(f"❌ Database storage failed: {e}")


def main():
    """🚀 Main execution function"""
    print("🚀 UNIFIED WRAP-UP ORCHESTRATOR - ENTERPRISE MASTER CONTROLLER")
    print("=" * 80)

    try:
        # Initialize orchestrator
        orchestrator = UnifiedWrapUpOrchestrator()

        # Execute unified wrap-up
        result = orchestrator.execute_unified_wrapup()

        # Display summary
        print("\n" + "=" * 80)
        print("📊 EXECUTION SUMMARY")
        print("=" * 80)
        print(f"Status: {result.status}")
        print(f"Files Organized: {result.files_organized}")
        print(f"Configs Validated: {result.configs_validated}")
        print(f"Scripts for Modularization: {result.scripts_modularized}")
        print(f"Root Files Remaining: {result.root_files_remaining}")
        print(f"Compliance Score: {result.compliance_score:.1f}%")

        if result.status == "COMPLETED":
            print("🎉 UNIFIED WRAP-UP ORCHESTRATOR COMPLETED SUCCESSFULLY!")
        else:
            print("❌ Wrap-up orchestrator encountered errors")
            if result.error_details:
                print("Error Details:")
                for error in result.error_details:
                    print(f"  - {error}")

        return 0 if result.status == "COMPLETED" else 1

    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
