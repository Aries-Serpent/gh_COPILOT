#!/usr/bin/env python3
"""
Enterprise Database-First Architecture Synchronization Engine
=============================================================

This script ensures full compliance with database-first architecture by:
1. Synchronizing all file system scripts to the database
2. Ensuring database-consumed scripts are reproducible
3. Creating missing database entries
4. Updating content mismatches
5. Validating database-first compliance

This is critical for enterprise mandates requiring all scripts to be stored
in both file system and database with full reproducibility.
"""


import sqlite3
import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path



class DatabaseFirstSynchronizer:
    def __init__(self, workspace_root="e:\\gh_COPILOT"):
        self.workspace_root = Path(workspace_root)
        self.database_dir = self.workspace_root / "databases"
        self.production_db = self.database_dir / "production.db"

        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

        self.sync_results = {
            "scripts_added": [],
            "scripts_updated": [],
            "content_synchronized": [],
            "errors": [],
            "statistics": {}
        }

    def ensure_database_structure(self):
        """Ensure required database tables exist"""
        self.logger.info("Ensuring database structure...")

        try:
            conn = sqlite3.connect(self.production_db)
            cursor = conn.cursor()

            # Enhanced script tracking table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS enhanced_script_tracking (
                    script_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    script_path TEXT UNIQUE NOT NULL,
                    script_content TEXT NOT NULL,
                    script_hash TEXT NOT NULL,
                    script_type TEXT DEFAULT 'python',
                    functionality_category TEXT,
                    dependencies TEXT,
                    configuration_requirements TEXT,
                    regeneration_priority INTEGER DEFAULT 3,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    recovery_tested BOOLEAN DEFAULT FALSE,
                    file_size INTEGER,
                    lines_of_code INTEGER
                )
            """)

            # Complete file system mapping table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS complete_file_system_mapping (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT UNIQUE NOT NULL,
                    file_content TEXT NOT NULL,
                    file_hash TEXT NOT NULL,
                    file_size INTEGER,
                    file_type TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'ACTIVE',
                    backup_location TEXT,
                    compression_type TEXT DEFAULT 'none',
                    encoding TEXT DEFAULT 'utf-8'
                )
            """)

            # Database-first compliance tracking
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS database_first_compliance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sync_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total_scripts INTEGER,
                    synchronized_scripts INTEGER,
                    reproducible_scripts INTEGER,
                    compliance_percentage REAL,
                    status TEXT,
                    validation_notes TEXT
                )
            """)

            conn.commit()
            conn.close()
            self.logger.info("Database structure ready")

        except Exception as e:
            self.logger.error(f"Error setting up database structure: {e}")
            raise

    def get_file_content(self, file_path):
        """Get file content with proper error handling"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            return content
        except Exception as e:
            self.logger.warning(f"Could not read {file_path}: {e}")
            return ""

    def get_file_hash(self, content):
        """Calculate SHA256 hash of content"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def categorize_script(self, file_path, content):
        """Categorize script based on path and content"""
        path_str = str(file_path).lower()
        content_lower = content.lower()

        if 'quantum' in path_str or 'quantum' in content_lower:
            return 'quantum_algorithms'
        elif 'database' in path_str or 'database' in content_lower:
            return 'database_management'
        elif 'web_gui' in path_str or 'flask' in content_lower or 'fastapi' in content_lower:
            return 'web_interface'
        elif 'test' in path_str or 'test_' in path_str:
            return 'testing'
        elif 'deploy' in path_str or 'deploy' in content_lower:
            return 'deployment'
        elif 'monitor' in path_str or 'monitor' in content_lower:
            return 'monitoring'
        elif 'template' in path_str or 'template' in content_lower:
            return 'template_management'
        elif 'framework' in path_str or 'framework' in content_lower:
            return 'core_framework'
        else:
            return 'utility'

    def extract_dependencies(self, content):
        """Extract dependencies from Python script"""
        dependencies = []
        lines = content.split('\n')

        for line in lines:
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                dependencies.append(line)

        return json.dumps(dependencies[:20])  # Limit to first 20 imports

    def count_lines_of_code(self, content):
        """Count actual lines of code (excluding comments and empty lines)"""
        lines = content.split('\n')
        code_lines = 0

        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('"""') and not line.startswith("'''"):
                code_lines += 1

        return code_lines

    def synchronize_file_to_database(self, file_path):
        """Synchronize a single file to the database"""
        try:
            absolute_path = file_path if file_path.is_absolute() else self.workspace_root / file_path
            relative_path = absolute_path.relative_to(self.workspace_root)

            content = self.get_file_content(absolute_path)
            if not content:
                return False

            file_hash = self.get_file_hash(content)
            file_size = absolute_path.stat().st_size
            category = self.categorize_script(file_path, content)
            dependencies = self.extract_dependencies(content)
            lines_of_code = self.count_lines_of_code(content)

            conn = sqlite3.connect(self.production_db)
            cursor = conn.cursor()

            # Check if script already exists
            cursor.execute("SELECT script_id, script_hash FROM enhanced_script_tracking WHERE script_path = ?",
                         (str(relative_path),))
            existing = cursor.fetchone()

            if existing:
                script_id, existing_hash = existing
                if existing_hash != file_hash:
                    # Update existing record
                    cursor.execute("""
                        UPDATE enhanced_script_tracking
                        SET script_content = ?, script_hash = ?, file_size = ?,
                            lines_of_code = ?, last_updated = CURRENT_TIMESTAMP,
                            functionality_category = ?, dependencies = ?
                        WHERE script_id = ?
                    """, (
                          content,
                          file_hash,
                          file_size,
                          lines_of_code,
                          category,
                          dependencies,
                          script_id)
                    """, (content, file_hash,)

                    self.sync_results["scripts_updated"].append(str(relative_path))
                    self.logger.info(f"Updated: {relative_path}")
            else:
                # Insert new record
                cursor.execute("""
                    INSERT INTO enhanced_script_tracking
                    (script_path, script_content, script_hash, file_size, lines_of_code,
                     functionality_category, dependencies, regeneration_priority)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (str(relative_path), content, file_hash, file_size, lines_of_code,
                      category, dependencies, 5))

                self.sync_results["scripts_added"].append(str(relative_path))
                self.logger.info(f"Added: {relative_path}")

            # Also add to complete file system mapping
            cursor.execute("""
                INSERT OR REPLACE INTO complete_file_system_mapping
                (file_path, file_content, file_hash, file_size, file_type, updated_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (str(relative_path), content, file_hash, file_size, 'python'))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            error_msg = f"Error synchronizing {file_path}: {e}"
            self.logger.error(error_msg)
            self.sync_results["errors"].append(error_msg)
            return False

    def synchronize_all_scripts(self):
        """Synchronize all Python scripts to database"""
        self.logger.info("Starting comprehensive script synchronization...")

        # Find all Python scripts
        python_files = list(self.workspace_root.rglob("*.py"))
        total_files = len(python_files)

        self.logger.info(f"Found {total_files} Python files to synchronize")

        successful = 0
        for i, file_path in enumerate(python_files, 1):
            if i % 100 == 0:
                self.logger.info(f"Progress: {i}/{total_files} ({(i/total_files)*100:.1f}%)")

            if self.synchronize_file_to_database(file_path):
                successful += 1

        self.logger.info(f"Synchronization complete: {successful}/{total_files} successful")
        return successful, total_files

    def validate_reproducibility(self):
        """Validate that all database scripts are reproducible"""
        self.logger.info("Validating script reproducibility...")

        try:
            conn = sqlite3.connect(self.production_db)
            cursor = conn.cursor()

            # Get all scripts with content
            cursor.execute("""
                SELECT script_path, script_content, script_hash
                FROM enhanced_script_tracking
                WHERE script_content IS NOT NULL AND script_content != ''
            """)

            scripts = cursor.fetchall()
            reproducible_count = 0

            for script_path, content, stored_hash in scripts:
                # Verify hash matches content
                calculated_hash = self.get_file_hash(content)
                if calculated_hash == stored_hash:
                    reproducible_count += 1
                    self.sync_results["content_synchronized"].append(script_path)
                else:
                    self.logger.warning(f"Hash mismatch for {script_path}")

            conn.close()

            self.logger.info(f"Reproducible scripts: {reproducible_count}/{len(scripts)}")
            return reproducible_count, len(scripts)

        except Exception as e:
            self.logger.error(f"Error validating reproducibility: {e}")
            return 0, 0

    def record_compliance_status(
                                 self,
                                 total_scripts,
                                 synchronized_scripts,
                                 reproducible_scripts)
    def record_compliance_status(sel)
        """Record compliance status in database"""
        try:
            compliance_percentage = (synchronized_scripts / max(total_scripts, 1)) * 100

            if compliance_percentage >= 95:
                status = "EXCELLENT"
            elif compliance_percentage >= 80:
                status = "GOOD"
            elif compliance_percentage >= 60:
                status = "NEEDS_IMPROVEMENT"
            else:
                status = "CRITICAL"

            conn = sqlite3.connect(self.production_db)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO database_first_compliance
                (total_scripts, synchronized_scripts, reproducible_scripts,
                 compliance_percentage, status, validation_notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (total_scripts, synchronized_scripts, reproducible_scripts,
                  compliance_percentage, status,
                  f"Sync completed: {len(
                                         self.sync_results['scripts_added'])} added,
                                         {len(self.sync_results['scripts_updated'])} updated")
                  f"Sync completed: {len(self.sync_results)

            conn.commit()
            conn.close()

            self.logger.info(f"Compliance status recorded: {status} ({compliance_percentage:.1f}%)")

        except Exception as e:
            self.logger.error(f"Error recording compliance status: {e}")

    def generate_sync_report(self):
        """Generate synchronization report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        self.sync_results["statistics"] = {
            "scripts_added": len(self.sync_results["scripts_added"]),
            "scripts_updated": len(self.sync_results["scripts_updated"]),
            "content_synchronized": len(self.sync_results["content_synchronized"]),
            "errors": len(self.sync_results["errors"]),
            "sync_timestamp": timestamp
        }

        report_file = self.workspace_root / f"database_first_synchronization_report_{timestamp}.json"

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.sync_results, f, indent=2, ensure_ascii=False)

        self.logger.info(f"Synchronization report saved: {report_file}")
        return report_file

    def run_full_synchronization(self):
        """Run complete database-first synchronization"""
        self.logger.info("=== ENTERPRISE DATABASE-FIRST SYNCHRONIZATION ===")

        try:
            # Ensure database structure
            self.ensure_database_structure()

            # Synchronize all scripts
            successful, total = self.synchronize_all_scripts()

            # Validate reproducibility
            reproducible, tracked = self.validate_reproducibility()

            # Record compliance status
            self.record_compliance_status(total, successful, reproducible)

            # Generate report
            report_file = self.generate_sync_report()

            # Print summary
            print("\n" + "="*80)
            print("DATABASE-FIRST SYNCHRONIZATION SUMMARY")
            print("="*80)
            print(f"Total Python Scripts: {total}")
            print(f"Successfully Synchronized: {successful}")
            print(f"Scripts Added: {len(self.sync_results['scripts_added'])}")
            print(f"Scripts Updated: {len(self.sync_results['scripts_updated'])}")
            print(f"Reproducible Scripts: {reproducible}")
            print(f"Errors: {len(self.sync_results['errors'])}")
            print(f"Compliance Rate: {(successful/max(total,1))*100:.1f}%")
            print(f"Reproducibility Rate: {(reproducible/max(tracked,1))*100:.1f}%")

            if successful/max(total,1) >= 0.95:
                print("STATUS: ✅ DATABASE-FIRST ARCHITECTURE COMPLIANT")
            else:
                print("STATUS: ⚠️ ADDITIONAL SYNCHRONIZATION NEEDED")

            print(f"\nDetailed report: {report_file}")
            print("="*80)

            return report_file

        except Exception as e:
            self.logger.error(f"Synchronization failed: {e}")
            raise


def main():
    synchronizer = DatabaseFirstSynchronizer()
    report_file = synchronizer.run_full_synchronization()

    print("\n🎯 Database-first synchronization complete!")
    print(f"📊 Report: {report_file}")

    # Show sample synchronized scripts
    if synchronizer.sync_results["scripts_added"]:
        print("\nSample newly added scripts:")
        for i, script in enumerate(synchronizer.sync_results["scripts_added"][:5]):
            print(f"  {i+1}. {script}")

    if synchronizer.sync_results["scripts_updated"]:
        print("\nSample updated scripts:")
        for i, script in enumerate(synchronizer.sync_results["scripts_updated"][:5]):
            print(f"  {i+1}. {script}")

if __name__ == "__main__":
    main()
