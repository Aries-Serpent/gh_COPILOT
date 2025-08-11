#!/usr/bin/env python3
"""
🚨 PYTHON SCRIPT RECOVERY ENGINE
Identifies and restores Python scripts that were incorrectly categorized as logs/reports
"""

import os
import sys
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from tqdm import tqdm

class PythonScriptRecoveryEngine:
    """🚨 Recovers Python scripts incorrectly moved to logs/reports folders"""
    
    def __init__(self, workspace_path: Optional[str] = None):
        """Initialize recovery engine"""
        self.workspace_path = Path(workspace_path) if workspace_path else Path(os.getenv("GH_COPILOT_WORKSPACE", "e:/gh_COPILOT"))
        self.production_db = self.workspace_path / "production.db"
        self.recovery_results = {
            "scripts_found": [],
            "scripts_restored": [],
            "scripts_failed": [],
            "database_updates": [],
            "recovery_timestamp": datetime.now().isoformat()
        }
        
        # Folders to check for misplaced Python scripts
        self.check_folders = ["logs", "reports", "documentation", "results"]
        
    def scan_for_misplaced_python_scripts(self) -> Dict[str, List[str]]:
        """🔍 Scan folders for Python scripts that should be executable"""
        print(f"🚀 PYTHON SCRIPT RECOVERY STARTED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        misplaced_scripts = {}
        
        with tqdm(total=len(self.check_folders), desc="🔍 Scanning Folders", unit="folders") as pbar:
            for folder_name in self.check_folders:
                pbar.set_description(f"🔍 Scanning {folder_name}/")
                
                folder_path = self.workspace_path / folder_name
                if folder_path.exists():
                    # Find all Python files in this folder
                    python_files = list(folder_path.rglob("*.py"))
                    
                    if python_files:
                        misplaced_scripts[folder_name] = []
                        for py_file in python_files:
                            # Check if this is actually an executable script
                            if self._is_executable_script(py_file):
                                relative_path = str(py_file.relative_to(self.workspace_path))
                                misplaced_scripts[folder_name].append(relative_path)
                                self.recovery_results["scripts_found"].append({
                                    "file": relative_path,
                                    "current_location": folder_name,
                                    "file_size": py_file.stat().st_size,
                                    "should_be_executable": True
                                })
                
                pbar.update(1)
        
        return misplaced_scripts
    
    def _is_executable_script(self, file_path: Path) -> bool:
        """🔍 Determine if a Python file is an executable script vs data file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(2000)  # Read first 2000 chars
                
            # Signs this is an executable script:
            executable_indicators = [
                "#!/usr/bin/env python",
                "if __name__ == \"__main__\":",
                "def main():",
                "class " in content and "def " in content,  # Has classes and methods
                "import " in content,  # Has imports
                "from " in content and "import" in content  # Has from imports
            ]
            
            # Signs this might be a data/template file:
            data_indicators = [
                content.strip().startswith("{") and content.strip().endswith("}"),  # JSON-like
                content.strip().startswith("[") and content.strip().endswith("]"),  # List-like
                len(content.strip()) < 100 and not any(indicator for indicator in executable_indicators)  # Very short
            ]
            
            # Count executable indicators
            executable_count = sum(1 for indicator in executable_indicators if 
                                 (isinstance(indicator, str) and indicator in content) or 
                                 (isinstance(indicator, bool) and indicator))
            
            data_count = sum(1 for indicator in data_indicators if indicator)
            
            # If it has multiple executable indicators and few data indicators, it's likely a script
            return executable_count >= 2 and data_count == 0
            
        except Exception as e:
            print(f"⚠️ Error analyzing {file_path}: {e}")
            return False
    
    def restore_python_scripts(self, misplaced_scripts: Dict[str, List[str]]) -> bool:
        """📦 Restore Python scripts to workspace root"""
        total_scripts = sum(len(scripts) for scripts in misplaced_scripts.values())
        
        if total_scripts == 0:
            print("✅ No misplaced Python scripts found!")
            return True
        
        print(f"🔧 Restoring {total_scripts} misplaced Python scripts...")
        
        with tqdm(total=total_scripts, desc="📦 Restoring Scripts", unit="scripts") as pbar:
            for folder_name, script_paths in misplaced_scripts.items():
                for script_path in script_paths:
                    pbar.set_description(f"📦 {Path(script_path).name[:20]}...")
                    
                    try:
                        source_path = self.workspace_path / script_path
                        # Extract just the filename for destination
                        script_name = Path(script_path).name
                        dest_path = self.workspace_path / script_name
                        
                        # Avoid overwriting existing files
                        if dest_path.exists():
                            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                            script_stem = dest_path.stem
                            script_suffix = dest_path.suffix
                            dest_path = self.workspace_path / f"{script_stem}_restored_{timestamp}{script_suffix}"
                        
                        # Move the file
                        shutil.move(str(source_path), str(dest_path))
                        
                        self.recovery_results["scripts_restored"].append({
                            "original_path": script_path,
                            "restored_path": str(dest_path.relative_to(self.workspace_path)),
                            "status": "success"
                        })
                        
                        print(f"✅ Restored: {script_name}")
                        
                    except Exception as e:
                        print(f"❌ Failed to restore {script_path}: {e}")
                        self.recovery_results["scripts_failed"].append({
                            "script_path": script_path,
                            "error": str(e)
                        })
                    
                    pbar.update(1)
        
        return len(self.recovery_results["scripts_failed"]) == 0
    
    def update_database_mappings(self) -> bool:
        """🗄️ Update production.db with corrected file mappings"""
        if not self.production_db.exists():
            print("⚠️ production.db not found, skipping database updates")
            return True
        
        try:
            with sqlite3.connect(self.production_db) as conn:
                cursor = conn.cursor()
                
                print("🗄️ Updating database mappings...")
                
                with tqdm(total=len(self.recovery_results["scripts_restored"]), 
                         desc="🗄️ Database Updates", unit="records") as pbar:
                    
                    for restoration in self.recovery_results["scripts_restored"]:
                        pbar.set_description(f"🗄️ Updating {Path(restoration['restored_path']).name[:15]}...")
                        
                        # Update the script path in database
                        cursor.execute("""
                            UPDATE enhanced_script_tracking 
                            SET script_path = ?, 
                                last_updated = CURRENT_TIMESTAMP,
                                notes = COALESCE(notes, '') || ' [RESTORED FROM MISCLASSIFICATION]'
                            WHERE script_path = ?
                        """, (restoration['restored_path'], restoration['original_path']))
                        
                        if cursor.rowcount > 0:
                            self.recovery_results["database_updates"].append({
                                "file": restoration['restored_path'],
                                "action": "path_updated",
                                "rows_affected": cursor.rowcount
                            })
                        
                        pbar.update(1)
                
                conn.commit()
                print(f"✅ Database updated with {len(self.recovery_results['database_updates'])} record changes")
                
        except Exception as e:
            print(f"❌ Database update failed: {e}")
            return False
        
        return True
    
    def generate_recovery_report(self) -> str:
        """📊 Generate comprehensive recovery report"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = self.workspace_path / f"python_script_recovery_report_{timestamp}.json"
        
        # Add summary statistics
        self.recovery_results["summary"] = {
            "total_scripts_found": len(self.recovery_results["scripts_found"]),
            "total_scripts_restored": len(self.recovery_results["scripts_restored"]),
            "total_scripts_failed": len(self.recovery_results["scripts_failed"]),
            "database_records_updated": len(self.recovery_results["database_updates"]),
            "recovery_success_rate": (len(self.recovery_results["scripts_restored"]) / 
                                    max(1, len(self.recovery_results["scripts_found"]))) * 100
        }
        
        with open(report_path, 'w') as f:
            import json
            json.dump(self.recovery_results, f, indent=2)
        
        print(f"📊 Recovery report saved: {report_path}")
        return str(report_path)
    
    def execute_full_recovery(self) -> bool:
        """🚀 Execute complete Python script recovery process"""
        print("="*80)
        print("🚨 PYTHON SCRIPT RECOVERY ENGINE")
        print("="*80)
        
        try:
            # Step 1: Scan for misplaced scripts
            misplaced_scripts = self.scan_for_misplaced_python_scripts()
            
            if not misplaced_scripts or not any(misplaced_scripts.values()):
                print("✅ No misplaced Python scripts found!")
                return True
            
            # Display what was found
            print("\n🔍 MISPLACED PYTHON SCRIPTS FOUND:")
            for folder, scripts in misplaced_scripts.items():
                if scripts:
                    print(f"  📁 {folder}/: {len(scripts)} scripts")
                    for script in scripts[:3]:  # Show first 3
                        print(f"    - {script}")
                    if len(scripts) > 3:
                        print(f"    ... and {len(scripts) - 3} more")
            
            # Step 2: Restore scripts
            restore_success = self.restore_python_scripts(misplaced_scripts)
            
            # Step 3: Update database
            if restore_success:
                database_success = self.update_database_mappings()
            else:
                database_success = False
            
            # Step 4: Generate report
            report_path = self.generate_recovery_report()
            
            # Step 5: Display summary
            print("\n" + "="*80)
            print("📊 RECOVERY SUMMARY")
            print("="*80)
            print(f"Scripts Found: {self.recovery_results['summary']['total_scripts_found']}")
            print(f"Scripts Restored: {self.recovery_results['summary']['total_scripts_restored']}")
            print(f"Scripts Failed: {self.recovery_results['summary']['total_scripts_failed']}")
            print(f"Database Updates: {self.recovery_results['summary']['database_records_updated']}")
            print(f"Success Rate: {self.recovery_results['summary']['recovery_success_rate']:.1f}%")
            print(f"Report Location: {report_path}")
            
            overall_success = restore_success and database_success
            if overall_success:
                print("\n✅ PYTHON SCRIPT RECOVERY COMPLETED SUCCESSFULLY")
            else:
                print("\n⚠️ PYTHON SCRIPT RECOVERY COMPLETED WITH ISSUES")
            
            return overall_success
            
        except Exception as e:
            print(f"❌ CRITICAL ERROR: {e}")
            return False

def main():
    """🚀 Main execution function"""
    recovery_engine = PythonScriptRecoveryEngine()
    success = recovery_engine.execute_full_recovery()
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
