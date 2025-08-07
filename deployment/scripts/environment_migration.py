#!/usr/bin/env python3
"""Environment migration utilities for deployment scripts.

This module validates and prepares database files before migration.
It now supports additional databases such as the quantum database.
"""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Iterable, List

# Determine workspace and production database path
WORKSPACE = Path(os.environ.get("GH_COPILOT_WORKSPACE", Path(__file__).resolve().parents[2]))
PRODUCTION_DB = WORKSPACE / "databases" / "production.db"
MAX_DB_SIZE_MB = 100

# Known databases participating in environment migrations
SUPPORTED_DATABASES = {
    "production": PRODUCTION_DB,
    "analytics": WORKSPACE / "databases" / "analytics_collector.db",
    # Newly supported quantum database
    "quantum": WORKSPACE / "databases" / "quantum_algorithms.db",
}


def validate_database_file(path: Path) -> None:
    """Ensure a database file exists, is not empty, and is a valid SQLite DB."""
    if not path.exists():
        raise FileNotFoundError(f"Database file missing: {path}")
    if path.stat().st_size == 0 or path.stat().st_size > MAX_DB_SIZE_MB * 1024 * 1024:
        raise ValueError(f"Database size out of bounds: {path}")
    sqlite3.connect(path).close()


def register_database(name: str, path: Path) -> None:
    """Register an additional database for migrations.

    Parameters
    ----------
    name:
        Unique identifier for the database.
    path:
        Location of the SQLite database file.
    """

    if name in SUPPORTED_DATABASES:
        raise ValueError(f"Database already registered: {name}")
    validate_database_file(path)
    SUPPORTED_DATABASES[name] = path


def migrate_environment(names: Iterable[str]) -> List[str]:
    """Validate databases and simulate migration.

    Parameters
    ----------
    names:
        Iterable of database keys to migrate.

    Returns
    -------
    list[str]
        Ordered list of successfully processed database names.
    """

    if not PRODUCTION_DB.exists():
        raise FileNotFoundError("production.db missing; cannot verify environment")

    processed: List[str] = []
    for name in names:
        path = SUPPORTED_DATABASES.get(name)
        if path is None:
            raise ValueError(f"Unsupported database: {name}")
        validate_database_file(Path(path))
        processed.append(name)
    return processed


__all__ = [
    "migrate_environment",
    "SUPPORTED_DATABASES",
    "validate_database_file",
    "register_database",
]
