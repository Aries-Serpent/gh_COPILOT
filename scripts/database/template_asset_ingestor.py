"""Simplified template asset ingestor used for tests.

This module provides a lightweight `ingest_templates` function that
records Markdown templates into `enterprise_assets.db`. It avoids
optional enterprise dependencies so it can run in minimal environments.
"""

from __future__ import annotations

import hashlib
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


def ingest_templates(workspace: Path, template_dir: Path | None = None) -> None:
    """Ingest `.md` files from ``template_dir`` into ``enterprise_assets.db``.

    The database and table are created if they do not already exist.
    """

    workspace = Path(workspace)
    template_dir = Path(template_dir or (workspace / "prompts"))
    db_dir = workspace / "databases"
    db_dir.mkdir(parents=True, exist_ok=True)
    db_path = db_dir / "enterprise_assets.db"

    _initialize_database(db_path)
    with sqlite3.connect(db_path) as conn:
        for path in template_dir.glob("*.md"):
            conn.execute(
                "INSERT INTO template_assets (template_path, content_hash, created_at) VALUES (?, ?, ?)",
                (str(path), _hash_file(path), datetime.now(timezone.utc).isoformat()),
            )
        conn.commit()


def _initialize_database(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
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
