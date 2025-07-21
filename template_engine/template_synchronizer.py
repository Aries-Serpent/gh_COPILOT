from __future__ import annotations
# pyright: reportMissingModuleSource=false

import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Iterable

from tqdm import tqdm

logger = logging.getLogger(__name__)

DEFAULT_DATABASES = [
    Path("development.db"),
    Path("staging.db"),
    Path("production.db"),
]

ANALYTICS_DB = Path("databases") / "analytics.db"


def _extract_templates(db: Path) -> list[tuple[str, str]]:
    if not db.exists():
        return []
    try:
        with sqlite3.connect(db) as conn:
            rows = conn.execute(
                "SELECT name, template_content FROM templates"
            ).fetchall()
            return [(r[0], r[1]) for r in rows]
    except sqlite3.Error as exc:
        logger.warning("Failed to read templates from %s: %s", db, exc)
        return []


def _validate_template(name: str, content: str) -> bool:
    return bool(name and content and content.strip())


def _compliance_score(content: str) -> float:
    """Return a simple compliance score for template content."""
    return 50.0 if "TODO" in content.upper() else 100.0


def _log_sync_event(source: str, target: str) -> None:
    """Record a synchronization event."""
    ANALYTICS_DB.parent.mkdir(exist_ok=True)
    with sqlite3.connect(ANALYTICS_DB) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS sync_events (timestamp TEXT, source_db TEXT, target_db TEXT)"
        )
        conn.execute(
            "INSERT INTO sync_events (timestamp, source_db, target_db) VALUES (?, ?, ?)",
            (datetime.utcnow().isoformat(), source, target),
        )


def _log_audit(db_name: str, details: str) -> None:
    """Log synchronization failures."""
    ANALYTICS_DB.parent.mkdir(exist_ok=True)
    with sqlite3.connect(ANALYTICS_DB) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS audit_log (timestamp TEXT, db_name TEXT, details TEXT)"
        )
        conn.execute(
            "INSERT INTO audit_log (timestamp, db_name, details) VALUES (?, ?, ?)",
            (datetime.utcnow().isoformat(), db_name, details),
        )


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

    source_names = ",".join(str(d) for d in databases)
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
                        if _compliance_score(content) < 60.0:
                            raise ValueError(f"Compliance failure for {name}")
                        cur.execute(
                            "INSERT OR REPLACE INTO templates (name, template_content) VALUES (?, ?)",
                            (name, content),
                        )
                    conn.commit()
                    synced += 1
                    _log_sync_event(source_names, str(db))
                except Exception as exc:
                    conn.rollback()
                    logger.error("Failed to synchronize %s: %s", db, exc)
                    _log_audit(str(db), str(exc))
        except sqlite3.Error as exc:
            logger.error("Database error %s: %s", db, exc)
            _log_audit(str(db), str(exc))
    return synced


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    count = synchronize_templates()
    logger.info("Synchronized %d databases", count)
