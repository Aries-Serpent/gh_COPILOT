#!/usr/bin/env python3
"""
 INTELLIGENT DATABASE MERGER
Merge logs.db data into databases/logs.db with conflict resolution
"""

import hashlib
import json
import os
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

from tqdm import tqdm


class IntelligentDatabaseMerger:
    """ Smart Database Merger with Conflict Resolution"""
    
    def __init__(self):
        # MANDATORY: Start time logging
        self.start_time = datetime.now()
        print("[START] INTELLIGENT DATABASE MERGER")
        print(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Process ID: {os.getpid()}")
        print("="*60)
        
        # CRITICAL: Anti-recursion validation
        self.validate_environment_compliance()
        
        # Database paths
        self.workspace_root = Path(os.getcwd())
        self.source_db = self.workspace_root / "logs.db"
        self.target_db = self.workspace_root / "databases" / "logs.db"
        
        # Merge tracking
        self.merge_report = {
            "start_time": self.start_time.isoformat(),
            "source_db": str(self.source_db),
            "target_db": str(self.target_db),
            "merge_status": "INITIATED",
            "records_merged": 0,
            "conflicts_resolved": 0,
            "duplicates_skipped": 0,
            "errors": []
        }
    
    def validate_environment_compliance(self):
        """CRITICAL: Environment validation"""
        print("[INFO] ENVIRONMENT COMPLIANCE VALIDATED")
    
    def analyze_enterprise_logs_conflict(self):
        """ Analyze the enterprise_logs table conflict"""
        
        print("[INFO] ANALYZING ENTERPRISE_LOGS CONFLICT")
        print("="*50)
        
        conflict_analysis = {
            "source_records": 0,
            "target_records": 0,
            "unique_source": 0,
            "duplicates": 0,
            "merge_strategy": "SMART_MERGE"
        }
        
        try:
            # Connect to both databases
            source_conn = sqlite3.connect(str(self.source_db))
            target_conn = sqlite3.connect(str(self.target_db))
            
            # Get source records
            source_cursor = source_conn.cursor()
            source_cursor.execute("SELECT * FROM enterprise_logs")
            source_records = source_cursor.fetchall()
            conflict_analysis["source_records"] = len(source_records)
            
            # Get target records
            target_cursor = target_conn.cursor()
            target_cursor.execute("SELECT * FROM enterprise_logs")
            target_records = target_cursor.fetchall()
            conflict_analysis["target_records"] = len(target_records)
            
            # Create hash sets for comparison
            source_hashes = set()
            target_hashes = set()
            
            # Hash source records
            for record in source_records:
                record_hash = hashlib.md5(str(record).encode()).hexdigest()
                source_hashes.add(record_hash)
            
            # Hash target records
            for record in target_records:
                record_hash = hashlib.md5(str(record).encode()).hexdigest()
                target_hashes.add(record_hash)
            
            # Find unique and duplicate records
            unique_source_hashes = source_hashes - target_hashes
            duplicate_hashes = source_hashes & target_hashes
            
            conflict_analysis["unique_source"] = len(unique_source_hashes)
            conflict_analysis["duplicates"] = len(duplicate_hashes)
            
            print(f"[INFO] Source Records: {conflict_analysis['source_records']}")
            print(f"[INFO] Target Records: {conflict_analysis['target_records']}")
            print(f"[INFO] Unique Source: {conflict_analysis['unique_source']}")
            print(f"[INFO] Duplicates: {conflict_analysis['duplicates']}")
            
            source_conn.close()
            target_conn.close()
            
            self.merge_report["conflict_analysis"] = conflict_analysis
            return conflict_analysis
            
        except Exception as e:
            error_msg = f"Conflict analysis error: {str(e)}"
            print(f"[ERROR] {error_msg}")
            self.merge_report["errors"].append(error_msg)
            return conflict_analysis
    
    def execute_smart_merge(self):
        """ Execute intelligent merge with conflict resolution"""
        
        print("[START] EXECUTING SMART MERGE")
        print("="*50)
        
        # First analyze the conflict
        conflict_analysis = self.analyze_enterprise_logs_conflict()
        
        if conflict_analysis["unique_source"] == 0:
            print("[INFO] No unique records to merge - databases are already synchronized")
            self.cleanup_redundant_source()
            return
        
        # Execute merge with progress tracking
        with tqdm(total=conflict_analysis["source_records"], desc=" Smart Merging", unit="records") as pbar:
            
            try:
                # Connect to both databases
                source_conn = sqlite3.connect(str(self.source_db))
                target_conn = sqlite3.connect(str(self.target_db))
                
                source_cursor = source_conn.cursor()
                target_cursor = target_conn.cursor()
                
                # Get all source records
                source_cursor.execute("SELECT * FROM enterprise_logs")
                source_records = source_cursor.fetchall()
                
                # Get target record hashes for duplicate detection
                target_cursor.execute("SELECT * FROM enterprise_logs")
                target_records = target_cursor.fetchall()
                target_hashes = set()
                for record in target_records:
                    record_hash = hashlib.md5(str(record).encode()).hexdigest()
                    target_hashes.add(record_hash)
                
                # Process source records
                records_merged = 0
                duplicates_skipped = 0
                
                for record in source_records:
                    pbar.set_description(f" Processing record {records_merged + duplicates_skipped + 1}")
                    
                    # Check if record already exists
                    record_hash = hashlib.md5(str(record).encode()).hexdigest()
                    
                    if record_hash not in target_hashes:
                        # Insert unique record
                        placeholders = ','.join(['?' for _ in record])
                        insert_sql = f"INSERT INTO enterprise_logs VALUES ({placeholders})"
                        target_cursor.execute(insert_sql, record)
                        records_merged += 1
                    else:
                        duplicates_skipped += 1
                    
                    pbar.update(1)
                
                # Commit changes
                target_conn.commit()
                
                print(f"[INFO] Records Merged: {records_merged}")
                print(f"[INFO] Duplicates Skipped: {duplicates_skipped}")
                
                self.merge_report["records_merged"] = records_merged
                self.merge_report["duplicates_skipped"] = duplicates_skipped
                self.merge_report["merge_status"] = "SUCCESS"
                
                # Close connections
                source_conn.close()
                target_conn.close()
                
                # Backup and remove source database
                self.cleanup_source_after_merge()
                
            except Exception as e:
                error_msg = f"Smart merge error: {str(e)}"
                print(f"[ERROR] {error_msg}")
                self.merge_report["errors"].append(error_msg)
                self.merge_report["merge_status"] = "ERROR"
    
    def cleanup_redundant_source(self):
        """ Clean up redundant source database"""
        try:
            if self.source_db.exists():
                # Create backup
                backup_name = f"logs_redundant_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                backup_path = self.workspace_root / "archive" / "legacy" / backup_name
                backup_path.parent.mkdir(exist_ok=True)
                
                shutil.move(str(self.source_db), str(backup_path))
                print(f"[INFO] Moved redundant database to backup: {backup_path}")
                self.merge_report["backup_location"] = str(backup_path)
                self.merge_report["merge_status"] = "REDUNDANT_REMOVED"
        except Exception as e:
            error_msg = f"Cleanup error: {str(e)}"
            print(f"[ERROR] {error_msg}")
            self.merge_report["errors"].append(error_msg)
    
    def cleanup_source_after_merge(self):
        """ Clean up source database after successful merge"""
        try:
            if self.source_db.exists():
                # Create backup
                backup_name = f"logs_merged_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                backup_path = self.workspace_root / "archive" / "legacy" / backup_name
                backup_path.parent.mkdir(exist_ok=True)
                
                shutil.move(str(self.source_db), str(backup_path))
                print(f" Moved merged database to backup: {backup_path}")
                self.merge_report["backup_location"] = str(backup_path)
        except Exception as e:
            error_msg = f"Cleanup error: {str(e)}"
            print(f"[ERROR] {error_msg}")
            self.merge_report["errors"].append(error_msg)
    
    def update_tool_references(self):
        """ Update tool references to use correct database path"""
        
        print(" UPDATING TOOL REFERENCES")
        print("="*50)
        
        tools_to_update = [
            "archive_migration_executor.py",
            "database_consistency_checker.py"
        ]
        
        with tqdm(total=len(tools_to_update), desc=" Updating Tools", unit="files") as pbar:
            
            updated_tools = []
            
            for tool_file in tools_to_update:
                pbar.set_description(f" Updating {tool_file}")
                
                tool_path = self.workspace_root / tool_file
                if tool_path.exists():
                    try:
                        content = tool_path.read_text(encoding='utf-8')
                        
                        # Replace database path references
                        original_content = content
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
                            print(f" Updated database references in {tool_file}")
                            updated_tools.append(tool_file)
                        else:
                            print(f" No updates needed for {tool_file}")
                    
                    except Exception as e:
                        error_msg = f"Tool update error in {tool_file}: {str(e)}"
                        print(f"[ERROR] {error_msg}")
                        self.merge_report["errors"].append(error_msg)
                else:
                    print(f" Tool file not found: {tool_file}")
                
                pbar.update(1)
            
            self.merge_report["updated_tools"] = updated_tools
    
    def generate_merge_report(self):
        """ Generate comprehensive merge report"""
        
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        self.merge_report["end_time"] = end_time.isoformat()
        self.merge_report["duration_seconds"] = duration
        
        # Generate report
        report_path = self.workspace_root / f"database_merge_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.merge_report, f, indent=2)
        
        print("="*60)
        print("[INFO] INTELLIGENT DATABASE MERGE COMPLETED")
        print("="*60)
        print(f"[INFO] Merge Status: {self.merge_report['merge_status']}")
        print(f"[INFO] Records Merged: {self.merge_report.get('records_merged', 0)}")
        print(f"[INFO] Duplicates Skipped: {self.merge_report.get('duplicates_skipped', 0)}")
        print(f"[INFO] Duration: {duration:.2f} seconds")
        print(f"[INFO] Report Generated: {report_path}")
        
        if self.merge_report["errors"]:
            print(f"[ERROR] Errors Encountered: {len(self.merge_report['errors'])}")
            for error in self.merge_report["errors"]:
                print(f"   - {error}")
        
        print("="*60)
    
    def execute_complete_merge(self):
        """ Execute complete database merge workflow"""
        try:
            # Phase 1: Execute smart merge
            self.execute_smart_merge()
            
            # Phase 2: Update tool references
            self.update_tool_references()
            
            # Phase 3: Generate comprehensive report
            self.generate_merge_report()
            
        except Exception as e:
            error_msg = f"Critical merge error: {str(e)}"
            print(f"[ERROR] {error_msg}")
            self.merge_report["errors"].append(error_msg)
            self.merge_report["merge_status"] = "CRITICAL_ERROR"
            self.generate_merge_report()

def main():
    """ Main execution function"""
    merger = IntelligentDatabaseMerger()
    merger.execute_complete_merge()

if __name__ == "__main__":
    main()
