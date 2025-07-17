#!/usr/bin/env python3
"""
🗄️ DATABASE CONSOLIDATION EXECUTOR
================================================================
Safe execution of database consolidation plan with:
- Comprehensive backup before operations
- Validation and rollback capabilities
- Transactional approach to ensure data integrity
- Compliance with enterprise standards
================================================================
"""

import os
import sqlite3
import shutil
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging


class DatabaseConsolidationExecutor:
    """🚀 Safe Database Consolidation Implementation"""
    
    def __init__(self, databases_path: str = "databases"):
        self.databases_path = Path(databases_path)
        self.execution_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_path = Path(f"backup_consolidation_{self.execution_timestamp}")
        self.archives_path = Path("archives")
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'consolidation_execution_{self.execution_timestamp}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        self.execution_results = {
            "timestamp": self.execution_timestamp,
            "status": "INITIALIZED",
            "actions_completed": [],
            "actions_failed": [],
            "size_saved_mb": 0,
            "databases_removed": 0,
            "backup_created": False,
            "rollback_available": False
        }
    
    def create_full_backup(self) -> bool:
        """🛡️ Create complete backup before any operations"""
        try:
            self.logger.info("🛡️ Creating full backup of databases...")
            
            # Create backup directory
            self.backup_path.mkdir(exist_ok=True)
            
            # Copy all databases
            copied_count = 0
            total_size = 0
            
            for db_file in self.databases_path.glob("*.db"):
                backup_file = self.backup_path / db_file.name
                shutil.copy2(db_file, backup_file)
                copied_count += 1
                total_size += db_file.stat().st_size
            
            self.logger.info(f"✅ Backup created: {copied_count} files, {total_size/(1024*1024):.2f} MB")
            self.execution_results["backup_created"] = True
            self.execution_results["rollback_available"] = True
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Backup creation failed: {e}")
            return False
    
    def validate_database_integrity(self, db_path: Path) -> bool:
        """🔍 Validate database integrity"""
        try:
            with sqlite3.connect(str(db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA integrity_check")
                result = cursor.fetchone()
                
                if result and result[0] == "ok":
                    return True
                else:
                    self.logger.warning(f"⚠️ Integrity check failed for {db_path.name}: {result}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"❌ Database validation failed for {db_path.name}: {e}")
            return False
    
    def merge_databases(self, source_path: Path, target_path: Path) -> bool:
        """🔄 Safely merge source database into target"""
        try:
            self.logger.info(f"🔄 Merging {source_path.name} into {target_path.name}")
            
            # Validate both databases first
            if not self.validate_database_integrity(source_path):
                self.logger.error(f"❌ Source database {source_path.name} failed integrity check")
                return False
                
            if not self.validate_database_integrity(target_path):
                self.logger.error(f"❌ Target database {target_path.name} failed integrity check")
                return False
            
            # Get source database schema and data
            with sqlite3.connect(str(source_path)) as source_conn:
                source_cursor = source_conn.cursor()
                
                # Get all tables in source
                source_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                source_tables = [row[0] for row in source_cursor.fetchall()]
                
                if not source_tables:
                    self.logger.info(f"ℹ️ Source database {source_path.name} is empty, skipping merge")
                    return True
                
                # Connect to target database
                with sqlite3.connect(str(target_path)) as target_conn:
                    target_cursor = target_conn.cursor()
                    
                    # Get target tables
                    target_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    target_tables = [row[0] for row in target_cursor.fetchall()]
                    
                    # For each table in source, merge data
                    for table in source_tables:
                        try:
                            # Get table schema from source
                            source_cursor.execute(f"SELECT sql FROM sqlite_master WHERE name='{table}'")
                            schema_result = source_cursor.fetchone()
                            
                            if schema_result and schema_result[0]:
                                table_schema = schema_result[0]
                                
                                # If table doesn't exist in target, create it
                                if table not in target_tables:
                                    target_cursor.execute(table_schema)
                                    self.logger.info(f"  📋 Created table {table} in target")
                                
                                # Get data from source table
                                source_cursor.execute(f"SELECT * FROM `{table}`")
                                rows = source_cursor.fetchall()
                                
                                if rows:
                                    # Get column info to build INSERT statement
                                    source_cursor.execute(f"PRAGMA table_info(`{table}`)")
                                    columns = [col[1] for col in source_cursor.fetchall()]
                                    
                                    # Prepare INSERT with conflict resolution
                                    placeholders = ",".join(["?" for _ in columns])
                                    column_names = ",".join([f"`{col}`" for col in columns])
                                    
                                    insert_sql = f"INSERT OR IGNORE INTO `{table}` ({column_names}) VALUES ({placeholders})"
                                    
                                    # Insert data
                                    target_cursor.executemany(insert_sql, rows)
                                    inserted_count = target_cursor.rowcount
                                    
                                    self.logger.info(f"  📊 Merged {len(rows)} rows from {table} ({inserted_count} new)")
                                
                        except Exception as e:
                            self.logger.warning(f"⚠️ Failed to merge table {table}: {e}")
                            continue
                    
                    # Commit all changes
                    target_conn.commit()
            
            # Final integrity check
            if self.validate_database_integrity(target_path):
                self.logger.info(f"✅ Successfully merged {source_path.name} into {target_path.name}")
                return True
            else:
                self.logger.error(f"❌ Target database integrity check failed after merge")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Merge operation failed: {e}")
            return False
    
    def archive_database(self, source_path: Path) -> bool:
        """🗂️ Archive database to archives folder"""
        try:
            # Ensure archives directory exists
            self.archives_path.mkdir(exist_ok=True)
            
            archive_file = self.archives_path / source_path.name
            
            # If file already exists in archives, create versioned name
            counter = 1
            while archive_file.exists():
                name_parts = source_path.stem, counter, source_path.suffix
                archive_file = self.archives_path / f"{name_parts[0]}_v{name_parts[1]}{name_parts[2]}"
                counter += 1
            
            shutil.move(str(source_path), str(archive_file))
            self.logger.info(f"🗂️ Archived {source_path.name} to {archive_file}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Archive operation failed for {source_path.name}: {e}")
            return False
    
    def remove_database(self, db_path: Path) -> bool:
        """🗑️ Safely remove database file"""
        try:
            if db_path.exists():
                size_mb = db_path.stat().st_size / (1024 * 1024)
                db_path.unlink()
                self.execution_results["size_saved_mb"] += size_mb
                self.execution_results["databases_removed"] += 1
                self.logger.info(f"🗑️ Removed {db_path.name} ({size_mb:.2f} MB)")
                return True
            else:
                self.logger.warning(f"⚠️ Database {db_path.name} not found for removal")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Remove operation failed for {db_path.name}: {e}")
            return False
    
    def create_consolidated_database(self, target_path: Path, source_paths: List[Path]) -> bool:
        """🏗️ Create new consolidated database from multiple sources"""
        try:
            self.logger.info(f"🏗️ Creating consolidated database {target_path.name}")
            
            # Validate all source databases first
            for source_path in source_paths:
                if not source_path.exists():
                    self.logger.error(f"❌ Source database {source_path.name} not found")
                    return False
                if not self.validate_database_integrity(source_path):
                    self.logger.error(f"❌ Source database {source_path.name} failed integrity check")
                    return False
            
            # Create new database
            with sqlite3.connect(str(target_path)) as target_conn:
                target_cursor = target_conn.cursor()
                
                # Merge each source database
                for source_path in source_paths:
                    self.logger.info(f"  📥 Merging {source_path.name}...")
                    
                    with sqlite3.connect(str(source_path)) as source_conn:
                        source_cursor = source_conn.cursor()
                        
                        # Get all tables in source
                        source_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                        source_tables = [row[0] for row in source_cursor.fetchall()]
                        
                        for table in source_tables:
                            try:
                                # Get table schema
                                source_cursor.execute(f"SELECT sql FROM sqlite_master WHERE name='{table}'")
                                schema_result = source_cursor.fetchone()
                                
                                if schema_result and schema_result[0]:
                                    table_schema = schema_result[0]
                                    
                                    # Create table if it doesn't exist
                                    try:
                                        target_cursor.execute(table_schema)
                                    except sqlite3.Error:
                                        # Table might already exist, continue
                                        pass
                                    
                                    # Get and insert data
                                    source_cursor.execute(f"SELECT * FROM `{table}`")
                                    rows = source_cursor.fetchall()
                                    
                                    if rows:
                                        # Get column info
                                        source_cursor.execute(f"PRAGMA table_info(`{table}`)")
                                        columns = [col[1] for col in source_cursor.fetchall()]
                                        
                                        # Prepare INSERT statement
                                        placeholders = ",".join(["?" for _ in columns])
                                        column_names = ",".join([f"`{col}`" for col in columns])
                                        
                                        insert_sql = f"INSERT OR IGNORE INTO `{table}` ({column_names}) VALUES ({placeholders})"
                                        
                                        # Insert data
                                        target_cursor.executemany(insert_sql, rows)
                                        inserted_count = target_cursor.rowcount
                                        
                                        self.logger.info(f"    📊 Merged {len(rows)} rows from {source_path.name}.{table} ({inserted_count} new)")
                                
                            except Exception as e:
                                self.logger.warning(f"⚠️ Failed to merge table {table} from {source_path.name}: {e}")
                                continue
                
                # Commit all changes
                target_conn.commit()
            
            # Validate the new database
            if self.validate_database_integrity(target_path):
                self.logger.info(f"✅ Successfully created consolidated database {target_path.name}")
                return True
            else:
                self.logger.error(f"❌ Consolidated database {target_path.name} failed integrity check")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Failed to create consolidated database {target_path.name}: {e}")
            return False

    def execute_consolidation_plan(self, plan_file: str) -> bool:
        """🚀 Execute the consolidation plan"""
        try:
            # Load plan
            with open(plan_file, 'r') as f:
                plan = json.load(f)
            
            self.logger.info(f"🚀 Starting consolidation execution from {plan_file}")
            self.logger.info(f"📊 Plan contains {len(plan['consolidation_actions'])} actions")
            
            # Create backup first
            if not self.create_full_backup():
                self.logger.error("❌ Backup creation failed, aborting consolidation")
                return False
            
            # Process each action
            for action in plan['consolidation_actions']:
                action_type = action['action']
                target = action.get('target')
                
                success = False
                
                if action_type == "MERGE_AND_REMOVE":
                    source = action['source']
                    source_path = self.databases_path / source
                    target_path = self.databases_path / target
                    
                    # Skip if source doesn't exist
                    if not source_path.exists():
                        self.logger.warning(f"⚠️ Source file {source} not found, skipping")
                        continue
                    
                    if target_path.exists():
                        # Merge first
                        if self.merge_databases(source_path, target_path):
                            # Then remove source
                            success = self.remove_database(source_path)
                        else:
                            self.logger.error(f"❌ Merge failed for {source}, skipping removal")
                    else:
                        self.logger.error(f"❌ Target {target} not found for merge operation")
                
                elif action_type == "MERGE_INTO_NEW":
                    sources = action['sources']
                    source_paths = [self.databases_path / src for src in sources]
                    target_path = self.databases_path / target
                    
                    # Check if all sources exist
                    missing_sources = [src for src in sources if not (self.databases_path / src).exists()]
                    if missing_sources:
                        self.logger.warning(f"⚠️ Missing sources {missing_sources}, skipping action")
                        continue
                    
                    # Create consolidated database
                    if self.create_consolidated_database(target_path, source_paths):
                        # Remove source databases
                        all_removed = True
                        for source_path in source_paths:
                            if not self.remove_database(source_path):
                                all_removed = False
                        success = all_removed
                    
                elif action_type == "MERGE_INTO_EXISTING":
                    sources = action['sources']
                    source_paths = [self.databases_path / src for src in sources]
                    target_path = self.databases_path / target
                    
                    # Check if target exists and all sources exist
                    if not target_path.exists():
                        self.logger.error(f"❌ Target {target} not found for merge operation")
                        continue
                        
                    missing_sources = [src for src in sources if not (self.databases_path / src).exists()]
                    if missing_sources:
                        self.logger.warning(f"⚠️ Missing sources {missing_sources}, skipping action")
                        continue
                    
                    # Merge each source into target
                    all_merged = True
                    for source_path in source_paths:
                        if not self.merge_databases(source_path, target_path):
                            all_merged = False
                            break
                    
                    if all_merged:
                        # Remove source databases
                        all_removed = True
                        for source_path in source_paths:
                            if not self.remove_database(source_path):
                                all_removed = False
                        success = all_removed
                
                elif action_type == "ARCHIVE_AND_REMOVE":
                    source = action['source']
                    source_path = self.databases_path / source
                    
                    if source_path.exists():
                        success = self.archive_database(source_path)
                    else:
                        self.logger.warning(f"⚠️ Source file {source} not found, skipping")
                        continue
                
                elif action_type == "REMOVE":
                    source = action['source']
                    source_path = self.databases_path / source
                    
                    if source_path.exists():
                        success = self.remove_database(source_path)
                    else:
                        self.logger.warning(f"⚠️ Source file {source} not found, skipping")
                        continue
                
                # Record result
                if success:
                    self.execution_results["actions_completed"].append(action)
                    self.logger.info(f"✅ Completed: {action_type}")
                else:
                    self.execution_results["actions_failed"].append(action)
                    self.logger.error(f"❌ Failed: {action_type}")
            
            # Final status
            completed = len(self.execution_results["actions_completed"])
            failed = len(self.execution_results["actions_failed"])
            total = completed + failed
            
            if failed == 0:
                self.execution_results["status"] = "SUCCESS"
                self.logger.info(f"🎊 Consolidation completed successfully! {completed}/{total} actions succeeded")
            else:
                self.execution_results["status"] = "PARTIAL_SUCCESS"
                self.logger.warning(f"⚠️ Consolidation completed with {failed} failures. {completed}/{total} actions succeeded")
            
            return failed == 0
            
        except Exception as e:
            self.logger.error(f"❌ Consolidation execution failed: {e}")
            self.execution_results["status"] = "FAILED"
            return False
    
    def validate_post_consolidation(self) -> bool:
        """🔍 Validate system functionality after consolidation"""
        try:
            self.logger.info("🔍 Performing post-consolidation validation...")
            
            # Count remaining databases
            remaining_dbs = list(self.databases_path.glob("*.db"))
            self.logger.info(f"📊 Remaining databases: {len(remaining_dbs)}")
            
            # Check integrity of remaining databases
            integrity_failures = []
            for db_path in remaining_dbs:
                if not self.validate_database_integrity(db_path):
                    integrity_failures.append(db_path.name)
            
            if integrity_failures:
                self.logger.error(f"❌ Integrity check failed for: {integrity_failures}")
                return False
            
            # Check key databases exist
            critical_dbs = ["production.db", "analytics.db", "deployment_logs.db"]
            missing_critical = []
            
            for critical_db in critical_dbs:
                if not (self.databases_path / critical_db).exists():
                    missing_critical.append(critical_db)
            
            if missing_critical:
                self.logger.error(f"❌ Critical databases missing: {missing_critical}")
                return False
            
            self.logger.info("✅ Post-consolidation validation passed")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Post-consolidation validation failed: {e}")
            return False
    
    def rollback_consolidation(self) -> bool:
        """🔄 Rollback consolidation if needed"""
        try:
            if not self.execution_results["rollback_available"]:
                self.logger.error("❌ No backup available for rollback")
                return False
            
            self.logger.info("🔄 Rolling back consolidation...")
            
            # Remove current databases
            for db_file in self.databases_path.glob("*.db"):
                db_file.unlink()
            
            # Restore from backup
            restored_count = 0
            for backup_file in self.backup_path.glob("*.db"):
                target_file = self.databases_path / backup_file.name
                shutil.copy2(backup_file, target_file)
                restored_count += 1
            
            self.logger.info(f"✅ Rollback completed: {restored_count} databases restored")
            self.execution_results["status"] = "ROLLED_BACK"
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Rollback failed: {e}")
            return False
    
    def save_execution_report(self) -> str:
        """💾 Save execution report"""
        report_file = f"consolidation_execution_report_{self.execution_timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump(self.execution_results, f, indent=2)
        
        self.logger.info(f"📄 Execution report saved to {report_file}")
        return report_file
    
    def print_summary(self):
        """📋 Print execution summary"""
        print("\n" + "="*80)
        print("🗄️  DATABASE CONSOLIDATION EXECUTION SUMMARY")
        print("="*80)
        
        print(f"⏰ Execution Time: {self.execution_timestamp}")
        print(f"📊 Status: {self.execution_results['status']}")
        print(f"✅ Actions Completed: {len(self.execution_results['actions_completed'])}")
        print(f"❌ Actions Failed: {len(self.execution_results['actions_failed'])}")
        print(f"🗑️ Databases Removed: {self.execution_results['databases_removed']}")
        print(f"💾 Size Saved: {self.execution_results['size_saved_mb']:.2f} MB")
        print(f"🛡️ Backup Available: {self.execution_results['rollback_available']}")


def main():
    """🚀 Main execution function"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python database_consolidation_executor.py <plan_file>")
        sys.exit(1)
    
    plan_file = sys.argv[1]
    
    if not Path(plan_file).exists():
        print(f"❌ Plan file {plan_file} not found")
        sys.exit(1)
    
    print("🗄️ DATABASE CONSOLIDATION EXECUTOR")
    print("="*50)
    
    executor = DatabaseConsolidationExecutor()
    
    # Execute consolidation
    success = executor.execute_consolidation_plan(plan_file)
    
    # Validate results
    if success:
        validation_success = executor.validate_post_consolidation()
        if not validation_success:
            print("❌ Post-consolidation validation failed. Consider rollback.")
            response = input("🔄 Perform rollback? (y/N): ")
            if response.lower() == 'y':
                executor.rollback_consolidation()
    
    # Print summary and save report
    executor.print_summary()
    report_file = executor.save_execution_report()
    
    print(f"\n📄 Full execution log: consolidation_execution_{executor.execution_timestamp}.log")
    print(f"📄 Execution report: {report_file}")
    
    return success


if __name__ == "__main__":
    main()