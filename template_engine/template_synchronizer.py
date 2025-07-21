from __future__ import annotations
# pyright: reportMissingModuleSource=false

import logging
import sqlite3
from pathlib import Path
from typing import Iterable
from datetime import datetime

from tqdm import tqdm

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


def _log_template_sync(name: str, source: Path) -> None:
    """Record a template synchronization event in analytics.db."""
    try:
        with sqlite3.connect("analytics.db") as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS templates_sync_log (name TEXT, source TEXT, synced_at TEXT)"
            )
            conn.execute(
                "INSERT INTO templates_sync_log (name, source, synced_at) VALUES (?, ?, ?)",
                (name, str(source), datetime.utcnow().isoformat()),
            )
            conn.commit()
    except sqlite3.Error as exc:
        logger.warning("Failed to log template %s from %s: %s", name, source, exc)


def synchronize_templates(source_dbs: Iterable[Path] | None = None) -> int:
    """Synchronize templates across multiple databases with transactional integrity."""
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
                        _log_template_sync(name, db)
                    conn.commit()
                    synced += 1
                except sqlite3.Error as exc:
                    conn.rollback()
                    logger.error("Failed to synchronize %s: %s", db, exc)
        except sqlite3.Error as exc:
            logger.error("Database error %s: %s", db, exc)
    return synced

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    count = synchronize_templates()
    logger.info("Synchronized %d databases", count)
