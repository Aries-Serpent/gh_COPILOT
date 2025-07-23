#!/usr/bin/env python3
"""Analyze and clean documentation database."""

from __future__ import annotations

import json
import logging
import os
import shutil
import sqlite3
import time
from datetime import datetime, timezone
from template_engine.placeholder_utils import DEFAULT_ANALYTICS_DB
from pathlib import Path
from typing import List, Tuple, Optional
from tqdm import tqdm
import importlib.util

_LOG_UTILS_PATH = (
    Path(__file__).resolve().parents[2] / "template_engine" / "log_utils.py"
)
spec = importlib.util.spec_from_file_location("log_utils", _LOG_UTILS_PATH)
_log_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_log_mod)
_log_event = _log_mod._log_event

logger = logging.getLogger(__name__)
ANALYTICS_DB = DEFAULT_ANALYTICS_DB


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
    backup = (
        backup_root / f"{db.name}.{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.bak"
    )
    shutil.copy(db, backup)
    return backup


def rollback_db(db: Path, backup: Path) -> None:
    if backup.exists():
        shutil.copy(backup, db)
        _log_event(
            {"db": str(db), "rollback": str(backup)},
            table="doc_analysis",
            db_path=ANALYTICS_DB,
        )


CLEANUP_SQL = (
    "DELETE FROM enterprise_documentation "
    "WHERE doc_type='BACKUP_LOG' OR source_path LIKE '%backup%'"
)

DEDUP_SQL = (
    "DELETE FROM enterprise_documentation WHERE rowid NOT IN ("
    "SELECT MIN(rowid) FROM enterprise_documentation GROUP BY title, source_path)"
)


def _audit_placeholders_conn(conn: sqlite3.Connection) -> List[Tuple[str, str]]:
    """Return all placeholder entries from ``conn``."""
    placeholders: List[Tuple[str, str]] = []
    cur = conn.execute("PRAGMA table_info(enterprise_documentation)")
    columns = [row[1] for row in cur.fetchall()]
    if "title" in columns:
        query = "SELECT title, content FROM enterprise_documentation"
    else:
        query = "SELECT NULL as title, content FROM enterprise_documentation"
    for title, content in conn.execute(query).fetchall():
        text = content or ""
        if any(tok in text.upper() for tok in ["TODO", "FIXME", "PLACEHOLDER"]):
            placeholders.append((title or "", text))
    return placeholders


def audit_placeholders(db_path: Path) -> int:
    """Return count of placeholder entries in ``db_path``."""
    if not db_path.exists():
        return 0
    with sqlite3.connect(db_path) as conn:
        placeholders = _audit_placeholders_conn(conn)
    _log_event(
        {"db": str(db_path), "placeholders": len(placeholders)},
        table="doc_analysis",
        db_path=ANALYTICS_DB,
    )
    return len(placeholders)


def analyze_and_cleanup(
    db_path: Path, backup_path: Path | None = None
) -> dict[str, int]:
    """Remove backups and duplicates from ``db_path`` and return a report.
    Optionally record removed entries for rollback.
    """
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found at {db_path}")

    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        placeholders = _audit_placeholders_conn(conn)
        before = cur.execute(
            "SELECT COUNT(*) FROM enterprise_documentation"
        ).fetchone()[0]
        removed_backups = cur.execute(CLEANUP_SQL).rowcount
        removed_dupes = cur.execute(DEDUP_SQL).rowcount
        after = cur.execute("SELECT COUNT(*) FROM enterprise_documentation").fetchone()[
            0
        ]
        conn.commit()
        _log_event(
            {
                "db": str(db_path),
                "before": before,
                "after": after,
                "removed_backups": removed_backups,
                "removed_duplicates": removed_dupes,
                "placeholders": len(placeholders),
            },
            table="doc_analysis",
            db_path=ANALYTICS_DB,
        )

        if backup_path:
            backup_path.write_text(json.dumps(placeholders, indent=2), encoding="utf-8")

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
        "placeholders": len(placeholders),
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


def calculate_etc(start_time: float, current_progress: int, total_work: int) -> str:
    elapsed = time.time() - start_time
    if current_progress > 0:
        total_estimated = elapsed / (current_progress / total_work)
        remaining = total_estimated - elapsed
        return f"{remaining:.2f}s remaining"
    return "N/A"


def rollback_cleanup(db_path: Path, backup_path: Path) -> bool:
    """Restore ``db_path`` from ``backup_path``."""
    if not backup_path.exists():
        logger.error("Backup not found: %s", backup_path)
        return False
    shutil.copy2(backup_path, db_path)
    _log_event(
        {"db": str(db_path), "rollback": str(backup_path)},
        table="doc_analysis",
        db_path=ANALYTICS_DB,
    )
    logger.info("Database restored from backup: %s", backup_path)
    return True


def restore_entries(db_path: Path, backup_path: Path) -> None:
    """Restore entries from ``backup_path`` JSON into ``db_path``."""
    if not backup_path.exists() or not db_path.exists():
        logger.error("Backup or database not found for rollback")
        return
    items = json.loads(backup_path.read_text())
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        for title, content in items:
            cur.execute(
                "INSERT OR IGNORE INTO enterprise_documentation (title, content) VALUES (?, ?)",
                (title, content),
            )
        conn.commit()
    _log_event(
        {
            "db": str(db_path),
            "rollback_restored": len(items),
            "backup": str(backup_path),
        },
        table="doc_analysis",
        db_path=ANALYTICS_DB,
    )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    db_path = repo_root / "archives" / "documentation.db"
    start_ts = time.time()
    backup = repo_root / "reports" / "doc_placeholders_backup.json"
    for step in tqdm(["cleanup"], desc="[PROGRESS]", unit="step"):
        report = analyze_and_cleanup(db_path, backup)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    report_path = (
        repo_root / "reports" / f"documentation_cleanup_report_{timestamp}.json"
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2))
    _log_report(report)
    etc = calculate_etc(start_ts, 1, 1)
    logger.info("Cleanup complete: %s | ETC: %s", report_path, etc)
    _log_event(
        {"db": str(db_path), "report": str(report_path)},
        table="doc_analysis",
        db_path=ANALYTICS_DB,
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
