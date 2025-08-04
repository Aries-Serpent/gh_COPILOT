#!/usr/bin/env python3
"""Point-in-time backup helpers for SQLite databases.

This module provides simple utilities to create timestamped backups of
SQLite databases and restore them when required.  Backups are written to
``GH_COPILOT_BACKUP_ROOT`` to comply with anti-recursion policies.
"""

from __future__ import annotations

import logging
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Iterable

from enterprise_modules.compliance import validate_enterprise_operation
from utils.logging_utils import log_enterprise_operation, setup_enterprise_logging


logger = logging.getLogger(__name__)


def _backup_path(name: str) -> Path:
    root = Path(os.getenv("GH_COPILOT_BACKUP_ROOT", "/tmp/gh_COPILOT_Backups"))
    root.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    return root / f"{name}_{timestamp}.sqlite"


def create_snapshot(db_path: Path) -> Path:
    """Create a timestamped backup of ``db_path`` and return its path."""
    validate_enterprise_operation()
    backup_file = _backup_path(db_path.stem)
    with sqlite3.connect(db_path) as src, sqlite3.connect(backup_file) as dst:
        src.backup(dst)
    log_enterprise_operation("snapshot_created", "SUCCESS", str(backup_file))
    return backup_file


def restore_snapshot(backup_file: Path, target_path: Path) -> None:
    """Restore ``backup_file`` to ``target_path``."""
    validate_enterprise_operation()
    with sqlite3.connect(backup_file) as src, sqlite3.connect(target_path) as dst:
        src.backup(dst)
    log_enterprise_operation("snapshot_restored", "SUCCESS", str(target_path))


def snapshot_many(paths: Iterable[Path]) -> None:
    for path in paths:
        create_snapshot(path)


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Point-in-time database backups")
    parser.add_argument("database", nargs="+", type=Path, help="Databases to snapshot")
    parser.add_argument("--restore", type=Path, help="Restore from backup to target")
    parser.add_argument("--target", type=Path, help="Target database when using --restore")

    args = parser.parse_args()
    setup_enterprise_logging()

    if args.restore and args.target:
        restore_snapshot(args.restore, args.target)
    else:
        snapshot_many(args.database)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

