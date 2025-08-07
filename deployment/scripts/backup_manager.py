#!/usr/bin/env python3
"""Database backup management for deployment scripts."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from .environment_migration import SUPPORTED_DATABASES


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

    if backup_root is None:
        backup_root = Path(os.environ["GH_COPILOT_BACKUP_ROOT"]) / "backups"
    else:
        backup_root = Path(backup_root)

    backup_root.mkdir(parents=True, exist_ok=True)
    destination = backup_root / f"{name}.db"
    shutil.copy2(path, destination)
    return destination


__all__ = ["create_backup"]
