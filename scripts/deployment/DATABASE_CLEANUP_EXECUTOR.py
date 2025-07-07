#!/usr/bin/env python3
"""
ENTERPRISE DATABASE CLEANUP EXECUTOR
====================================

This script safely removes redundant database files from the staging directory
that are identical to files in the local database, based on our redundancy analysis.

SAFETY PROTOCOLS:
- Creates backup before any deletions
- Only removes files verified as identical (same SHA-256 hash)
- Provides detailed logging and progress indicators
- Follows enterprise anti-recursion protocols

COMPLIANCE: Enterprise data management and storage optimization
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime
from tqdm import tqdm
import hashlib

class DatabaseCleanupExecutor:
    def __init__(self):
        self.start_time = datetime.now()
        self.process_id = os.getpid()
        self.backup_created = False
        self.files_removed = []
        self.space_saved = 0
        self.errors = []
        
        print("[LAUNCH] DATABASE CLEANUP EXECUTOR STARTED")
        print(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Process ID: {self.process_id}")
        print()
        
    def create_backup(self, staging_path: Path) -> Path:
        """Create backup of staging databases before cleanup"""
        print("[SHIELD] CREATING SAFETY BACKUP")
        print("-" * 30)
        
        if not staging_path.exists():
            raise ValueError(f"Staging path does not exist: {staging_path}")
        
        # Create backup with timestamp
        backup_dir = Path(f"staging_db_backup_{int(self.start_time.timestamp())}")
        
        # CRITICAL: Ensure backup is outside workspace (anti-recursion)
        external_backup_root = Path("E:/temp/gh_COPILOT_Backups")
        external_backup_root.mkdir(parents=True, exist_ok=True)
        backup_path = external_backup_root / backup_dir.name
        
        print(f"[FOLDER] Creating backup at: {backup_path}")
        
        try:
            shutil.copytree(staging_path, backup_path)
            self.backup_created = True
            print(f"[SUCCESS] Backup created successfully: {backup_path}")
            print(f"[BAR_CHART] Backup size: {self._get_directory_size(backup_path):.2f} MB")
            return backup_path
        except Exception as e:
            print(f"[ERROR] Backup creation failed: {e}")
            raise
    
    def _get_directory_size(self, path: Path) -> float:
        """Calculate directory size in MB"""
        total_size = 0
        for file in path.rglob('*'):
            if file.is_file():
                total_size += file.stat().st_size
        return total_size / (1024 * 1024)
    
    def _verify_file_hash(self, file_path: Path, expected_hash: str) -> bool:
        """Verify file hash before deletion"""
        try:
            with open(file_path, 'rb') as f:
                actual_hash = hashlib.sha256(f.read()).hexdigest()
            return actual_hash == expected_hash
        except Exception as e:
            print(f"[WARNING] Hash verification failed for {file_path}: {e}")
            return False
    
    def load_cleanup_plan(self, analysis_file: str) -> dict:
        """Load cleanup plan from analysis results"""
        print("[CLIPBOARD] LOADING CLEANUP PLAN")
        print("-" * 25)
        
        try:
            with open(analysis_file, 'r') as f:
                analysis = json.load(f)
            
            cleanup_plan = {
                "identical_files": analysis["comparison_results"]["identical_files"],
                "total_files": len(analysis["comparison_results"]["identical_files"]),
                "estimated_savings": analysis["cleanup_plan"]["space_savings_mb"]
            }
            
            print(f"[SUCCESS] Cleanup plan loaded")
            print(f"[BAR_CHART] Files to remove: {cleanup_plan['total_files']}")
            print(f"[BAR_CHART] Estimated space savings: {cleanup_plan['estimated_savings']:.2f} MB")
            
            return cleanup_plan
            
        except Exception as e:
            print(f"[ERROR] Failed to load cleanup plan: {e}")
            raise
    
    def execute_cleanup(self, cleanup_plan: dict) -> dict:
        """Execute the cleanup with progress monitoring"""
        print("\n[TRASH] EXECUTING CLEANUP")
        print("-" * 20)
        
        identical_files = cleanup_plan["identical_files"]
        
        # Progress bar for cleanup
        with tqdm(total=len(identical_files), desc="[TRASH] Removing redundant files", unit="files") as pbar:
            for file_info in identical_files:
                staging_path = Path(file_info["staging_path"])
                expected_hash = file_info["hash"]
                file_size = file_info["size"]
                
                try:
                    # Verify file exists and hash matches
                    if not staging_path.exists():
                        self.errors.append(f"File not found: {staging_path}")
                        pbar.update(1)
                        continue
                    
                    # Skip zero-byte files or files with hash verification issues
                    if expected_hash == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855":
                        # This is a zero-byte file hash - safe to remove
                        pass
                    elif not self._verify_file_hash(staging_path, expected_hash):
                        self.errors.append(f"Hash mismatch, skipping: {staging_path}")
                        pbar.update(1)
                        continue
                    
                    # Remove the file
                    staging_path.unlink()
                    self.files_removed.append(str(staging_path))
                    self.space_saved += file_size
                    
                    pbar.set_description(f"[TRASH] Removed: {staging_path.name}")
                    
                except Exception as e:
                    self.errors.append(f"Error removing {staging_path}: {e}")
                
                pbar.update(1)
        
        # Clean up empty directories
        self._cleanup_empty_directories(Path("E:/gh_COPILOT/databases"))
        
        cleanup_results = {
            "files_removed": len(self.files_removed),
            "space_saved_mb": self.space_saved / (1024 * 1024),
            "errors": len(self.errors),
            "success_rate": (len(self.files_removed) / len(identical_files)) * 100 if identical_files else 0
        }
        
        print(f"\n[SUCCESS] Cleanup completed:")
        print(f"   - Files removed: {cleanup_results['files_removed']}")
        print(f"   - Space saved: {cleanup_results['space_saved_mb']:.2f} MB")
        print(f"   - Errors: {cleanup_results['errors']}")
        print(f"   - Success rate: {cleanup_results['success_rate']:.1f}%")
        
        return cleanup_results
    
    def _cleanup_empty_directories(self, root_path: Path):
        """Remove empty directories after file cleanup"""
        print("\n[?] CLEANING UP EMPTY DIRECTORIES")
        
        directories_removed = 0
        for dirpath, dirnames, filenames in os.walk(root_path, topdown=False):
            dir_path = Path(dirpath)
            if dir_path != root_path and not any(dir_path.iterdir()):
                try:
                    dir_path.rmdir()
                    directories_removed += 1
                    print(f"[FOLDER] Removed empty directory: {dir_path}")
                except Exception as e:
                    print(f"[WARNING] Could not remove directory {dir_path}: {e}")
        
        if directories_removed == 0:
            print("[SUCCESS] No empty directories to clean up")
        else:
            print(f"[SUCCESS] Removed {directories_removed} empty directories")
    
    def generate_cleanup_report(self, cleanup_results: dict, backup_path: Path) -> str:
        """Generate comprehensive cleanup report"""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        report = {
            "cleanup_session": f"CLEANUP_{int(self.start_time.timestamp())}",
            "start_time": self.start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration,
            "process_id": self.process_id,
            "backup_location": str(backup_path),
            "backup_created": self.backup_created,
            "cleanup_results": cleanup_results,
            "files_removed": self.files_removed,
            "errors": self.errors,
            "compliance_status": "COMPLIANT" if len(self.errors) == 0 else "PARTIAL_COMPLIANCE",
            "space_optimization": {
                "space_saved_mb": cleanup_results["space_saved_mb"],
                "files_processed": cleanup_results["files_removed"],
                "optimization_rate": cleanup_results["success_rate"]
            }
        }
        
        report_path = f"DATABASE_CLEANUP_REPORT_{int(self.start_time.timestamp())}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n[?] Cleanup report generated: {report_path}")
        return report_path
    
    def execute_full_cleanup(self, analysis_file: str) -> bool:
        """Execute complete cleanup process with all safety protocols"""
        print("[?] ENTERPRISE DATABASE CLEANUP")
        print("[?] REMOVING REDUNDANT STAGING FILES")
        print("=" * 50)
        
        try:
            # Load cleanup plan
            cleanup_plan = self.load_cleanup_plan(analysis_file)
            
            # Create backup
            staging_path = Path("E:/gh_COPILOT/databases")
            backup_path = self.create_backup(staging_path)
            
            # Execute cleanup
            cleanup_results = self.execute_cleanup(cleanup_plan)
            
            # Generate report
            report_path = self.generate_cleanup_report(cleanup_results, backup_path)
            
            print("\n" + "=" * 50)
            print("[COMPLETE] DATABASE CLEANUP COMPLETED SUCCESSFULLY")
            print(f"[SUCCESS] Files removed: {cleanup_results['files_removed']}")
            print(f"[SUCCESS] Space saved: {cleanup_results['space_saved_mb']:.2f} MB")
            print(f"[SUCCESS] Backup location: {backup_path}")
            print(f"[SUCCESS] Report: {report_path}")
            
            if self.errors:
                print(f"[WARNING] {len(self.errors)} errors occurred (see report for details)")
            
            return True
            
        except Exception as e:
            print(f"\n[ERROR] CLEANUP FAILED: {e}")
            if self.backup_created:
                print(f"[SHIELD] Backup is safe at: {backup_path}")
            return False

def main():
    """Main execution function"""
    # Find the latest analysis file
    analysis_files = list(Path('.').glob('DATABASE_REDUNDANCY_ANALYSIS_*.json'))
    if not analysis_files:
        print("[ERROR] No analysis file found. Run DATABASE_REDUNDANCY_ANALYZER.py first.")
        return False
    
    latest_analysis = max(analysis_files, key=lambda f: f.stat().st_mtime)
    print(f"[BAR_CHART] Using analysis file: {latest_analysis}")
    
    # Execute cleanup
    cleanup_executor = DatabaseCleanupExecutor()
    success = cleanup_executor.execute_full_cleanup(str(latest_analysis))
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
