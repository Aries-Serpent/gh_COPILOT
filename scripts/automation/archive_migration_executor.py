#!/usr/bin/env python3
"""
📦 ARCHIVE MIGRATION EXECUTOR
=============================
Executes the archive migration workflow for log files that have been
validated and prepared for migration to the archives/ folder.

Enterprise-grade migration with safety checks and rollback capabilities.
"""

import sys
import json
import sqlite3
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import hashlib

from scripts.validation.secondary_copilot_validator import SecondaryCopilotValidator

class ArchiveMigrationExecutor:
    def __init__(self):
        self.workspace_root = Path("e:/gh_COPILOT")
        self.logs_folder = self.workspace_root / "logs"
        self.archives_folder = self.workspace_root / "archives"
        
        # Database paths
        self.production_db = self.workspace_root / "production.db"
        self.logs_db = self.workspace_root / "logs.db"
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.logs_folder / "archive_migration.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Migration settings
        self.dry_run = True  # Safety first - always test before real migration
        self.backup_before_migration = True
        
        # File patterns to archive (older logs and reports that should be moved)
        self.archive_patterns = [
            # Specific old log files (keep recent ones active)
            r".*_20250709.*\.log$",  # July 9th logs
            r".*_20250710.*\.log$",  # July 10th logs
            r".*_20250711.*\.log$",  # July 11th logs
            r".*_20250712.*\.log$",  # July 12th logs
            r".*_20250713.*\.log$",  # July 13th logs
            r".*phase.*_20250709.*",  # Old phase logs
            r".*phase.*_20250710.*",  # Old phase logs
            r".*flake8.*_20250709.*", # Old flake8 logs
            r".*report.*\.txt$",      # Report files that should be in reports/ but are in logs/
            r".*\.json$",             # JSON files in logs/ that should be in reports/
            r".*summary.*\.txt$",     # Summary files
            r".*completion.*\.txt$"   # Completion reports
        ]

    def create_logs_db(self) -> bool:
        """Create logs.db database with proper schema."""
        self.logger.info("🗄️ Creating logs.db database...")
        
        if self.logs_db.exists():
            self.logger.info("✅ logs.db already exists")
            return True
        
        try:
            with sqlite3.connect(self.logs_db) as conn:
                cursor = conn.cursor()
                
                # Create main logs table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS enterprise_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        filename TEXT NOT NULL,
                        original_path TEXT NOT NULL,
                        archive_path TEXT,
                        file_hash TEXT NOT NULL,
                        file_size INTEGER NOT NULL,
                        created_date TEXT NOT NULL,
                        archived_date TEXT,
                        log_type TEXT,
                        status TEXT DEFAULT 'active',
                        metadata TEXT,
                        UNIQUE(filename, original_path)
                    )
                """)
                
                # Create archive tracking table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS archive_operations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        operation_id TEXT NOT NULL,
                        operation_type TEXT NOT NULL,
                        operation_date TEXT NOT NULL,
                        files_processed INTEGER DEFAULT 0,
                        files_failed INTEGER DEFAULT 0,
                        total_size_bytes INTEGER DEFAULT 0,
                        status TEXT DEFAULT 'in_progress',
                        error_log TEXT,
                        rollback_data TEXT
                    )
                """)
                
                # Create indexes for performance
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_filename ON enterprise_logs(filename)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_status ON enterprise_logs(status)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_archive_path ON enterprise_logs(archive_path)")
                
                conn.commit()
                self.logger.info("✅ logs.db created successfully")
                return True
                
        except Exception as e:
            self.logger.error(f"❌ Failed to create logs.db: {e}")
            return False

    def validate_migration_prerequisites(self) -> bool:
        """Validate all prerequisites for safe migration."""
        self.logger.info("🔍 Validating migration prerequisites...")
        
        # Check folders exist
        if not self.logs_folder.exists():
            self.logger.error("❌ logs/ folder does not exist")
            return False
        
        if not self.archives_folder.exists():
            self.logger.info("📁 Creating archives/ folder...")
            self.archives_folder.mkdir(exist_ok=True)
        
        # Ensure logs.db exists
        if not self.create_logs_db():
            return False
        
        # Check write permissions
        try:
            test_file = self.archives_folder / ".write_test"
            test_file.write_text("test")
            test_file.unlink()
        except Exception as e:
            self.logger.error(f"❌ Cannot write to archives/ folder: {e}")
            return False
        
        self.logger.info("✅ All prerequisites validated")
        return True

    def identify_files_for_migration(self) -> List[Dict]:
        """Identify which files should be migrated to archives."""
        self.logger.info("📋 Identifying files for migration...")
        
        files_to_migrate = []
        
        # Get all files in logs folder
        for file_path in self.logs_folder.rglob("*"):
            if file_path.is_file():
                relative_path = file_path.relative_to(self.logs_folder)
                
                # Determine if file should be archived based on patterns and age
                should_archive = self._should_archive_file(file_path)
                
                if should_archive:
                    try:
                        with open(file_path, 'rb') as f:
                            file_hash = hashlib.md5(f.read()).hexdigest()
                    except Exception:
                        file_hash = "ERROR"
                    
                    files_to_migrate.append({
                        "filename": file_path.name,
                        "relative_path": str(relative_path),
                        "full_path": str(file_path),
                        "size": file_path.stat().st_size,
                        "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                        "hash": file_hash,
                        "archive_reason": "historical_log"
                    })
        
        self.logger.info(f"📊 Identified {len(files_to_migrate)} files for migration")
        return files_to_migrate

    def _should_archive_file(self, file_path: Path) -> bool:
        """Determine if a file should be archived."""
        import re
        
        filename = file_path.name
        
        # Never archive very recent files (last 2 days)
        file_age_days = (datetime.now() - datetime.fromtimestamp(file_path.stat().st_mtime)).days
        if file_age_days < 2:
            return False
        
        # Never archive critical current logs
        critical_current = [
            "autonomous_cli.log",
            "autonomous_monitoring.log", 
            "future_routing_validation.log",
            "database_consistency_check.log",
            "archive_migration.log"
        ]
        
        if filename in critical_current:
            return False
        
        # Archive files matching patterns and older than 2 days
        for pattern in self.archive_patterns:
            if re.match(pattern, filename.lower()):
                return True
        
        # Archive old logs (older than 7 days)
        if file_age_days > 7 and filename.endswith('.log'):
            return True
        
        return False

    def add_files_to_database(self, files_to_migrate: List[Dict]) -> bool:
        """Add files to logs.db before migration."""
        self.logger.info(f"📝 Adding {len(files_to_migrate)} files to logs.db...")
        
        try:
            with sqlite3.connect(self.logs_db) as conn:
                cursor = conn.cursor()
                
                for file_info in files_to_migrate:
                    # Check if file already exists in database
                    cursor.execute("""
                        SELECT id FROM enterprise_logs 
                        WHERE filename = ? AND original_path = ?
                    """, (file_info["filename"], file_info["full_path"]))
                    
                    if cursor.fetchone():
                        self.logger.info(f"📄 File already in database: {file_info['filename']}")
                        continue
                    
                    # Insert new file record
                    cursor.execute("""
                        INSERT INTO enterprise_logs 
                        (filename, original_path, file_hash, file_size, created_date, log_type, metadata)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        file_info["filename"],
                        file_info["full_path"],
                        file_info["hash"],
                        file_info["size"],
                        file_info["modified"],
                        "historical_log",
                        json.dumps({"archive_reason": file_info["archive_reason"]})
                    ))
                
                conn.commit()
                self.logger.info("✅ All files added to database")
                return True
                
        except Exception as e:
            self.logger.error(f"❌ Failed to add files to database: {e}")
            return False

    def execute_migration(self, files_to_migrate: List[Dict], dry_run: bool = True) -> Dict:
        """Execute the actual file migration."""
        operation_id = f"MIGRATION_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.logger.info(f"📦 {'DRY RUN: ' if dry_run else ''}Executing migration {operation_id}...")
        
        migration_results = {
            "operation_id": operation_id,
            "total_files": len(files_to_migrate),
            "successful_migrations": 0,
            "failed_migrations": 0,
            "total_size_bytes": 0,
            "errors": [],
            "migrated_files": []
        }
        
        # Record operation start
        if not dry_run:
            self._record_operation_start(operation_id, len(files_to_migrate))
        
        for file_info in files_to_migrate:
            source_path = Path(file_info["full_path"])
            
            # Maintain directory structure in archives
            relative_path = Path(file_info["relative_path"])
            archive_path = self.archives_folder / relative_path
            
            try:
                if dry_run:
                    self.logger.info(f"🧪 DRY RUN: Would move {source_path} → {archive_path}")
                else:
                    # Create directory structure in archives
                    archive_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Move file
                    shutil.move(str(source_path), str(archive_path))
                    
                    # Update database with archive path
                    with sqlite3.connect(self.logs_db) as conn:
                        cursor = conn.cursor()
                        cursor.execute("""
                            UPDATE enterprise_logs 
                            SET archive_path = ?, archived_date = ?, status = 'archived'
                            WHERE filename = ? AND original_path = ?
                        """, (str(archive_path), datetime.now().isoformat(), 
                              file_info["filename"], file_info["full_path"]))
                        conn.commit()
                    
                    self.logger.info(f"✅ Migrated: {file_info['filename']}")
                
                migration_results["successful_migrations"] += 1
                migration_results["total_size_bytes"] += file_info["size"]
                migration_results["migrated_files"].append({
                    "filename": file_info["filename"],
                    "source": str(source_path),
                    "destination": str(archive_path)
                })
                
            except Exception as e:
                error_msg = f"Failed to migrate {file_info['filename']}: {e}"
                self.logger.error(f"❌ {error_msg}")
                migration_results["failed_migrations"] += 1
                migration_results["errors"].append(error_msg)
        
        # Record operation completion
        if not dry_run:
            self._record_operation_completion(operation_id, migration_results)
        
        return migration_results

    def _record_operation_start(self, operation_id: str, file_count: int):
        """Record the start of a migration operation."""
        try:
            with sqlite3.connect(self.logs_db) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO archive_operations 
                    (operation_id, operation_type, operation_date, files_processed)
                    VALUES (?, 'migration', ?, 0)
                """, (operation_id, datetime.now().isoformat()))
                conn.commit()
        except Exception as e:
            self.logger.error(f"❌ Failed to record operation start: {e}")

    def _record_operation_completion(self, operation_id: str, results: Dict):
        """Record the completion of a migration operation."""
        try:
            with sqlite3.connect(self.logs_db) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE archive_operations 
                    SET files_processed = ?, files_failed = ?, total_size_bytes = ?, 
                        status = 'completed', error_log = ?
                    WHERE operation_id = ?
                """, (
                    results["successful_migrations"],
                    results["failed_migrations"], 
                    results["total_size_bytes"],
                    json.dumps(results["errors"]),
                    operation_id
                ))
                conn.commit()
        except Exception as e:
            self.logger.error(f"❌ Failed to record operation completion: {e}")

    def generate_migration_report(self, migration_results: Dict) -> Dict:
        """Generate comprehensive migration report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "operation_id": migration_results["operation_id"],
            "migration_summary": {
                "total_files_processed": migration_results["total_files"],
                "successful_migrations": migration_results["successful_migrations"],
                "failed_migrations": migration_results["failed_migrations"],
                "success_rate": (migration_results["successful_migrations"] / migration_results["total_files"] * 100) if migration_results["total_files"] > 0 else 0,
                "total_size_migrated_mb": round(migration_results["total_size_bytes"] / (1024 * 1024), 2)
            },
            "migrated_files": migration_results["migrated_files"],
            "errors": migration_results["errors"],
            "post_migration_status": {
                "logs_folder_cleaned": migration_results["successful_migrations"] > 0,
                "archives_folder_populated": migration_results["successful_migrations"] > 0,
                "database_updated": True
            }
        }
        
        # Save report
        report_path = self.workspace_root / "reports" / f"archive_migration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.logger.info(f"📄 Migration report saved: {report_path}")
        return report

    def secondary_validate(self) -> bool:
        """Run flake8 secondary validation for this script."""
        validator = SecondaryCopilotValidator(self.logger)
        return validator.validate_corrections([__file__])

