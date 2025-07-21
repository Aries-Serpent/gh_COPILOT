# [Script]: Template Synchronizer Engine
# > Generated: 2025-07-21 20:24:49 | Author: mbaetiong

from __future__ import annotations
# pyright: reportMissingModuleSource=false

import logging
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Iterable

try:
    from tqdm import tqdm
except ModuleNotFoundError:  # pragma: no cover - fallback if tqdm not installed
    def tqdm(iterable, **_: object) -> Iterable:
        return iterable

# Workspace/environment detection
WORKSPACE_ROOT = Path(os.getenv("GH_COPILOT_WORKSPACE", str(Path.cwd())))
DEFAULT_DATABASES = [
    WORKSPACE_ROOT / "databases" / "development.db",
    WORKSPACE_ROOT / "databases" / "staging.db",
    WORKSPACE_ROOT / "databases" / "production.db",
]
DEFAULT_ANALYTICS_DB = WORKSPACE_ROOT / "databases" / "analytics.db"
DEFAULT_ANALYTICS_DB.parent.mkdir(exist_ok=True, parents=True)

logger = logging.getLogger(__name__)

def _extract_templates(db: Path) -> list[tuple[str, str, Path]]:
    """Extract templates from a database."""
    if not db.exists():
        logger.warning("Database does not exist: %s", db)
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
    """Validate that template has a name and non-empty content."""
    return bool(name and content and content.strip())

def _compliance_score(content: str) -> float:
    """Return a simple compliance score for template content."""
    if "TODO" in content.upper() or not content.strip():
        return 50.0
    return 100.0

def _log_sync(template: str, source: Path, analytics_db: Path) -> None:
    """Log template synchronization events to analytics database."""
    try:
        with sqlite3.connect(analytics_db) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS templates_sync_log (timestamp TEXT, template_name TEXT, source_db TEXT)"
            )
            conn.execute(
                "INSERT INTO templates_sync_log (timestamp, template_name, source_db) VALUES (?, ?, ?)",
                (datetime.utcnow().isoformat(), template, str(source)),
            )
    except sqlite3.Error as exc:
        logger.error("Failed to log template sync event: %s", exc)

def _log_audit(db_name: str, details: str, analytics_db: Path) -> None:
    """Log synchronization failures or audit events to analytics database."""
    try:
        with sqlite3.connect(analytics_db) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS audit_log (timestamp TEXT, db_name TEXT, details TEXT)"
            )
            conn.execute(
                "INSERT INTO audit_log (timestamp, db_name, details) VALUES (?, ?, ?)",
                (datetime.utcnow().isoformat(), db_name, details),
            )
    except sqlite3.Error as exc:
        logger.error("Failed to log audit event: %s", exc)

def _compliance_check(conn: sqlite3.Connection) -> bool:
    """Check that all templates in DB are compliant (PEP8/flake8 placeholder)."""
    try:
        rows = conn.execute("SELECT template_content FROM templates").fetchall()
        for (content,) in rows:
            if _compliance_score(content) < 60.0:
                return False
        return True
    except Exception as exc:
        logger.error("Compliance check failed: %s", exc)
        return False

def synchronize_templates(
    source_dbs: Iterable[Path] | None = None,
    *,
    analytics_db: Path | None = None,
) -> int:
    """
    Synchronize templates across multiple databases with transactional integrity.
    Each synchronized template is logged to analytics DB with a timestamp and source.
    """
    databases = list(source_dbs) if source_dbs else DEFAULT_DATABASES
    analytics_path = analytics_db or DEFAULT_ANALYTICS_DB
    all_templates: dict[str, tuple[str, Path]] = {}

    # Extract and validate templates from all databases
    for db in databases:
        for name, content, src in _extract_templates(db):
            if _validate_template(name, content):
                all_templates[name] = (content, src)
            else:
                logger.warning("Invalid template from %s: %s", db, name)

    synced = 0

    for db in tqdm(databases, desc="Syncing DBs", unit="db"):
        if not db.exists():
            logger.warning("Skipping missing DB: %s", db)
            continue
        try:
            with sqlite3.connect(db) as conn:
                cur = conn.cursor()
                try:
                    cur.execute("BEGIN")
                    for name, (content, src_db) in all_templates.items():
                        if _compliance_score(content) < 60.0:
                            raise ValueError(f"Compliance failure for {name}")
                        cur.execute(
                            "INSERT OR REPLACE INTO templates (name, template_content) VALUES (?, ?)",
                            (name, content),
                        )
                        _log_sync(name, src_db, analytics_path)
                    if not _compliance_check(conn):
                        raise RuntimeError(f"Validation failed for DB: {db}")
                    conn.commit()
                    synced += 1
                except Exception as exc:
                    conn.rollback()
                    _log_audit(str(db), f"Sync failure: {exc}", analytics_path)
                    logger.error("Failed to synchronize %s: %s", db, exc)
        except sqlite3.Error as exc:
            _log_audit(str(db), f"DB connection error: {exc}", analytics_path)
            logger.error("Database error %s: %s", db, exc)

    return synced

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    count = synchronize_templates()
    logger.info("Synchronized %d databases", count)