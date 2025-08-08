#!/usr/bin/env python3
"""Database backup management for deployment scripts."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from .environment_migration import SUPPORTED_DATABASES, WORKSPACE, validate_database_file
from .restoration_engine import restore_backup


def create_backup(name: str, backup_root: Path | None = None) -> Path:
    """Create a backup of the specified database.

    Parameters
    ----------
    name:
        Key from ``SUPPORTED_DATABASES`` identifying the database.
    backup_root:
        Optional path to the backup directory. Defaults to ``GH_COPILOT_BACKUP_ROOT``.
    """

    path = SUPPORTED_DATABASES.get(name)
    if path is None:
        raise ValueError(f"Unsupported database: {name}")

    validate_database_file(path)

    if backup_root is None:
        backup_root = Path(os.environ["GH_COPILOT_BACKUP_ROOT"]) / "backups"
    else:
        backup_root = Path(backup_root)

    if WORKSPACE in backup_root.resolve().parents:
        raise ValueError("Backup root must be outside the workspace")

    backup_root.mkdir(parents=True, exist_ok=True)
    destination = backup_root / f"{name}.db"
    shutil.copy2(path, destination)
    validate_database_file(destination)
    return destination


__all__ = ["create_backup", "restore_backup"]
