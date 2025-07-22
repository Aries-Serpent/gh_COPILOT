#!/usr/bin/env python3
"""Analyze and clean documentation database."""

from __future__ import annotations

import json
import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from tqdm import tqdm

from tqdm import tqdm

logger = logging.getLogger(__name__)
ANALYTICS_DB = Path("analytics.db")


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


def analyze_and_cleanup(db_path: Path) -> dict[str, int]:
    """Remove backups and duplicates from ``db_path`` and return a report."""
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found at {db_path}")

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
    for step in tqdm(["cleanup"], desc="[PROGRESS]", unit="step"):
        report = analyze_and_cleanup(db_path)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    report_path = (
        repo_root / "reports" / f"documentation_cleanup_report_{timestamp}.json"
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2))
    _log_report(report)
    logger.info("Cleanup complete: %s", report_path)
    _log_event(db_path, {"report": str(report_path)})


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
