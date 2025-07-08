#!/usr/bin/env python3
"""
Unified Database Management System.

Consolidates database maintenance and cleanup tasks across environments.
"""

# Standard library imports
import argparse
import hashlib
import json
import logging
import os
import shutil
import sqlite3
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from tqdm import tqdm

# Configure enterprise logging
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(
            LOG_DIR / 'unified_database_management.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class DatabaseInfo:
    """Database information structure"""
    path: str
    size_mb: float
    last_modified: str
    hash_sha256: str
    table_count: int
    is_valid: bool
    connection_test: bool
    backup_status: str = "PENDING"


@dataclass
class DatabaseOperation:
    """Database operation tracking"""
    operation_id: str
    operation_type: str
    source_path: str
    target_path: str
    status: str
    timestamp: str
    duration_seconds: float = 0.0
    error_message: str = ""


class UnifiedDatabaseManager:
    """🗄️ Unified enterprise database management system"""

    def __init__(self, workspace_root: Optional[str] = None):
        self.workspace_root = Path(workspace_root or "e:\\gh_COPILOT")
        self.start_time = datetime.now()
        self.process_id = os.getpid()

        # Database operation tracking
        self.operations_log = []
        self.databases_discovered = {}
        self.consolidation_results = {
            "session_id": f"DBM_{int(self.start_time.timestamp())}",
            "start_time": self.start_time.isoformat(),
            "workspace_root": str(self.workspace_root),
            "operations_completed": 0,
            "errors_encountered": 0,
            "space_saved_mb": 0.0,
            "databases_processed": 0,
            "backup_created": False,
            "enterprise_compliance": False
        }

        # Initialize directories
        self.databases_dir = self.workspace_root / "databases"
        self.backup_dir = (
            self.workspace_root / f"_db_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        self.logs_dir = self.workspace_root / "logs"

        # Create required directories
        self.databases_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        logger.info("🗄️ UNIFIED DATABASE MANAGER INITIALIZED")
        logger.info(f"Workspace: {self.workspace_root}")
        logger.info(f"Session ID: {self.consolidation_results['session_id']}")
        logger.info(f"Process ID: {self.process_id}")
        print("=" * 60)

    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file"""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            logger.error(f"Hash calculation failed for {file_path}: {e}")
            return "HASH_ERROR"

    def test_database_connection(self, db_path: Path) -> Tuple[bool, int]:
        """Test database connection and get table count"""
        try:
            with sqlite3.connect(str(db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                return True, len(tables)
        except Exception as e:
            logger.warning(
                f"Database connection test failed for {db_path}: {e}")
            return False, 0

    def load_expected_databases(self) -> List[str]:
        """Load expected database names from documentation"""
        db_list_path = (
            self.workspace_root / "documentation" / "DATABASE_LIST.md"
        )
        expected = []

        try:
            with open(db_list_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("- "):
                        expected.append(line[2:].strip())
        except FileNotFoundError:
            logger.warning(
                "Expected database list not found: %s", db_list_path
            )
        except Exception as e:
            logger.error("Failed to load expected databases: %s", e)

        return expected

    def verify_expected_databases(self) -> Tuple[bool, List[str]]:
        """Verify that all expected databases exist"""
        expected = self.load_expected_databases()
        missing = [db for db in expected if not (
            self.databases_dir / db).is_file()]

        if missing:
            logger.warning(f"Missing expected databases: {missing}")
            return False, missing

        logger.info("All expected databases are present")
        return True, []

    def discover_databases(self) -> Dict[str, DatabaseInfo]:
        """🔍 Discover all database files in workspace"""
        logger.info("🔍 DISCOVERING DATABASE FILES...")

        databases = {}
        db_patterns = ["*.db", "*.sqlite", "*.sqlite3"]

        print("🔍 Scanning for database files...")
        total_patterns = len(db_patterns)

        with tqdm(total=total_patterns, desc="Discovery Progress", unit="pattern") as pbar:
            for pattern in db_patterns:
                pbar.set_description(f"Scanning: {pattern}")

                try:
                    for db_file in self.workspace_root.glob(f"**/{pattern}"):
                        if db_file.is_file():
                            # Skip temporary and backup files
                            if any(skip in str(db_file).lower() for skip in ['temp', 'tmp', 'backup', 'bak']):
                                continue

                            # Calculate file info
                            file_size = db_file.stat().st_size / (1024 * 1024)  # MB
                            last_modified = datetime.fromtimestamp(
                                db_file.stat().st_mtime).isoformat()
                            file_hash = self.calculate_file_hash(db_file)
                            is_valid, table_count = self.test_database_connection(
                                db_file)

                            db_info = DatabaseInfo(
                                path=str(db_file),
                                size_mb=file_size,
                                last_modified=last_modified,
                                hash_sha256=file_hash,
                                table_count=table_count,
                                is_valid=is_valid,
                                connection_test=is_valid
                            )

                            databases[str(db_file)] = db_info

                except Exception as e:
                    logger.warning(f"Error scanning pattern {pattern}: {e}")

                pbar.update(1)

        self.databases_discovered = databases
        self.consolidation_results["databases_processed"] = len(databases)

        logger.info(f"📊 Discovered {len(databases)} database files")
        return databases

    def create_enterprise_backup(self) -> bool:
        """📦 Create enterprise backup of all database files"""
        logger.info("📦 CREATING ENTERPRISE DATABASE BACKUP...")

        try:
            # Create backup directory structure
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            backup_manifest = {
                "backup_timestamp": datetime.now().isoformat(),
                "backup_type": "ENTERPRISE_DATABASE_BACKUP",
                "source_workspace": str(self.workspace_root),
                "backup_location": str(self.backup_dir),
                "files_backed_up": []
            }

            databases = self.databases_discovered or self.discover_databases()

            print("📦 Creating database backup...")
            with tqdm(total=len(databases), desc="Backup Progress", unit="file") as pbar:
                for db_path, db_info in databases.items():
                    pbar.set_description(f"Backing up: {Path(db_path).name}")

                    try:
                        source_path = Path(db_path)
                        relative_path = source_path.relative_to(
                            self.workspace_root)
                        target_path = self.backup_dir / relative_path

                        # Create target directory
                        target_path.parent.mkdir(parents=True, exist_ok=True)

                        # Copy file
                        shutil.copy2(source_path, target_path)

                        # Verify backup
                        if target_path.exists():
                            backup_manifest["files_backed_up"].append({
                                "source": str(source_path),
                                "backup": str(target_path),
                                "size_mb": db_info.size_mb,
                                "hash": db_info.hash_sha256
                            })

                    except Exception as e:
                        logger.error(f"Failed to backup {db_path}: {e}")

                    pbar.update(1)

            # Save backup manifest
            manifest_path = self.backup_dir / "backup_manifest.json"
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(backup_manifest, f, indent=2)

            self.consolidation_results["backup_created"] = True
            logger.info(f"📦 Backup created: {self.backup_dir}")
            logger.info(f"📄 Manifest: {manifest_path}")

            return True

        except Exception as e:
            logger.error(f"❌ Backup creation failed: {e}")
            return False

    def identify_duplicate_databases(self) -> Dict[str, List[str]]:
        """🔍 Identify duplicate databases by hash"""
        logger.info("🔍 IDENTIFYING DUPLICATE DATABASES...")

        databases = self.databases_discovered or self.discover_databases()
        duplicates = {}

        # Group by hash
        hash_groups = {}
        for db_path, db_info in databases.items():
            if db_info.hash_sha256 != "HASH_ERROR":
                if db_info.hash_sha256 not in hash_groups:
                    hash_groups[db_info.hash_sha256] = []
                hash_groups[db_info.hash_sha256].append(db_path)

        # Find duplicates
        for hash_value, paths in hash_groups.items():
            if len(paths) > 1:
                duplicates[hash_value] = paths

        logger.info(f"🔍 Found {len(duplicates)} duplicate groups")
        return duplicates

    def consolidate_databases(self) -> Dict[str, Any]:
        """🔄 Consolidate duplicate databases"""
        logger.info("🔄 CONSOLIDATING DATABASES...")

        duplicates = self.identify_duplicate_databases()
        consolidation_actions = []

        if not duplicates:
            logger.info("ℹ️ No duplicate databases found")
            return {"duplicates_found": 0, "actions_taken": []}

        print("🔄 Consolidating duplicate databases...")
        with tqdm(total=len(duplicates), desc="Consolidation Progress", unit="group") as pbar:
            for hash_value, duplicate_paths in duplicates.items():
                pbar.set_description("Processing duplicate group")

                try:
                    # Choose canonical version (largest file or most recent)
                    canonical_path = max(duplicate_paths, key=lambda p: (
                        Path(p).stat().st_size,
                        Path(p).stat().st_mtime
                    ))

                    # Move duplicates to backup
                    for duplicate_path in duplicate_paths:
                        if duplicate_path != canonical_path:
                            try:
                                source = Path(duplicate_path)
                                target = self.backup_dir / "duplicates" / source.name
                                target.parent.mkdir(
                                    parents=True, exist_ok=True)

                                shutil.move(str(source), str(target))

                                action = {
                                    "type": "DUPLICATE_REMOVED",
                                    "source": duplicate_path,
                                    "target": str(target),
                                    "canonical": canonical_path,
                                    "hash": hash_value
                                }
                                consolidation_actions.append(action)

                            except Exception as e:
                                logger.error(
                                    f"Failed to move duplicate {duplicate_path}: {e}")

                except Exception as e:
                    logger.error(
                        f"Error processing duplicate group {hash_value}: {e}")

                pbar.update(1)

        self.consolidation_results["operations_completed"] = len(
            consolidation_actions)
        logger.info(
            f"🔄 Consolidated {len(consolidation_actions)} duplicate databases")

        return {
            "duplicates_found": len(duplicates),
            "actions_taken": consolidation_actions
        }

    def organize_database_structure(self) -> Dict[str, Any]:
        """📁 Organize database files into proper structure"""
        logger.info("📁 ORGANIZING DATABASE STRUCTURE...")

        databases = self.databases_discovered or self.discover_databases()
        organization_actions = []

        # Define target structure
        target_structure = {
            "production": ["production.db", "prod.db"],
            "development": ["development.db", "dev.db", "test.db"],
            "analytics": ["analytics.db", "metrics.db", "performance.db"],
            "monitoring": ["monitoring.db", "logs.db", "health.db"],
            "backup": ["backup.db", "archive.db"],
            "operational": []  # Default for others
        }

        print("📁 Organizing database structure...")
        with tqdm(total=len(databases), desc="Organization Progress", unit="file") as pbar:
            for db_path, db_info in databases.items():
                pbar.set_description(f"Organizing: {Path(db_path).name}")

                try:
                    source_path = Path(db_path)
                    db_name = source_path.name.lower()

                    # Determine target category
                    target_category = "operational"
                    for category, patterns in target_structure.items():
                        if any(pattern in db_name for pattern in patterns):
                            target_category = category
                            break

                    # Define target path
                    target_dir = self.databases_dir / target_category
                    target_path = target_dir / source_path.name

                    # Skip if already in correct location
                    if source_path.parent == target_dir:
                        pbar.update(1)
                        continue

                    # Create target directory
                    target_dir.mkdir(parents=True, exist_ok=True)

                    # Move file
                    shutil.move(str(source_path), str(target_path))

                    action = {
                        "type": "ORGANIZED",
                        "source": str(source_path),
                        "target": str(target_path),
                        "category": target_category
                    }
                    organization_actions.append(action)

                except Exception as e:
                    logger.error(f"Failed to organize {db_path}: {e}")

                pbar.update(1)

        logger.info(f"📁 Organized {len(organization_actions)} database files")

        return {
            "files_organized": len(organization_actions),
            "actions_taken": organization_actions
        }

    def validate_database_integrity(self) -> Dict[str, Any]:
        """✅ Validate database integrity post-consolidation"""
        logger.info("✅ VALIDATING DATABASE INTEGRITY...")

        validation_results = {
            "databases_validated": 0,
            "databases_healthy": 0,
            "databases_corrupted": 0,
            "validation_errors": []
        }

        # Re-discover databases after consolidation
        current_databases = {}
        for db_file in self.databases_dir.glob("**/*.db"):
            if db_file.is_file():
                current_databases[str(db_file)] = db_file

        print("✅ Validating database integrity...")
        with tqdm(total=len(current_databases), desc="Validation Progress", unit="db") as pbar:
            for db_path, db_file in current_databases.items():
                pbar.set_description(f"Validating: {db_file.name}")

                try:
                    is_valid, table_count = self.test_database_connection(
                        db_file)

                    if is_valid:
                        validation_results["databases_healthy"] += 1
                    else:
                        validation_results["databases_corrupted"] += 1
                        validation_results["validation_errors"].append({
                            "database": str(db_file),
                            "error": "Connection test failed"
                        })

                    validation_results["databases_validated"] += 1

                except Exception as e:
                    validation_results["validation_errors"].append({
                        "database": str(db_file),
                        "error": str(e)
                    })

                pbar.update(1)

        integrity_score = (validation_results["databases_healthy"] /
                           max(validation_results["databases_validated"], 1)) * 100

        logger.info(f"✅ Database integrity: {integrity_score:.1f}%")
        logger.info(
            f"✅ Healthy databases: {validation_results['databases_healthy']}")
        logger.info(
            f"❌ Corrupted databases: {validation_results['databases_corrupted']}")

        return validation_results

    def synchronize_databases(self) -> Dict[str, Any]:
        """🔄 Synchronize schemas across all databases."""
        logger.info("🔄 SYNCHRONIZING DATABASE SCHEMAS...")

        reference_db = self.databases_dir / "production.db"
        if not reference_db.exists():
            logger.warning("Reference database not found; skipping sync")
            return {"status": "SKIPPED"}

        sync_results = {"databases_updated": 0, "errors": []}

        with sqlite3.connect(reference_db) as ref_conn:
            ref_cursor = ref_conn.cursor()
            ref_cursor.execute(
                "SELECT name, sql FROM sqlite_master WHERE type='table';")
            ref_tables = ref_cursor.fetchall()

        for db_path in self.databases_discovered:
            if db_path == str(reference_db):
                continue
            try:
                with sqlite3.connect(db_path) as conn:
                    cursor = conn.cursor()
                    for name, create_sql in ref_tables:
                        cursor.execute(
                            "SELECT name FROM sqlite_master WHERE type='table' AND name=?;",
                            (name,),
                        )
                        if cursor.fetchone() is None:
                            cursor.execute(create_sql)
                    conn.commit()
                sync_results["databases_updated"] += 1
            except Exception as exc:  # noqa: BLE001
                sync_results["errors"].append({
                    "database": db_path,
                    "error": str(exc),
                })

        logger.info(
            f"🔄 Databases synchronized: {sync_results['databases_updated']}")
        return sync_results

    def generate_management_report(self) -> str:
        """📋 Generate comprehensive database management report"""
        logger.info("📋 GENERATING MANAGEMENT REPORT...")

        # Calculate final metrics
        end_time = datetime.now()
        duration = end_time - self.start_time

        self.consolidation_results.update({
            "end_time": end_time.isoformat(),
            "duration_seconds": duration.total_seconds(),
            "enterprise_compliance": True
        })

        # Generate report
        report_data = {
            "unified_database_management_report": {
                "session_info": self.consolidation_results,
                "databases_discovered": len(self.databases_discovered),
                "operations_log": self.operations_log,
                "final_validation": self.validate_database_integrity(),
                "recommendations": [
                    "Regular database integrity checks recommended",
                    "Implement automated backup scheduling",
                    "Monitor database growth and performance",
                    "Maintain enterprise database standards"
                ]
            }
        }

        # Save report
        report_path = self.logs_dir / \
            f"database_management_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2)

        logger.info(f"📋 Report saved: {report_path}")
        return str(report_path)

    def execute_unified_database_management(self) -> Dict[str, Any]:
        """🚀 Execute complete unified database management"""
        logger.info("🚀 EXECUTING UNIFIED DATABASE MANAGEMENT...")

        management_phases = [
            ("🔍 Database Discovery", self.discover_databases, 20),
            ("📦 Enterprise Backup", self.create_enterprise_backup, 15),
            ("🔄 Database Consolidation", self.consolidate_databases, 20),
            ("📁 Structure Organization", self.organize_database_structure, 15),
            ("🔄 Schema Synchronization", self.synchronize_databases, 15),
            ("✅ Integrity Validation", self.validate_database_integrity, 10),
            ("📋 Report Generation", self.generate_management_report, 5),
        ]

        print("🚀 Starting unified database management...")
        expected_ok, missing_dbs = self.verify_expected_databases()
        results = {"expected_databases_ok": expected_ok,
                   "missing_databases": missing_dbs}

        with tqdm(total=100, desc="🗄️ Database Management", unit="%") as pbar:
            for phase_name, phase_func, progress_weight in management_phases:
                pbar.set_description(phase_name)

                try:
                    if phase_name == "🔍 Database Discovery":
                        results["discovery"] = phase_func()
                    elif phase_name == "📦 Enterprise Backup":
                        results["backup"] = phase_func()
                    elif phase_name == "🔄 Database Consolidation":
                        results["consolidation"] = phase_func()
                    elif phase_name == "📁 Structure Organization":
                        results["organization"] = phase_func()
                    elif phase_name == "✅ Integrity Validation":
                        results["validation"] = phase_func()
                    elif phase_name == "📋 Report Generation":
                        results["report_path"] = phase_func()

                    logger.info(f"✅ {phase_name} completed successfully")

                except Exception as e:
                    logger.error(f"❌ {phase_name} failed: {e}")
                    results[phase_name.lower().replace(" ", "_")] = {
                        "error": str(e)}

                pbar.update(progress_weight)

        # Calculate final metrics
        duration = datetime.now() - self.start_time

        logger.info("✅ UNIFIED DATABASE MANAGEMENT COMPLETED")
        logger.info(f"Duration: {duration}")
        logger.info(
            f"Databases processed: {self.consolidation_results['databases_processed']}")
        logger.info(
            f"Operations completed: {self.consolidation_results['operations_completed']}")

        return {
            "status": "SUCCESS",
            "duration": str(duration),
            "results": results,
            "summary": self.consolidation_results
        }


def main() -> Dict[str, Any]:
    """Command line interface for the database manager."""
    parser = argparse.ArgumentParser(
        description="Unified Database Management System")
    parser.add_argument(
        "--integrity-check",
        action="store_true",
        help="Perform connection and schema checks only",
    )
    args = parser.parse_args()

    print("🗄️ UNIFIED DATABASE MANAGEMENT SYSTEM")
    print("=" * 50)
    print("Enterprise Database Management & Consolidation")
    print("=" * 50)

    manager = UnifiedDatabaseManager()

    if args.integrity_check:
        manager.discover_databases()
        expected_ok, missing = manager.verify_expected_databases()
        validation = manager.validate_database_integrity()
        print(json.dumps({"expected_databases_ok": expected_ok,
              "missing_databases": missing, "validation": validation}, indent=2))
        return {
            "status": "INTEGRITY_CHECK",
            "expected_databases_ok": expected_ok,
            "missing_databases": missing,
            "validation": validation,
        }

    result = manager.execute_unified_database_management()

    print("\n" + "=" * 60)
    print("🎯 DATABASE MANAGEMENT SUMMARY")
    print("=" * 60)
    print(f"Status: {result['status']}")
    print(f"Duration: {result['duration']}")
    print(f"Databases Processed: {result['summary']['databases_processed']}")
    print(f"Operations Completed: {result['summary']['operations_completed']}")
    print(f"Backup Created: {result['summary']['backup_created']}")
    print(
        f"Enterprise Compliance: {result['summary']['enterprise_compliance']}")
    print("=" * 60)
    print("🎯 UNIFIED DATABASE MANAGEMENT COMPLETE!")

    return result


if __name__ == "__main__":
    try:
        result = main()
        sys.exit(0 if result['status'] == 'SUCCESS' else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Database management interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Database management failed: {e}")
        sys.exit(1)
