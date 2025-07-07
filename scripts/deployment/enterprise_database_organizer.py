#!/usr/bin/env python3
"""
Enterprise Database Organization Tool
====================================

DUAL COPILOT PATTERN - Database File Organization and Migration
- Scans for duplicate database files between root and databases/ folder
- Migrates all .db files to proper databases/ folder structure
- Updates all code references to use enterprise database organization
- Validates migration and eliminates duplicates
- Ensures zero database reference errors after migration

Enterprise Standards:
- All .db files in databases/ folder for centralized management
- No database files in project root directory
- All code references updated to databases/ path structure
- Backup of original structure before migration
- Validation of successful migration and code updates

Author: Enterprise Database Migration System
Version: 1.0.0
"""

import os
import sys
import sqlite3
import shutil
import glob
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import logging
import json

class EnterpriseDatabaseOrganizer:
    """Enterprise-grade database file organization and migration system"""
    
    def __init__(self, workspace_path: Optional[str] = None):
        self.workspace_path = Path(workspace_path or os.getcwd())
        self.databases_dir = self.workspace_path / "databases"
        self.backup_dir = self.workspace_path / f"_backup_database_organization_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Ensure databases directory exists
        self.databases_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self.log_path = self.workspace_path / "database_organization.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(str(self.log_path)),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # File tracking
        self.migration_report = {
            "timestamp": datetime.now().isoformat(),
            "workspace_path": str(self.workspace_path),
            "databases_directory": str(self.databases_dir),
            "backup_directory": str(self.backup_dir),
            "root_db_files": [],
            "databases_db_files": [],
            "duplicates_identified": [],
            "files_migrated": [],
            "code_files_updated": [],
            "errors": [],
            "validation_results": {}
        }
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file for duplicate detection"""
        try:
            hasher = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            self.logger.error(f"Error calculating hash for {file_path}: {e}")
            return ""
    
    def scan_database_files(self) -> Dict[str, List[Dict]]:
        """Scan for all .db files in workspace and categorize them"""
        self.logger.info("Scanning for database files in workspace...")
        
        db_files = {
            "root": [],
            "databases": [],
            "backups": []
        }
        
        # Scan root directory for .db files
        for db_file in self.workspace_path.glob("*.db"):
            file_info = {
                "path": str(db_file),
                "name": db_file.name,
                "size": db_file.stat().st_size,
                "modified": datetime.fromtimestamp(db_file.stat().st_mtime).isoformat(),
                "hash": self.calculate_file_hash(db_file)
            }
            db_files["root"].append(file_info)
            self.migration_report["root_db_files"].append(file_info)
        
        # Scan databases directory for .db files
        if self.databases_dir.exists():
            for db_file in self.databases_dir.glob("*.db"):
                file_info = {
                    "path": str(db_file),
                    "name": db_file.name,
                    "size": db_file.stat().st_size,
                    "modified": datetime.fromtimestamp(db_file.stat().st_mtime).isoformat(),
                    "hash": self.calculate_file_hash(db_file)
                }
                db_files["databases"].append(file_info)
                self.migration_report["databases_db_files"].append(file_info)
        
        # Scan backup directories for .db files (for information only)
        for backup_dir in self.workspace_path.glob("_backup_*"):
            if backup_dir.is_dir():
                for db_file in backup_dir.glob("**/*.db"):
                    file_info = {
                        "path": str(db_file),
                        "name": db_file.name,
                        "backup_dir": backup_dir.name,
                        "size": db_file.stat().st_size,
                        "modified": datetime.fromtimestamp(db_file.stat().st_mtime).isoformat(),
                        "hash": self.calculate_file_hash(db_file)
                    }
                    db_files["backups"].append(file_info)
        
        self.logger.info(f"Found {len(db_files['root'])} .db files in root directory")
        self.logger.info(f"Found {len(db_files['databases'])} .db files in databases/ directory")
        self.logger.info(f"Found {len(db_files['backups'])} .db files in backup directories")
        
        return db_files
    
    def identify_duplicates(self, db_files: Dict[str, List[Dict]]) -> List[Dict]:
        """Identify duplicate database files between root and databases directories"""
        self.logger.info("Analyzing for duplicate database files...")
        
        duplicates = []
        
        # Compare root files with databases files
        for root_file in db_files["root"]:
            for db_file in db_files["databases"]:
                if root_file["name"] == db_file["name"]:
                    duplicate_info = {
                        "filename": root_file["name"],
                        "root_file": root_file,
                        "databases_file": db_file,
                        "same_content": root_file["hash"] == db_file["hash"] and root_file["hash"] != "",
                        "newer_file": "root" if root_file["modified"] > db_file["modified"] else "databases"
                    }
                    duplicates.append(duplicate_info)
                    self.migration_report["duplicates_identified"].append(duplicate_info)
        
        self.logger.info(f"Identified {len(duplicates)} duplicate database files")
        
        return duplicates
    
    def create_backup(self) -> bool:
        """Create backup of current database file structure"""
        try:
            self.logger.info(f"Creating backup of current database structure...")
            self.backup_dir.mkdir(exist_ok=True)
            
            # Backup all root .db files
            for db_file in self.workspace_path.glob("*.db"):
                backup_path = self.backup_dir / db_file.name
                shutil.copy2(db_file, backup_path)
                self.logger.info(f"Backed up {db_file.name} to backup directory")
            
            self.logger.info(f"Backup completed in: {self.backup_dir}")
            return True
            
        except Exception as e:
            error_msg = f"Error creating backup: {e}"
            self.logger.error(error_msg)
            self.migration_report["errors"].append(error_msg)
            return False
    
    def migrate_databases(self, duplicates: List[Dict]) -> bool:
        """Migrate database files to proper enterprise structure"""
        self.logger.info("Starting database file migration...")
        
        try:
            # For each duplicate, keep the newer version in databases/
            for duplicate in duplicates:
                filename = duplicate["filename"]
                root_path = Path(duplicate["root_file"]["path"])
                db_path = Path(duplicate["databases_file"]["path"])
                
                # Determine which file is newer and has more data
                if duplicate["newer_file"] == "root":
                    # Root file is newer, move it to databases/ and remove old one
                    self.logger.info(f"Migrating newer {filename} from root to databases/")
                    
                    # Remove old file in databases/
                    if db_path.exists():
                        db_path.unlink()
                    
                    # Move root file to databases/
                    target_path = self.databases_dir / filename
                    shutil.move(str(root_path), str(target_path))
                    
                    migration_info = {
                        "filename": filename,
                        "action": "moved_root_to_databases",
                        "source": str(root_path),
                        "target": str(target_path)
                    }
                    
                else:
                    # Databases file is newer, just remove root file
                    self.logger.info(f"Removing older {filename} from root (keeping databases/ version)")
                    root_path.unlink()
                    
                    migration_info = {
                        "filename": filename,
                        "action": "removed_root_kept_databases",
                        "removed": str(root_path),
                        "kept": str(db_path)
                    }
                
                self.migration_report["files_migrated"].append(migration_info)
            
            # Move any remaining root .db files that don't have duplicates
            for db_file in self.workspace_path.glob("*.db"):
                target_path = self.databases_dir / db_file.name
                if not target_path.exists():
                    shutil.move(str(db_file), str(target_path))
                    self.logger.info(f"Migrated {db_file.name} to databases/")
                    
                    migration_info = {
                        "filename": db_file.name,
                        "action": "moved_unique_to_databases",
                        "source": str(db_file),
                        "target": str(target_path)
                    }
                    self.migration_report["files_migrated"].append(migration_info)
            
            self.logger.info("Database file migration completed successfully")
            return True
            
        except Exception as e:
            error_msg = f"Error during database migration: {e}"
            self.logger.error(error_msg)
            self.migration_report["errors"].append(error_msg)
            return False
    
    def update_code_references(self) -> bool:
        """Update all Python files to use databases/ path for database files"""
        self.logger.info("Updating code references to use databases/ path...")
        
        try:
            # Find all Python files that might reference databases
            python_files = []
            for pattern in ["step*.py", "master_*.py", "*_orchestrator.py", "*framework*.py"]:
                python_files.extend(self.workspace_path.glob(pattern))
            
            updated_files = []
            
            for py_file in python_files:
                if py_file.name.startswith("_backup_"):
                    continue  # Skip backup files
                
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    original_content = content
                    
                    # Update database path references
                    # Pattern: os.path.join(self.workspace_path, "database_name.db")
                    # Replace with: os.path.join(self.workspace_path, "databases", "database_name.db")
                    
                    db_names = [
                        "factory_deployment.db",
                        "learning_monitor.db", 
                        "analytics_collector.db",
                        "performance_analysis.db",
                        "capability_scaler.db",
                        "continuous_innovation.db",
                        "scaling_innovation.db",
                        "advanced_features.db"
                    ]
                    
                    for db_name in db_names:
                        # Pattern 1: os.path.join(self.workspace_path, "db_name.db")
                        old_pattern1 = f'os.path.join(self.workspace_path, "{db_name}")'
                        new_pattern1 = f'os.path.join(self.workspace_path, "databases", "{db_name}")'
                        content = content.replace(old_pattern1, new_pattern1)
                        
                        # Pattern 2: self.workspace_path / "db_name.db"
                        old_pattern2 = f'self.workspace_path / "{db_name}"'
                        new_pattern2 = f'self.workspace_path / "databases" / "{db_name}"'
                        content = content.replace(old_pattern2, new_pattern2)
                        
                        # Pattern 3: workspace_path / "db_name.db"  
                        old_pattern3 = f'workspace_path / "{db_name}"'
                        new_pattern3 = f'workspace_path / "databases" / "{db_name}"'
                        content = content.replace(old_pattern3, new_pattern3)
                    
                    # If content changed, write back to file
                    if content != original_content:
                        with open(py_file, 'w', encoding='utf-8') as f:
                            f.write(content)
                        
                        updated_files.append(str(py_file))
                        self.migration_report["code_files_updated"].append(str(py_file))
                        self.logger.info(f"Updated database references in {py_file.name}")
                
                except Exception as e:
                    error_msg = f"Error updating {py_file}: {e}"
                    self.logger.error(error_msg)
                    self.migration_report["errors"].append(error_msg)
            
            self.logger.info(f"Updated database references in {len(updated_files)} Python files")
            return True
            
        except Exception as e:
            error_msg = f"Error updating code references: {e}"
            self.logger.error(error_msg)
            self.migration_report["errors"].append(error_msg)
            return False
    
    def validate_migration(self) -> Dict:
        """Validate that database migration was successful"""
        self.logger.info("Validating database migration...")
        
        validation_results = {
            "root_db_files_remaining": 0,
            "databases_db_files_count": 0,
            "all_files_accessible": True,
            "code_references_updated": True,
            "database_integrity": {},
            "validation_errors": []
        }
        
        try:
            # Check no .db files remain in root
            root_db_files = list(self.workspace_path.glob("*.db"))
            validation_results["root_db_files_remaining"] = len(root_db_files)
            
            if root_db_files:
                validation_results["validation_errors"].append(f"Found {len(root_db_files)} .db files remaining in root directory")
            
            # Check databases/ directory has all files
            if self.databases_dir.exists():
                db_files = list(self.databases_dir.glob("*.db"))
                validation_results["databases_db_files_count"] = len(db_files)
                
                # Test database accessibility
                for db_file in db_files:
                    try:
                        conn = sqlite3.connect(str(db_file))
                        cursor = conn.cursor()
                        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                        tables = cursor.fetchall()
                        conn.close()
                        
                        validation_results["database_integrity"][db_file.name] = {
                            "accessible": True,
                            "table_count": len(tables)
                        }
                        
                    except Exception as e:
                        validation_results["all_files_accessible"] = False
                        validation_results["validation_errors"].append(f"Database {db_file.name} not accessible: {e}")
                        validation_results["database_integrity"][db_file.name] = {
                            "accessible": False,
                            "error": str(e)
                        }
            
            # Validate code references were updated
            python_files = list(self.workspace_path.glob("step*.py"))
            for py_file in python_files:
                if py_file.name.startswith("_backup_"):
                    continue
                
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check for old-style database references
                    old_patterns = [
                        'os.path.join(self.workspace_path, "factory_deployment.db")',
                        'os.path.join(self.workspace_path, "learning_monitor.db")',
                        'os.path.join(self.workspace_path, "analytics_collector.db")',
                        'os.path.join(self.workspace_path, "performance_analysis.db")',
                        'os.path.join(self.workspace_path, "capability_scaler.db")',
                        'os.path.join(self.workspace_path, "continuous_innovation.db")'
                    ]
                    
                    for pattern in old_patterns:
                        if pattern in content:
                            validation_results["code_references_updated"] = False
                            validation_results["validation_errors"].append(f"Old database reference found in {py_file.name}: {pattern}")
                
                except Exception as e:
                    validation_results["validation_errors"].append(f"Error validating {py_file.name}: {e}")
            
            self.migration_report["validation_results"] = validation_results
            
            if validation_results["validation_errors"]:
                self.logger.warning(f"Validation completed with {len(validation_results['validation_errors'])} issues")
            else:
                self.logger.info("Migration validation completed successfully - all checks passed")
            
            return validation_results
            
        except Exception as e:
            error_msg = f"Error during validation: {e}"
            self.logger.error(error_msg)
            validation_results["validation_errors"].append(error_msg)
            return validation_results
    
    def generate_report(self) -> str:
        """Generate comprehensive migration report"""
        report_path = self.workspace_path / f"database_migration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(self.migration_report, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Migration report saved to: {report_path}")
            return str(report_path)
            
        except Exception as e:
            self.logger.error(f"Error generating report: {e}")
            return ""
    
    def run_complete_migration(self) -> bool:
        """Execute complete database organization and migration process"""
        self.logger.info("=== STARTING ENTERPRISE DATABASE ORGANIZATION ===")
        self.logger.info(f"Workspace: {self.workspace_path}")
        self.logger.info(f"Target databases directory: {self.databases_dir}")
        
        try:
            # Step 1: Scan for database files
            db_files = self.scan_database_files()
            
            # Step 2: Identify duplicates
            duplicates = self.identify_duplicates(db_files)
            
            # Step 3: Create backup
            if not self.create_backup():
                return False
            
            # Step 4: Migrate database files
            if not self.migrate_databases(duplicates):
                return False
            
            # Step 5: Update code references
            if not self.update_code_references():
                return False
            
            # Step 6: Validate migration
            validation_results = self.validate_migration()
            
            # Step 7: Generate report
            report_path = self.generate_report()
            
            # Summary
            success = len(validation_results.get("validation_errors", [])) == 0
            
            if success:
                self.logger.info("=== DATABASE ORGANIZATION COMPLETED SUCCESSFULLY ===")
                self.logger.info(f"Migrated {len(self.migration_report['files_migrated'])} database files")
                self.logger.info(f"Updated {len(self.migration_report['code_files_updated'])} Python files")
                self.logger.info(f"All databases now organized in: {self.databases_dir}")
            else:
                self.logger.warning("=== DATABASE ORGANIZATION COMPLETED WITH ISSUES ===")
                self.logger.warning(f"Found {len(validation_results['validation_errors'])} validation issues")
            
            if report_path:
                self.logger.info(f"Detailed report: {report_path}")
            
            return success
            
        except Exception as e:
            error_msg = f"Critical error during database organization: {e}"
            self.logger.error(error_msg)
            self.migration_report["errors"].append(error_msg)
            return False

def main():
    """Main execution function"""
    print("Enterprise Database Organization Tool")
    print("===================================")
    
    # Check if workspace path provided
    workspace_path = None
    if len(sys.argv) > 1:
        workspace_path = sys.argv[1]
    
    # Initialize organizer
    organizer = EnterpriseDatabaseOrganizer(workspace_path)
    
    # Run complete migration
    success = organizer.run_complete_migration()
    
    if success:
        print("\nDatabase organization completed successfully!")
        print(f"All database files are now properly organized in: {organizer.databases_dir}")
        print("Enterprise database standards implemented.")
    else:
        print("\nDatabase organization completed with issues.")
        print("Please review the log and report files for details.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
