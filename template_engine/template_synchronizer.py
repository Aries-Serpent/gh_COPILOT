# [Script]: Template Synchronizer Engine
# > Generated: 2025-07-21 20:39:23 | Author: mbaetiong
# --- Enterprise Standards ---
# - Flake8/PEP8 Compliant
# - Explicit logging for validation and audit
# - Environment/workspace compliance (ANALYTICS_DB may be patched by test harnesses)

import logging
import os
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Iterable

from tqdm import tqdm


ANALYTICS_DB = Path("databases") / "analytics.db"
logger = logging.getLogger(__name__)


def _extract_templates(db: Path) -> list[tuple[str, str]]:
    """Extract templates from a database."""
    if not db.exists():
        logger.warning("Database does not exist: %s", db)
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
    """Validate that template has a name and non-empty content."""
    return bool(name and content and content.strip())


def _compliance_score(content: str) -> float:
    """Return a simple compliance score for template content."""
    # Example: flag TODOs or missing content as non-compliant
    if "TODO" in content.upper() or not content.strip():
        return 50.0
    return 100.0


def _log_sync_event(source: str, target: str) -> None:
    """Record a synchronization event in analytics DB."""
    try:
        ANALYTICS_DB.parent.mkdir(exist_ok=True, parents=True)
        with sqlite3.connect(ANALYTICS_DB) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS sync_events (timestamp TEXT, source_db TEXT, target_db TEXT)"
            )
            conn.execute(
                "INSERT INTO sync_events (timestamp, source_db, target_db) VALUES (?, ?, ?)",
                (datetime.utcnow().isoformat(), source, target),
            )
    except sqlite3.Error as exc:
        logger.error("Failed to log sync event: %s", exc)


def _log_audit(db_name: str, details: str) -> None:
    """Log synchronization failures or audit events."""
    try:
        ANALYTICS_DB.parent.mkdir(exist_ok=True, parents=True)
        with sqlite3.connect(ANALYTICS_DB) as conn:
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
) -> int:
    """
    Synchronize templates across multiple databases with transactional integrity.
    Each synchronized template is logged to analytics DB with a timestamp and source.
    """
    start = datetime.utcnow()
    databases = list(source_dbs) if source_dbs else []
    all_templates: dict[str, str] = {}

    # Extract and validate templates from all databases
    for db in tqdm(databases, desc="Extracting", unit="db"):
        for name, content in _extract_templates(db):
            if _validate_template(name, content):
                all_templates[name] = content
            else:
                logger.warning("Invalid template from %s: %s", db, name)

    source_names = ",".join(str(d) for d in databases)
    synced = 0

    for db in tqdm(databases, desc="Synchronizing", unit="db"):
        if not db.exists():
            logger.warning("Skipping missing DB: %s", db)
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
                    if not _compliance_check(conn):
                        raise ValueError("Post-sync compliance validation failed")
                    synced += 1
                    _log_sync_event(source_names, str(db))
                except Exception as exc:
                    conn.rollback()
                    _log_audit(str(db), f"Sync failure: {exc}")
                    logger.error("Failed to synchronize %s: %s", db, exc)
        except sqlite3.Error as exc:
            _log_audit(str(db), f"DB connection error: {exc}")
            logger.error("Database error %s: %s", db, exc)

    duration = (datetime.utcnow() - start).total_seconds()
    logger.info("Synchronization completed for %s databases in %.2fs", synced, duration)
    return synced


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    dbs_env = os.getenv("TEMPLATE_SYNC_DBS", "").split(os.pathsep)
    source_dbs = [Path(p) for p in dbs_env if p]
    synchronize_templates(source_dbs)
