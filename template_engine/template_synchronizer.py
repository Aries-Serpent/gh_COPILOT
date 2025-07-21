from __future__ import annotations
# pyright: reportMissingModuleSource=false

import logging
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Iterable

from tqdm import tqdm

WORKSPACE_ROOT = Path(os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
ANALYTICS_DB = WORKSPACE_ROOT / "analytics.db"

logger = logging.getLogger(__name__)

DEFAULT_DATABASES = [
    Path("development.db"),
    Path("staging.db"),
    Path("production.db"),
]

def _extract_templates(db: Path) -> list[tuple[str, str]]:
    if not db.exists():
        return []
    try:
        with sqlite3.connect(db) as conn:
            rows = conn.execute("SELECT name, template_content FROM templates").fetchall()
            return [(r[0], r[1]) for r in rows]
    except sqlite3.Error as exc:
        logger.warning("Failed to read templates from %s: %s", db, exc)
        return []

def _validate_template(name: str, content: str) -> bool:
    return bool(name and content and content.strip())


def _log_result(db: Path, result: str) -> None:
    with sqlite3.connect(ANALYTICS_DB) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS template_sync_log (timestamp DATETIME, source TEXT, result TEXT)"
        )
        conn.execute(
            "INSERT INTO template_sync_log (timestamp, source, result) VALUES (?, ?, ?)",
            (datetime.now(), str(db), result),
        )
        conn.commit()


def _compliance_check(conn: sqlite3.Connection) -> bool:
    cur = conn.execute(
        "SELECT COUNT(*) FROM templates WHERE template_content = '' OR template_content IS NULL"
    )
    return cur.fetchone()[0] == 0


def synchronize_templates(source_dbs: Iterable[Path] | None = None) -> int:
    """Synchronize templates across multiple databases with transactional integrity and logging."""
    databases = list(source_dbs) if source_dbs else DEFAULT_DATABASES
    all_templates: dict[str, str] = {}

    for db in databases:
        for name, content in _extract_templates(db):
            if _validate_template(name, content):
                all_templates[name] = content
            else:
                logger.warning("Invalid template from %s: %s", db, name)

    synced = 0
    for db in tqdm(databases, desc="Syncing DBs", unit="db"):
        if not db.exists():
            continue
        try:
            with sqlite3.connect(db) as conn:
                cur = conn.cursor()
                try:
                    cur.execute("BEGIN")
                    for name, content in all_templates.items():
                        cur.execute(
                            "INSERT OR REPLACE INTO templates (name, template_content) VALUES (?, ?)",
                            (name, content),
                        )
                    if not _compliance_check(conn):
                        raise RuntimeError("validation failed")
                    conn.commit()
                    synced += 1
                    _log_result(db, "success")
                except sqlite3.Error as exc:
                    conn.rollback()
                    _log_result(db, "failed")
                    logger.error("Failed to synchronize %s: %s", db, exc)
                    raise
        except sqlite3.Error as exc:
            _log_result(db, "failed")
            logger.error("Database error %s: %s", db, exc)
            raise
    return synced

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    count = synchronize_templates()
    logger.info("Synchronized %d databases", count)
