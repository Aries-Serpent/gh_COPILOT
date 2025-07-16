#!/usr/bin/env python3
"""
Database Consistency Checker - CORRECTED VERSION
Uses EXISTING databases/logs.db instead of creating new database
"""

import os
import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any
from tqdm import tqdm
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
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
            "recommendations": []
        }
        
        logger.info("🔄 Database Consistency Checker CORRECTED - Using existing databases/logs.db")
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
                    if not table.startswith('sqlite_'):
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
        log_patterns = ['*.log', '*.txt', '*.out', '*.err']
        
        with tqdm(desc="🔍 Scanning logs folder", unit="files") as pbar:
            for pattern in log_patterns:
                found_files = list(self.logs_folder.rglob(pattern))
                log_files.extend(found_files)
                pbar.update(len(found_files))
        
        self.validation_results["log_files_count"] = len(log_files)
        logger.info(f"📁 Found {len(log_files)} log files in logs folder")
        
        return log_files
    
    def check_database_consistency(self, log_files: List[Path]) -> Dict[str, Any]:
        """Check which log files are tracked in the existing database"""
        
        consistency_report = {
            "tracked_files": [],
            "untracked_files": [],
            "database_only_entries": [],
            "consistency_percentage": 0
        }
        
        if not self.validation_results["database_exists"]:
            logger.error("❌ Cannot check consistency - database not available")
            return consistency_report
        
        try:
            with sqlite3.connect(self.logs_db_path) as conn:
                cursor = conn.cursor()
                
                # Check if enterprise_logs table exists
                if 'enterprise_logs' in self.validation_results["database_tables"]:
                    # Get all file paths from database
                    cursor.execute("SELECT DISTINCT file_path FROM enterprise_logs")
                    db_file_paths = {row[0] for row in cursor.fetchall()}
                    
                    # Check each log file
                    with tqdm(desc="🔍 Checking file consistency", total=len(log_files)) as pbar:
                        for log_file in log_files:
                            relative_path = str(log_file.relative_to(self.workspace_root))
                            
                            if relative_path in db_file_paths:
                                consistency_report["tracked_files"].append(relative_path)
                            else:
                                consistency_report["untracked_files"].append(relative_path)
                            
                            pbar.update(1)
                    
                    # Find database entries without corresponding files
                    existing_files = {str(f.relative_to(self.workspace_root)) for f in log_files}
                    consistency_report["database_only_entries"] = list(db_file_paths - existing_files)
                    
                    # Calculate consistency percentage
                    if log_files:
                        consistency_report["consistency_percentage"] = (
                            len(consistency_report["tracked_files"]) / len(log_files)
                        ) * 100
                    
                    logger.info(f"📊 Consistency check complete:")
                    logger.info(f"   - Tracked files: {len(consistency_report['tracked_files'])}")
                    logger.info(f"   - Untracked files: {len(consistency_report['untracked_files'])}")
                    logger.info(f"   - Consistency: {consistency_report['consistency_percentage']:.1f}%")
                
                else:
                    logger.warning("⚠️ enterprise_logs table not found in database")
        
        except Exception as e:
            logger.error(f"❌ Consistency check error: {e}")
        
        return consistency_report
    
    def assess_migration_readiness(self, consistency_report: Dict[str, Any]) -> bool:
        """Assess if logs are ready for archive migration"""
        
        migration_ready = False
        recommendations = []
        
        # Check if majority of files are tracked
        if consistency_report["consistency_percentage"] >= 80:
            migration_ready = True
            recommendations.append("✅ High consistency - logs ready for archive migration")
        else:
            recommendations.append("⚠️ Low consistency - recommend updating database before migration")
        
        # Check for untracked files
        if consistency_report["untracked_files"]:
            recommendations.append(f"📝 {len(consistency_report['untracked_files'])} files need database tracking")
        
        # Check for orphaned database entries
        if consistency_report["database_only_entries"]:
            recommendations.append(f"🗑️ {len(consistency_report['database_only_entries'])} orphaned database entries")
        
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
                "status": "SUCCESS" if self.validation_results["migration_ready"] else "NEEDS_ATTENTION",
                "database_operational": self.validation_results["database_exists"],
                "files_tracked_percentage": consistency_report.get("consistency_percentage", 0),
                "migration_ready": self.validation_results["migration_ready"]
            }
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
    
    print("="*80)
    print("🔍 DATABASE CONSISTENCY CHECKER - CORRECTED VERSION")
    print("Using EXISTING databases/logs.db")
    print("="*80)
    
    try:
        checker = DatabaseConsistencyChecker()
        report = checker.execute_consistency_check()
        
        # Save report
        report_file = Path("reports/database_consistency_report_corrected.json")
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📊 CONSISTENCY CHECK COMPLETE")
        print(f"📄 Report saved: {report_file}")
        print(f"🗄️ Database: {report['database_path']}")
        print(f"📁 Log files: {report['validation_results']['log_files_count']}")
        print(f"📊 Consistency: {report['consistency_analysis'].get('consistency_percentage', 0):.1f}%")
        print(f"🚀 Migration ready: {'YES' if report['summary']['migration_ready'] else 'NO'}")
        
        return report
        
    except Exception as e:
        logger.error(f"❌ Critical error: {e}")
        return None

if __name__ == "__main__":
    main()
