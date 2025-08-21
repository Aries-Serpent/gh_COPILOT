"""Simplified template asset ingestor used for tests.

This module provides a lightweight `ingest_templates` function that
records Markdown templates into `enterprise_assets.db`. It avoids
optional enterprise dependencies so it can run in minimal environments.
"""

from __future__ import annotations

import argparse
import hashlib
import logging
import sqlite3
import sys
from pathlib import Path

import datetime

# Busy timeout for SQLite connections in milliseconds
BUSY_TIMEOUT_MS = 5_000


def connect_with_timeout(db_path: Path) -> sqlite3.Connection:
    """Return a SQLite connection using the global busy timeout."""
    return sqlite3.connect(db_path, timeout=BUSY_TIMEOUT_MS / 1000)


def ingest_templates(
    workspace: Path,
    template_dir: Path | None = None,
    dry_run: bool = False,
    verbose: bool = False,
) -> None:
    """Ingest `.md` files from ``template_dir`` into ``enterprise_assets.db``.

    The database and table are created if they do not already exist.
    """

    logger = logging.getLogger("template_asset_ingestor")
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(levelname)s %(message)s",
    )

    workspace = Path(workspace)
    template_dir = Path(template_dir or (workspace / "prompts"))
    db_dir = workspace / "databases"
    db_dir.mkdir(parents=True, exist_ok=True)
    db_path = db_dir / "enterprise_assets.db"

    _initialize_database(db_path)

    if dry_run:
        logger.info("[DRY-RUN] Would ingest templates from %s", template_dir)
        return

    with connect_with_timeout(db_path) as conn:
        conn.execute(f"PRAGMA busy_timeout={BUSY_TIMEOUT_MS};")
        for path in template_dir.glob("*.md"):
            conn.execute(
                "INSERT INTO template_assets (template_path, content_hash, created_at) VALUES (?, ?, ?)",
                (
                    str(path),
                    _hash_file(path),
                    datetime.datetime.now(datetime.timezone.utc).isoformat(),
                ),
            )
        conn.commit()


def _initialize_database(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with connect_with_timeout(db_path) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS documentation_assets ("
            "id INTEGER PRIMARY KEY,"
            "doc_path TEXT NOT NULL,"
            "content_hash TEXT NOT NULL UNIQUE,"
            "version INTEGER NOT NULL DEFAULT 1,"
            "created_at TEXT NOT NULL,"
            "modified_at TEXT NOT NULL"
            ")"
        )
        conn.execute(
            "CREATE TABLE IF NOT EXISTS template_assets ("
            "id INTEGER PRIMARY KEY,"
            "template_path TEXT NOT NULL,"
            "content_hash TEXT NOT NULL UNIQUE,"
            "version INTEGER NOT NULL DEFAULT 1,"
            "created_at TEXT NOT NULL"
            ")"
        )
        conn.commit()


def _hash_file(path: Path) -> str:
    h = hashlib.sha256(path.read_bytes())
    return h.hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--templates-dir", default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args(argv)

    ingest_templates(
        Path(args.workspace),
        Path(args.templates_dir) if args.templates_dir else None,
        dry_run=args.dry_run,
        verbose=args.verbose,
    )
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    sys.exit(main())
