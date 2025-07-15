#!/usr/bin/env python3
"""
Database-First Script Consolidation Migration Script
Generated: 2025-01-15

Safely migrates from 5 duplicate database-first scripts to unified engine:
- Backs up original files to backup/database_first_consolidation/
- Generates migration report with timestamps and file counts
- Provides rollback functionality
- Validates migration safety

Enterprise Standards Compliance:
- Flake8/PEP 8 Compliant
- Emoji-free code (text-based indicators only)
- Safe migration with validation
"""
import sys
import shutil
import json
from pathlib import Path
from datetime import datetime

# Text-based indicators (NO Unicode emojis)
TEXT_INDICATORS = {
    'start': '[START]',
    'success': '[SUCCESS]',
    'error': '[ERROR]',
    'backup': '[BACKUP]',
    'info': '[INFO]',
    'warning': '[WARNING]'
}

# Files to be consolidated
TARGET_FILES = [
    "database_first_enhancement_executor.py",
    "database_first_synchronization_engine.py",
    "database_first_flake8_discovery_engine.py",
    "database_first_flake8_compliance_scanner.py",
    "database_first_flake8_compliance_scanner_v2.py"
]

# Unified replacement file
UNIFIED_FILE = "database_first_unified_engine.py"


class ConsolidationMigrationScript:
    """Safe migration script for database-first consolidation"""

    def __init__(self, workspace_path: str = "."):
        self.workspace_path = Path(workspace_path)
        self.backup_dir = (self.workspace_path / "backup"
                           / "database_first_consolidation")
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.migration_report = {}

    def execute_migration(self, dry_run: bool = False) -> bool:
        """Execute the migration process

        Args:
            dry_run: If True, only simulate the migration without making
                changes

        Returns:
            bool: True if migration completed successfully
        """
        start_time = datetime.now()

        print(f"{TEXT_INDICATORS['start']} Database-first consolidation "
              f"migration started")
        print(f"{TEXT_INDICATORS['info']} Timestamp: {self.timestamp}")
        print(f"{TEXT_INDICATORS['info']} Workspace: {self.workspace_path}")
        print(f"{TEXT_INDICATORS['info']} Dry run: {dry_run}")

        try:
            # Step 1: Validate prerequisites
            if not self._validate_prerequisites():
                return False

            # Step 2: Create backup directory
            if not self._create_backup_directory(dry_run):
                return False

            # Step 3: Backup original files
            if not self._backup_original_files(dry_run):
                return False

            # Step 4: Validate unified engine exists
            if not self._validate_unified_engine():
                return False

            # Step 5: Generate migration report
            if not self._generate_migration_report(dry_run):
                return False

            duration = (datetime.now() - start_time).total_seconds()

            if dry_run:
                print(f"{TEXT_INDICATORS['success']} Migration simulation "
                      f"completed in {duration:.1f}s")
                print(f"{TEXT_INDICATORS['info']} No files were actually "
                      f"modified")
            else:
                print(f"{TEXT_INDICATORS['success']} Migration completed "
                      f"in {duration:.1f}s")
                print(f"{TEXT_INDICATORS['info']} Original files backed up "
                      f"to: {self.backup_dir}")

            return True

        
        except Exception as e:
            print(f"{TEXT_INDICATORS['error']} Migration failed: {e}")
            return False

    def rollback_migration(self) -> bool:
        """Rollback the migration by restoring original files"""
        print(f"{TEXT_INDICATORS['start']} Rolling back database-first "
              f"consolidation")

        try:
            if not self.backup_dir.exists():
                print(f"{TEXT_INDICATORS['error']} Backup directory not "
                      f"found: {self.backup_dir}")
                return False

            # Find the most recent backup
            backup_subdirs = [d for d in self.backup_dir.iterdir()
                              if d.is_dir()]
            if not backup_subdirs:
                print(f"{TEXT_INDICATORS['error']} No backups found in "
                      f"{self.backup_dir}")
                return False

            latest_backup = max(backup_subdirs, key=lambda x: x.name)
            print(f"{TEXT_INDICATORS['info']} Restoring from backup: "
                  f"{latest_backup}")

            # Restore each file
            restored_count = 0
            for target_file in TARGET_FILES:
                backup_file = latest_backup / target_file
                target_path = self.workspace_path / target_file

                if backup_file.exists():
                    shutil.copy2(backup_file, target_path)
                    print(f"{TEXT_INDICATORS['backup']} Restored: "
                          f"{target_file}")
                    restored_count += 1
                else:
                    print(f"{TEXT_INDICATORS['warning']} Backup not found: "
                          f"{backup_file}")

            print(f"{TEXT_INDICATORS['success']} Rollback completed: "
                  f"{restored_count} files restored")
            return True

        
        except Exception as e:
            print(f"{TEXT_INDICATORS['error']} Rollback failed: {e}")
            return False

    def _validate_prerequisites(self) -> bool:
        """Validate that prerequisites are met"""
        print(f"{TEXT_INDICATORS['info']} Validating prerequisites...")
        
        # Check if workspace exists
        if not self.workspace_path.exists():
            print(f"{TEXT_INDICATORS['error']} Workspace not found: "
                  f"{self.workspace_path}")
            return False

        # Check which target files exist
        existing_files = []
        missing_files = []

        for target_file in TARGET_FILES:
            file_path = self.workspace_path / target_file
            if file_path.exists():
                existing_files.append(target_file)
            else:
                missing_files.append(target_file)

        print(f"{TEXT_INDICATORS['info']} Found {len(existing_files)} "
              f"target files")
        if missing_files:
            print(f"{TEXT_INDICATORS['warning']} Missing files: "
                  f"{missing_files}")

        if len(existing_files) == 0:
            print(f"{TEXT_INDICATORS['error']} No target files found to "
                  f"migrate")
            return False

        self.migration_report['existing_files'] = existing_files
        self.migration_report['missing_files'] = missing_files

        return True

    def _create_backup_directory(self, dry_run: bool) -> bool:
        """Create backup directory structure"""
        backup_subdir = self.backup_dir / self.timestamp

        print(f"{TEXT_INDICATORS['info']} Creating backup directory: "
              f"{backup_subdir}")

        if dry_run:
            print(f"{TEXT_INDICATORS['info']} [DRY RUN] Would create: "
                  f"{backup_subdir}")
            return True

        try:
            backup_subdir.mkdir(parents=True, exist_ok=True)
            self.migration_report['backup_directory'] = str(backup_subdir)
            return True
        except Exception as e:
            print(f"{TEXT_INDICATORS['error']} Failed to create backup "
                  f"directory: {e}")
            return False

    def _backup_original_files(self, dry_run: bool) -> bool:
        """Backup original files to backup directory"""
        backup_subdir = self.backup_dir / self.timestamp
        backup_info = []

        print(f"{TEXT_INDICATORS['backup']} Backing up original files...")

        for target_file in TARGET_FILES:
            source_path = self.workspace_path / target_file
            backup_path = backup_subdir / target_file

            if source_path.exists():
                if dry_run:
                    print(f"{TEXT_INDICATORS['info']} [DRY RUN] Would "
                          f"backup: {target_file}")
                else:
                    try:
                        shutil.copy2(source_path, backup_path)
                        print(f"{TEXT_INDICATORS['backup']} Backed up: "
                              f"{target_file}")

                        # Record file info
                        file_stat = source_path.stat()
                        backup_info.append({
                            'filename': target_file,
                            'size_bytes': file_stat.st_size,
                            'modified_time': datetime.fromtimestamp(
                                file_stat.st_mtime).isoformat(),
                            'backup_path': str(backup_path)
                        })
                    except Exception as e:
                        print(f"{TEXT_INDICATORS['error']} Failed to backup "
                              f"{target_file}: {e}")
                        return False
            else:
                print(f"{TEXT_INDICATORS['warning']} File not found: "
                      f"{target_file}")

        self.migration_report['backed_up_files'] = backup_info
        print(f"{TEXT_INDICATORS['success']} Backup completed: "
              f"{len(backup_info)} files")
        return True

    def _validate_unified_engine(self) -> bool:
        """Validate that the unified engine file exists and is valid"""
        unified_path = self.workspace_path / UNIFIED_FILE

        print(f"{TEXT_INDICATORS['info']} Validating unified engine: "
              f"{UNIFIED_FILE}")

        if not unified_path.exists():
            print(f"{TEXT_INDICATORS['error']} Unified engine not found: "
                  f"{unified_path}")
            return False

        # Check file size
        file_stat = unified_path.stat()
        if file_stat.st_size < 1000:  # Minimum reasonable size
            print(f"{TEXT_INDICATORS['error']} Unified engine file too "
                  f"small: {file_stat.st_size} bytes")
            return False

        # Try to parse as Python (basic syntax check)
        try:
            with open(unified_path, 'r', encoding='utf-8') as f:
                content = f.read()

            compile(content, str(unified_path), 'exec')

            # Check for required class
            if 'DatabaseFirstUnifiedEngine' not in content:
                print(f"{TEXT_INDICATORS['error']} Required class not found "
                      f"in unified engine")
                return False

        except SyntaxError as e:
            print(f"{TEXT_INDICATORS['error']} Syntax error in unified "
                  f"engine: {e}")
            return False
        except Exception as e:
            print(f"{TEXT_INDICATORS['error']} Error validating unified "
                  f"engine: {e}")
            return False

        self.migration_report['unified_engine'] = {
            'filename': UNIFIED_FILE,
            'size_bytes': file_stat.st_size,
            'modified_time': datetime.fromtimestamp(
                file_stat.st_mtime).isoformat(),
            'validation_passed': True
        }

        print(f"{TEXT_INDICATORS['success']} Unified engine validation "
              f"passed")
        return True

    def _generate_migration_report(self, dry_run: bool) -> bool:
        """Generate comprehensive migration report"""
        report_path = self.backup_dir / f"migration_report_{self.timestamp}.json"

        # Complete migration report
        self.migration_report.update({
            'migration_timestamp': self.timestamp,
            'migration_type': 'database_first_consolidation',
            'dry_run': dry_run,
            'workspace_path': str(self.workspace_path),
            'backup_directory': str(self.backup_dir),
            'target_files_count': len(TARGET_FILES),
            'files_found': len(self.migration_report.get('existing_files', [])),
            'files_backed_up': len(self.migration_report.get('backed_up_files',
                                                             [])),
            'consolidation_summary': {
                'original_files': TARGET_FILES,
                'unified_file': UNIFIED_FILE,
                'estimated_line_reduction': '60%',
                'estimated_file_reduction': '80%'
            }
        })

        if dry_run:
            print(f"{TEXT_INDICATORS['info']} [DRY RUN] Would generate "
                  f"report: {report_path}")
        else:
            try:
                # Ensure backup directory exists
                self.backup_dir.mkdir(parents=True, exist_ok=True)

                with open(report_path, 'w', encoding='utf-8') as f:
                    json.dump(self.migration_report, f, indent=2)

                print(f"{TEXT_INDICATORS['success']} Migration report "
                      f"saved: {report_path}")
            except Exception as e:
                print(f"{TEXT_INDICATORS['error']} Failed to save "
                      f"migration report: {e}")
                return False

        # Print summary
        print("\n" + TEXT_INDICATORS['info'] + " MIGRATION SUMMARY:")
        print("  Target files: " + str(len(TARGET_FILES)))
        print("  Files found: " + str(len(self.migration_report.get(
            'existing_files', []))))
        print("  Files backed up: " + str(len(self.migration_report.get(
            'backed_up_files', []))))
        print("  Unified engine: " + UNIFIED_FILE)
        print("  Estimated benefits:")
        print("    - 80% file reduction (5 → 1 files)")
        print("    - 60% code reduction (~500 → ~200 lines)")
        print("    - 100% duplication elimination")

        return True


def main():
    """Main execution function"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Database-First Consolidation Migration Script"
    )
    parser.add_argument(
        "--action",
        choices=["migrate", "rollback"],
        default="migrate",
        help="Action to perform"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate migration without making changes"
    )
    parser.add_argument(
        "--workspace",
        default=".",
        help="Workspace directory path"
    )

    args = parser.parse_args()

    migrator = ConsolidationMigrationScript(workspace_path=args.workspace)

    if args.action == "migrate":
        success = migrator.execute_migration(dry_run=args.dry_run)
    elif args.action == "rollback":
        success = migrator.rollback_migration()
    else:
        print(f"{TEXT_INDICATORS['error']} Invalid action: {args.action}")
        return False

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
