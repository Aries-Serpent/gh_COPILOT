#!/usr/bin/env python3
"""
Database-File System Synchronization Validator
===============================================

This script performs a comprehensive comparison between scripts stored in the file system
and scripts tracked in databases to ensure full database-first architecture compliance.

Validates:
- All scripts exist in both file system and database
- Database-consumed scripts are reproducible 
- Script content synchronization
- Missing scripts in either location
- Database-first architecture compliance
"""

import os
import sqlite3
import hashlib
import json
from datetime import datetime
from pathlib import Path
import logging

class DatabaseFileSystemValidator:
    def __init__(self, workspace_root="e:\\gh_COPILOT"):
        self.workspace_root = Path(workspace_root)
        self.database_dir = self.workspace_root / "databases"
        self.results = {
            "file_system_scripts": {},
            "database_scripts": {},
            "synchronized_scripts": [],
            "missing_in_database": [],
            "missing_in_filesystem": [],
            "content_mismatches": [],
            "reproducible_scripts": [],
            "database_only_scripts": [],
            "summary": {}
        }
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def get_file_hash(self, file_path):
        """Calculate SHA256 hash of file content"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            return hashlib.sha256(content.encode('utf-8')).hexdigest()
        except Exception as e:
            self.logger.warning(f"Could not hash {file_path}: {e}")
            return None

    def scan_file_system_scripts(self):
        """Scan file system for all Python scripts"""
        self.logger.info("Scanning file system for Python scripts...")
        
        python_files = list(self.workspace_root.rglob("*.py"))
        
        for file_path in python_files:
            try:
                relative_path = file_path.relative_to(self.workspace_root)
                file_hash = self.get_file_hash(file_path)
                file_size = file_path.stat().st_size
                
                self.results["file_system_scripts"][str(relative_path)] = {
                    "absolute_path": str(file_path),
                    "size": file_size,
                    "hash": file_hash,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                }
            except Exception as e:
                self.logger.warning(f"Error processing {file_path}: {e}")
        
        self.logger.info(f"Found {len(self.results['file_system_scripts'])} Python files in file system")

    def scan_database_scripts(self):
        """Scan all databases for tracked scripts"""
        self.logger.info("Scanning databases for tracked scripts...")
        
        databases = [
            "production.db",
            "analytics.db", 
            "development.db",
            "staging.db",
            "script_generation.db"
        ]
        
        for db_name in databases:
            db_path = self.database_dir / db_name
            if db_path.exists():
                self._scan_single_database(db_path, db_name)
        
        self.logger.info(f"Found {len(self.results['database_scripts'])} scripts tracked in databases")

    def _scan_single_database(self, db_path, db_name):
        """Scan a single database for script tracking tables"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get all table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [t[0] for t in cursor.fetchall()]
            
            # Look for script-related tables
            script_tables = [t for t in tables if any(keyword in t.lower() 
                           for keyword in ['script', 'file', 'code', 'template'])]
            
            for table in script_tables:
                self._extract_scripts_from_table(cursor, table, db_name)
            
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error scanning database {db_path}: {e}")

    def _extract_scripts_from_table(self, cursor, table_name, db_name):
        """Extract script information from a specific table"""
        try:
            # Get table schema
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [col[1] for col in cursor.fetchall()]
            
            # Look for relevant columns
            path_col = None
            content_col = None
            hash_col = None
            size_col = None
            
            for col in columns:
                if any(keyword in col.lower() for keyword in ['path', 'name']):
                    path_col = col
                elif any(keyword in col.lower() for keyword in ['content', 'code', 'template']):
                    content_col = col
                elif 'hash' in col.lower():
                    hash_col = col
                elif 'size' in col.lower():
                    size_col = col
            
            if path_col:
                # Get all records
                cursor.execute(f"SELECT * FROM {table_name}")
                records = cursor.fetchall()
                
                for record in records:
                    record_dict = dict(zip(columns, record))
                    script_path = record_dict.get(path_col, "")
                    
                    if script_path and script_path.endswith('.py'):
                        # Normalize path
                        normalized_path = script_path.replace('\\', '/').lstrip('/')
                        
                        script_info = {
                            "database": db_name,
                            "table": table_name,
                            "content": record_dict.get(content_col, ""),
                            "hash": record_dict.get(hash_col, ""),
                            "size": record_dict.get(size_col, 0),
                            "full_record": record_dict
                        }
                        
                        # Use a unique key for database scripts
                        key = f"{db_name}:{table_name}:{normalized_path}"
                        self.results["database_scripts"][key] = script_info
                        
        except Exception as e:
            self.logger.warning(f"Error extracting from table {table_name}: {e}")

    def compare_scripts(self):
        """Compare file system scripts with database scripts"""
        self.logger.info("Comparing file system and database scripts...")
        
        # Normalize file system paths for comparison
        fs_normalized = {}
        for path, info in self.results["file_system_scripts"].items():
            normalized = path.replace('\\', '/')
            fs_normalized[normalized] = info
        
        # Check each database script
        for db_key, db_info in self.results["database_scripts"].items():
            db_name, table, script_path = db_key.split(':', 2)
            
            # Try to find matching file system script
            fs_match = None
            for fs_path, fs_info in fs_normalized.items():
                if script_path in fs_path or fs_path.endswith(script_path):
                    fs_match = (fs_path, fs_info)
                    break
            
            if fs_match:
                fs_path, fs_info = fs_match
                
                # Check if content can be reproduced from database
                db_content = db_info["content"]
                has_content = db_content and str(db_content).strip()
                
                if has_content:
                    # Compare hashes if available
                    if db_info["hash"] and fs_info["hash"]:
                        if db_info["hash"] == fs_info["hash"]:
                            self.results["synchronized_scripts"].append({
                                "path": script_path,
                                "fs_path": fs_path,
                                "database": db_name,
                                "table": table,
                                "status": "SYNCHRONIZED"
                            })
                        else:
                            self.results["content_mismatches"].append({
                                "path": script_path,
                                "fs_path": fs_path,
                                "database": db_name,
                                "table": table,
                                "fs_hash": fs_info["hash"],
                                "db_hash": db_info["hash"]
                            })
                    
                    # Mark as reproducible if database has content
                    content_length = len(str(db_content)) if has_content else 0
                    self.results["reproducible_scripts"].append({
                        "path": script_path,
                        "fs_path": fs_path,
                        "database": db_name,
                        "table": table,
                        "content_length": content_length
                    })
                else:
                    # Database has reference but no content
                    self.results["missing_in_database"].append({
                        "path": script_path,
                        "fs_path": fs_path,
                        "database": db_name,
                        "table": table,
                        "issue": "NO_CONTENT_IN_DATABASE"
                    })
            else:
                # Script exists in database but not in file system
                self.results["database_only_scripts"].append({
                    "path": script_path,
                    "database": db_name,
                    "table": table,
                    "has_content": bool(str(db_info["content"]).strip()) if db_info["content"] else False
                })
        
        # Check for file system scripts not in database
        for fs_path, fs_info in fs_normalized.items():
            found_in_db = False
            for db_key in self.results["database_scripts"]:
                _, _, script_path = db_key.split(':', 2)
                if script_path in fs_path or fs_path.endswith(script_path):
                    found_in_db = True
                    break
            
            if not found_in_db:
                self.results["missing_in_database"].append({
                    "path": fs_path,
                    "fs_path": fs_path,
                    "database": "NONE",
                    "table": "NONE",
                    "issue": "NOT_TRACKED_IN_DATABASE"
                })

    def generate_summary(self):
        """Generate summary statistics"""
        self.results["summary"] = {
            "total_file_system_scripts": len(self.results["file_system_scripts"]),
            "total_database_scripts": len(self.results["database_scripts"]),
            "synchronized_scripts": len(self.results["synchronized_scripts"]),
            "reproducible_scripts": len(self.results["reproducible_scripts"]),
            "missing_in_database": len(self.results["missing_in_database"]),
            "missing_in_filesystem": len(self.results["missing_in_filesystem"]),
            "content_mismatches": len(self.results["content_mismatches"]),
            "database_only_scripts": len(self.results["database_only_scripts"]),
            "database_first_compliance": {
                "reproducible_percentage": (len(self.results["reproducible_scripts"]) / 
                                          max(len(self.results["file_system_scripts"]), 1)) * 100,
                "synchronization_percentage": (len(self.results["synchronized_scripts"]) / 
                                              max(len(self.results["file_system_scripts"]), 1)) * 100,
                "database_coverage_percentage": ((len(self.results["file_system_scripts"]) - 
                                                 len(self.results["missing_in_database"])) / 
                                                max(len(self.results["file_system_scripts"]), 1)) * 100
            }
        }

    def save_results(self):
        """Save validation results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.workspace_root / f"database_filesystem_synchronization_report_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Results saved to {output_file}")
        return output_file

    def print_summary(self):
        """Print summary to console"""
        summary = self.results["summary"]
        compliance = summary["database_first_compliance"]
        
        print("\n" + "="*80)
        print("DATABASE-FILE SYSTEM SYNCHRONIZATION VALIDATION SUMMARY")
        print("="*80)
        
        print(f"\nFILE SYSTEM SCRIPTS: {summary['total_file_system_scripts']}")
        print(f"DATABASE TRACKED SCRIPTS: {summary['total_database_scripts']}")
        print(f"SYNCHRONIZED SCRIPTS: {summary['synchronized_scripts']}")
        print(f"REPRODUCIBLE SCRIPTS: {summary['reproducible_scripts']}")
        
        print(f"\nISSUES FOUND:")
        print(f"Missing in Database: {summary['missing_in_database']}")
        print(f"Missing in File System: {summary['missing_in_filesystem']}")
        print(f"Content Mismatches: {summary['content_mismatches']}")
        print(f"Database-Only Scripts: {summary['database_only_scripts']}")
        
        print(f"\nDATABASE-FIRST COMPLIANCE:")
        print(f"Reproducible Coverage: {compliance['reproducible_percentage']:.1f}%")
        print(f"Synchronization Rate: {compliance['synchronization_percentage']:.1f}%")
        print(f"Database Coverage: {compliance['database_coverage_percentage']:.1f}%")
        
        # Determine overall compliance status
        if compliance['database_coverage_percentage'] >= 95 and compliance['reproducible_percentage'] >= 90:
            status = "EXCELLENT"
        elif compliance['database_coverage_percentage'] >= 80 and compliance['reproducible_percentage'] >= 75:
            status = "GOOD"
        elif compliance['database_coverage_percentage'] >= 60 and compliance['reproducible_percentage'] >= 50:
            status = "NEEDS IMPROVEMENT"
        else:
            status = "CRITICAL - DATABASE-FIRST ARCHITECTURE NOT COMPLIANT"
        
        print(f"\nOVERALL STATUS: {status}")
        print("="*80)

    def run_validation(self):
        """Run complete validation process"""
        self.logger.info("Starting database-file system synchronization validation...")
        
        self.scan_file_system_scripts()
        self.scan_database_scripts()
        self.compare_scripts()
        self.generate_summary()
        
        self.print_summary()
        output_file = self.save_results()
        
        self.logger.info("Validation complete!")
        return output_file

def main():
    validator = DatabaseFileSystemValidator()
    output_file = validator.run_validation()
    
    print(f"\nDetailed results saved to: {output_file}")
    
    # Print some sample issues for immediate attention
    if validator.results["missing_in_database"]:
        print(f"\nSample scripts missing in database:")
        for i, missing in enumerate(validator.results["missing_in_database"][:5]):
            print(f"  {i+1}. {missing['path']} - {missing['issue']}")
    
    if validator.results["content_mismatches"]:
        print(f"\nSample content mismatches:")
        for i, mismatch in enumerate(validator.results["content_mismatches"][:3]):
            print(f"  {i+1}. {mismatch['path']} - Hash mismatch between FS and DB")

if __name__ == "__main__":
    main()
