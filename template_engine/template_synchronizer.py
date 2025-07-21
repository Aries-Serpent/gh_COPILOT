from __future__ import annotations
# pyright: reportMissingModuleSource=false

import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Iterable

try:
    from tqdm import tqdm
except ModuleNotFoundError:  # pragma: no cover - fallback if tqdm not installed
    def tqdm(iterable, **_: object) -> Iterable:
        return iterable

logger = logging.getLogger(__name__)

DEFAULT_DATABASES = [
    Path("development.db"),
    Path("staging.db"),
    Path("production.db"),
]

DEFAULT_ANALYTICS_DB = Path("analytics.db")

def _extract_templates(db: Path) -> list[tuple[str, str, Path]]:
    if not db.exists():
        return []
    try:
        with sqlite3.connect(db) as conn:
            rows = conn.execute(
                "SELECT name, template_content FROM templates"
            ).fetchall()
            return [(r[0], r[1], db) for r in rows]
    except sqlite3.Error as exc:
        logger.warning("Failed to read templates from %s: %s", db, exc)
        return []

def _validate_template(name: str, content: str) -> bool:
    return bool(name and content and content.strip())


def _log_sync(template: str, source: Path, analytics_db: Path) -> None:
    """Log template synchronization."""
    with sqlite3.connect(analytics_db) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS templates_sync_log (timestamp TEXT, template_name TEXT, source_db TEXT)"
        )
        conn.execute(
            "INSERT INTO templates_sync_log (timestamp, template_name, source_db) VALUES (?, ?, ?)",
            (datetime.utcnow().isoformat(), template, str(source)),
        )


def synchronize_templates(
    source_dbs: Iterable[Path] | None = None,
    *,
    analytics_db: Path | None = None,
) -> int:
    """Synchronize templates across multiple databases with transactional integrity."""
    databases = list(source_dbs) if source_dbs else DEFAULT_DATABASES
    analytics_path = analytics_db or DEFAULT_ANALYTICS_DB
    all_templates: dict[str, tuple[str, Path]] = {}

    for db in databases:
        for name, content, src in _extract_templates(db):
            if _validate_template(name, content):
                all_templates[name] = (content, src)
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
                    for name, (content, src_db) in all_templates.items():
                        cur.execute(
                            "INSERT OR REPLACE INTO templates (name, template_content) VALUES (?, ?)",
                            (name, content),
                        )
                        _log_sync(name, src_db, analytics_path)
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
