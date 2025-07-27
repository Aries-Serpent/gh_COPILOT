"""Enterprise session management consolidation utility."""

from __future__ import annotations

import logging
import os
from datetime import datetime
from pathlib import Path

from utils.log_utils import _log_event


class EnterpriseUtility:
    """Simplified executor for session consolidation tests."""

    def __init__(
        self,
        workspace_path: str | Path | None = None,
        analytics_db: str | Path | None = None,
    ) -> None:
        self.workspace_path = Path(workspace_path or os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
        self.analytics_db = Path(
            analytics_db or os.getenv("ANALYTICS_DB", self.workspace_path / "databases" / "analytics.db")
        )
        self.logger = logging.getLogger(__name__)

    def _validate_environment(self) -> bool:
        return bool(os.getenv("GH_COPILOT_WORKSPACE")) and bool(os.getenv("GH_COPILOT_BACKUP_ROOT"))

    def perform_utility_function(self) -> bool:
        """Return ``False`` if any zero-byte files are present."""
        for file in self.workspace_path.iterdir():
            if file.is_file() and file.stat().st_size == 0:
                self.logger.error("[ERROR] zero byte file detected: %s", file)
                _log_event({"event": "zero_byte_detected", "file": str(file)}, db_path=self.analytics_db)
                return False
        return True

    def execute_utility(self) -> bool:
        """Execute consolidation routine with logging."""
        self.logger.info("[START] Utility started: %s", datetime.now().isoformat())
        if not self._validate_environment():
            self.logger.error("[ERROR] Environment not configured")
            _log_event({"event": "environment_invalid"}, db_path=self.analytics_db)
            return False
        _log_event({"event": "utility_start"}, db_path=self.analytics_db)
        success = self.perform_utility_function()
        if success:
            self.logger.info("[SUCCESS] Utility completed")
            _log_event({"event": "utility_complete"}, db_path=self.analytics_db)
        else:
            self.logger.error("[ERROR] Utility failed")
            _log_event({"event": "utility_failed"}, db_path=self.analytics_db)
        return success


__all__ = ["EnterpriseUtility", "main"]


def main() -> int:
    """Run :class:`EnterpriseUtility` from the command line."""
    util = EnterpriseUtility()
    return 0 if util.execute_utility() else 1


if __name__ == "__main__":
    raise SystemExit(main())
