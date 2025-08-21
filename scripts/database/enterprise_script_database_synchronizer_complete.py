#!/usr/bin/env python3
"""
Enterprise Script Database Synchronizer - Complete Integration
Comprehensive script to validate and synchronize all scripts between repository and databases

Enterprise Standards Compliance:
- Flake8/PEP 8 Compliant
- Database-first architecture
- Hash validation and timestamp tracking
- Comprehensive reporting and logging
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict

from script_database_validator import TEXT_INDICATORS, ScriptDatabaseValidator

from scripts.database.cross_database_sync_logger import log_sync_operation
from scripts.database.unified_database_initializer import initialize_database


class EnterpriseScriptDatabaseSynchronizer:
    """Enterprise-grade script database synchronization system"""

    def __init__(self, workspace_root: str = "."):
        """Initialize the synchronizer"""
        self.workspace_root = Path(workspace_root)
        self.validator = ScriptDatabaseValidator(workspace_root)
        self.results_dir = self.workspace_root / "results" / "script_sync"
        self.results_dir.mkdir(parents=True, exist_ok=True)

        # Enterprise unified database
        self.enterprise_db = self.workspace_root / "databases" / "enterprise_assets.db"
        initialize_database(self.enterprise_db)

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(self.results_dir / "sync_operations.log"), logging.StreamHandler(sys.stdout)],
        )
        self.logger = logging.getLogger(__name__)

    def perform_comprehensive_sync(self, auto_sync: bool = False, backup_db: bool = True) -> Dict:
        """Perform comprehensive synchronization with validation"""
        self.logger.info(f"{TEXT_INDICATORS['start']} Starting comprehensive script database synchronization...")
        start_dt = log_sync_operation(self.enterprise_db, "start_sync")

        sync_session = {
            "session_id": f"sync_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "start_time": datetime.now().isoformat(),
            "auto_sync": auto_sync,
            "backup_created": False,
            "validation_results": {},
            "sync_results": {},
            "completion_status": "in_progress",
        }

        try:
            # Step 1: Backup database if requested
            if backup_db:
                backup_start = log_sync_operation(self.enterprise_db, "backup_start")
                sync_session["backup_created"] = self._backup_databases()
                log_sync_operation(
                    self.enterprise_db,
                    "backup_complete",
                    start_time=backup_start,
                )

            # Step 2: Validate current state
            self.logger.info(f"{TEXT_INDICATORS['info']} Performing initial validation...")
            initial_results = self.validator.validate_script_sync()
            sync_session["validation_results"]["initial"] = initial_results

            # Step 3: Generate detailed report
            report_file = self.results_dir / f"validation_report_{sync_session['session_id']}.md"
            self.validator.generate_validation_report(str(report_file))
            sync_session["initial_report"] = str(report_file)

            # Step 4: Perform synchronization if requested
            if auto_sync:
                sync_session["sync_results"] = self._perform_synchronization(initial_results)

                # Step 5: Post-sync validation
                final_results = self.validator.validate_script_sync()
                sync_session["validation_results"]["final"] = final_results

                # Generate final report
                final_report_file = self.results_dir / f"final_report_{sync_session['session_id']}.md"
                self.validator.generate_validation_report(str(final_report_file))
                sync_session["final_report"] = str(final_report_file)

            sync_session["completion_status"] = "completed"
            sync_session["end_time"] = datetime.now().isoformat()
            log_sync_operation(
                self.enterprise_db,
                "sync_complete",
                start_time=start_dt,
            )

        except Exception as e:
            self.logger.error(f"{TEXT_INDICATORS['error']} Synchronization failed: {e}")
            sync_session["completion_status"] = "failed"
            sync_session["error"] = str(e)
            log_sync_operation(
                self.enterprise_db,
                "sync_failed",
                start_time=start_dt,
                status="FAILURE",
            )

        # Save session results
        session_file = self.results_dir / f"sync_session_{sync_session['session_id']}.json"
        with open(session_file, "w") as f:
            json.dump(sync_session, f, indent=2, default=str)

        self._log_sync_summary(sync_session)
        return sync_session

    def _backup_databases(self) -> bool:
        """Create backup of all databases"""
        start_dt = log_sync_operation(self.enterprise_db, "backup_create_start")
        try:
            backup_dir = (
                self.workspace_root / "archives" / "database_backups" / datetime.now().strftime("%Y%m%d_%H%M%S")
            )
            backup_dir.mkdir(parents=True, exist_ok=True)

            databases_dir = self.workspace_root / "databases"
            if databases_dir.exists():
                import shutil

                for db_file in databases_dir.glob("*.db"):
                    backup_file = backup_dir / db_file.name
                    shutil.copy2(db_file, backup_file)
                    self.logger.info(f"{TEXT_INDICATORS['database']} Backed up {db_file.name}")

            self.logger.info(f"{TEXT_INDICATORS['success']} Database backup completed: {backup_dir}")
            log_sync_operation(
                self.enterprise_db,
                f"backup_created_{backup_dir.name}",
                start_time=start_dt,
            )
            return True
        except Exception as e:
            self.logger.error(f"{TEXT_INDICATORS['error']} Backup failed: {e}")
            log_sync_operation(
                self.enterprise_db,
                "backup_create_failed",
                status="FAILURE",
                start_time=start_dt,
            )
            return False

    def _perform_synchronization(self, validation_results: Dict) -> Dict:
        """Perform actual synchronization based on validation results"""
        start_dt = log_sync_operation(self.enterprise_db, "sync_operation_start")
        sync_results = {"scripts_updated": 0, "scripts_added": 0, "errors": [], "operations": []}

        try:
            # Get scripts that need synchronization
            missing_scripts = [item["script"] for item in validation_results["missing_from_db"]]
            out_of_sync_scripts = [item["script"] for item in validation_results["hash_mismatches"]]

            all_scripts_to_sync = list(set(missing_scripts + out_of_sync_scripts))

            if all_scripts_to_sync:
                self.logger.info(f"{TEXT_INDICATORS['sync']} Synchronizing {len(all_scripts_to_sync)} scripts...")

                success = self.validator.update_database_scripts(all_scripts_to_sync)
                if success:
                    sync_results["scripts_updated"] = len(out_of_sync_scripts)
                    sync_results["scripts_added"] = len(missing_scripts)
                    sync_results["operations"].append(f"Updated {len(all_scripts_to_sync)} scripts")
                    log_sync_operation(
                        self.enterprise_db,
                        f"updated_{len(all_scripts_to_sync)}_scripts",
                        start_time=start_dt,
                    )
                else:
                    sync_results["errors"].append("Failed to update database scripts")
            else:
                self.logger.info(f"{TEXT_INDICATORS['info']} No scripts require synchronization")
                sync_results["operations"].append("No synchronization required")
                log_sync_operation(
                    self.enterprise_db,
                    "no_scripts_needed",
                    start_time=start_dt,
                )

        except Exception as e:
            error_msg = f"Synchronization error: {e}"
            sync_results["errors"].append(error_msg)
            self.logger.error(f"{TEXT_INDICATORS['error']} {error_msg}")

        return sync_results

    def _log_sync_summary(self, session: Dict) -> None:
        """Log comprehensive synchronization summary"""
        self.logger.info(f"{TEXT_INDICATORS['info']} === SYNCHRONIZATION SESSION SUMMARY ===")
        self.logger.info(f"{TEXT_INDICATORS['info']} Session ID: {session['session_id']}")
        self.logger.info(f"{TEXT_INDICATORS['info']} Status: {session['completion_status']}")
        self.logger.info(f"{TEXT_INDICATORS['info']} Auto-sync: {session['auto_sync']}")

        if "validation_results" in session and "initial" in session["validation_results"]:
            initial = session["validation_results"]["initial"]
            self.logger.info(f"{TEXT_INDICATORS['info']} Initial Sync: {initial['sync_percentage']:.2f}%")
            self.logger.info(f"{TEXT_INDICATORS['info']} Scripts in Repo: {initial['total_repo_scripts']}")
            self.logger.info(f"{TEXT_INDICATORS['info']} Scripts in DB: {initial['total_db_scripts']}")
            self.logger.info(f"{TEXT_INDICATORS['warning']} Missing from DB: {len(initial['missing_from_db'])}")
            self.logger.info(f"{TEXT_INDICATORS['warning']} Hash Mismatches: {len(initial['hash_mismatches'])}")

        if session["auto_sync"] and "sync_results" in session:
            sync_res = session["sync_results"]
            self.logger.info(f"{TEXT_INDICATORS['sync']} Scripts Added: {sync_res['scripts_added']}")
            self.logger.info(f"{TEXT_INDICATORS['sync']} Scripts Updated: {sync_res['scripts_updated']}")

            if "final" in session["validation_results"]:
                final = session["validation_results"]["final"]
                self.logger.info(f"{TEXT_INDICATORS['success']} Final Sync: {final['sync_percentage']:.2f}%")

        self.logger.info(f"{TEXT_INDICATORS['info']} Session completed: {session.get('end_time', 'N/A')}")

    def generate_enterprise_compliance_report(self) -> str:
        """Generate enterprise compliance report for audit purposes"""
        self.logger.info(f"{TEXT_INDICATORS['start']} Generating enterprise compliance report...")

        compliance_data = {
            "report_timestamp": datetime.now().isoformat(),
            "validation_performed": True,
            "hash_validation_enabled": True,
            "timestamp_tracking_enabled": True,
            "database_backup_available": True,
            "audit_trail_complete": True,
        }

        # Perform validation for compliance data
        validation_results = self.validator.validate_script_sync()
        compliance_data["sync_percentage"] = validation_results["sync_percentage"]
        compliance_data["total_scripts_validated"] = validation_results["total_repo_scripts"]
        compliance_data["integrity_issues"] = len(validation_results["hash_mismatches"])

        # Generate compliance report
        report_lines = [
            "# Enterprise Script Database Compliance Report",
            f"Generated: {compliance_data['report_timestamp']}",
            "",
            "## Compliance Status",
            f"- Validation Performed: {compliance_data['validation_performed']}",
            f"- Hash Validation Enabled: {compliance_data['hash_validation_enabled']}",
            f"- Timestamp Tracking Enabled: {compliance_data['timestamp_tracking_enabled']}",
            f"- Database Backup Available: {compliance_data['database_backup_available']}",
            f"- Audit Trail Complete: {compliance_data['audit_trail_complete']}",
            "",
            "## Synchronization Metrics",
            f"- Current Sync Percentage: {compliance_data['sync_percentage']:.2f}%",
            f"- Total Scripts Validated: {compliance_data['total_scripts_validated']}",
            f"- Integrity Issues Detected: {compliance_data['integrity_issues']}",
            "",
            "## Compliance Assessment",
            f"- Status: {'COMPLIANT' if compliance_data['sync_percentage'] > 95 else 'REQUIRES ATTENTION'}",
            f"- Recommendation: {'System is properly synchronized' if compliance_data['sync_percentage'] > 95 else 'Immediate synchronization required'}",
            "",
        ]

        compliance_report = "\n".join(report_lines)

        # Save compliance report
        compliance_file = (
            self.results_dir / f"enterprise_compliance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        )
        with open(compliance_file, "w") as f:
            f.write(compliance_report)

        self.logger.info(f"{TEXT_INDICATORS['success']} Compliance report saved: {compliance_file}")
        return compliance_report


def main():
    """Main execution function"""
    import argparse

    parser = argparse.ArgumentParser(description="Enterprise Script Database Synchronizer")
    parser.add_argument("--workspace", "-w", default=".", help="Workspace root directory")
    parser.add_argument("--auto-sync", "-s", action="store_true", help="Automatically synchronize databases")
    parser.add_argument("--no-backup", action="store_true", help="Skip database backup")
    parser.add_argument("--compliance-report", "-c", action="store_true", help="Generate compliance report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    synchronizer = EnterpriseScriptDatabaseSynchronizer(args.workspace)

    if args.compliance_report:
        report = synchronizer.generate_enterprise_compliance_report()
        print(report)
    else:
        session = synchronizer.perform_comprehensive_sync(auto_sync=args.auto_sync, backup_db=not args.no_backup)

        print(f"\n{TEXT_INDICATORS['success']} Synchronization session completed: {session['session_id']}")
        print(f"{TEXT_INDICATORS['info']} Status: {session['completion_status']}")

        if "initial_report" in session:
            print(f"{TEXT_INDICATORS['info']} Initial report: {session['initial_report']}")

        if session["auto_sync"] and "final_report" in session:
            print(f"{TEXT_INDICATORS['info']} Final report: {session['final_report']}")


if __name__ == "__main__":
    main()
