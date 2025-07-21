from __future__ import annotations

import logging
import sqlite3
from pathlib import Path
from typing import Iterable

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

def synchronize_templates(source_dbs: Iterable[Path] | None = None) -> int:
    """Synchronize templates across multiple databases."""
    databases = list(source_dbs) if source_dbs else DEFAULT_DATABASES
    all_templates: dict[str, str] = {}
    for db in databases:
        for name, content in _extract_templates(db):
            all_templates[name] = content
    synced = 0
    for db in databases:
        if not db.exists():
            continue
        try:
            with sqlite3.connect(db) as conn:
                for name, content in all_templates.items():
                    conn.execute(
                        "INSERT OR REPLACE INTO templates (name, template_content) VALUES (?, ?)",
                        (name, content),
                    )
                conn.commit()
            synced += 1
        except sqlite3.Error as exc:
            logger.error("Failed to synchronize %s: %s", db, exc)
    return synced

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    count = synchronize_templates()
    logger.info("Synchronized %d databases", count)
