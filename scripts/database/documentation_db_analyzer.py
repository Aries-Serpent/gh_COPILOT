#!/usr/bin/env python3
"""Analyze and clean documentation database."""

from __future__ import annotations

import json
import logging
import shutil
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
import shutil
import os

logger = logging.getLogger(__name__)
ANALYTICS_DB = Path("databases") / "analytics.db"


def _calculate_etc(start_ts: float, current: int, total: int) -> str:
    if current == 0:
        return "N/A"
    elapsed = time.time() - start_ts
    est_total = elapsed / (current / total)
    remaining = est_total - elapsed
    return f"{remaining:.2f}s remaining"


def _create_backup(db: Path) -> Optional[Path]:
    backup_root = Path(os.getenv("GH_COPILOT_BACKUP_ROOT", "/tmp"))
    backup_root.mkdir(parents=True, exist_ok=True)
    if not db.exists():
        return None
    backup = backup_root / f"{db.name}.{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.bak"
    shutil.copy(db, backup)
    return backup


def rollback_db(db: Path, backup: Path) -> None:
    if backup.exists():
        shutil.copy(backup, db)
        _log_event(db, {"rollback": str(backup)})


CLEANUP_SQL = (
    "DELETE FROM enterprise_documentation "
    "WHERE doc_type='BACKUP_LOG' OR source_path LIKE '%backup%'"
)

DEDUP_SQL = (
    "DELETE FROM enterprise_documentation WHERE rowid NOT IN ("
    "SELECT MIN(rowid) FROM enterprise_documentation GROUP BY title, source_path)"
)


def _log_event(db: Path, data: dict) -> None:
    """Log audit results to analytics.db."""
    analytics = Path("analytics.db")
    try:
        with sqlite3.connect(analytics) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS doc_analysis (timestamp TEXT, db TEXT, details TEXT)"
            )
            conn.execute(
                "INSERT INTO doc_analysis (timestamp, db, details) VALUES (?, ?, ?)",
                (datetime.utcnow().isoformat(), str(db), json.dumps(data)),
            )
    except sqlite3.Error:
        logger.error("Failed to log analysis results")


def audit_placeholders(db_path: Path) -> int:
    """Log TODO/FIXME placeholders from documentation table."""
    if not db_path.exists():
        return 0
    count = 0
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            "SELECT rowid, content FROM enterprise_documentation"
        ).fetchall()
        for rowid, content in rows:
            if any(tag in content.upper() for tag in ("TODO", "FIXME", "PLACEHOLDER")):
                count += 1
                with sqlite3.connect(ANALYTICS_DB) as aconn:
                    aconn.execute(
                        "CREATE TABLE IF NOT EXISTS placeholder_audit (ts TEXT, db TEXT, rowid INTEGER)"
                    )
                    aconn.execute(
                        "INSERT INTO placeholder_audit (ts, db, rowid) VALUES (?,?,?)",
                        (datetime.utcnow().isoformat(), str(db_path), rowid),
                    )
    logger.info("Placeholder audit complete: %s issues", count)
    return count


def analyze_and_cleanup(db_path: Path) -> dict[str, int]:
    """Remove backups and duplicates from ``db_path`` and return a report."""
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found at {db_path}")
    backup = _create_backup(db_path)
    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            before = cur.execute(
                "SELECT COUNT(*) FROM enterprise_documentation"
            ).fetchone()[0]
            removed_backups = cur.execute(CLEANUP_SQL).rowcount
            removed_dupes = cur.execute(DEDUP_SQL).rowcount
            after = cur.execute("SELECT COUNT(*) FROM enterprise_documentation").fetchone()[
                0
            ]
            conn.commit()
            _log_event(db_path, {
                "before": before,
                "after": after,
                "removed_backups": removed_backups,
                "removed_duplicates": removed_dupes,
            })
    except Exception as exc:
        logger.error("Cleanup failed: %s", exc)
        if backup:
            rollback_db(db_path, backup)
        raise

    try:
        ANALYTICS_DB.parent.mkdir(exist_ok=True, parents=True)
        with sqlite3.connect(ANALYTICS_DB) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS doc_audit (ts TEXT, db TEXT, removed_backups INTEGER, removed_dupes INTEGER)"
            )
            conn.execute(
                "INSERT INTO doc_audit (ts, db, removed_backups, removed_dupes) VALUES (?,?,?,?)",
                (
                    datetime.utcnow().isoformat(),
                    str(db_path),
                    removed_backups,
                    removed_dupes,
                ),
            )
    except sqlite3.Error as exc:
        logger.warning("Failed to log audit: %s", exc)

    return {
        "before": before,
        "after": after,
        "removed_backups": removed_backups,
        "removed_duplicates": removed_dupes,
    }


def rollback_cleanup(db_path: Path, backup_path: Path) -> bool:
    """Restore ``db_path`` from ``backup_path``."""
    if not backup_path.exists():
        logger.error("Backup not found: %s", backup_path)
        return False
    shutil.copy2(backup_path, db_path)
    logger.info("Database restored from backup: %s", backup_path)
    return True


def _log_report(report: dict) -> None:
    """Persist report summary to analytics DB."""
    try:
        ANALYTICS_DB.parent.mkdir(exist_ok=True, parents=True)
        with sqlite3.connect(ANALYTICS_DB) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS doc_audit (timestamp TEXT, details TEXT)"
            )
            conn.execute(
                "INSERT INTO doc_audit (timestamp, details) VALUES (?, ?)",
                (datetime.utcnow().isoformat(), json.dumps(report)),
            )
    except Exception as exc:  # pragma: no cover - logging failure should not fail tests
        logger.debug("analytics log failed: %s", exc)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    db_path = repo_root / "archives" / "documentation.db"
    steps = ["cleanup", "audit"]
    for step in tqdm(steps, desc="[PROGRESS]", unit="step"):
        if step == "cleanup":
            report = analyze_and_cleanup(db_path)
        else:
            audit_placeholders(db_path)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    report_path = (
        repo_root / "reports" / f"documentation_cleanup_report_{timestamp}.json"
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2))
    _log_report(report)
    log_correction(db_path, json.dumps(report))
    logger.info("Cleanup complete: %s", report_path)
    _log_event(db_path, {"report": str(report_path)})


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
