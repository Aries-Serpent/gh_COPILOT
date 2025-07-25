#!/usr/bin/env python3
"""Unified Legacy Cleanup System
================================

Provides enterprise-compliant cleanup and archival of legacy scripts.
Implements database-first validation for safe file operations and logs key events
to ``analytics.db`` for compliance auditing.
Implements database-first validation for safe file operations and logs key events
to ``analytics.db`` for compliance auditing.
"""


from __future__ import annotations

import argparse
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import List

from db_tools.core.connection import DatabaseConnection
from db_tools.core.models import DatabaseConfig
from utils.log_utils import _log_event
from utils.log_utils import _log_event

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(message)s")


@dataclass
class CleanupConfig:
    workspace_path: Path
    legacy_db: Path
    file_mgmt_db: Path
    class_db: Path


class UnifiedLegacyCleanupSystem:
    """Autonomous workspace optimization with intelligent file management."""

    def __init__(self, workspace_path: str | Path | None = None) -> None:
        if workspace_path is None:
            workspace_path = os.getenv("GH_COPILOT_WORKSPACE", Path.cwd())
        self.config = CleanupConfig(
            workspace_path=Path(workspace_path),
            legacy_db=Path(workspace_path) / "databases" / "legacy_cleanup.db",
            file_mgmt_db=Path(workspace_path) / "databases" / "file_management.db",
            class_db=Path(workspace_path) / "databases" / "file_classification.db",
            file_mgmt_db=Path(workspace_path) / "databases" / "file_management.db",
            class_db=Path(workspace_path) / "databases" / "file_classification.db",
        )
        self.legacy_conn = DatabaseConnection(DatabaseConfig(database_path=self.config.legacy_db))
        self.file_conn = DatabaseConnection(DatabaseConfig(database_path=self.config.file_mgmt_db))
        self.analytics_db = self.config.workspace_path / "databases" / "analytics.db"
        self.legacy_conn = DatabaseConnection(DatabaseConfig(database_path=self.config.legacy_db))
        self.file_conn = DatabaseConnection(DatabaseConfig(database_path=self.config.file_mgmt_db))
        self.analytics_db = self.config.workspace_path / "databases" / "analytics.db"

    # ------------------------------------------------------------------
    # Discovery
    def discover_legacy_scripts(self) -> List[Path]:
        """Discover legacy scripts via database."""
        query = "SELECT script_path FROM legacy_scripts WHERE active = 1"
        query = "SELECT script_path FROM legacy_scripts WHERE active = 1"
        try:
            rows = self.file_conn.execute_query(query)
            scripts = [self.config.workspace_path / r["script_path"] for r in rows]
            valid_scripts = [s for s in scripts if s.exists()]
            _log_event({"event": "discover_legacy_scripts", "count": len(valid_scripts)})
            return valid_scripts
        except Exception as exc:  # pragma: no cover - database might not exist
            logger.warning(f"Database query failed: {exc}")
            _log_event({"event": "discover_legacy_scripts_failed", "error": str(exc)}, db_path=self.analytics_db)
            _log_event({"event": "discover_legacy_scripts_failed", "error": str(exc)}, db_path=self.analytics_db)
            return []

    # ------------------------------------------------------------------
    def archive_script(self, script: Path, dry_run: bool = False) -> bool:
        """Move script to archive directory with safety checks."""
        if not script.is_file():
            return False
        archive_dir = self.config.workspace_path / "archive" / "legacy"
        archive_dir.mkdir(parents=True, exist_ok=True)
        target = archive_dir / script.name
        logger.info(f"Archiving {script} -> {target}")
        _log_event({"event": "archive_script", "script": str(script)}, db_path=self.analytics_db)
        _log_event({"event": "archive_script", "script": str(script)}, db_path=self.analytics_db)
        if dry_run:
            return True
        try:
            script.rename(target)
            _log_event({"event": "archive_script", "script": str(script)})
            return True
        except Exception as exc:  # pragma: no cover - file system errors
            logger.error(f"Archive failed: {exc}")
            _log_event({"event": "archive_failed", "script": str(script), "error": str(exc)})
            return False

    def optimize_workspace(self, dry_run: bool = False) -> None:
        """Placeholder workspace optimization step."""
        logger.info("Optimizing workspace layout")
        _log_event({"event": "optimize_workspace_start"}, db_path=self.analytics_db)
        _log_event({"event": "optimize_workspace_start"}, db_path=self.analytics_db)
        if dry_run:
            return
        _log_event({"event": "optimize_workspace_start"})
        # Currently a no-op; real implementation would reorganize files
        _log_event({"event": "optimize_workspace_complete"})
        return

    def run_cleanup(self, dry_run: bool = False) -> None:
        """Run archival and optimization."""
        _log_event({"event": "legacy_cleanup_start"}, db_path=self.analytics_db)
        _log_event({"event": "legacy_cleanup_start"}, db_path=self.analytics_db)
        scripts = self.discover_legacy_scripts()
        logger.info(f"Discovered {len(scripts)} legacy scripts")
        for script in scripts:
            self.archive_script(script, dry_run=dry_run)
        self.optimize_workspace(dry_run=dry_run)
        _log_event({"event": "legacy_cleanup_complete", "count": len(scripts)}, db_path=self.analytics_db)
        _log_event({"event": "legacy_cleanup_complete", "count": len(scripts)}, db_path=self.analytics_db)


# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------
def parse_args(args: List[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Unified Legacy Cleanup System")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform a trial run without modifying files",
    )
    return parser.parse_args(args)


def main(args: List[str] | None = None) -> int:
    ns = parse_args(args)
    system = UnifiedLegacyCleanupSystem()
    system.run_cleanup(dry_run=ns.dry_run)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
