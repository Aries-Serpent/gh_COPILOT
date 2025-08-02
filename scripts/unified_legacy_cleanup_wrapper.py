from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Optional

from scripts.unified_legacy_cleanup_system import (
    UnifiedLegacyCleanupSystem as _BaseCleanup,
    parse_args,
)
from scripts.database.add_violation_logs import ensure_violation_logs
from scripts.database.add_rollback_logs import ensure_rollback_logs
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


__all__ = ["UnifiedLegacyCleanupSystem", "main"]


def main(args: Optional[List[str]] = None) -> int:
    ns = parse_args(args)
    system = UnifiedLegacyCleanupSystem()
    system.run_cleanup(dry_run=ns.dry_run)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
