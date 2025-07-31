"""Unified Legacy Cleanup System wrapper.

This module removes deprecated files based on simple
pattern matching, logs operations to ``analytics.db`` and
uses the DualCopilot validation pattern via
:class:`SecondaryCopilotValidator`.
It performs a backup using ``UnifiedDisasterRecoverySystem``
before deletion to ensure recoverability.
"""

from __future__ import annotations

import logging
import os
import shutil
from pathlib import Path
from typing import Iterable, List

from secondary_copilot_validator import SecondaryCopilotValidator
from unified_disaster_recovery_system import UnifiedDisasterRecoverySystem
from utils.log_utils import _log_event

__all__ = ["UnifiedLegacyCleanupSystem", "main"]

DEPRECATED_PATTERNS: List[str] = ["*_deprecated.py", "*.old"]


class UnifiedLegacyCleanupSystem:
    """Clean up deprecated files with backup and analytics logging."""

    def __init__(self, workspace_root: str | None = None) -> None:
        self.workspace_root = Path(workspace_root or os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
        self.backup_root = Path(os.getenv("GH_COPILOT_BACKUP_ROOT", "/tmp/gh_COPILOT_Backups"))
        self.analytics_db = self.workspace_root / "databases" / "analytics.db"
        self.logger = logging.getLogger(self.__class__.__name__)
        self.validator = SecondaryCopilotValidator(self.logger)
        self.recovery = UnifiedDisasterRecoverySystem(str(self.workspace_root))

    # ------------------------------------------------------------------
    def _find_deprecated_files(self) -> List[Path]:
        files: List[Path] = []
        for pattern in DEPRECATED_PATTERNS:
            files.extend(self.workspace_root.rglob(pattern))
        return [p for p in files if p.is_file()]

    def _backup_files(self, files: Iterable[Path]) -> None:
        backup_dir = self.backup_root / "legacy_cleanup"
        backup_dir.mkdir(parents=True, exist_ok=True)
        for f in files:
            try:
                shutil.copy2(f, backup_dir / f.name)
                _log_event({"event": "backup", "file": str(f)}, db_path=self.analytics_db)
            except OSError as exc:  # pragma: no cover - copy errors rare
                self.logger.error("Backup failed for %s: %s", f, exc)
                _log_event(
                    {"event": "backup_failed", "file": str(f), "error": str(exc)},
                    db_path=self.analytics_db,
                )
                raise

    def _delete_files(self, files: Iterable[Path]) -> None:
        for f in files:
            try:
                f.unlink()
                _log_event({"event": "removed_file", "file": str(f)}, db_path=self.analytics_db)
            except OSError as exc:
                self.logger.error("Deletion failed for %s: %s", f, exc)
                _log_event(
                    {"event": "delete_failed", "file": str(f), "error": str(exc)},
                    db_path=self.analytics_db,
                )
                # rollback using disaster recovery
                self.recovery.perform_recovery()
                raise

    def run_cleanup(self) -> bool:
        """Execute cleanup routine and return ``True`` on success."""
        _log_event({"event": "legacy_cleanup_started"}, db_path=self.analytics_db)
        files = self._find_deprecated_files()
        if not files:
            _log_event({"event": "no_deprecated_files"}, db_path=self.analytics_db)
            return True
        self._backup_files(files)
        try:
            self._delete_files(files)
        except OSError:
            return False
        result = self.validator.validate_corrections([__file__])
        _log_event({"event": "legacy_cleanup_complete", "success": result}, db_path=self.analytics_db)
        return result


def main() -> int:
    system = UnifiedLegacyCleanupSystem()
    success = system.run_cleanup()
    return 0 if success else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
