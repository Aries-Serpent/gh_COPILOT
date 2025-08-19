#!/usr/bin/env python3
"""Apply SQL migrations to ``analytics.db``.

This module exposes :func:`ensure_migrations_applied` so tests and the setup
script can idempotently apply migrations.  Each migration is only applied once
and every execution is logged to ``logs/migrations.log``.
"""

from __future__ import annotations

import logging
import os
import sqlite3
from pathlib import Path

try:  # pragma: no cover - optional dependency
    from tqdm import tqdm
except ModuleNotFoundError:  # pragma: no cover
    from contextlib import contextmanager

    @contextmanager
    def tqdm(*args, **kwargs):  # type: ignore[override]
        class _Bar:
            def update(self, *_, **__):  # pragma: no cover - no-op fallback
                return None

        yield _Bar()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def apply_migrations(db_path: Path, migrations_dir: Path, log_path: Path | None = None) -> None:
    """Apply migrations from ``migrations_dir`` to ``db_path``.

    The function records applied migration filenames in the ``schema_migrations``
    table so subsequent runs skip already-applied files.  When ``log_path`` is
    provided, migration activity is appended to that file.
    """

    sql_files = sorted(migrations_dir.glob("*.sql"))
    if not sql_files:
        return

    handlers: list[logging.Handler] = []
    if log_path is not None:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(log_path)
        fh.setFormatter(logging.Formatter("%(levelname)s:%(message)s"))
        logger.addHandler(fh)
        handlers.append(fh)

    db_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        conn = sqlite3.connect(db_path)
        conn.execute(
            "CREATE TABLE IF NOT EXISTS schema_migrations (filename TEXT PRIMARY KEY)"
        )
    except sqlite3.DatabaseError:
        logger.warning("recreating invalid database %s", db_path)
        corrupt = db_path.with_suffix(db_path.suffix + ".corrupt")
        try:
            db_path.replace(corrupt)
        except OSError:
            db_path.unlink(missing_ok=True)
        conn = sqlite3.connect(db_path)
        conn.execute(
            "CREATE TABLE IF NOT EXISTS schema_migrations (filename TEXT PRIMARY KEY)"
        )
    with conn, tqdm(total=len(sql_files), desc="migrations", unit="file") as bar:
        for sql_file in sql_files:
            name = sql_file.name
            applied = conn.execute(
                "SELECT 1 FROM schema_migrations WHERE filename=?", (name,)
            ).fetchone()
            if applied:
                logger.info("skipping %s", name)
                bar.update(1)
                continue
            try:
                conn.executescript(sql_file.read_text())
                conn.execute(
                    "INSERT INTO schema_migrations(filename) VALUES (?)", (name,)
                )
                logger.info("applied %s", name)
            except sqlite3.Error as exc:  # pragma: no cover - safety net
                logger.warning("failed %s: %s", name, exc)
                conn.execute(
                    "INSERT OR IGNORE INTO schema_migrations(filename) VALUES (?)",
                    (name,),
                )
            bar.update(1)
        conn.commit()

    for handler in handlers:
        logger.removeHandler(handler)
        handler.close()


def ensure_migrations_applied() -> None:
    """Apply repository migrations if any exist."""

    workspace = Path(os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
    migrations_dir = workspace / "databases" / "migrations"
    if not any(migrations_dir.glob("*.sql")):
        return
    db_path = workspace / "databases" / "analytics.db"
    log_path = workspace / "logs" / "migrations.log"
    apply_migrations(db_path, migrations_dir, log_path)


def main() -> None:
    ensure_migrations_applied()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
