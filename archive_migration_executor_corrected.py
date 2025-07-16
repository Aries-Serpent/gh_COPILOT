#!/usr/bin/env python3
"""
Archive Migration Executor - CORRECTED VERSION
Uses EXISTING databases/logs.db and proper migration logic
"""

import os
import sqlite3
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any
from tqdm import tqdm
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ArchiveMigrationExecutor:
    """Execute archive migration using EXISTING databases/logs.db"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.workspace_root = Path.cwd()
        
        # CORRECTED: Use existing databases/logs.db
        self.logs_db_path = self.workspace_root / "databases" / "logs.db"
        self.logs_folder = self.workspace_root / "logs"
        self.archives_folder = self.workspace_root / "archives"
        
        # Migration tracking
        self.migration_results = {
            "database_operational": False,
            "migration_candidates": [],
            "migration_executed": [],
            "migration_skipped": [],
            "migration_errors": [],
            "migration_summary": {},
            "dry_run": True  # Default to dry run for safety
        }
        
        logger.info("🗂️ Archive Migration Executor CORRECTED - Using existing databases/logs.db")
        logger.info(f"Database: {self.logs_db_path}")
        logger.info(f"Source: {self.logs_folder}")
        logger.info(f"Target: {self.archives_folder}")
    
    def validate_migration_prerequisites(self) -> bool:
        """Validate all prerequisites for migration"""
        
        prerequisites = {
            "database_exists": False,
            "logs_folder_exists": False,
            "archives_folder_ready": False,
            "database_operational": False
        }
        
        # Check database
        if self.logs_db_path.exists():
            prerequisites["database_exists"] = True
            try:
                with sqlite3.connect(self.logs_db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM enterprise_logs")
                    count = cursor.fetchone()[0]
                    if count > 0:
                        prerequisites["database_operational"] = True
                        logger.info(f"✅ Database operational with {count} enterprise log entries")
            except Exception as e:
                logger.error(f"❌ Database validation error: {e}")
        
        # Check logs folder
        if self.logs_folder.exists():
            prerequisites["logs_folder_exists"] = True
            logger.info(f"✅ Logs folder exists: {self.logs_folder}")
        
        # Prepare archives folder
        try:
            self.archives_folder.mkdir(exist_ok=True)
            prerequisites["archives_folder_ready"] = True
            logger.info(f"✅ Archives folder ready: {self.archives_folder}")
        except Exception as e:
            logger.error(f"❌ Cannot create archives folder: {e}")
        
        self.migration_results["database_operational"] = prerequisites["database_operational"]
        
        # All prerequisites must be met
        all_ready = all(prerequisites.values())
        logger.info(f"📋 Prerequisites check: {'✅ PASSED' if all_ready else '❌ FAILED'}")
        
        return all_ready
    
    def identify_migration_candidates(self) -> List[Dict[str, Any]]:
        """Identify files that are fully tracked in database and ready for migration"""
        
        candidates = []
        
        if not self.migration_results["database_operational"]:
            logger.error("❌ Cannot identify candidates - database not operational")
            return candidates
        
        try:
            with sqlite3.connect(self.logs_db_path) as conn:
                cursor = conn.cursor()
                
                # Get files that are fully processed and tracked
                cursor.execute("""
                    SELECT 
                        source_path,
                        title,
                        log_level,
                        last_updated,
                        file_size,
                        status,
                        archival_date
                    FROM enterprise_logs 
                    WHERE source_path IS NOT NULL 
                    AND status = 'active'
                    AND archival_date IS NULL
                    ORDER BY last_updated ASC
                """)
                
                tracked_files = cursor.fetchall()
                
                with tqdm(desc="🔍 Identifying migration candidates", total=len(tracked_files)) as pbar:
                    for file_record in tracked_files:
                        source_path, title, log_level, last_updated, file_size, status, archival_date = file_record
                        
                        # Convert database path to actual file path
                        file_path = Path(source_path)
                        
                        # Check if file still exists in logs folder
                        if file_path.exists() and self.logs_folder in file_path.parents:
                            candidate = {
                                "source_path": str(file_path),
                                "relative_path": str(file_path.relative_to(self.workspace_root)),
                                "title": title,
                                "log_level": log_level,
                                "last_updated": last_updated,
                                "file_size": file_size,
                                "status": status,
                                "database_tracked": True,
                                "migration_priority": self._calculate_migration_priority(file_record),
                                "target_archive_path": self._calculate_target_path(file_path)
                            }
                            candidates.append(candidate)
                        
                        pbar.update(1)
                
                logger.info(f"📁 Identified {len(candidates)} migration candidates")
                
        except Exception as e:
            logger.error(f"❌ Error identifying candidates: {e}")
        
        self.migration_results["migration_candidates"] = candidates
        return candidates
    
    def _calculate_migration_priority(self, file_record: Tuple) -> int:
        """Calculate migration priority based on file attributes"""
        
        source_path, title, log_level, last_updated, file_size, status, archival_date = file_record
        
        priority = 50  # Base priority
        
        # Older files have higher priority
        if last_updated:
            try:
                update_date = datetime.fromisoformat(last_updated.replace(' ', 'T'))
                days_old = (datetime.now() - update_date).days
                if days_old > 30:
                    priority += 30
                elif days_old > 7:
                    priority += 10
            except:
                pass
        
        # Larger files have higher priority
        if file_size and file_size > 1024 * 1024:  # > 1MB
            priority += 20
        
        # Certain log levels have higher priority
        if log_level in ['ERROR', 'CRITICAL']:
            priority += 15
        
        return priority
    
    def _calculate_target_path(self, source_file: Path) -> Path:
        """Calculate target archive path maintaining folder structure"""
        
        try:
            # Get relative path from logs folder
            relative_to_logs = source_file.relative_to(self.logs_folder)
            
            # Create date-based archive structure
            archive_date = datetime.now().strftime("%Y/%m")
            target_path = self.archives_folder / archive_date / relative_to_logs
            
            return target_path
            
        except ValueError:
            # File not in logs folder, use direct archive
            return self.archives_folder / "misc" / source_file.name
    
    def execute_migration(self, candidates: List[Dict[str, Any]], dry_run: bool = True) -> Dict[str, Any]:
        """Execute migration of candidates"""
        
        self.migration_results["dry_run"] = dry_run
        migration_summary = {
            "total_candidates": len(candidates),
            "successful_migrations": 0,
            "skipped_migrations": 0,
            "failed_migrations": 0,
            "total_size_migrated": 0
        }
        
        if dry_run:
            logger.info("🧪 DRY RUN MODE - No files will be moved")
        else:
            logger.info("🚀 LIVE MIGRATION MODE - Files will be moved")
        
        # Sort candidates by priority
        sorted_candidates = sorted(candidates, key=lambda x: x["migration_priority"], reverse=True)
        
        with tqdm(desc="📦 Migrating files", total=len(sorted_candidates)) as pbar:
            for candidate in sorted_candidates:
                try:
                    source_path = Path(candidate["source_path"])
                    target_path = Path(candidate["target_archive_path"])
                    
                    if not source_path.exists():
                        self.migration_results["migration_skipped"].append({
                            "file": str(source_path),
                            "reason": "Source file not found"
                        })
                        migration_summary["skipped_migrations"] += 1
                        pbar.update(1)
                        continue
                    
                    # Create target directory
                    if not dry_run:
                        target_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        # Move file
                        shutil.move(str(source_path), str(target_path))
                        
                        # Update database
                        self._update_database_archival_status(candidate, target_path)
                    
                    # Record migration
                    migration_record = {
                        "source": str(source_path),
                        "target": str(target_path),
                        "size": candidate.get("file_size", 0),
                        "timestamp": datetime.now().isoformat(),
                        "dry_run": dry_run
                    }
                    
                    self.migration_results["migration_executed"].append(migration_record)
                    migration_summary["successful_migrations"] += 1
                    migration_summary["total_size_migrated"] += candidate.get("file_size", 0)
                    
                    if dry_run:
                        logger.debug(f"DRY RUN: Would move {source_path} → {target_path}")
                    else:
                        logger.info(f"✅ Migrated: {source_path} → {target_path}")
                
                except Exception as e:
                    error_record = {
                        "file": candidate["source_path"],
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    }
                    self.migration_results["migration_errors"].append(error_record)
                    migration_summary["failed_migrations"] += 1
                    logger.error(f"❌ Migration failed: {candidate['source_path']} - {e}")
                
                pbar.update(1)
        
        self.migration_results["migration_summary"] = migration_summary
        
        logger.info("📊 Migration Summary:")
        logger.info(f"   - Total candidates: {migration_summary['total_candidates']}")
        logger.info(f"   - Successful: {migration_summary['successful_migrations']}")
        logger.info(f"   - Skipped: {migration_summary['skipped_migrations']}")
        logger.info(f"   - Failed: {migration_summary['failed_migrations']}")
        logger.info(f"   - Size migrated: {migration_summary['total_size_migrated']} bytes")
        
        return migration_summary
    
    def _update_database_archival_status(self, candidate: Dict[str, Any], target_path: Path):
        """Update database with archival information"""
        
        try:
            with sqlite3.connect(self.logs_db_path) as conn:
                cursor = conn.cursor()
                
                # Update archival status
                cursor.execute("""
                    UPDATE enterprise_logs 
                    SET archival_date = ?, 
                        status = 'archived'
                    WHERE source_path = ?
                """, (datetime.now().isoformat(), candidate["source_path"]))
                
                conn.commit()
                logger.debug(f"✅ Updated database archival status for {candidate['source_path']}")
                
        except Exception as e:
            logger.error(f"❌ Database update failed: {e}")
    
    def generate_migration_report(self) -> Dict[str, Any]:
        """Generate comprehensive migration report"""
        
        duration = (datetime.now() - self.start_time).total_seconds()
        
        # Convert Path objects to strings for JSON serialization
        def convert_paths_to_strings(obj):
            if isinstance(obj, Path):
                return str(obj)
            elif isinstance(obj, dict):
                return {k: convert_paths_to_strings(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_paths_to_strings(item) for item in obj]
            else:
                return obj
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": round(duration, 2),
            "database_path": str(self.logs_db_path),
            "logs_folder": str(self.logs_folder),
            "archives_folder": str(self.archives_folder),
            "migration_results": convert_paths_to_strings(self.migration_results),
            "summary": {
                "database_operational": self.migration_results["database_operational"],
                "total_candidates": len(self.migration_results["migration_candidates"]),
                "migration_executed": len(self.migration_results["migration_executed"]),
                "migration_skipped": len(self.migration_results["migration_skipped"]),
                "migration_errors": len(self.migration_results["migration_errors"]),
                "dry_run_mode": self.migration_results["dry_run"]
            }
        }
        
        return report
    
    def execute_archive_migration(self, dry_run: bool = True) -> Dict[str, Any]:
        """Execute complete archive migration workflow"""
        
        logger.info("🗂️ Starting archive migration process...")
        
        with tqdm(total=100, desc="🗂️ Archive Migration", unit="%") as pbar:
            
            # Step 1: Validate prerequisites (25%)
            pbar.set_description("📋 Validating prerequisites")
            if not self.validate_migration_prerequisites():
                logger.error("❌ Prerequisites not met - aborting migration")
                return {"error": "Prerequisites not met"}
            pbar.update(25)
            
            # Step 2: Identify candidates (35%)
            pbar.set_description("🔍 Identifying migration candidates")
            candidates = self.identify_migration_candidates()
            pbar.update(35)
            
            # Step 3: Execute migration (30%)
            pbar.set_description("📦 Executing migration")
            migration_summary = self.execute_migration(candidates, dry_run)
            pbar.update(30)
            
            # Step 4: Generate report (10%)
            pbar.set_description("📄 Generating report")
            final_report = self.generate_migration_report()
            pbar.update(10)
        
        logger.info(f"✅ Archive migration completed in {final_report['duration_seconds']}s")
        
        return final_report

def main():
    """Main execution function"""
    
    print("="*80)
    print("🗂️ ARCHIVE MIGRATION EXECUTOR - CORRECTED VERSION")
    print("Using EXISTING databases/logs.db")
    print("="*80)
    
    try:
        # Default to dry run for safety
        dry_run = True
        
        executor = ArchiveMigrationExecutor()
        report = executor.execute_archive_migration(dry_run=dry_run)
        
        # Save report
        report_file = Path("reports/archive_migration_report_corrected.json")
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📊 ARCHIVE MIGRATION COMPLETE")
        print(f"📄 Report saved: {report_file}")
        print(f"🗄️ Database: {report.get('database_path', 'N/A')}")
        print(f"🔍 Candidates found: {report['summary']['total_candidates']}")
        print(f"📦 Migrations executed: {report['summary']['migration_executed']}")
        print(f"⏸️ Migrations skipped: {report['summary']['migration_skipped']}")
        print(f"❌ Migration errors: {report['summary']['migration_errors']}")
        print(f"🧪 Dry run mode: {report['summary']['dry_run_mode']}")
        
        if report['summary']['dry_run_mode']:
            print(f"\n💡 This was a DRY RUN - no files were actually moved")
            print(f"💡 To execute live migration, set dry_run=False")
        
        return report
        
    except Exception as e:
        logger.error(f"❌ Critical error: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return None

if __name__ == "__main__":
    main()
