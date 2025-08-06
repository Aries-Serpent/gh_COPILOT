#!/usr/bin/env python3
"""
Database Consistency Checker - FINAL CORRECTED VERSION
Uses EXISTING databases/logs.db with correct column names
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from tqdm import tqdm
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class DatabaseConsistencyChecker:
    """Check consistency between logs folder and EXISTING databases/logs.db"""

    def __init__(self):
        self.start_time = datetime.now()
        self.workspace_root = Path.cwd()

        # CORRECTED: Use existing databases/logs.db
        self.logs_db_path = self.workspace_root / "databases" / "logs.db"
        self.logs_folder = self.workspace_root / "logs"

        # Validation results
        self.validation_results = {
            "database_exists": False,
            "logs_folder_exists": False,
            "database_tables": [],
            "log_files_count": 0,
            "database_records": {},
            "consistency_status": "PENDING",
            "migration_ready": False,
            "recommendations": [],
        }

        logger.info("🔄 Database Consistency Checker FINAL - Using existing databases/logs.db")
        logger.info(f"Database path: {self.logs_db_path}")
        logger.info(f"Logs folder: {self.logs_folder}")

    def validate_existing_database(self) -> bool:
        """Validate the existing databases/logs.db"""

        if not self.logs_db_path.exists():
            logger.error(f"❌ CRITICAL: logs.db not found at {self.logs_db_path}")
            return False

        self.validation_results["database_exists"] = True

        try:
            with sqlite3.connect(self.logs_db_path) as conn:
                cursor = conn.cursor()

                # Get all tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                self.validation_results["database_tables"] = tables

                # Get record counts for each table
                for table in tables:
                    if not table.startswith("sqlite_"):
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cursor.fetchone()[0]
                        self.validation_results["database_records"][table] = count
                        logger.info(f"📊 Table {table}: {count} records")

                logger.info(f"✅ Existing database validated: {len(tables)} tables found")
                return True

        except Exception as e:
            logger.error(f"❌ Database validation error: {e}")
            return False

    def scan_logs_folder(self) -> List[Path]:
        """Scan logs folder for log files"""

        if not self.logs_folder.exists():
            logger.warning(f"⚠️ Logs folder not found: {self.logs_folder}")
            self.validation_results["logs_folder_exists"] = False
            return []

        self.validation_results["logs_folder_exists"] = True

        # Find all log files
        log_files = []
        log_patterns = ["*.log", "*.txt", "*.out", "*.err"]

        with tqdm(desc="🔍 Scanning logs folder", unit="files") as pbar:
            for pattern in log_patterns:
                found_files = list(self.logs_folder.rglob(pattern))
                log_files.extend(found_files)
                pbar.update(len(found_files))

        self.validation_results["log_files_count"] = len(log_files)
        logger.info(f"📁 Found {len(log_files)} log files in logs folder")

        return log_files

    def check_database_consistency(self, log_files: List[Path]) -> Dict[str, Any]:
        """Check which log files are tracked in the existing database using correct column names"""

        consistency_report = {
            "tracked_files": [],
            "untracked_files": [],
            "database_only_entries": [],
            "consistency_percentage": 0,
            "database_file_paths": [],
            "log_folder_paths": [],
        }

        if not self.validation_results["database_exists"]:
            logger.error("❌ Cannot check consistency - database not available")
            return consistency_report

        try:
            with sqlite3.connect(self.logs_db_path) as conn:
                cursor = conn.cursor()

                # Check if enterprise_logs table exists
                if "enterprise_logs" in self.validation_results["database_tables"]:
                    # Get all source_path values from database (correct column name)
                    cursor.execute("SELECT DISTINCT source_path FROM enterprise_logs WHERE source_path IS NOT NULL")
                    db_paths = cursor.fetchall()

                    # Convert to set of normalized paths
                    db_file_paths = set()
                    for path_tuple in db_paths:
                        if path_tuple[0]:  # Check if not None
                            # Normalize path separators and make relative to workspace
                            normalized_path = Path(path_tuple[0]).as_posix()
                            db_file_paths.add(normalized_path)

                    consistency_report["database_file_paths"] = list(db_file_paths)
                    logger.info(f"📊 Database contains {len(db_file_paths)} file paths")

                    # Convert log files to relative paths
                    log_folder_paths = set()
                    for log_file in log_files:
                        try:
                            relative_path = log_file.relative_to(self.workspace_root).as_posix()
                            log_folder_paths.add(relative_path)
                        except ValueError:
                            # File is outside workspace, use absolute path
                            log_folder_paths.add(log_file.as_posix())

                    consistency_report["log_folder_paths"] = list(log_folder_paths)
                    logger.info(f"📁 Logs folder contains {len(log_folder_paths)} files")

                    # Check each log file for database tracking
                    with tqdm(desc="🔍 Checking file consistency", total=len(log_files)) as pbar:
                        for log_file in log_files:
                            try:
                                relative_path = log_file.relative_to(self.workspace_root).as_posix()
                            except ValueError:
                                relative_path = log_file.as_posix()

                            # Check if this file path exists in database
                            found_in_db = any(
                                relative_path in db_path or db_path in relative_path for db_path in db_file_paths
                            )

                            if found_in_db:
                                consistency_report["tracked_files"].append(relative_path)
                            else:
                                consistency_report["untracked_files"].append(relative_path)

                            pbar.update(1)

                    # Find database entries without corresponding files
                    consistency_report["database_only_entries"] = list(db_file_paths - log_folder_paths)

                    # Calculate consistency percentage
                    if log_files:
                        consistency_report["consistency_percentage"] = (
                            len(consistency_report["tracked_files"]) / len(log_files)
                        ) * 100

                    logger.info(f"📊 Consistency analysis:")
                    logger.info(f"   - Files tracked in database: {len(consistency_report['tracked_files'])}")
                    logger.info(f"   - Files not tracked: {len(consistency_report['untracked_files'])}")
                    logger.info(f"   - Orphaned database entries: {len(consistency_report['database_only_entries'])}")
                    logger.info(f"   - Consistency percentage: {consistency_report['consistency_percentage']:.1f}%")

                else:
                    logger.warning("⚠️ enterprise_logs table not found in database")

        except Exception as e:
            logger.error(f"❌ Consistency check error: {e}")
            import traceback

            logger.error(f"Traceback: {traceback.format_exc()}")

        return consistency_report

    def assess_migration_readiness(self, consistency_report: Dict[str, Any]) -> bool:
        """Assess if logs are ready for archive migration"""

        migration_ready = False
        recommendations = []

        total_files = self.validation_results["log_files_count"]
        tracked_files = len(consistency_report["tracked_files"])
        untracked_files = len(consistency_report["untracked_files"])

        # Detailed assessment
        if total_files == 0:
            recommendations.append("📁 No log files found in logs folder")
            migration_ready = True  # Nothing to migrate
        elif consistency_report["consistency_percentage"] >= 80:
            migration_ready = True
            recommendations.append("✅ High consistency - logs ready for archive migration")
        elif consistency_report["consistency_percentage"] >= 50:
            recommendations.append("⚠️ Medium consistency - some files may be ready for migration")
            recommendations.append(f"📝 Consider tracking {untracked_files} untracked files")
        else:
            recommendations.append("❌ Low consistency - recommend updating database before migration")
            recommendations.append(f"📝 {untracked_files} files need database tracking")

        # Check for orphaned database entries
        if consistency_report["database_only_entries"]:
            recommendations.append(f"🗑️ {len(consistency_report['database_only_entries'])} orphaned database entries")
            recommendations.append("💡 Consider cleaning up database entries for deleted files")

        # Database health check
        enterprise_logs_count = self.validation_results["database_records"].get("enterprise_logs", 0)
        if enterprise_logs_count > 0:
            recommendations.append(f"✅ Database operational with {enterprise_logs_count} enterprise log entries")

        self.validation_results["migration_ready"] = migration_ready
        self.validation_results["recommendations"] = recommendations

        return migration_ready

    def generate_report(self, consistency_report: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive consistency report"""

        duration = (datetime.now() - self.start_time).total_seconds()

        final_report = {
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": round(duration, 2),
            "database_path": str(self.logs_db_path),
            "logs_folder_path": str(self.logs_folder),
            "validation_results": self.validation_results,
            "consistency_analysis": consistency_report,
            "summary": {
                "status": "SUCCESS" if self.validation_results["database_exists"] else "NEEDS_ATTENTION",
                "database_operational": self.validation_results["database_exists"],
                "logs_folder_exists": self.validation_results["logs_folder_exists"],
                "total_log_files": self.validation_results["log_files_count"],
                "database_tables": len(self.validation_results["database_tables"]),
                "files_tracked_percentage": consistency_report.get("consistency_percentage", 0),
                "migration_ready": self.validation_results["migration_ready"],
            },
        }

        return final_report

    def execute_consistency_check(self) -> Dict[str, Any]:
        """Execute complete consistency check workflow"""

        logger.info("🚀 Starting database consistency check...")

        with tqdm(total=100, desc="🔍 Consistency Check", unit="%") as pbar:
            # Step 1: Validate existing database (30%)
            pbar.set_description("🗄️ Validating existing database")
            db_valid = self.validate_existing_database()
            pbar.update(30)

            # Step 2: Scan logs folder (20%)
            pbar.set_description("📁 Scanning logs folder")
            log_files = self.scan_logs_folder()
            pbar.update(20)

            # Step 3: Check consistency (30%)
            pbar.set_description("🔍 Checking consistency")
            consistency_report = self.check_database_consistency(log_files)
            pbar.update(30)

            # Step 4: Assess migration readiness (20%)
            pbar.set_description("📋 Assessing migration readiness")
            migration_ready = self.assess_migration_readiness(consistency_report)
            pbar.update(20)

        # Generate final report
        final_report = self.generate_report(consistency_report)

        # Set overall status
        if db_valid and self.validation_results["logs_folder_exists"]:
            self.validation_results["consistency_status"] = "OPERATIONAL"
        else:
            self.validation_results["consistency_status"] = "NEEDS_ATTENTION"

        logger.info(f"✅ Consistency check completed in {final_report['duration_seconds']}s")
        logger.info(f"📊 Overall status: {self.validation_results['consistency_status']}")

        return final_report


