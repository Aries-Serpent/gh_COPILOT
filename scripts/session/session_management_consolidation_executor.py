"""Enterprise session management consolidation utility."""

from __future__ import annotations

import logging
import os
from datetime import datetime
from pathlib import Path

from enterprise_modules.compliance import validate_enterprise_operation
from utils.log_utils import _log_event
from utils.lessons_learned_integrator import (
    apply_lessons,
    load_lessons,
    store_lesson,
)
from validation.protocols.session import SessionProtocolValidator


class EnterpriseUtility:
    """Simplified executor for session consolidation tests."""

    def __init__(self, workspace_path: str | Path | None = None) -> None:
        self.workspace_path = Path(workspace_path or os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
        validate_enterprise_operation()
        self.logger = logging.getLogger(__name__)
        self.validator = SessionProtocolValidator(str(self.workspace_path))
        self.analytics_db = self.workspace_path / "databases" / "analytics.db"
        self.learning_db = self.workspace_path / "databases" / "learning_monitor.db"
        self.loaded_lessons = load_lessons(self.learning_db)
        apply_lessons(self.logger, self.loaded_lessons)

    def _validate_environment(self) -> bool:
        valid = bool(os.getenv("GH_COPILOT_WORKSPACE")) and bool(os.getenv("GH_COPILOT_BACKUP_ROOT"))
        _log_event(
            {"event": "environment_check", "valid": valid},
            db_path=self.analytics_db,
        )
        return valid

    def perform_utility_function(self) -> bool:
        """Return ``False`` if any zero-byte files are present."""
        for file in self.workspace_path.iterdir():
            if file.is_file() and file.stat().st_size == 0:
                self.logger.error("[ERROR] zero byte file detected: %s", file)
                _log_event({"event": "zero_byte_detected", "file": str(file)}, db_path=self.analytics_db)
                return False
        return True

    def execute_utility(self) -> bool:
        """Execute consolidation routine with logging and validation."""
        self.logger.info("[START] Utility started: %s", datetime.now().isoformat())
        _log_event({"event": "utility_start"}, db_path=self.workspace_path / "analytics.db")
        env_ok = self._validate_environment()
        validation = self.validator.validate_startup()
        success = env_ok and validation.is_success and self.perform_utility_function()
        if success:
            self.logger.info("[SUCCESS] Utility completed")
            _log_event({"event": "utility_success"}, db_path=self.workspace_path / "analytics.db")
            store_lesson(
                "Session utility completed successfully",
                source="session_management",
                timestamp=datetime.utcnow().isoformat(),
                validation_status="validated",
                db_path=self.learning_db,
            )
        else:
            self.logger.error("[ERROR] Utility failed")
            _log_event({"event": "utility_failed"}, db_path=self.workspace_path / "analytics.db")
            store_lesson(
                "Session utility encountered an error",
                source="session_management",
                timestamp=datetime.utcnow().isoformat(),
                validation_status="pending",
                db_path=self.learning_db,
            )
        return success


__all__ = ["EnterpriseUtility", "main"]


def main() -> int:
    """Run :class:`EnterpriseUtility` from the command line."""
    util = EnterpriseUtility()
    return 0 if util.execute_utility() else 1


if __name__ == "__main__":
    raise SystemExit(main())
