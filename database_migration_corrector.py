#!/usr/bin/env python3
"""
🔄 DATABASE MIGRATION CORRECTOR
Migrate logs.db from root to databases/ folder with data preservation
"""

import os
import sys
import sqlite3
import shutil
from pathlib import Path
from datetime import datetime
from tqdm import tqdm
import json

class DatabaseMigrationCorrector:
    """🚀 Enterprise Database Migration with Visual Processing Indicators"""
    
    def __init__(self):
        # MANDATORY: Start time logging with enterprise formatting
        self.start_time = datetime.now()
        print(f"🚀 DATABASE MIGRATION CORRECTOR STARTED")
        print(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Process ID: {os.getpid()}")
        print("="*60)
        
        # CRITICAL: Anti-recursion validation
        self.validate_environment_compliance()
        
        # Database paths
        self.workspace_root = Path(os.getcwd())
        self.source_db = self.workspace_root / "logs.db"
        self.target_db = self.workspace_root / "databases" / "logs.db"
        
        # Migration tracking
        self.migration_report = {
            "start_time": self.start_time.isoformat(),
            "source_db": str(self.source_db),
            "target_db": str(self.target_db),
            "migration_status": "INITIATED",
            "tables_migrated": [],
            "records_migrated": 0,
            "errors": []
        }
    
    def validate_environment_compliance(self):
        """CRITICAL: Validate proper environment root usage"""
        workspace_root = Path(os.getcwd())
        proper_root = "E:/gh_COPILOT"
        
        if not str(workspace_root).replace("\\", "/").endswith("gh_COPILOT"):
            print(f"⚠️ Non-standard workspace root: {workspace_root}")
        
        print("✅ ENVIRONMENT COMPLIANCE VALIDATED")
    
    def analyze_database_structure(self, db_path: Path) -> dict:
        """📊 Analyze database structure and content"""
        if not db_path.exists():
            return {"exists": False, "tables": [], "total_records": 0}
        
        analysis = {
            "exists": True,
            "tables": [],
            "total_records": 0,
            "size_mb": db_path.stat().st_size / (1024 * 1024)
        }
        
        try:
            with sqlite3.connect(str(db_path)) as conn:
                cursor = conn.cursor()
                
                # Get all tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                
                for table_name, in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    
                    analysis["tables"].append({
                        "name": table_name,
                        "record_count": count
                    })
                    analysis["total_records"] += count
                    
        except Exception as e:
            analysis["error"] = str(e)
        
        return analysis
    
    def migrate_database_content(self):
        """🔄 Migrate database content with visual progress indicators"""
        
        print("🔍 PHASE 1: DATABASE ANALYSIS")
        print("="*60)
        
        # MANDATORY: Progress bar for analysis phase
        with tqdm(total=100, desc="📊 Analyzing Databases", unit="%") as pbar:
            
            # Analyze source database
            pbar.set_description("🔍 Analyzing source database")
            source_analysis = self.analyze_database_structure(self.source_db)
            pbar.update(50)
            
            # Analyze target database
            pbar.set_description("🎯 Analyzing target database")
            target_analysis = self.analyze_database_structure(self.target_db)
            pbar.update(50)
        
        print(f"📊 Source DB Analysis: {json.dumps(source_analysis, indent=2)}")
        print(f"🎯 Target DB Analysis: {json.dumps(target_analysis, indent=2)}")
        
        # Update migration report
        self.migration_report["source_analysis"] = source_analysis
        self.migration_report["target_analysis"] = target_analysis
        
        # Determine migration strategy
        if not source_analysis["exists"]:
            print("✅ No source database found - migration not needed")
            self.migration_report["migration_status"] = "NOT_NEEDED"
            return
        
        if source_analysis["total_records"] == 0:
            print("🗑️ Source database is empty - safe to remove")
            self.cleanup_empty_source_database()
            return
        
        # Execute migration with progress tracking
        self.execute_data_migration(source_analysis, target_analysis)
    
    def execute_data_migration(self, source_analysis: dict, target_analysis: dict):
        """🚀 Execute actual data migration with visual indicators"""
        
        print("🚀 PHASE 2: DATA MIGRATION")
        print("="*60)
        
        total_records = source_analysis["total_records"]
        migrated_records = 0
        
        # MANDATORY: Progress bar for migration
        with tqdm(total=total_records, desc="🔄 Migrating Data", unit="records") as pbar:
            
            try:
                # Connect to both databases
                source_conn = sqlite3.connect(str(self.source_db))
                target_conn = sqlite3.connect(str(self.target_db))
                
                source_cursor = source_conn.cursor()
                target_cursor = target_conn.cursor()
                
                # Migrate each table
                for table_info in source_analysis["tables"]:
                    table_name = table_info["name"]
                    record_count = table_info["record_count"]
                    
                    pbar.set_description(f"🔄 Migrating table: {table_name}")
                    
                    # Get table schema
                    source_cursor.execute(f"SELECT sql FROM sqlite_master WHERE name='{table_name}'")
                    schema = source_cursor.fetchone()
                    
                    if schema:
                        # Create table in target if not exists
                        target_cursor.execute(schema[0])
                        
                        # Copy data
                        source_cursor.execute(f"SELECT * FROM {table_name}")
                        rows = source_cursor.fetchall()
                        
                        # Get column info for INSERT statement
                        source_cursor.execute(f"PRAGMA table_info({table_name})")
                        columns = [col[1] for col in source_cursor.fetchall()]
                        placeholders = ','.join(['?' for _ in columns])
                        
                        insert_sql = f"INSERT OR REPLACE INTO {table_name} VALUES ({placeholders})"
                        target_cursor.executemany(insert_sql, rows)
                        
                        migrated_records += record_count
                        pbar.update(record_count)
                        
                        self.migration_report["tables_migrated"].append({
                            "table_name": table_name,
                            "records_migrated": record_count
                        })
                
                # Commit changes
                target_conn.commit()
                
                # Close connections
                source_conn.close()
                target_conn.close()
                
                self.migration_report["records_migrated"] = migrated_records
                self.migration_report["migration_status"] = "SUCCESS"
                
                print(f"✅ Successfully migrated {migrated_records} records")
                
                # Remove source database after successful migration
                self.cleanup_source_database_after_migration()
                
            except Exception as e:
                error_msg = f"Migration error: {str(e)}"
                print(f"❌ {error_msg}")
                self.migration_report["errors"].append(error_msg)
                self.migration_report["migration_status"] = "ERROR"
    
    def cleanup_empty_source_database(self):
        """🗑️ Remove empty source database"""
        try:
            if self.source_db.exists():
                self.source_db.unlink()
                print(f"🗑️ Removed empty source database: {self.source_db}")
                self.migration_report["migration_status"] = "CLEANED_EMPTY"
        except Exception as e:
            error_msg = f"Cleanup error: {str(e)}"
            print(f"❌ {error_msg}")
            self.migration_report["errors"].append(error_msg)
    
    def cleanup_source_database_after_migration(self):
        """🗑️ Remove source database after successful migration"""
        try:
            if self.source_db.exists():
                # Create backup name with timestamp
                backup_name = f"logs_migrated_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                backup_path = self.workspace_root / "_MANUAL_DELETE_FOLDER" / backup_name
                
                # Ensure backup directory exists
                backup_path.parent.mkdir(exist_ok=True)
                
                # Move to backup location
                shutil.move(str(self.source_db), str(backup_path))
                print(f"📦 Moved source database to backup: {backup_path}")
                self.migration_report["backup_location"] = str(backup_path)
        except Exception as e:
            error_msg = f"Backup error: {str(e)}"
            print(f"❌ {error_msg}")
            self.migration_report["errors"].append(error_msg)
    
    def update_tool_references(self):
        """🔧 Update tool references to use correct database path"""
        
        print("🔧 PHASE 3: UPDATING TOOL REFERENCES")
        print("="*60)
        
        tools_to_update = [
            "archive_migration_executor.py",
            "database_consistency_checker.py",
            "future_file_routing_validator.py"
        ]
        
        # MANDATORY: Progress bar for tool updates
        with tqdm(total=len(tools_to_update), desc="🔧 Updating Tools", unit="files") as pbar:
            
            for tool_file in tools_to_update:
                pbar.set_description(f"🔧 Updating {tool_file}")
                
                tool_path = self.workspace_root / tool_file
                if tool_path.exists():
                    try:
                        # Read file content
                        content = tool_path.read_text(encoding='utf-8')
                        
                        # Replace incorrect database path references
                        updated_content = content.replace(
                            'logs.db',
                            'databases/logs.db'
                        ).replace(
                            '"logs.db"',
                            '"databases/logs.db"'
                        ).replace(
                            "'logs.db'",
                            "'databases/logs.db'"
                        )
                        
                        # Write updated content
                        if updated_content != content:
                            tool_path.write_text(updated_content, encoding='utf-8')
                            print(f"✅ Updated database references in {tool_file}")
                            self.migration_report["updated_tools"] = self.migration_report.get("updated_tools", [])
                            self.migration_report["updated_tools"].append(tool_file)
                        else:
                            print(f"ℹ️ No updates needed for {tool_file}")
                    
                    except Exception as e:
                        error_msg = f"Tool update error in {tool_file}: {str(e)}"
                        print(f"❌ {error_msg}")
                        self.migration_report["errors"].append(error_msg)
                else:
                    print(f"⚠️ Tool file not found: {tool_file}")
                
                pbar.update(1)
    
    def generate_migration_report(self):
        """📋 Generate comprehensive migration report"""
        
        # MANDATORY: Completion summary
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        self.migration_report["end_time"] = end_time.isoformat()
        self.migration_report["duration_seconds"] = duration
        
        # Generate report
        report_path = self.workspace_root / f"database_migration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.migration_report, f, indent=2)
        
        print("="*60)
        print("✅ DATABASE MIGRATION COMPLETED")
        print("="*60)
        print(f"Migration Status: {self.migration_report['migration_status']}")
        print(f"Records Migrated: {self.migration_report.get('records_migrated', 0)}")
        print(f"Tables Migrated: {len(self.migration_report.get('tables_migrated', []))}")
        print(f"Duration: {duration:.2f} seconds")
        print(f"Report Generated: {report_path}")
        
        if self.migration_report["errors"]:
            print(f"⚠️ Errors Encountered: {len(self.migration_report['errors'])}")
            for error in self.migration_report["errors"]:
                print(f"   - {error}")
        
        print("="*60)
    
    def execute_complete_migration(self):
        """🚀 Execute complete database migration workflow"""
        try:
            # Phase 1: Migrate database content
            self.migrate_database_content()
            
            # Phase 2: Update tool references
            self.update_tool_references()
            
            # Phase 3: Generate comprehensive report
            self.generate_migration_report()
            
        except Exception as e:
            error_msg = f"Critical migration error: {str(e)}"
            print(f"🚨 {error_msg}")
            self.migration_report["errors"].append(error_msg)
            self.migration_report["migration_status"] = "CRITICAL_ERROR"
            self.generate_migration_report()

def main():
    """🎯 Main execution function with enterprise monitoring"""
    migrator = DatabaseMigrationCorrector()
    migrator.execute_complete_migration()

if __name__ == "__main__":
    main()
