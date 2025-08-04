from __future__ import annotations

import logging
import os
import shutil
import sqlite3
from pathlib import Path
from typing import List, Optional

from scripts.unified_legacy_cleanup_system import (
    UnifiedLegacyCleanupSystem as _BaseCleanup,
    parse_args,
)
from scripts.database.add_violation_logs import ensure_violation_logs
from scripts.database.add_rollback_logs import ensure_rollback_logs
from scripts.database.add_legacy_cleanup_log import (
    ensure_legacy_cleanup_log,
    log_cleanup_event,
)
from unified_disaster_recovery_system import UnifiedDisasterRecoverySystem
from secondary_copilot_validator import SecondaryCopilotValidator
from utils.log_utils import _log_event


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(message)s")


class UnifiedLegacyCleanupSystem(_BaseCleanup):
    """Extended cleanup system with secondary validation and analytics logging."""

    def __init__(self, workspace_path: str | Path | None = None) -> None:
        super().__init__(workspace_path)
        ensure_violation_logs(self.analytics_db)
        ensure_rollback_logs(self.analytics_db)
        ensure_legacy_cleanup_log(self.analytics_db)
        self.validator = SecondaryCopilotValidator()

    def archive_script(self, script: Path, dry_run: bool = False) -> bool:
        if not script.is_file():
            return False
        if not self.validator.validate_corrections([str(script)]):
            _log_event(
                {"event": "validation_failed", "details": str(script)},
                table="violation_logs",
                db_path=self.analytics_db,
            )
            return False
        archived = self.config.workspace_path / "archive" / "legacy" / script.name
        result = super().archive_script(script, dry_run=dry_run)
        if result:
            log_cleanup_event(
                str(script),
                action="archived",
                reason="legacy script archived",
                db_path=self.analytics_db,
            )
            _log_event(
                {"target": str(script), "backup": str(archived)},
                table="rollback_logs",
                db_path=self.analytics_db,
            )
        return result

    def optimize_workspace(self, dry_run: bool = False) -> None:
        super().optimize_workspace(dry_run=dry_run)
        _log_event(
            {"details": "workspace_optimized"},
            table="violation_logs",
            db_path=self.analytics_db,
        )
        log_cleanup_event(
            "workspace",
            action="optimized",
            reason="workspace optimization complete",
            db_path=self.analytics_db,
        )

    def run_cleanup(self, dry_run: bool = False) -> bool:
        """Run cleanup and return ``True`` on success."""
        with sqlite3.connect(self.analytics_db) as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS event_log (event TEXT)")
            conn.commit()
        try:
            _log_event({"event": "legacy_cleanup_start"}, db_path=self.analytics_db)
            removed_any = False
            pattern = "*deprecated*.py"
            for file in self.config.workspace_path.glob(pattern):
                if not file.is_file():
                    continue
                backup_root = Path(os.environ.get("GH_COPILOT_BACKUP_ROOT", "/tmp")) / "legacy_cleanup"
                backup_root.mkdir(parents=True, exist_ok=True)
                backup = backup_root / file.name
                shutil.copy2(file, backup)
                file.unlink()
                removed_any = True
                try:
                    _log_event(
                        {"event": "removed_file", "path": str(file)},
                        db_path=self.analytics_db,
                    )
                except Exception:
                    pass
                log_cleanup_event(
                    str(file),
                    action="removed",
                    reason="deprecated",
                    db_path=self.analytics_db,
                )
            _log_event(
                {"event": "legacy_cleanup_complete", "count": int(removed_any)},
                db_path=self.analytics_db,
            )
            log_cleanup_event(
                "run_cleanup",
                action="completed",
                reason="cleanup executed",
                db_path=self.analytics_db,
            )
            return True
        except Exception as exc:  # pragma: no cover - safety net
            UnifiedDisasterRecoverySystem().perform_recovery()
            log_cleanup_event(
                "run_cleanup",
                action="failed",
                reason=str(exc),
                db_path=self.analytics_db,
            )
            return False


__all__ = ["UnifiedLegacyCleanupSystem", "main"]


def main(args: Optional[List[str]] = None) -> int:
    ns = parse_args(args)
    system = UnifiedLegacyCleanupSystem()
    system.run_cleanup(dry_run=ns.dry_run)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
