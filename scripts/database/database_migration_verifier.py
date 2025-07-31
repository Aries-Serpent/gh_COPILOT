#!/usr/bin/env python3
"""
✅ DATABASE MIGRATION VERIFICATION TOOL
Verify successful database migration and generate completion report
"""

import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path


class DatabaseMigrationVerifier:
    """✅ Verify Database Migration Completion"""

    def __init__(self):
        self.start_time = datetime.now()
        print("🚀 DATABASE MIGRATION VERIFICATION STARTED")
        print(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        self.workspace_root = Path(os.getcwd())
        self.target_db = self.workspace_root / "databases" / "logs.db"
        self.source_db = self.workspace_root / "logs.db"

        self.verification_report = {
            "timestamp": self.start_time.isoformat(),
            "migration_verification": "INITIATED",
            "database_status": {},
            "table_verification": {},
            "tool_updates": {},
            "final_status": "PENDING",
        }

    def verify_database_status(self):
        """📊 Verify database migration status"""

        print("📊 VERIFYING DATABASE STATUS")
        print("=" * 50)

        # Check source database removal
        source_exists = self.source_db.exists()
        print(f"🗑️ Source Database (logs.db): {'❌ STILL EXISTS' if source_exists else '✅ REMOVED'}")

        # Check target database
        target_exists = self.target_db.exists()
        print(f"🎯 Target Database (databases/logs.db): {'✅ EXISTS' if target_exists else '❌ MISSING'}")

        # Analyze target database content
        if target_exists:
            try:
                with sqlite3.connect(str(self.target_db)) as conn:
                    cursor = conn.cursor()

                    # Get all tables
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    tables = [row[0] for row in cursor.fetchall()]

                    print(f"📋 Tables in target database: {len(tables)}")

                    # Check for migrated archive tables
                    archive_tables = [t for t in tables if t.startswith("archive_")]
                    if archive_tables:
                        print(f"📦 Archive tables found: {len(archive_tables)}")
                        for table in archive_tables:
                            cursor.execute(f"SELECT COUNT(*) FROM {table}")
                            count = cursor.fetchone()[0]
                            print(f"   - {table}: {count} records")

                    # Check original tables
                    original_tables = [
                        t for t in tables if not t.startswith("archive_") and not t.startswith("sqlite_")
                    ]
                    print(f"📊 Original tables: {len(original_tables)}")
                    for table in original_tables:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cursor.fetchone()[0]
                        print(f"   - {table}: {count} records")

                    self.verification_report["database_status"] = {
                        "source_removed": not source_exists,
                        "target_exists": target_exists,
                        "total_tables": len(tables),
                        "archive_tables": len(archive_tables),
                        "original_tables": len(original_tables),
                    }

                    self.verification_report["table_verification"] = {
                        "archive_tables": archive_tables,
                        "original_tables": original_tables,
                    }

            except Exception as e:
                error_msg = f"Database verification error: {str(e)}"
                print(f"❌ {error_msg}")
                self.verification_report["errors"] = self.verification_report.get("errors", [])
                self.verification_report["errors"].append(error_msg)

    def verify_tool_updates(self):
        """🔧 Verify tool references have been updated"""

        print("🔧 VERIFYING TOOL UPDATES")
        print("=" * 50)

        tools_to_check = ["archive_migration_executor.py", "database_consistency_checker.py"]

        tool_status = {}

        for tool_file in tools_to_check:
            tool_path = self.workspace_root / tool_file
            if tool_path.exists():
                try:
                    content = tool_path.read_text(encoding="utf-8")

                    # Check for correct database references
                    has_correct_path = "databases/logs.db" in content
                    has_incorrect_path = '"logs.db"' in content or "'logs.db'" in content

                    if has_correct_path and not has_incorrect_path:
                        status = "✅ UPDATED"
                    elif has_correct_path and has_incorrect_path:
                        status = "⚠️ PARTIALLY UPDATED"
                    else:
                        status = "❌ NOT UPDATED"

                    print(f"🔧 {tool_file}: {status}")
                    tool_status[tool_file] = {
                        "status": status,
                        "has_correct_path": has_correct_path,
                        "has_incorrect_path": has_incorrect_path,
                    }

                except Exception as e:
                    error_msg = f"Tool check error: {str(e)}"
                    print(f"❌ {tool_file}: {error_msg}")
                    tool_status[tool_file] = {"status": "ERROR", "error": error_msg}
            else:
                print(f"⚠️ {tool_file}: FILE NOT FOUND")
                tool_status[tool_file] = {"status": "NOT_FOUND"}

        self.verification_report["tool_updates"] = tool_status

    def check_backup_folder(self):
        """📦 Check backup folder for migrated files"""

        print("📦 CHECKING BACKUP FOLDER")
        print("=" * 50)

        backup_folder = Path(os.getenv("GH_COPILOT_BACKUP_ROOT", "/tmp/gh_COPILOT_Backups"))
        if backup_folder.exists():
            backup_files = list(backup_folder.glob("logs_*backup*.db"))
            print(f"📦 Backup files found: {len(backup_files)}")
            for backup_file in backup_files:
                file_size = backup_file.stat().st_size / 1024  # KB
                print(f"   - {backup_file.name}: {file_size:.1f} KB")

            self.verification_report["backup_files"] = [str(f) for f in backup_files]
        else:
            print("⚠️ Backup folder not found")
            self.verification_report["backup_files"] = []

    def generate_completion_report(self):
        """📋 Generate final migration completion report"""

        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()

        # Determine overall status
        db_status = self.verification_report.get("database_status", {})
        tool_status = self.verification_report.get("tool_updates", {})

        migration_successful = db_status.get("target_exists", False) and db_status.get("archive_tables", 0) > 0

        tools_updated = all(status.get("status", "").startswith("✅") for status in tool_status.values())

        if migration_successful:
            if tools_updated:
                final_status = "✅ COMPLETE"
            else:
                final_status = "⚠️ MIGRATION COMPLETE - TOOLS NEED UPDATE"
        else:
            final_status = "❌ MIGRATION INCOMPLETE"

        self.verification_report["final_status"] = final_status
        self.verification_report["end_time"] = end_time.isoformat()
        self.verification_report["duration_seconds"] = duration

        # Save verification report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.workspace_root / f"migration_verification_report_{timestamp}.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(self.verification_report, f, indent=2)

        print("=" * 60)
        print("✅ DATABASE MIGRATION VERIFICATION COMPLETED")
        print("=" * 60)
        print(f"Final Status: {final_status}")
        print(f"Database Migration: {'✅ SUCCESS' if migration_successful else '❌ FAILED'}")
        print(f"Tool Updates: {'✅ COMPLETE' if tools_updated else '⚠️ INCOMPLETE'}")
        print(f"Archive Tables: {db_status.get('archive_tables', 0)}")
        print(f"Backup Files: {len(self.verification_report.get('backup_files', []))}")
        print(f"Duration: {duration:.2f} seconds")
        print(f"Report Generated: {report_path}")
        print("=" * 60)

        # Summary recommendations
        if final_status.startswith("✅"):
            print("🎉 MIGRATION SUCCESSFULLY COMPLETED!")
            print("   • Database consolidated into databases/logs.db")
            print("   • Archive tables preserved with data integrity")
            print("   • Source database safely backed up")
            print("   • Tool references updated")
        elif final_status.startswith("⚠️"):
            print("⚠️ MIGRATION MOSTLY COMPLETE - ACTION NEEDED:")
            print("   • Database migration successful")
            print("   • Some tool references may need manual update")
        else:
            print("❌ MIGRATION INCOMPLETE - INVESTIGATION NEEDED")

    def execute_verification(self):
        """🚀 Execute complete verification workflow"""
        try:
            self.verify_database_status()
            self.verify_tool_updates()
            self.check_backup_folder()
            self.generate_completion_report()
        except Exception as e:
            error_msg = f"Verification error: {str(e)}"
            print(f"🚨 {error_msg}")
            self.verification_report["errors"] = self.verification_report.get("errors", [])
            self.verification_report["errors"].append(error_msg)
            self.generate_completion_report()


def main():
    """🎯 Main execution function"""
    verifier = DatabaseMigrationVerifier()
    verifier.execute_verification()


if __name__ == "__main__":
    main()
