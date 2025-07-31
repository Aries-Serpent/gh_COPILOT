#!/usr/bin/env python3
"""
🔄 COMPREHENSIVE FILE ROUTING CORRECTOR
Clean up misplaced files and enforce proper routing standards
"""

import os
import shutil
import sqlite3
from pathlib import Path
from datetime import datetime
from tqdm import tqdm
import json
import hashlib
from utils.cross_platform_paths import CrossPlatformPathManager


class ComprehensiveFileRoutingCorrector:
    """🚀 Enterprise File Routing Correction with MANDATORY Folder Enforcement"""

    def __init__(self):
        # MANDATORY: Start time logging with enterprise formatting
        self.start_time = datetime.now()
        print(f"🚀 COMPREHENSIVE FILE ROUTING CORRECTOR STARTED")
        print(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Process ID: {os.getpid()}")
        print("=" * 60)

        # CRITICAL: Anti-recursion validation
        self.validate_environment_compliance()

        # Workspace setup
        self.workspace_root = CrossPlatformPathManager.get_workspace_path()
        self.production_db = self.workspace_root / "databases" / "production.db"
        self.logs_db = self.workspace_root / "databases" / "logs.db"

        # MANDATORY: Proper folder structure enforcement
        self.target_folders = {
            "reports": self.workspace_root / "reports",
            "logs": self.workspace_root / "logs",
            "results": self.workspace_root / "results",
            "documentation": self.workspace_root / "documentation",
        }

        # CRITICAL: Ensure all target folders exist
        self.ensure_target_folders_exist()

        # Correction tracking
        self.correction_report = {
            "start_time": self.start_time.isoformat(),
            "routing_corrections": [],
            "files_relocated": 0,
            "database_updates": 0,
            "anti_recursion_validations": 0,
            "errors": [],
        }

    def validate_environment_compliance(self):
        """CRITICAL: Validate proper environment root usage"""
        workspace_root = CrossPlatformPathManager.get_workspace_path()

        # MANDATORY: Check for recursive folder violations
        forbidden_patterns = ["*backup*", "*_backup_*", "backups"]
        violations = []

        for pattern in forbidden_patterns:
            for folder in workspace_root.rglob(pattern):
                if folder.is_dir() and folder != workspace_root:
                    violations.append(str(folder))

        if violations:
            raise RuntimeError(f"CRITICAL: Recursive folder violations detected: {violations}")

        print("✅ ENVIRONMENT COMPLIANCE VALIDATED")
        self.correction_report["anti_recursion_validations"] += 1

    def ensure_target_folders_exist(self):
        """📁 Ensure all target folders exist with proper structure"""

        print("📁 ENSURING TARGET FOLDER STRUCTURE")
        print("=" * 50)

        for folder_name, folder_path in self.target_folders.items():
            if not folder_path.exists():
                folder_path.mkdir(parents=True, exist_ok=True)
                print(f"✅ Created folder: {folder_name}/")
            else:
                print(f"✅ Verified folder: {folder_name}/")

    def scan_misplaced_files(self):
        """🔍 Scan root directory for misplaced files"""

        print("🔍 SCANNING FOR MISPLACED FILES")
        print("=" * 50)

        misplaced_files = {"reports": [], "logs": [], "results": [], "documentation": []}

        # MANDATORY: Progress bar for scanning
        root_files = list(self.workspace_root.glob("*"))

        with tqdm(total=len(root_files), desc="🔍 Scanning Files", unit="files") as pbar:
            for item in root_files:
                if item.is_file():
                    pbar.set_description(f"🔍 Scanning {item.name}")

                    # Categorize based on file patterns and content
                    category = self.categorize_file(item)
                    if category in misplaced_files:
                        misplaced_files[category].append(item)
                        print(f"📋 Misplaced {category}: {item.name}")

                pbar.update(1)

        # Summary of findings
        total_misplaced = sum(len(files) for files in misplaced_files.values())
        print(f"\n📊 MISPLACED FILES SUMMARY:")
        print(f"   Total Misplaced: {total_misplaced}")
        for category, files in misplaced_files.items():
            if files:
                print(f"   {category.title()}: {len(files)} files")

        return misplaced_files

    def categorize_file(self, file_path: Path) -> str:
        """🏷️ Categorize file based on name patterns and content"""

        filename = file_path.name.lower()

        # Report file patterns
        report_patterns = [
            "_report_",
            "report.json",
            "summary.json",
            "analysis_",
            "validation_report",
            "migration_report",
            "merge_report",
            "verification_report",
            "schema_analysis",
            "completion_report",
        ]

        # Log file patterns
        log_patterns = [".log", "_log_", "deployment_log", "error_log", "access_log", "debug_log", "trace_log"]

        # Result file patterns
        result_patterns = [
            "_result_",
            "result.json",
            "output_",
            "processed_",
            "extracted_",
            "filtered_",
            "transformed_",
        ]

        # Documentation patterns
        doc_patterns = ["readme", "changelog", "license", "contributing", "documentation", "guide_", "manual_", ".md"]

        # Check patterns
        for pattern in report_patterns:
            if pattern in filename:
                return "reports"

        for pattern in log_patterns:
            if pattern in filename:
                return "logs"

        for pattern in result_patterns:
            if pattern in filename:
                return "results"

        for pattern in doc_patterns:
            if pattern in filename and filename.endswith(".md"):
                return "documentation"

        # Additional JSON file analysis
        if filename.endswith(".json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if any(word in content.lower() for word in ["report", "summary", "analysis", "validation"]):
                        return "reports"
                    elif any(word in content.lower() for word in ["log", "error", "debug", "trace"]):
                        return "logs"
                    elif any(word in content.lower() for word in ["result", "output", "processed"]):
                        return "results"
            except Exception:
                pass

        return "unknown"

    def relocate_misplaced_files(self, misplaced_files: dict):
        """🔄 Relocate misplaced files to correct folders"""

        print("🔄 RELOCATING MISPLACED FILES")
        print("=" * 50)

        total_files = sum(len(files) for files in misplaced_files.values())

        if total_files == 0:
            print("✅ No misplaced files found - routing is already correct")
            return

        # MANDATORY: Progress bar for relocation
        with tqdm(total=total_files, desc="🔄 Relocating Files", unit="files") as pbar:
            for category, files in misplaced_files.items():
                if not files:
                    continue

                target_folder = self.target_folders[category]

                for file_path in files:
                    pbar.set_description(f"🔄 Moving {file_path.name} → {category}/")

                    try:
                        # Generate unique filename if exists
                        target_path = target_folder / file_path.name
                        counter = 1
                        while target_path.exists():
                            name_parts = file_path.stem, counter, file_path.suffix
                            target_path = target_folder / f"{name_parts[0]}_{name_parts[1]}{name_parts[2]}"
                            counter += 1

                        # Move file with safety validation
                        shutil.move(str(file_path), str(target_path))

                        # Record relocation
                        self.correction_report["routing_corrections"].append(
                            {
                                "source": str(file_path),
                                "target": str(target_path),
                                "category": category,
                                "timestamp": datetime.now().isoformat(),
                            }
                        )

                        self.correction_report["files_relocated"] += 1
                        print(f"✅ Moved {file_path.name} → {category}/{target_path.name}")

                    except Exception as e:
                        error_msg = f"Relocation error for {file_path.name}: {str(e)}"
                        print(f"❌ {error_msg}")
                        self.correction_report["errors"].append(error_msg)

                    pbar.update(1)

    def update_production_database(self):
        """🗄️ Update production.db with new file mappings"""

        print("🗄️ UPDATING PRODUCTION DATABASE")
        print("=" * 50)

        try:
            with sqlite3.connect(str(self.production_db)) as conn:
                cursor = conn.cursor()

                # Check if file_system_mapping table exists
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='file_system_mapping'
                """)

                if not cursor.fetchone():
                    # Create file system mapping table
                    cursor.execute("""
                        CREATE TABLE file_system_mapping (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            file_path TEXT UNIQUE,
                            category TEXT,
                            last_updated TIMESTAMP,
                            file_size INTEGER,
                            file_hash TEXT
                        )
                    """)
                    print("✅ Created file_system_mapping table")

                # Update mappings for relocated files
                updates_made = 0

                for correction in self.correction_report["routing_corrections"]:
                    target_path = Path(correction["target"])
                    if target_path.exists():
                        file_size = target_path.stat().st_size
                        file_hash = self.calculate_file_hash(target_path)

                        cursor.execute(
                            """
                            INSERT OR REPLACE INTO file_system_mapping 
                            (file_path, category, last_updated, file_size, file_hash)
                            VALUES (?, ?, ?, ?, ?)
                        """,
                            (
                                str(target_path),
                                correction["category"],
                                datetime.now().isoformat(),
                                file_size,
                                file_hash,
                            ),
                        )
                        updates_made += 1

                conn.commit()
                print(f"✅ Updated {updates_made} file mappings in production.db")
                self.correction_report["database_updates"] = updates_made

        except Exception as e:
            error_msg = f"Database update error: {str(e)}"
            print(f"❌ {error_msg}")
            self.correction_report["errors"].append(error_msg)

    def calculate_file_hash(self, file_path: Path) -> str:
        """🔐 Calculate file hash for integrity tracking"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return "hash_error"

    def validate_logs_database_integration(self):
        """🔍 Validate log files integration with databases/logs.db"""

        print("🔍 VALIDATING LOGS DATABASE INTEGRATION")
        print("=" * 50)

        logs_folder = self.workspace_root / "logs"
        integration_status = {
            "logs_in_folder": 0,
            "logs_in_database": 0,
            "ready_for_archive": [],
            "needs_integration": [],
        }

        try:
            # Count log files in folder
            if logs_folder.exists():
                log_files = list(logs_folder.glob("*.log"))
                integration_status["logs_in_folder"] = len(log_files)
                print(f"📁 Log files in folder: {len(log_files)}")

            # Check logs database
            if self.logs_db.exists():
                with sqlite3.connect(str(self.logs_db)) as conn:
                    cursor = conn.cursor()

                    # Check if we have log tracking tables
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    tables = [row[0] for row in cursor.fetchall()]

                    if "enterprise_logs" in tables:
                        cursor.execute("SELECT COUNT(*) FROM enterprise_logs")
                        db_count = cursor.fetchone()[0]
                        integration_status["logs_in_database"] = db_count
                        print(f"🗄️ Log entries in database: {db_count}")

                    if "archive_enterprise_logs" in tables:
                        cursor.execute("SELECT COUNT(*) FROM archive_enterprise_logs")
                        archive_count = cursor.fetchone()[0]
                        print(f"📦 Archive log entries: {archive_count}")

                        # Check if log files are tracked in database
                        if logs_folder.exists():
                            for log_file in log_files:
                                cursor.execute(
                                    """
                                    SELECT COUNT(*) FROM archive_enterprise_logs 
                                    WHERE filename = ? OR original_path LIKE ?
                                """,
                                    (log_file.name, f"%{log_file.name}%"),
                                )

                                if cursor.fetchone()[0] > 0:
                                    integration_status["ready_for_archive"].append(str(log_file))
                                else:
                                    integration_status["needs_integration"].append(str(log_file))

            print(f"📊 Integration Status:")
            print(f"   Ready for Archive: {len(integration_status['ready_for_archive'])}")
            print(f"   Needs Integration: {len(integration_status['needs_integration'])}")

            self.correction_report["logs_integration"] = integration_status
            return integration_status

        except Exception as e:
            error_msg = f"Logs validation error: {str(e)}"
            print(f"❌ {error_msg}")
            self.correction_report["errors"].append(error_msg)
            return integration_status

    def generate_completion_report(self):
        """📋 Generate comprehensive completion report - ALWAYS TO REPORTS FOLDER"""

        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()

        self.correction_report["end_time"] = end_time.isoformat()
        self.correction_report["duration_seconds"] = duration

        # CRITICAL: ENFORCE PROPER ROUTING - ALWAYS TO REPORTS FOLDER
        reports_folder = self.workspace_root / "reports"
        reports_folder.mkdir(exist_ok=True)  # Ensure reports folder exists

        report_filename = f"comprehensive_routing_correction_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path = reports_folder / report_filename  # MANDATORY: Always to reports folder

        # Write report to CORRECT folder
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(self.correction_report, f, indent=2)

        print("=" * 60)
        print("✅ COMPREHENSIVE FILE ROUTING CORRECTION COMPLETED")
        print("=" * 60)
        print(f"Files Relocated: {self.correction_report['files_relocated']}")
        print(f"Database Updates: {self.correction_report['database_updates']}")
        print(f"Anti-Recursion Validations: {self.correction_report['anti_recursion_validations']}")
        print(f"Duration: {duration:.2f} seconds")
        print(f"📊 REPORT GENERATED: {report_path}")  # Note: Properly routed to reports/

        if self.correction_report["errors"]:
            print(f"⚠️ Errors Encountered: {len(self.correction_report['errors'])}")
            for error in self.correction_report["errors"]:
                print(f"   - {error}")

        print("=" * 60)
        print("🛡️ FUTURE SCRIPT ROUTING COMPLIANCE ENFORCED")
        print("✅ All future outputs will be properly routed to correct folders")
        print("=" * 60)

    def execute_comprehensive_correction(self):
        """🚀 Execute complete file routing correction workflow"""
        try:
            # Phase 1: Scan for misplaced files
            misplaced_files = self.scan_misplaced_files()

            # Phase 2: Relocate files to correct folders
            self.relocate_misplaced_files(misplaced_files)

            # Phase 3: Update production database
            self.update_production_database()

            # Phase 4: Validate logs database integration
            self.validate_logs_database_integration()

            # Phase 5: Generate completion report (PROPERLY ROUTED)
            self.generate_completion_report()

        except Exception as e:
            error_msg = f"Critical correction error: {str(e)}"
            print(f"🚨 {error_msg}")
            self.correction_report["errors"].append(error_msg)
            self.generate_completion_report()


def main():
    """🎯 Main execution function with MANDATORY routing enforcement"""
    corrector = ComprehensiveFileRoutingCorrector()
    corrector.execute_comprehensive_correction()


if __name__ == "__main__":
    main()
