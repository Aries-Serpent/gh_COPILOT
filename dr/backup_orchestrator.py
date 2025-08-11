"""Simple backup orchestrator for pre-operation backups and restores."""
from __future__ import annotations

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable

from utils.log_utils import DEFAULT_ANALYTICS_DB, log_event


class BackupOrchestrator:
    """Handle backups before write operations and perform restores.

    Parameters
    ----------
    backup_root:
        Directory where backups and manifests are stored. Falls back to the
        ``GH_COPILOT_BACKUP_ROOT`` environment variable or ``/tmp`` when not
        provided.
    analytics_db:
        Path to ``analytics.db`` for logging rollback events.
    """

    def __init__(self, backup_root: Path | None = None, analytics_db: Path = DEFAULT_ANALYTICS_DB) -> None:
        self.backup_root = Path(backup_root or os.getenv("GH_COPILOT_BACKUP_ROOT", "/tmp/gh_copilot_backups"))
        self.analytics_db = analytics_db
        self.backup_root.mkdir(parents=True, exist_ok=True)
        (self.backup_root / "manifests").mkdir(exist_ok=True)

    def pre_op_backup(self, paths: Iterable[Path]) -> Path:
        """Backup ``paths`` before a write operation.

        Each existing path is copied to a timestamped folder under
        ``backup_root``. A manifest mapping original paths to backup copies is
        written and a ``rollback_logs`` entry is recorded for each file.

        Parameters
        ----------
        paths:
            Iterable of file paths that will be written to.

        Returns
        -------
        Path
            Location of the created manifest file.
        """

        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
        backup_dir = self.backup_root / timestamp
        backup_dir.mkdir(parents=True, exist_ok=True)
        manifest: Dict[str, str] = {}
        for p in paths:
            src = Path(p)
            if not src.exists():
                continue
            dest = backup_dir / src.name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            manifest[str(src)] = str(dest)
            log_event(
                {"event": "pre_op_backup", "target": str(src), "backup": str(dest)},
                table="rollback_logs",
                db_path=self.analytics_db,
            )
        manifest_path = self.backup_root / "manifests" / f"{timestamp}.json"
        with open(manifest_path, "w", encoding="utf-8") as fh:
            json.dump(manifest, fh, indent=2)
        return manifest_path

    def restore(self, manifest_path: Path) -> None:
        """Restore files from ``manifest_path`` backups."""

        with open(manifest_path, "r", encoding="utf-8") as fh:
            manifest: Dict[str, str] = json.load(fh)
        for target, backup in manifest.items():
            src = Path(backup)
            dest = Path(target)
            if not src.exists():
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            log_event(
                {"event": "restore", "target": str(dest), "backup": str(src)},
                table="rollback_logs",
                db_path=self.analytics_db,
            )
