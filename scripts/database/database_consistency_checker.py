#!/usr/bin/env python3
"""
🗄️ DATABASE CONSISTENCY CHECKER
==================================
Checks if log files within the logs/ folder are properly tracked in logs.db
and prepares for archive migration workflow.

Enterprise-grade database consistency validation with migration readiness assessment.
"""

import os
import sys
import json
import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set, Any
import hashlib

class DatabaseConsistencyChecker:
    def __init__(self):
        self.workspace_root = Path("e:/gh_COPILOT")
        self.logs_folder = self.workspace_root / "logs"
        self.archives_folder = self.workspace_root / "archives"
        
        # Database paths
        self.production_db = self.workspace_root / "production.db"
        self.logs_db = self.workspace_root / "logs.db"
        self.documentation_db = self.workspace_root / "documentation.db"
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.logs_folder / "database_consistency_check.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def scan_logs_folder(self) -> Dict[str, Dict]:
        """Scan the logs/ folder and catalog all files."""
        self.logger.info("📁 Scanning logs/ folder for all files...")
        
        log_files = {}
        
        if not self.logs_folder.exists():
            self.logger.warning("❌ logs/ folder does not exist")
            return log_files
        
        for file_path in self.logs_folder.rglob("*"):
            if file_path.is_file():
                # Calculate file hash for integrity checking
                try:
                    with open(file_path, 'rb') as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()
                except Exception as e:
                    file_hash = "ERROR"
                    self.logger.warning(f"⚠️ Could not hash {file_path}: {e}")
                
                relative_path = file_path.relative_to(self.logs_folder)
                
                log_files[str(relative_path)] = {
                    "full_path": str(file_path),
                    "size": file_path.stat().st_size,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                    "extension": file_path.suffix.lower(),
                    "hash": file_hash,
                    "is_log_file": self._is_log_file(file_path),
                    "archive_ready": False  # Will be determined later
                }
        
        self.logger.info(f"📊 Found {len(log_files)} files in logs/ folder")
        return log_files

    def _is_log_file(self, file_path: Path) -> bool:
        """Determine if a file is actually a log file."""
        log_extensions = {".log", ".txt"}
        log_keywords = ["log", "debug", "trace", "error", "session", "audit"]
        
        # Check extension
        if file_path.suffix.lower() in log_extensions:
            return True
        
        # Check filename for log keywords
        filename_lower = file_path.name.lower()
        for keyword in log_keywords:
            if keyword in filename_lower:
                return True
        
        return False

    def check_logs_db_existence(self) -> bool:
        """Check if logs.db exists and analyze its structure."""
        self.logger.info("🗄️ Checking logs.db database...")
        
        if not self.logs_db.exists():
            self.logger.warning("❌ logs.db does not exist")
            return False
        
        try:
            with sqlite3.connect(self.logs_db) as conn:
                cursor = conn.cursor()
                
                # Check if database has tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                
                if not tables:
                    self.logger.warning("⚠️ logs.db exists but has no tables")
                    return False
                
                self.logger.info(f"✅ logs.db exists with {len(tables)} tables")
                
                # List tables for reference
                table_names = [table[0] for table in tables]
                self.logger.info(f"📋 Tables in logs.db: {', '.join(table_names)}")
                
                return True
                
        except Exception as e:
            self.logger.error(f"❌ Error accessing logs.db: {e}")
            return False

    def check_documentation_db_logs(self) -> Dict[str, Any]:
        """Check what log files are stored in documentation.db."""
        self.logger.info("📚 Checking documentation.db for log entries...")
        
        log_entries = {}
        
        if not self.documentation_db.exists():
            self.logger.warning("❌ documentation.db does not exist")
            return log_entries
        
        try:
            with sqlite3.connect(self.documentation_db) as conn:
                cursor = conn.cursor()
                
                # Check if there's a docs table
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [table[0] for table in cursor.fetchall()]
                
                if 'docs' in tables:
                    # Query for log-related documents
                    cursor.execute("""
                        SELECT title, content_length, created_date, file_path 
                        FROM docs 
                        WHERE title LIKE '%log%' OR title LIKE '%debug%' OR title LIKE '%trace%'
                        ORDER BY title
                    """)
                    
                    log_docs = cursor.fetchall()
                    
                    for title, content_length, created_date, file_path in log_docs:
                        log_entries[title] = {
                            "content_length": content_length,
                            "created_date": created_date,
                            "file_path": file_path,
                            "in_database": True
                        }
                    
                    self.logger.info(f"📊 Found {len(log_docs)} log entries in documentation.db")
                else:
                    self.logger.warning("⚠️ No 'docs' table found in documentation.db")
                    
        except Exception as e:
            self.logger.error(f"❌ Error accessing documentation.db: {e}")
        
        return log_entries

    def analyze_migration_readiness(self, log_files: Dict[str, Dict], db_log_entries: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze which files are ready for archive migration."""
        self.logger.info("🔍 Analyzing migration readiness...")
        
        migration_analysis = {
            "ready_for_archive": [],
            "needs_database_entry": [],
            "database_only": [],
            "conflicting_entries": [],
            "total_files": len(log_files),
            "total_db_entries": len(db_log_entries)
        }
        
        # Files that exist in logs/ folder
        log_file_names = set(log_files.keys())
        
        # Files that exist in database
        db_entry_names = set(db_log_entries.keys())
        
        # Analyze each file in logs/ folder
        for filename, file_info in log_files.items():
            file_basename = Path(filename).stem
            
            # Check if file has corresponding database entry
            has_db_entry = any(file_basename in db_name for db_name in db_entry_names)
            
            if has_db_entry:
                migration_analysis["ready_for_archive"].append({
                    "file": filename,
                    "size": file_info["size"],
                    "modified": file_info["modified"],
                    "database_tracked": True,
                    "is_log_file": file_info["is_log_file"]
                })
            else:
                migration_analysis["needs_database_entry"].append({
                    "file": filename,
                    "size": file_info["size"],
                    "modified": file_info["modified"],
                    "is_log_file": file_info["is_log_file"]
                })
        
        # Check for database entries without corresponding files
        for db_name, db_info in db_log_entries.items():
            file_exists = any(Path(filename).stem in db_name for filename in log_file_names)
            
            if not file_exists:
                migration_analysis["database_only"].append({
                    "db_entry": db_name,
                    "content_length": db_info["content_length"],
                    "created_date": db_info["created_date"]
                })
        
        # Calculate statistics
        ready_count = len(migration_analysis["ready_for_archive"])
        needs_entry_count = len(migration_analysis["needs_database_entry"])
        db_only_count = len(migration_analysis["database_only"])
        
        self.logger.info(f"📊 Migration Analysis:")
        self.logger.info(f"  ✅ Ready for archive: {ready_count} files")
        self.logger.info(f"  📝 Need database entry: {needs_entry_count} files")
        self.logger.info(f"  🗄️ Database only: {db_only_count} entries")
        
        return migration_analysis

    def calculate_archive_impact(self, migration_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate the impact of moving files to archives."""
        self.logger.info("📈 Calculating archive migration impact...")
        
        ready_files = migration_analysis["ready_for_archive"]
        
        total_size = sum(file_info["size"] for file_info in ready_files)
        total_count = len(ready_files)
        
        # Group by file type
        by_type = {}
        for file_info in ready_files:
            filename = file_info["file"]
            ext = Path(filename).suffix.lower() or "no_extension"
            
            if ext not in by_type:
                by_type[ext] = {"count": 0, "size": 0}
            
            by_type[ext]["count"] += 1
            by_type[ext]["size"] += file_info["size"]
        
        # Calculate space savings
        space_savings_mb = total_size / (1024 * 1024)
        
        impact = {
            "total_files_to_archive": total_count,
            "total_size_bytes": total_size,
            "total_size_mb": round(space_savings_mb, 2),
            "by_file_type": by_type,
            "estimated_logs_folder_reduction": f"{space_savings_mb:.1f} MB",
            "archive_folder_increase": f"{space_savings_mb:.1f} MB"
        }
        
        self.logger.info(f"💾 Archive Impact: {total_count} files, {space_savings_mb:.1f} MB")
        
        return impact

    def generate_migration_plan(self, migration_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed migration plan."""
        self.logger.info("📋 Generating migration plan...")
        
        plan = {
            "phase_1_database_updates": {
                "description": "Add missing log files to database before archiving",
                "files_to_process": migration_analysis["needs_database_entry"],
                "estimated_time": f"{len(migration_analysis['needs_database_entry']) * 2} minutes"
            },
            "phase_2_archive_migration": {
                "description": "Move database-tracked files to archives",
                "files_to_move": migration_analysis["ready_for_archive"],
                "estimated_time": f"{len(migration_analysis['ready_for_archive']) * 1} minutes"
            },
            "phase_3_cleanup": {
                "description": "Clean up empty folders and update references",
                "tasks": [
                    "Remove empty subdirectories in logs/",
                    "Update file path references in databases",
                    "Validate archive folder structure"
                ],
                "estimated_time": "5 minutes"
            },
            "validation_requirements": [
                "All files have database entries before archiving",
                "No critical log files are archived (recent logs stay active)",
                "Archive folder maintains same directory structure",
                "Database references updated to point to archives"
            ]
        }
        
        return plan

    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive database consistency and migration report."""
        self.logger.info("📄 Generating comprehensive consistency report...")
        
        # Gather all data
        log_files = self.scan_logs_folder()
        logs_db_exists = self.check_logs_db_existence()
        db_log_entries = self.check_documentation_db_logs()
        migration_analysis = self.analyze_migration_readiness(log_files, db_log_entries)
        archive_impact = self.calculate_archive_impact(migration_analysis)
        migration_plan = self.generate_migration_plan(migration_analysis)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "workspace_root": str(self.workspace_root),
            "database_consistency": {
                "logs_db_exists": logs_db_exists,
                "documentation_db_log_entries": len(db_log_entries),
                "logs_folder_files": len(log_files),
                "consistency_status": "GOOD" if logs_db_exists else "NEEDS_ATTENTION"
            },
            "file_inventory": {
                "logs_folder_files": log_files,
                "database_log_entries": db_log_entries
            },
            "migration_readiness": migration_analysis,
            "archive_impact": archive_impact,
            "migration_plan": migration_plan,
            "recommendations": [
                "Create logs.db if it doesn't exist" if not logs_db_exists else "logs.db exists ✅",
                f"Add {len(migration_analysis['needs_database_entry'])} files to database before archiving",
                f"Archive {len(migration_analysis['ready_for_archive'])} database-tracked files",
                "Implement automated log rotation to prevent future accumulation"
            ],
            "overall_status": "READY_FOR_MIGRATION" if logs_db_exists and migration_analysis["ready_for_archive"] else "PREP_REQUIRED"
        }
        
        # Save report
        report_path = self.workspace_root / "reports" / f"database_consistency_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.logger.info(f"📄 Report saved: {report_path}")
        
        return report

def main():
    """Main execution function."""
    print("🗄️ DATABASE CONSISTENCY CHECKER")
    print("=" * 50)
    
    checker = DatabaseConsistencyChecker()
    
    try:
        # Generate comprehensive report
        report = checker.generate_comprehensive_report()
        
        # Display summary
        print(f"\n📊 CONSISTENCY SUMMARY")
        print(f"Overall Status: {report['overall_status']}")
        print(f"logs.db Status: {'EXISTS' if report['database_consistency']['logs_db_exists'] else 'MISSING'}")
        print(f"Files in logs/: {report['database_consistency']['logs_folder_files']}")
        print(f"DB Log Entries: {report['database_consistency']['documentation_db_log_entries']}")
        print(f"Ready for Archive: {len(report['migration_readiness']['ready_for_archive'])} files")
        print(f"Need DB Entry: {len(report['migration_readiness']['needs_database_entry'])} files")
        print(f"Archive Impact: {report['archive_impact']['total_size_mb']} MB")
        
        print(f"\n📋 RECOMMENDATIONS:")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"  {i}. {rec}")
        
        if report['overall_status'] == 'READY_FOR_MIGRATION':
            print("\n✅ READY FOR ARCHIVE MIGRATION!")
        else:
            print("\n⚠️ PREPARATION REQUIRED BEFORE MIGRATION")
        
        return report['overall_status'] == 'READY_FOR_MIGRATION'
        
    except Exception as e:
        print(f"❌ Consistency check failed: {e}")
        checker.logger.error(f"Consistency check failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