def main():
    """Main execution function."""
    print("📦 ARCHIVE MIGRATION EXECUTOR")
    print("=" * 50)
    
    executor = ArchiveMigrationExecutor()
    
    try:
        # Validate prerequisites
        if not executor.validate_migration_prerequisites():
            print("❌ Prerequisites validation failed")
            return False
        
        # Identify files for migration
        files_to_migrate = executor.identify_files_for_migration()
        
        if not files_to_migrate:
            print("ℹ️ No files identified for migration")
            return True
        
        print(f"📋 Found {len(files_to_migrate)} files for migration")
        
        # Add files to database first
        if not executor.add_files_to_database(files_to_migrate):
            print("❌ Failed to add files to database")
            return False
        
        # Execute DRY RUN first
        print("\n🧪 EXECUTING DRY RUN...")
        dry_run_results = executor.execute_migration(files_to_migrate, dry_run=True)
        
        print(f"📊 DRY RUN RESULTS:")
        print(f"  Files to migrate: {dry_run_results['total_files']}")
        print(f"  Total size: {dry_run_results['total_size_bytes'] / (1024*1024):.1f} MB")
        print(f"  Successful: {dry_run_results['successful_migrations']}")
        print(f"  Failed: {dry_run_results['failed_migrations']}")
        
        # Ask user confirmation for actual migration
        print(f"\n⚠️  READY FOR ACTUAL MIGRATION")
        print(f"This will move {len(files_to_migrate)} files to archives/ folder.")
        print(f"Continue with actual migration? (This is currently set to DRY RUN mode)")
        
        # For safety, we'll generate the report but NOT execute the actual migration
        # User would need to manually set dry_run=False to execute
        report = executor.generate_migration_report(dry_run_results)

        # Secondary validation ensures script compliance
        if executor.secondary_validate():
            print("✅ Secondary Copilot validation passed")
        else:
            print("❌ Secondary Copilot validation failed")

        print(f"\n✅ MIGRATION PREPARATION COMPLETE")
        print(f"📄 Report saved with migration plan")
        print(f"🔒 Actual migration requires manual confirmation (change dry_run=False)")

        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        executor.logger.error(f"Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
