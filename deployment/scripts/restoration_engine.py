#!/usr/bin/env python3
"""Restore databases from backups."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from .environment_migration import SUPPORTED_DATABASES


def restore_backup(name: str, backup_root: Path | None = None) -> Path:
    """Restore a database from its backup."""
    path = SUPPORTED_DATABASES.get(name)
    if path is None:
        raise ValueError(f"Unsupported database: {name}")

    if backup_root is None:
        backup_root = Path(os.environ["GH_COPILOT_BACKUP_ROOT"]) / "backups"
    else:
        backup_root = Path(backup_root)

    source = backup_root / f"{name}.db"
    if not source.exists():
        raise FileNotFoundError(f"Backup not found for {name}")

    shutil.copy2(source, path)
    return path


__all__ = ["restore_backup"]
