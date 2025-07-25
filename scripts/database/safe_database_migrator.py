#!/usr/bin/env python3
"""
🚀 SAFE DATABASE MIGRATION TOOL
Migrate logs.db to databases/logs.db with table renaming for schema conflicts
"""

import json
import os
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

from tqdm import tqdm


class SafeDatabaseMigrator:
    """🛡️ Safe Database Migration with Table Renaming"""
    
    def __init__(self):
        # MANDATORY: Start time logging
        self.start_time = datetime.now()
        print("🚀 SAFE DATABASE MIGRATOR STARTED")
        print(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Process ID: {os.getpid()}")
        print("="*60)
        
        # Database paths
        self.workspace_root = Path(os.getcwd())
        self.source_db = self.workspace_root / "logs.db"
        self.target_db = self.workspace_root / "databases" / "logs.db"
        
        # Migration report
        self.migration_report = {
            "start_time": self.start_time.isoformat(),
            "source_db": str(self.source_db),
            "target_db": str(self.target_db),
            "migration_status": "INITIATED",
            "tables_migrated": [],
            "records_migrated": 0,
            "conflicts_resolved": 0,
            "errors": []
        }
    
    def execute_safe_migration(self):
        """🛡️ Execute safe migration with table renaming"""
        
        print("🔍 PHASE 1: ANALYZING MIGRATION REQUIREMENTS")
        print("="*60)
        
        if not self.source_db.exists():
            print("✅ No source database found - migration not needed")
            self.migration_report["migration_status"] = "NOT_NEEDED"
            self.generate_migration_report()
            return
        
        # MANDATORY: Progress bar for migration phases
        with tqdm(total=100, desc="🚀 Safe Migration", unit="%") as pbar:
            
            # Phase 1: Analyze tables (20%)
            pbar.set_description("🔍 Analyzing tables")
            source_tables = self.get_source_tables()
            pbar.update(20)
            
            # Phase 2: Prepare target database (20%)
            pbar.set_description("🎯 Preparing target database")
            self.prepare_target_database()
            pbar.update(20)
            
            # Phase 3: Migrate tables with renaming (40%)
            pbar.set_description("🔄 Migrating tables")
            self.migrate_tables_with_renaming(source_tables)
            pbar.update(40)
            
            # Phase 4: Update references (20%)
            pbar.set_description("🔧 Updating references")
            self.update_tool_references()
            pbar.update(20)
        
        # Cleanup source database
        self.cleanup_source_database()
        
        # Generate final report
        self.generate_migration_report()
    
    def get_source_tables(self):
        """📊 Get all tables from source database"""
        tables = []
        
        try:
            with sqlite3.connect(str(self.source_db)) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                table_results = cursor.fetchall()
                
                for table_name, in table_results:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    
                    tables.append({
                        "name": table_name,
                        "record_count": count
                    })
                    
                    print(f"📋 Found table: {table_name} ({count} records)")
        
        except Exception as e:
            error_msg = f"Source analysis error: {str(e)}"
            print(f"❌ {error_msg}")
            self.migration_report["errors"].append(error_msg)
        
        return tables
    
    def prepare_target_database(self):
        """🎯 Ensure target database exists and is accessible"""
        try:
            self.target_db.parent.mkdir(parents=True, exist_ok=True)
            
            # Test connection
            with sqlite3.connect(str(self.target_db)) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                existing_tables = [row[0] for row in cursor.fetchall()]
                
                print(f"🎯 Target database accessible with {len(existing_tables)} existing tables")
                
        except Exception as e:
            error_msg = f"Target preparation error: {str(e)}"
            print(f"❌ {error_msg}")
            self.migration_report["errors"].append(error_msg)
    
    def migrate_tables_with_renaming(self, source_tables):
        """🔄 Migrate tables with intelligent renaming for conflicts"""
        
        total_records = sum(table["record_count"] for table in source_tables)
        
        if total_records == 0:
            print("ℹ️ No records to migrate")
            return
        
        # Sub-progress for table migration
        with tqdm(total=total_records, desc="🔄 Migrating Records", unit="records") as pbar:
            
            try:
                # Connect to both databases
                source_conn = sqlite3.connect(str(self.source_db))
                target_conn = sqlite3.connect(str(self.target_db))
                
                source_cursor = source_conn.cursor()
                target_cursor = target_conn.cursor()
                
                # Get existing target tables
                target_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                existing_tables = [row[0] for row in target_cursor.fetchall()]
                
                for table_info in source_tables:
                    table_name = table_info["name"]
                    record_count = table_info["record_count"]
                    
                    pbar.set_description(f"🔄 Migrating {table_name}")
                    
                    # Determine target table name
                    if table_name in existing_tables:
                        # Rename to avoid conflict
                        target_table_name = f"archive_{table_name}"
                        print(f"🔄 Renaming {table_name} → {target_table_name} (conflict resolution)")
                        self.migration_report["conflicts_resolved"] += 1
                    else:
                        target_table_name = table_name
                    
                    # Get table schema
                    source_cursor.execute(f"SELECT sql FROM sqlite_master WHERE name='{table_name}'")
                    schema_result = source_cursor.fetchone()
                    
                    if schema_result:
                        # Modify CREATE statement for new table name
                        create_sql = schema_result[0].replace(
                            f"CREATE TABLE {table_name}",
                            f"CREATE TABLE {target_table_name}",
                        )
                        
                        # Create table in target
                        target_cursor.execute(create_sql)
                        
                        # Copy data
                        source_cursor.execute(f"SELECT * FROM {table_name}")
                        rows = source_cursor.fetchall()
                        
                        if rows:
                            # Prepare INSERT statement
                            placeholders = ','.join(['?' for _ in rows[0]])
                            insert_sql = f"INSERT INTO {target_table_name} VALUES ({placeholders})"
                            
                            # Insert all rows
                            target_cursor.executemany(insert_sql, rows)
                            
                            self.migration_report["records_migrated"] += len(rows)
                            pbar.update(len(rows))
                        
                        self.migration_report["tables_migrated"].append({
                            "source_table": table_name,
                            "target_table": target_table_name,
                            "records_migrated": len(rows) if rows else 0
                        })
                        
                        print(f"✅ Migrated {table_name} → {target_table_name} ({len(rows) if rows else 0} records)")
                    
                    else:
                        pbar.update(record_count)  # Skip this table
                
                # Commit all changes
                target_conn.commit()
                
                # Close connections
                source_conn.close()
                target_conn.close()
                
                self.migration_report["migration_status"] = "SUCCESS"
                print("✅ Migration completed successfully")
                
            except Exception as e:
                error_msg = f"Migration error: {str(e)}"
                print(f"❌ {error_msg}")
                self.migration_report["errors"].append(error_msg)
                self.migration_report["migration_status"] = "ERROR"
    
    def update_tool_references(self):
        """🔧 Update tool references to use correct database path"""
        
        tools_to_update = [
            "archive_migration_executor.py",
            "database_consistency_checker.py"
        ]
        
        updated_tools = []
        
        for tool_file in tools_to_update:
            tool_path = self.workspace_root / tool_file
            if tool_path.exists():
                try:
                    content = tool_path.read_text(encoding='utf-8')
                    original_content = content
                    
                    # Update database path references
                    content = content.replace(
                        'self.logs_db = "logs.db"',
                        'self.logs_db = "databases/logs.db"'
                    ).replace(
                        '"logs.db"',
                        '"databases/logs.db"'
                    ).replace(
                        "'logs.db'",
                        "'databases/logs.db'"
                    )
                    
                    if content != original_content:
                        tool_path.write_text(content, encoding='utf-8')
                        print(f"✅ Updated {tool_file}")
                        updated_tools.append(tool_file)
                    else:
                        print(f"ℹ️ No updates needed for {tool_file}")
                
                except Exception as e:
                    error_msg = f"Tool update error in {tool_file}: {str(e)}"
                    print(f"❌ {error_msg}")
                    self.migration_report["errors"].append(error_msg)
            else:
                print(f"⚠️ Tool file not found: {tool_file}")
        
        self.migration_report["updated_tools"] = updated_tools
    
    def cleanup_source_database(self):
        """🗑️ Clean up source database after successful migration"""
        
        if self.migration_report["migration_status"] != "SUCCESS":
            print("⚠️ Skipping cleanup due to migration errors")
            return
        
        try:
            if self.source_db.exists():
                # Create backup
                backup_name = f"logs_migrated_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                backup_root = Path(os.getenv("GH_COPILOT_BACKUP_ROOT", "/tmp/gh_COPILOT_Backups"))
                backup_path = backup_root / backup_name
                backup_path.parent.mkdir(exist_ok=True)
                
                shutil.move(str(self.source_db), str(backup_path))
                print(f"📦 Moved source database to backup: {backup_path}")
                self.migration_report["backup_location"] = str(backup_path)
        
        except Exception as e:
            error_msg = f"Cleanup error: {str(e)}"
            print(f"❌ {error_msg}")
            self.migration_report["errors"].append(error_msg)
    
    def generate_migration_report(self):
        """📋 Generate comprehensive migration report"""
        
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        self.migration_report["end_time"] = end_time.isoformat()
        self.migration_report["duration_seconds"] = duration
        
        # Generate report file
        report_path = self.workspace_root / f"safe_migration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.migration_report, f, indent=2)
        
        print("="*60)
        print("✅ SAFE DATABASE MIGRATION COMPLETED")
        print("="*60)
        print(f"Migration Status: {self.migration_report['migration_status']}")
        print(f"Tables Migrated: {len(self.migration_report.get('tables_migrated', []))}")
        print(f"Records Migrated: {self.migration_report.get('records_migrated', 0)}")
        print(f"Conflicts Resolved: {self.migration_report.get('conflicts_resolved', 0)}")
        print(f"Duration: {duration:.2f} seconds")
        print(f"Report Generated: {report_path}")
        
        if self.migration_report["errors"]:
            print(f"⚠️ Errors Encountered: {len(self.migration_report['errors'])}")
            for error in self.migration_report["errors"]:
                print(f"   - {error}")
        
        print("="*60)

def main():
    """🎯 Main execution function"""
    migrator = SafeDatabaseMigrator()
    migrator.execute_safe_migration()

if __name__ == "__main__":
    main()
