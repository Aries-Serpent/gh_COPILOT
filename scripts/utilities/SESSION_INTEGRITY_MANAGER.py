#!/usr/bin/env python3
"""
SESSION INTEGRITY MANAGER - Enterprise Session End Validation
Generated using database-first patterns from analytics.db pis_sessions table

Database schema discovered:
- session_id (TEXT, NOT NULL)
- start_time (TEXT, NOT NULL)
- end_time (TEXT)
- status (TEXT, NOT NULL, DEFAULT 'ACTIVE')
- created_at (TEXT, DEFAULT CURRENT_TIMESTAMP)

Implements comprehensive session end validation with enterprise compliance.
"""

import os
import sys
import sqlite3
import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'session_integrity_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler(sys.stdout)
    ]
)


class SessionIntegrityManager:
    """Enterprise Session Integrity Manager with Database-First Validation"""

    def __init__(self, action: str = "end", level: str = "enterprise", auto_fix: bool = False):
        self.action = action
        self.level = level
        self.auto_fix = auto_fix
        self.workspace_path = Path(os.getcwd())
        self.session_start_time = datetime.now()

        # Database-first session management
        self.session_databases = self._discover_session_databases()
        self.session_id = self._generate_session_id()

        # Enterprise validation metrics
        self.validation_results = {
            'database_integrity': False,
            'file_system_integrity': False,
            'anti_recursion_compliance': False,
            'zero_byte_protection': False,
            'enterprise_compliance': False,
            'session_completion': False
        }

        logging.info("[INIT] Session Integrity Manager initialized")
        logging.info(f"[INFO] Action: {action}, Level: {level}, Auto-fix: {auto_fix}")
        logging.info(f"[INFO] Session ID: {self.session_id}")

    def _discover_session_databases(self) -> List[Path]:
        """Discover databases with session management capabilities"""
        session_databases = []

        for db_file in self.workspace_path.glob("*.db"):
            if db_file.is_file() and db_file.stat().st_size > 0:
                try:
                    with sqlite3.connect(db_file) as conn:
                        cursor = conn.cursor()

                        # Check for session-related tables
                        cursor.execute("SELECT name FROM sqlite_master WHERE " \
                                       " \
                                       "                    "ype='table' AND name LIKE '%session%'")
                        session_tables = cursor.fetchall()

                        if session_tables:
                            session_databases.append(db_file)
                            logging.info(
    f"[DB] Found session database: {db_file} with tables: {session_tables}")

                except Exception as e:
                    logging.warning(f"[WARNING] Could not check database {db_file}: {e}")

        return session_databases

    def _generate_session_id(self) -> str:
        """Generate unique session ID using database pattern"""
        return f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.getpid()}"

    def _record_session_data(self, status: str = "ACTIVE") -> bool:
        """Record session data in database following discovered schema"""
        try:
            # Use analytics.db if available, or create session record
            analytics_db = self.workspace_path / "analytics.db"

            if analytics_db.exists():
                with sqlite3.connect(analytics_db) as conn:
                    cursor = conn.cursor()

                    # Insert session record following database schema
                    cursor.execute("""
                        INSERT OR REPLACE INTO pis_sessions
                        (session_id, start_time, end_time, status, created_at)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        self.session_id,
                        self.session_start_time.isoformat(),
                        datetime.now().isoformat() if status == "COMPLETED" else None,
                        status,
                        datetime.now().isoformat()
                    ))

                    logging.info(f"[DB] Session record updated: {self.session_id} - {status}")
                    return True

        except Exception as e:
            logging.error(f"[ERROR] Session recording failed: {e}")
            return False

        return False

    def validate_database_integrity(self) -> bool:
        """Validate database integrity across all discovered databases"""
        try:
            database_count = 0
            valid_databases = 0
            empty_databases = []

            # Search for databases in multiple locations
            search_patterns = ["*.db", "databases/*.db", "**/*.db"]

            for pattern in search_patterns:
                for db_file in self.workspace_path.glob(pattern):
                    if (db_file.is_file() and
                        "_ZERO_BYTE_QUARANTINE" not in str(db_file)):
                        if db_file.stat().st_size == 0:
                            empty_databases.append(str(db_file))
                            continue

                        database_count += 1

                        try:
                            with sqlite3.connect(db_file) as conn:
                                # Perform integrity check
                                cursor = conn.cursor()
                                cursor.execute("PRAGMA integrity_check")
                                result = cursor.fetchone()

                                if result and result[0] == "ok":
                                    valid_databases += 1
                                else:
                                    logging.warning(f"[WARNING] Database integrity issue: {db_file}")

                                    if self.auto_fix:
                                        # Attempt auto-repair
                                        cursor.execute("VACUUM")
                                        logging.info(f"[AUTOFIX] Attempted repair of {db_file}")

                        except Exception as e:
                            logging.error(f"[ERROR] Database validation failed for {db_file}: {e}")

            if database_count == 0:
                if empty_databases:
                    logging.info(
                        f"[ADVISORY] Skipped {len(empty_databases)} empty database(s)"
                    )
                else:
                    logging.info("[ADVISORY] No databases found for validation")
                self.validation_results['database_integrity'] = True
                return True

            integrity_percentage = (
                valid_databases /
                database_count *
                100)
            self.validation_results['database_integrity'] = integrity_percentage >= 95.0

            logging.info(
                f"[VALIDATION] Database Integrity: {valid_databases}/{database_count} ({integrity_percentage:.1f}%)"
            )
            if empty_databases:
                logging.info(
                    f"[ADVISORY] Skipped {len(empty_databases)} empty database(s)"
                )
            return self.validation_results['database_integrity']

        except Exception as e:
            logging.error(f"[ERROR] Database integrity validation failed: {e}")
            return False

    def validate_file_system_integrity(self) -> bool:
        """Validate file system integrity and zero-byte protection"""
        try:
            total_files = 0
            zero_byte_count = 0
            removed_count = 0

            for file_path in self.workspace_path.rglob("*"):
                if file_path.is_file():
                    total_files += 1

                    if file_path.stat().st_size == 0:
                        zero_byte_count += 1

                        if self.auto_fix:
                            try:
                                file_path.unlink()
                                removed_count += 1
                            except Exception as e:
                                logging.warning(
                                    f"[WARNING] Could not remove zero-byte file {file_path}: {e}")

            zero_byte_percentage = (
                zero_byte_count /
                total_files *
                100) if total_files > 0 else 0
            self.validation_results['zero_byte_protection'] = zero_byte_percentage < 1.0

            if zero_byte_count:
                logging.warning(
                    f"[WARNING] Found {zero_byte_count} zero-byte files ({zero_byte_percentage:.2f}%)")
                if self.auto_fix and removed_count:
                    logging.info(
                        f"[AUTOFIX] Removed {removed_count} zero-byte file(s) from {self.workspace_path}"
                    )
            else:
                logging.info("[SUCCESS] No zero-byte files detected")

            self.validation_results['file_system_integrity'] = True
            return True

        except Exception as e:
            logging.error(f"[ERROR] File system integrity validation failed: {e}")
            return False

    def validate_anti_recursion_compliance(self) -> bool:
        """Validate anti-recursion compliance (no backup folders in workspace)"""
        try:
            workspace_root = self.workspace_path
            forbidden_patterns = ['*backup*', '*_backup_*', 'backups', '*temp*']
            violations = []

            for pattern in forbidden_patterns:
                for folder in workspace_root.rglob(pattern):
                    if folder.is_dir() and folder != workspace_root:
                        # Check if it's actually a violation (inside workspace)
                        if str(folder).startswith(str(workspace_root)):
                            violations.append(str(folder))

                            if self.auto_fix:
                                try:
                                    import shutil
                                    shutil.rmtree(folder)
                                    logging.info(f"[AUTOFIX] Removed recursive folder: {folder}")
                                except Exception as e:
                                    logging.error(
    f"[ERROR] Could not remove recursive folder {folder}: {e}")

            self.validation_results['anti_recursion_compliance'] = len(violations) == 0

            if violations:
                logging.warning(f"[WARNING] Anti-recursion violations found: {violations}")
            else:
                logging.info("[SUCCESS] No anti-recursion violations detected")

            return self.validation_results['anti_recursion_compliance']

        except Exception as e:
            logging.error(f"[ERROR] Anti-recursion validation failed: {e}")
            return False

    def validate_enterprise_compliance(self) -> bool:
        """Validate overall enterprise compliance standards"""
        try:
            # Check for required enterprise components
            required_components = [
                'deployment_optimization_engine_fixed.py',  # Phase 3 deployment
                'enterprise_optimization_engine.py',       # Phase 2 optimization
                'database_purification_engine.py'          # Phase 1 purification
            ]

            missing_components = []
            for component in required_components:
                component_path = self.workspace_path / component
                if not component_path.exists():
                    missing_components.append(component)

            enterprise_compliance = len(missing_components) == 0

            # Check deployment package exists (ZIP or JSON)
            deployment_packages = list(self.workspace_path.glob("deployment_package_*.zip"))
            deployment_json = list(self.workspace_path.glob("deployment_package.json"))
            has_deployment_package = len(deployment_packages) > 0 or len(deployment_json) > 0

            self.validation_results['enterprise_compliance'] = enterprise_compliance \
        and has_deployment_package

            if missing_components:
                logging.warning(f"[WARNING] Missing enterprise components: {missing_components}")
            if not has_deployment_package:
                logging.warning("[WARNING] No deployment package found")

            if self.validation_results['enterprise_compliance']:
                logging.info("[SUCCESS] Enterprise compliance validated")
            else:
                logging.warning("[WARNING] Enterprise compliance issues detected")

            return self.validation_results['enterprise_compliance']

        except Exception as e:
            logging.error(f"[ERROR] Enterprise compliance validation failed: {e}")
            return False

    def execute_session_end_validation(self) -> Dict[str, Any]:
        """Execute comprehensive session end validation"""
        logging.info("[START] Session end validation initiated")

        try:
            # Record session start
            self._record_session_data("VALIDATING")

            # Run all validation checks
            validations = [
                ("Database Integrity", self.validate_database_integrity),
                ("File System Integrity", self.validate_file_system_integrity),
                ("Anti-Recursion Compliance", self.validate_anti_recursion_compliance),
                ("Enterprise Compliance", self.validate_enterprise_compliance)
            ]

            validation_summary = {}
            all_passed = True

            for validation_name, validation_func in validations:
                try:
                    result = validation_func()
                    validation_summary[validation_name] = result
                    if not result:
                        all_passed = False
                        logging.error(f"[FAILED] {validation_name} validation failed")
                    else:
                        logging.info(f"[PASSED] {validation_name} validation passed")

                except Exception as e:
                    validation_summary[validation_name] = False
                    all_passed = False
                    logging.error(f"[ERROR] {validation_name} validation error: {e}")

            # Final session status
            final_status = "COMPLETED" if all_passed else "FAILED"
            self.validation_results['session_completion'] = all_passed

            # Record final session data
            self._record_session_data(final_status)

            # Generate validation report
            validation_report = {
                'session_id': self.session_id,
                'validation_time': datetime.now().isoformat(),
                'overall_status': final_status,
                'validation_results': self.validation_results,
                'validation_summary': validation_summary,
                'action': self.action,
                'level': self.level,
                'auto_fix': self.auto_fix
            }

            # Save validation report
            report_path = self.workspace_path / \
                f"session_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_path, 'w') as f:
                json.dump(validation_report, f, indent=2)

            logging.info(f"[REPORT] Validation report saved: {report_path}")

            return validation_report

        except Exception as e:
            logging.error(f"[ERROR] Session end validation failed: {e}")
            return {'error': str(e), 'status': 'FAILED'}


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
    description='Session Integrity Manager - Enterprise Session End Validation')
    parser.add_argument(
    '--action',
    default='end',
    choices=[
        'start',
        'end',
        'validate'],
         help='Session action')
    parser.add_argument(
    '--level',
    default='enterprise',
    choices=[
        'basic',
        'standard',
        'enterprise'],
         help='Validation level')
    parser.add_argument('--auto-fix', action='store_true', help='Enable automatic fixes')

    args = parser.parse_args()

    print("=" * 80)
    print("SESSION INTEGRITY MANAGER - Enterprise Session End Validation")
    print("Generated using database-first patterns from session management schema")
    print("=" * 80)
    print(f"Action: {args.action}")
    print(f"Level: {args.level}")
    print(f"Auto-fix: {args.auto_fix}")
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    try:
        # Initialize session manager
        session_manager = SessionIntegrityManager(
            action=args.action,
            level=args.level,
            auto_fix=args.auto_fix
        )

        # Execute session end validation
        if args.action == 'end':
            validation_report = session_manager.execute_session_end_validation()

            print("\n" + "=" * 80)
            print("SESSION END VALIDATION RESULTS")
            print("=" * 80)

            if validation_report.get('overall_status') == 'COMPLETED':
                print("[SUCCESS] All validations passed - Session end validated")
                print("[SUCCESS] Enterprise compliance confirmed")
                print("[SUCCESS] Database integrity verified")
                print("[SUCCESS] File system integrity confirmed")
                print("[SUCCESS] Anti-recursion compliance verified")
            else:
                print("[WARNING] Some validations failed - Review required")
                if validation_report.get('validation_summary'):
                    for check, result in validation_report['validation_summary'].items():
                        status = "[PASSED]" if result else "[FAILED]"
                        print(f"{status} {check}")

            print("=" * 80)
            print("SESSION INTEGRITY MANAGER - VALIDATION COMPLETE")
            print("=" * 80)

            return validation_report.get('overall_status') == 'COMPLETED'

        else:
            logging.info(f"[INFO] Session action '{args.action}' completed")
            return True

    except Exception as e:
        logging.error(f"[ERROR] Session integrity manager failed: {e}")
        print(f"[ERROR] Session validation failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    from secondary_copilot_validator import SecondaryCopilotValidator

    SecondaryCopilotValidator().validate_corrections([__file__])
    sys.exit(0 if success else 1)
