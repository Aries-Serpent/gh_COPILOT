#!/usr/bin/env python3
"""Apply all SQL migrations to analytics.db."""

from __future__ import annotations

import logging
import os
import sqlite3
from pathlib import Path

from tqdm import tqdm

logger = logging.getLogger(__name__)


def apply_migrations(db_path: Path, migrations_dir: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    sql_files = sorted(migrations_dir.glob("*.sql"))
    with sqlite3.connect(db_path) as conn, tqdm(total=len(sql_files), desc="migrations", unit="file") as bar:
        for sql_file in sql_files:
            logger.info("applying %s", sql_file.name)
            conn.executescript(sql_file.read_text())
            bar.update(1)
        conn.commit()


def main() -> None:
    workspace = Path(os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
    db_path = workspace / "databases" / "analytics.db"
    migrations_dir = workspace / "databases" / "migrations"
    apply_migrations(db_path, migrations_dir)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
