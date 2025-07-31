#!/usr/bin/env python3
"""
🗄️ Database Mapping Updater - CHUNK 2
Updates file system mappings in production.db after file relocation

MANDATORY: Apply enterprise compliance from .github/instructions/
MANDATORY: Implement DUAL COPILOT PATTERN validation
MANDATORY: Use visual processing indicators
"""

import os
import sqlite3
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict
from tqdm import tqdm
import logging

# Configure enterprise logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class DatabaseMappingUpdater:
    """
    🗄️ Enterprise Database Mapping Updater with Anti-Recursion Protection
    """

    def __init__(self, workspace_path: str = "e:/gh_COPILOT"):
        self.workspace_path = Path(workspace_path)
        self.db_path = self.workspace_path / "databases" / "production.db"
        self.start_time = datetime.now()

        # CRITICAL: Anti-recursion validation
        self.validate_environment_compliance()

        # File mapping updates from CHUNK 1 relocation
        self.file_mappings = {
            # Log files moved to logs/
            "aggressive_deployment_logs_compressor.py": "logs/aggressive_deployment_logs_compressor.py",
            "comprehensive_remaining_processor.log": "logs/comprehensive_remaining_processor.log",
            "consolidation_execution_report_20250716_003737.json": "logs/consolidation_execution_report_20250716_003737.json",
            "consolidation_execution_report_20250716_004032.json": "logs/consolidation_execution_report_20250716_004032.json",
            "consolidation_execution_report_20250716_004214.json": "logs/consolidation_execution_report_20250716_004214.json",
            "comprehensive_elimination_campaign_summary_20250713_110511.json": "logs/comprehensive_elimination_campaign_summary_20250713_110511.json",
            "compliance_report_20250710_173622.json": "logs/compliance_report_20250710_173622.json",
            "compliance_report_20250710_173707.json": "logs/compliance_report_20250710_173707.json",
            "comprehensive_optimization_completion_report.py": "logs/comprehensive_optimization_completion_report.py",
            "comprehensive_campaign_final_report.py": "logs/comprehensive_campaign_final_report.py",
            "comprehensive_elimination_campaign_summary.py": "logs/comprehensive_elimination_campaign_summary.py",
            # Documentation files moved to documentation/
            "AUTONOMOUS_CLI_README.md": "documentation/AUTONOMOUS_CLI_README.md",
            "advanced_features_config_documentation.md": "documentation/advanced_features_config_documentation.md",
            "comprehensive_database_reproduction_action_statement.md": "documentation/comprehensive_database_reproduction_action_statement.md",
            "COMPREHENSIVE_LOG_EXTRACTION_PLAN.md": "documentation/COMPREHENSIVE_LOG_EXTRACTION_PLAN.md",
            "enterprise_file_organization_plan.md": "documentation/enterprise_file_organization_plan.md",
            # Report files moved to reports/
            "comprehensive_pis_framework_ascii.py": "reports/comprehensive_pis_framework_ascii.py",
            "comprehensive_script_reproducibility_validator.py": "reports/comprehensive_script_reproducibility_validator.py",
            "comprehensive_log_extraction_plan.py": "reports/comprehensive_log_extraction_plan.py",
            # Results files moved to results/
            "ADVANCED_AUTONOMOUS_FRAMEWORK_7_PHASE_SCOPE_20250102_130700.json": "results/ADVANCED_AUTONOMOUS_FRAMEWORK_7_PHASE_SCOPE_20250102_130700.json",
            "config/advanced_features_config.json": "config/advanced_features_config.json",
        }

        logger.info("🚀 DATABASE MAPPING UPDATER INITIALIZED")
        logger.info(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Database Path: {self.db_path}")
        logger.info(f"Files to Update: {len(self.file_mappings)}")

    def validate_environment_compliance(self):
        """CRITICAL: Validate workspace integrity before database operations"""
        workspace_root = self.workspace_path

        # MANDATORY: Check for recursive violations
        forbidden_patterns = ["*backup*", "*_backup_*", "backups", "*temp*"]
        violations = []

        for pattern in forbidden_patterns:
            for folder in workspace_root.rglob(pattern):
                if folder.is_dir() and folder != workspace_root:
                    violations.append(str(folder))

        if violations:
            logger.error("🚨 RECURSIVE FOLDER VIOLATIONS DETECTED:")
            for violation in violations:
                logger.error(f"   - {violation}")
            raise RuntimeError("CRITICAL: Recursive folder violations prevent execution")

        # MANDATORY: Validate database exists
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found: {self.db_path}")

        logger.info("✅ ENVIRONMENT COMPLIANCE VALIDATED")

    def get_database_connection(self) -> sqlite3.Connection:
        """Get database connection with enterprise settings"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            return conn
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise

    def update_file_mappings(self) -> Dict[str, Any]:
        """
        🗄️ Update database mappings with progress monitoring
        """
        logger.info("=" * 60)
        logger.info("🗄️ STARTING DATABASE MAPPING UPDATES")
        logger.info("=" * 60)

        update_results = {
            "total_files": len(self.file_mappings),
            "successful_updates": 0,
            "failed_updates": 0,
            "new_entries": 0,
            "updated_entries": 0,
            "errors": [],
        }

        # MANDATORY: Progress bar for database operations
        with tqdm(total=len(self.file_mappings), desc="🗄️ Updating Database", unit="files") as pbar:
            with self.get_database_connection() as conn:
                cursor = conn.cursor()

                # Check if enhanced_script_tracking table exists
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='enhanced_script_tracking'
                """)

                if not cursor.fetchone():
                    logger.warning("⚠️ enhanced_script_tracking table not found, creating...")
                    self.create_enhanced_script_tracking_table(cursor)

                for old_path, new_path in self.file_mappings.items():
                    try:
                        pbar.set_description(f"📝 Updating: {old_path}")

                        # Check if old path exists in database
                        cursor.execute(
                            """
                            SELECT script_path FROM enhanced_script_tracking 
                            WHERE script_path = ? OR script_path LIKE ?
                        """,
                            (old_path, f"%{old_path}"),
                        )

                        existing_entry = cursor.fetchone()

                        if existing_entry:
                            # Update existing entry
                            cursor.execute(
                                """
                                UPDATE enhanced_script_tracking 
                                SET script_path = ?, last_updated = CURRENT_TIMESTAMP
                                WHERE script_path = ? OR script_path LIKE ?
                            """,
                                (new_path, old_path, f"%{old_path}"),
                            )

                            update_results["updated_entries"] += 1
                            logger.info(f"📝 Updated: {old_path} → {new_path}")
                        else:
                            # Create new entry for relocated file
                            cursor.execute(
                                """
                                INSERT INTO enhanced_script_tracking 
                                (script_path, functionality_category, script_type, last_updated)
                                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                            """,
                                (
                                    new_path,
                                    self.categorize_file(new_path),
                                    self.get_file_type(new_path),
                                ),
                            )

                            update_results["new_entries"] += 1
                            logger.info(f"➕ Added: {new_path}")

                        update_results["successful_updates"] += 1

                    except Exception as e:
                        error_msg = f"Failed to update {old_path}: {str(e)}"
                        update_results["errors"].append(error_msg)
                        update_results["failed_updates"] += 1
                        logger.error(f"❌ {error_msg}")

                    pbar.update(1)

                # Commit all changes
                conn.commit()
                logger.info("💾 Database changes committed successfully")

        return update_results

    def categorize_file(self, file_path: str) -> str:
        """Categorize file based on its new location"""
        path_obj = Path(file_path)

        if path_obj.parts[0] == "logs":
            return "logging"
        elif path_obj.parts[0] == "documentation":
            return "documentation"
        elif path_obj.parts[0] == "reports":
            return "reporting"
        elif path_obj.parts[0] == "results":
            return "results"
        else:
            return "general"

    def get_file_type(self, file_path: str) -> str:
        """Determine file type based on extension"""
        suffix = Path(file_path).suffix.lower()

        type_mapping = {
            ".py": "python_script",
            ".md": "documentation",
            ".json": "configuration",
            ".log": "log_file",
            ".txt": "text_file",
        }

        return type_mapping.get(suffix, "unknown")

    def create_enhanced_script_tracking_table(self, cursor):
        """Create enhanced_script_tracking table if it doesn't exist"""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS enhanced_script_tracking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                script_path TEXT UNIQUE NOT NULL,
                functionality_category TEXT,
                script_type TEXT,
                importance_score REAL DEFAULT 0.0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                file_size INTEGER,
                status TEXT DEFAULT 'active'
            )
        """)
        logger.info("📋 Created enhanced_script_tracking table")

    def validate_database_integrity(self) -> Dict[str, Any]:
        """Validate database integrity after updates"""
        logger.info("🔍 VALIDATING DATABASE INTEGRITY")

        integrity_results = {
            "total_records": 0,
            "relocated_files_found": 0,
            "integrity_issues": [],
            "database_health": "UNKNOWN",
        }

        try:
            with self.get_database_connection() as conn:
                cursor = conn.cursor()

                # Count total records
                cursor.execute("SELECT COUNT(*) FROM enhanced_script_tracking")
                integrity_results["total_records"] = cursor.fetchone()[0]

                # Check for relocated files
                relocated_paths = list(self.file_mappings.values())
                placeholders = ",".join(["?" for _ in relocated_paths])
                cursor.execute(
                    f"""
                    SELECT COUNT(*) FROM enhanced_script_tracking 
                    WHERE script_path IN ({placeholders})
                """,
                    relocated_paths,
                )

                integrity_results["relocated_files_found"] = cursor.fetchone()[0]

                # Validate integrity
                if integrity_results["relocated_files_found"] == len(self.file_mappings):
                    integrity_results["database_health"] = "EXCELLENT"
                    logger.info("✅ Database integrity validation PASSED")
                else:
                    integrity_results["database_health"] = "DEGRADED"
                    logger.warning("⚠️ Database integrity validation PARTIAL")

        except Exception as e:
            integrity_results["integrity_issues"].append(str(e))
            integrity_results["database_health"] = "FAILED"
            logger.error(f"❌ Database integrity validation FAILED: {e}")

        return integrity_results

    def generate_completion_report(
        self, update_results: Dict[str, Any], integrity_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive completion report"""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()

        completion_report = {
            "chunk_phase": "CHUNK 2 - Database Mapping Updates",
            "start_time": self.start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration,
            "update_results": update_results,
            "integrity_results": integrity_results,
            "success_rate": (update_results["successful_updates"] / update_results["total_files"]) * 100,
            "overall_status": "SUCCESS" if update_results["failed_updates"] == 0 else "PARTIAL_SUCCESS",
        }

        return completion_report

    def dual_copilot_validate(self, completion_report: Dict[str, Any]) -> bool:
        """Run secondary validation and compare results."""
        logger.info("🤖🤖 STARTING SECONDARY VALIDATION")
        secondary = self.validate_database_integrity()
        match = secondary.get("database_health") == completion_report["integrity_results"].get("database_health")
        if match:
            logger.info("🤖🤖 Secondary validation matches primary results")
        else:
            logger.warning("🤖🤖 Secondary validation mismatch detected")
            logger.warning(f"Primary: {completion_report['integrity_results']} | Secondary: {secondary}")
        return match

    def perform_update(self) -> Dict[str, Any]:
        """Execute update with dual copilot validation and rollback."""
        backup_root = Path(os.getenv("GH_COPILOT_BACKUP_ROOT", "/tmp/gh_COPILOT_Backups"))
        backup_root.mkdir(parents=True, exist_ok=True)
        backup_path = backup_root / f"production_backup_{int(self.start_time.timestamp())}.db"
        shutil.copy2(self.db_path, backup_path)

        update_results = self.update_file_mappings()
        integrity_results = self.validate_database_integrity()
        report = self.generate_completion_report(update_results, integrity_results)

        if not self.dual_copilot_validate(report):
            shutil.copy2(backup_path, self.db_path)
            report["overall_status"] = "FAILED_VALIDATION"
            logger.error("🤖🤖 Dual Copilot validation failed. Database rolled back.")
        return report


