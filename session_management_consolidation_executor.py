"""Enterprise session management consolidation utility."""

from __future__ import annotations

import logging
import os
import shutil
from datetime import datetime
from pathlib import Path

from enterprise_modules.compliance import (
    ComplianceError,
    enforce_anti_recursion,
    validate_enterprise_operation,
)
from utils.log_utils import _log_event
from validation.protocols.session import SessionProtocolValidator
from utils.validation_utils import (
    anti_recursion_guard,
    validate_enterprise_environment,
)
from unified_session_management_system import ensure_no_zero_byte_files, finalize_session
from session.session_lifecycle_metrics import start_session, end_session
from unified_disaster_recovery_system import ComplianceLogger, schedule_backups


class EnterpriseUtility:
    """Simplified executor for session consolidation tests."""

    def __init__(self, workspace_path: str | Path | None = None) -> None:
        self.workspace_path = Path(workspace_path or os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
        validate_enterprise_operation()
        self.logger = logging.getLogger(__name__)
        self.validator = SessionProtocolValidator(str(self.workspace_path))
        self.analytics_db = self.workspace_path / "databases" / "analytics.db"
        self.compliance_logger = ComplianceLogger()
        backup_root = Path(os.getenv("GH_COPILOT_BACKUP_ROOT", "/tmp"))
        self.pid_file = backup_root / "session_management_consolidation_executor.pid"
        self.recursion_depth = 0

    def _validate_environment(self) -> bool:
        """Ensure workspace and backup paths are set and non-recursive."""
        try:
            validate_enterprise_environment()
            valid = True
        except EnvironmentError as exc:  # pragma: no cover - explicit logging
            self.logger.error("[ERROR] %s", exc)
            valid = False
        _log_event({"event": "environment_check", "valid": valid}, db_path=self.analytics_db)
        return valid

    def _backup_analytics_db(self) -> None:
        """Back up analytics database and record rollback log."""
        backup_root = Path(os.getenv("GH_COPILOT_BACKUP_ROOT", "/tmp")).resolve()
        workspace = self.workspace_path.resolve()
        if workspace in backup_root.parents or backup_root == workspace:
            self.logger.error("[ERROR] Backup root inside workspace: %s", backup_root)
            _log_event(
                {"event": "backup_failed", "target": str(self.analytics_db)},
                table="rollback_logs",
                db_path=self.analytics_db,
            )
            return
        backup_root.mkdir(parents=True, exist_ok=True)
        backup_file = backup_root / f"{self.analytics_db.name}.bak"
        try:
            shutil.copy2(self.analytics_db, backup_file)
        except OSError as exc:  # pragma: no cover - rare filesystem error
            self.logger.error("[ERROR] Backup failed: %s", exc)
            _log_event(
                {"event": "backup_failed", "target": str(self.analytics_db)},
                table="rollback_logs",
                db_path=self.analytics_db,
            )
            return
        _log_event(
            {"event": "backup_created", "target": str(self.analytics_db), "backup": str(backup_file)},
            table="rollback_logs",
            db_path=self.analytics_db,
        )

    def perform_utility_function(self) -> bool:
        """Check workspace for zero-byte files and log any findings."""
        try:
            with ensure_no_zero_byte_files(self.workspace_path, "consolidation"):
                return True
        except RuntimeError as exc:
            self.logger.error("[ERROR] %s", exc)
            _log_event(
                {"description": "zero_byte_detected", "details": str(exc)},
                db_path=self.analytics_db,
            )
            return False

    @anti_recursion_guard
    def execute_utility(self) -> bool:
        """Execute consolidation routine with logging and validation."""
        try:
            enforce_anti_recursion(self)
        except ComplianceError as exc:
            self.logger.error("[ABORT] %s", exc)
            _log_event(
                {"event": "recursion_abort", "details": str(exc)},
                db_path=self.analytics_db,
            )
            return False

        self._register_pid()
        session_id = "consolidation"
        start_session(session_id, workspace=str(self.workspace_path))
        success = False
        zero_byte_violations = 0
        try:
            self.logger.info("[START] Utility started: %s", datetime.now().isoformat())
            _log_event({"event": "utility_start"}, db_path=self.workspace_path / "analytics.db")
            env_ok = self._validate_environment()
            if env_ok:
                self._backup_analytics_db()
            validation = self.validator.validate_startup()
            success = env_ok and validation.is_success and self.perform_utility_function()
            if success:
                self.logger.info("[SUCCESS] Utility completed")
                _log_event({"event": "utility_success"}, db_path=self.workspace_path / "analytics.db")
            else:
                self.logger.error("[ERROR] Utility failed")
                _log_event({"event": "utility_failed"}, db_path=self.workspace_path / "analytics.db")
                zero_byte_violations = 1
            return success
        finally:
            try:
                finalize_session(self.workspace_path / "logs", self.workspace_path, session_id)
            except Exception as exc:  # pragma: no cover - logging
                self.logger.error("[ERROR] finalize_session failed: %s", exc)
            end_session(
                session_id,
                zero_byte_violations=zero_byte_violations,
                workspace=str(self.workspace_path),
                status="success" if success else "failed",
            )
            try:
                backup_file = schedule_backups()
                backup_root = Path(
                    os.getenv("GH_COPILOT_BACKUP_ROOT", "/tmp/gh_COPILOT_Backups")
                ).resolve()
                if backup_root in backup_file.parents:
                    self.compliance_logger.log(
                        "session_backup", path=str(backup_file)
                    )
                else:
                    self.logger.error(
                        "[ERROR] backup outside root: %s", backup_file
                    )
                    self.compliance_logger.log(
                        "session_backup_failed",
                        path=str(backup_file),
                        reason="outside_root",
                    )
            except Exception as exc:  # pragma: no cover - logging only
                self.logger.error("[ERROR] backup scheduling failed: %s", exc)
            self._clear_pid()
            if hasattr(self, "recursion_depth") and self.recursion_depth > 0:
                self.recursion_depth -= 1

    def _register_pid(self) -> None:
        """Record the current PID to prevent recursive execution."""
        current_pid = os.getpid()
        if self.pid_file.exists():
            try:
                existing = int(self.pid_file.read_text().strip())
            except ValueError:
                existing = None
            if existing and Path(f"/proc/{existing}").exists():
                raise RuntimeError("Recursive invocation detected")
        self.pid_file.write_text(str(current_pid))

    def _clear_pid(self) -> None:
        """Remove the PID file if it exists."""
        if self.pid_file.exists():
            self.pid_file.unlink()


__all__ = ["EnterpriseUtility", "main"]


def main() -> int:
    """Run :class:`EnterpriseUtility` from the command line."""
    util = EnterpriseUtility()
    return 0 if util.execute_utility() else 1


if __name__ == "__main__":
    raise SystemExit(main())
