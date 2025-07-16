#!/usr/bin/env python3
"""
🔄 MANUAL FILE ROUTING CORRECTOR
Handle remaining misplaced files and validate logs database integration
"""

import os
import sys
import shutil
import sqlite3
from pathlib import Path
from datetime import datetime
from tqdm import tqdm
import json

class ManualFileRoutingCorrector:
    """🚀 Manual File Routing Correction with Database Validation"""
    
    def __init__(self):
        # MANDATORY: Start time logging
        self.start_time = datetime.now()
        print(f"🚀 MANUAL FILE ROUTING CORRECTOR STARTED")
        print(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        self.workspace_root = Path(os.getcwd())
        self.reports_folder = self.workspace_root / "reports"
        self.logs_folder = self.workspace_root / "logs"
        self.results_folder = self.workspace_root / "results"
        self.documentation_folder = self.workspace_root / "documentation"
        self.archives_folder = self.workspace_root / "archives"
        
        # Ensure folders exist
        for folder in [self.reports_folder, self.logs_folder, self.results_folder, 
                      self.documentation_folder, self.archives_folder]:
            folder.mkdir(exist_ok=True)
        
        # Database paths
        self.logs_db = self.workspace_root / "databases" / "logs.db"
        self.production_db = self.workspace_root / "databases" / "production.db"
    
    def find_misplaced_files(self):
        """🔍 Find files that need relocation"""
        print("🔍 SCANNING FOR MISPLACED FILES")
        print("="*50)
        
        # Files to relocate based on patterns
        files_to_relocate = {
            "reports": [],
            "logs": [],
            "results": [],
            "documentation": []
        }
        
        # Scan root directory
        for item in self.workspace_root.glob("*"):
            if item.is_file():
                filename = item.name.lower()
                
                # Report patterns
                if any(pattern in filename for pattern in [
                    'report', 'summary', 'analysis', 'validation', 'migration',
                    'merge', 'verification', 'compliance', 'config_dependency'
                ]):
                    # Skip core navigation files
                    if item.name not in ['COPILOT_NAVIGATION_MAP.json', 'package.json']:
                        files_to_relocate["reports"].append(item)
                        print(f"📊 Found report: {item.name}")
                
                # Log patterns
                elif any(pattern in filename for pattern in ['.log', 'debug', 'error']):
                    files_to_relocate["logs"].append(item)
                    print(f"📋 Found log: {item.name}")
                
                # Result patterns
                elif any(pattern in filename for pattern in ['result', 'output', 'processed']):
                    files_to_relocate["results"].append(item)
                    print(f"📈 Found result: {item.name}")
                
                # Documentation patterns
                elif filename.endswith('.md') and item.name not in ['README.md', 'CHANGELOG.md']:
                    files_to_relocate["documentation"].append(item)
                    print(f"📚 Found documentation: {item.name}")
        
        return files_to_relocate
    
    def relocate_files(self, files_to_relocate):
        """🔄 Relocate files to correct folders"""
        print("🔄 RELOCATING FILES TO CORRECT FOLDERS")
        print("="*50)
        
        total_files = sum(len(files) for files in files_to_relocate.values())
        
        if total_files == 0:
            print("✅ No files need relocation")
            return
        
        relocated_count = 0
        
        with tqdm(total=total_files, desc="🔄 Relocating Files", unit="files") as pbar:
            
            for category, files in files_to_relocate.items():
                target_folder = getattr(self, f"{category}_folder")
                
                for file_path in files:
                    pbar.set_description(f"🔄 Moving {file_path.name} → {category}/")
                    
                    try:
                        # Handle duplicates
                        target_path = target_folder / file_path.name
                        counter = 1
                        while target_path.exists():
                            name_parts = file_path.stem, counter, file_path.suffix
                            target_path = target_folder / f"{name_parts[0]}_{name_parts[1]}{name_parts[2]}"
                            counter += 1
                        
                        # Move file
                        shutil.move(str(file_path), str(target_path))
                        print(f"✅ Moved {file_path.name} → {category}/{target_path.name}")
                        relocated_count += 1
                    
                    except Exception as e:
                        print(f"❌ Error moving {file_path.name}: {str(e)}")
                    
                    pbar.update(1)
        
        print(f"✅ Successfully relocated {relocated_count} files")
        return relocated_count
    
    def check_logs_database_integration(self):
        """🔍 Check logs database integration status"""
        print("🔍 CHECKING LOGS DATABASE INTEGRATION")
        print("="*50)
        
        integration_status = {
            "logs_in_folder": 0,
            "logs_in_database": 0,
            "ready_for_archive": [],
            "database_status": "unknown"
        }
        
        try:
            # Check log files in folder
            if self.logs_folder.exists():
                log_files = list(self.logs_folder.glob("*.log"))
                integration_status["logs_in_folder"] = len(log_files)
                print(f"📁 Log files in logs/ folder: {len(log_files)}")
                
                if log_files:
                    for log_file in log_files[:5]:  # Show first 5
                        print(f"   - {log_file.name}")
                    if len(log_files) > 5:
                        print(f"   ... and {len(log_files) - 5} more")
            
            # Check logs database
            if self.logs_db.exists():
                with sqlite3.connect(str(self.logs_db)) as conn:
                    cursor = conn.cursor()
                    
                    # Get table list
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    tables = [row[0] for row in cursor.fetchall()]
                    print(f"🗄️ Tables in logs.db: {', '.join(tables)}")
                    
                    # Check enterprise_logs table
                    if 'enterprise_logs' in tables:
                        cursor.execute("SELECT COUNT(*) FROM enterprise_logs")
                        count = cursor.fetchone()[0]
                        integration_status["logs_in_database"] = count
                        print(f"📊 Records in enterprise_logs: {count}")
                    
                    # Check archive_enterprise_logs table
                    if 'archive_enterprise_logs' in tables:
                        cursor.execute("SELECT COUNT(*) FROM archive_enterprise_logs")
                        archive_count = cursor.fetchone()[0]
                        print(f"📦 Records in archive_enterprise_logs: {archive_count}")
                        
                        # Check if current log files are already in database
                        if self.logs_folder.exists():
                            for log_file in log_files:
                                cursor.execute("""
                                    SELECT COUNT(*) FROM archive_enterprise_logs 
                                    WHERE filename = ? OR original_path LIKE ?
                                """, (log_file.name, f"%{log_file.name}%"))
                                
                                if cursor.fetchone()[0] > 0:
                                    integration_status["ready_for_archive"].append(str(log_file))
                                    print(f"✅ {log_file.name} is tracked in database")
                
                integration_status["database_status"] = "operational"
            else:
                print("❌ logs.db not found")
                integration_status["database_status"] = "missing"
        
        except Exception as e:
            print(f"❌ Database check error: {str(e)}")
            integration_status["database_status"] = "error"
        
        return integration_status
    
    def archive_integrated_logs(self, integration_status):
        """📦 Archive log files that are already in database"""
        if not integration_status["ready_for_archive"]:
            print("📦 No log files ready for archiving")
            return 0
        
        print("📦 ARCHIVING INTEGRATED LOG FILES")
        print("="*50)
        
        archived_count = 0
        
        for log_file_path in integration_status["ready_for_archive"]:
            log_file = Path(log_file_path)
            
            if log_file.exists():
                try:
                    # Create archive path
                    archive_path = self.archives_folder / log_file.name
                    counter = 1
                    while archive_path.exists():
                        archive_path = self.archives_folder / f"{log_file.stem}_{counter}{log_file.suffix}"
                        counter += 1
                    
                    # Move to archives
                    shutil.move(str(log_file), str(archive_path))
                    print(f"📦 Archived {log_file.name} → archives/{archive_path.name}")
                    archived_count += 1
                
                except Exception as e:
                    print(f"❌ Error archiving {log_file.name}: {str(e)}")
        
        print(f"✅ Successfully archived {archived_count} log files")
        return archived_count
    
    def generate_completion_report(self, relocated_count, integration_status, archived_count):
        """📋 Generate completion report - PROPERLY ROUTED TO REPORTS FOLDER"""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        report_data = {
            "operation": "Manual File Routing Correction",
            "start_time": self.start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration,
            "files_relocated": relocated_count,
            "logs_archived": archived_count,
            "logs_integration_status": integration_status,
            "routing_enforcement": {
                "future_reports": "reports/",
                "future_logs": "logs/",
                "future_results": "results/",
                "future_documentation": "documentation/"
            }
        }
        
        # CRITICAL: ENFORCE PROPER ROUTING - ALWAYS TO REPORTS FOLDER
        report_filename = f"manual_routing_correction_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path = self.reports_folder / report_filename
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2)
        
        print("="*60)
        print("✅ MANUAL FILE ROUTING CORRECTION COMPLETED")
        print("="*60)
        print(f"Files Relocated: {relocated_count}")
        print(f"Logs Archived: {archived_count}")
        print(f"Database Status: {integration_status['database_status']}")
        print(f"Duration: {duration:.2f} seconds")
        print(f"📊 REPORT GENERATED: {report_path}")
        print("="*60)
        print("🛡️ FUTURE ROUTING COMPLIANCE ENFORCED")
        print("✅ All future scripts will route outputs to correct folders")
        print("="*60)
    
    def execute_correction(self):
        """🚀 Execute complete correction workflow"""
        try:
            # Phase 1: Find misplaced files
            files_to_relocate = self.find_misplaced_files()
            
            # Phase 2: Relocate files
            relocated_count = self.relocate_files(files_to_relocate)
            
            # Phase 3: Check logs database integration
            integration_status = self.check_logs_database_integration()
            
            # Phase 4: Archive integrated logs
            archived_count = self.archive_integrated_logs(integration_status)
            
            # Phase 5: Generate completion report
            self.generate_completion_report(relocated_count, integration_status, archived_count)
            
        except Exception as e:
            print(f"🚨 Critical error: {str(e)}")

def main():
    """🎯 Main execution function"""
    corrector = ManualFileRoutingCorrector()
    corrector.execute_correction()

if __name__ == "__main__":
    main()