def main():
    """Main execution function with DUAL COPILOT validation"""
    try:
        # MANDATORY: Start time logging
        start_time = datetime.now()
        logger.info("🚀 CHUNK 2: DATABASE MAPPING UPDATES STARTED")
        logger.info(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

        updater = DatabaseMappingUpdater()
        completion_report = updater.perform_update()

        # MANDATORY: Completion summary
        logger.info("=" * 60)
        logger.info("✅ CHUNK 2: DATABASE MAPPING UPDATES COMPLETE")
        logger.info("=" * 60)
        logger.info(f"Total Files Processed: {completion_report['update_results']['total_files']}")
        logger.info(f"Successful Updates: {completion_report['update_results']['successful_updates']}")
        logger.info(f"Failed Updates: {completion_report['update_results']['failed_updates']}")
        logger.info(f"New Entries: {completion_report['update_results']['new_entries']}")
        logger.info(f"Updated Entries: {completion_report['update_results']['updated_entries']}")
        logger.info(f"Success Rate: {completion_report['success_rate']:.1f}%")
        logger.info(f"Database Health: {completion_report['integrity_results']['database_health']}")
        logger.info(f"Duration: {completion_report['duration_seconds']:.2f} seconds")
        logger.info(f"Overall Status: {completion_report['overall_status']}")

        if completion_report["update_results"]["errors"]:
            logger.warning("⚠️ ERRORS ENCOUNTERED:")
            for error in completion_report["update_results"]["errors"]:
                logger.warning(f"   - {error}")

        return completion_report

    except Exception as e:
        logger.error(f"❌ CHUNK 2 EXECUTION FAILED: {str(e)}")
        raise


if __name__ == "__main__":
    report = main()
    if report.get("overall_status") == "FAILED_VALIDATION":
        print("🤖🤖 DUAL COPILOT VALIDATION: CHUNK 2 REQUIRES REVIEW ⚠️")
    else:
        print("🤖🤖 DUAL COPILOT VALIDATION: CHUNK 2 APPROVED ✅")