def main():
    """Main execution function"""

    print("=" * 80)
    print("🔍 DATABASE CONSISTENCY CHECKER - FINAL CORRECTED VERSION")
    print("Using EXISTING databases/logs.db with correct column names")
    print("=" * 80)

    try:
        checker = DatabaseConsistencyChecker()
        report = checker.execute_consistency_check()

        # Save report
        report_file = Path("config/database_consistency_report_final.json")
        report_file.parent.mkdir(exist_ok=True)

        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\n📊 CONSISTENCY CHECK COMPLETE")
        print(f"📄 Report saved: {report_file}")
        print(f"🗄️ Database: {report['database_path']}")
        print(f"📁 Log files found: {report['summary']['total_log_files']}")
        print(f"📊 Database tables: {report['summary']['database_tables']}")
        print(f"💾 Enterprise logs in DB: {report['validation_results']['database_records'].get('enterprise_logs', 0)}")
        print(f"🔍 Files tracked: {len(report['consistency_analysis']['tracked_files'])}")
        print(f"❓ Files untracked: {len(report['consistency_analysis']['untracked_files'])}")
        print(f"📊 Consistency: {report['summary']['files_tracked_percentage']:.1f}%")
        print(f"🚀 Migration ready: {'YES' if report['summary']['migration_ready'] else 'NO'}")

        # Show recommendations
        if report["validation_results"]["recommendations"]:
            print(f"\n📋 RECOMMENDATIONS:")
            for rec in report["validation_results"]["recommendations"]:
                print(f"   {rec}")

        return report

    except Exception as e:
        logger.error(f"❌ Critical error: {e}")
        import traceback

        logger.error(f"Traceback: {traceback.format_exc()}")
        return None


if __name__ == "__main__":
    main()
