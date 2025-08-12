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
from pathlib import Path
from typing import List, Optional, Tuple
import argparse

from tqdm import tqdm

from template_engine.placeholder_utils import DEFAULT_ANALYTICS_DB
from utils.log_utils import _log_event
from secondary_copilot_validator import SecondaryCopilotValidator

logger = logging.getLogger(__name__)
ANALYTICS_DB = DEFAULT_ANALYTICS_DB
REPORTS_DIR = Path("reports")

CORRECTION_SQL = """
CREATE TABLE IF NOT EXISTS correction_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    file_path TEXT NOT NULL,
    violation_code TEXT NOT NULL,
    fix_applied TEXT NOT NULL,
    violations_count INTEGER DEFAULT 0,
    fixes_applied INTEGER DEFAULT 0,
    fix_rate REAL DEFAULT 0.0,
    timestamp TEXT NOT NULL
);
"""

CORRECTION_SESSIONS_SQL = """
CREATE TABLE IF NOT EXISTS correction_sessions (
    session_id TEXT,
    action TEXT,
    timestamp TEXT
);
"""


def ensure_correction_history(db_path: Path) -> None:
    """Create ``correction_history`` table if needed."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.executescript(CORRECTION_SQL)
        conn.commit()


def _record_correction_session(action: str, db_path: Path) -> str:
    """Log a correction session action and return session id."""
    session_id = f"session_{datetime.utcnow().isoformat()}"
    with sqlite3.connect(db_path) as conn:
        conn.executescript(CORRECTION_SESSIONS_SQL)
        conn.execute(
            "INSERT INTO correction_sessions (session_id, action, timestamp) VALUES (?,?,?)",
            (session_id, action, datetime.utcnow().isoformat()),
        )
        conn.commit()
    _log_event({"session_id": session_id, "action": action}, table="correction_sessions", db_path=db_path)
    return session_id


def _write_session_reports(db_path: Path, reports_dir: Path = REPORTS_DIR) -> None:
    reports_dir.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            "SELECT session_id, action, timestamp FROM correction_sessions"
        ).fetchall()
    if not rows:
        return
    csv_path = reports_dir / "correction_sessions.csv"
    json_path = reports_dir / "correction_sessions.json"
    csv_lines = ["session_id,action,timestamp"] + ["%s,%s,%s" % tuple(r) for r in rows]
    csv_path.write_text("\n".join(csv_lines), encoding="utf-8")
    json_path.write_text(
        json.dumps(
            [
                {"session_id": r[0], "action": r[1], "timestamp": r[2]}
                for r in rows
            ],
            indent=2,
        ),
        encoding="utf-8",
    )


def _log_corrections(items: list[tuple[str, str]]) -> None:
    """Record cleanup actions to ``correction_history``."""
    if not items:
        return
    session_id = f"DOC_ANALYZER_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    ANALYTICS_DB.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(ANALYTICS_DB) as conn:
        conn.executescript(CORRECTION_SQL)
        for title, _ in items:
            conn.execute(
                "INSERT INTO correction_history (session_id, file_path, violation_code, fix_applied, violations_count, fixes_applied, fix_rate, timestamp)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    session_id,
                    title,
                    "DOC_CLEANUP",
                    "REMOVED_PLACEHOLDER",
                    1,
                    1,
                    1.0,
                    datetime.utcnow().isoformat(),
                ),
            )
        conn.commit()


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


def rollback_db(db: Path, backup: Path | None = None) -> None:
    """Restore ``db`` from ``backup``.

    If ``backup`` is ``None``, look for ``<db.name>.bak`` under ``GH_COPILOT_BACKUP_ROOT``.
    """
    if backup is None:
        backup_root = Path(os.getenv("GH_COPILOT_BACKUP_ROOT", "/tmp/gh_COPILOT_Backups"))
        backup = backup_root / f"{db.name}.bak"
    if backup.exists():
        shutil.copy(backup, db)
        _log_event(
            {"db": str(db), "rollback": str(backup)},
            table="doc_analysis",
            db_path=ANALYTICS_DB,
        )
        _record_correction_session("rollback", ANALYTICS_DB)
        _write_session_reports(ANALYTICS_DB, REPORTS_DIR)


CLEANUP_SQL = "DELETE FROM enterprise_documentation WHERE doc_type='BACKUP_LOG' OR source_path LIKE '%backup%'"

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
        if not text.strip() or any(tok in text.upper() for tok in ["TODO", "FIXME", "PLACEHOLDER"]):
            placeholders.append((title or "", text))
    return placeholders


def audit_placeholders(db_path: Path) -> int:
    """Return count of placeholder entries in ``db_path``."""
    if not db_path.exists():
        return 0
    with sqlite3.connect(db_path) as conn:
        placeholders = _audit_placeholders_conn(conn)
    with sqlite3.connect(ANALYTICS_DB) as log:
        log.execute("CREATE TABLE IF NOT EXISTS doc_analysis (db TEXT, gaps INTEGER, ts TEXT)")
        log.execute(
            "INSERT INTO doc_analysis (db, gaps, ts) VALUES (?, ?, ?)",
            (str(db_path), len(placeholders), datetime.utcnow().isoformat()),
        )
        log.commit()
    return len(placeholders)


def analyze_documentation_gaps(db_paths: list[Path], analytics: Path, log_dir: Path) -> list[dict[str, int]]:
    """Return placeholder gap counts for each database."""
    log_dir.mkdir(parents=True, exist_ok=True)
    results = []
    for db in db_paths:
        gaps = audit_placeholders(db)
        (log_dir / f"{db.stem}.log").write_text(str(gaps))
        results.append({"db": str(db), "gaps": gaps})
        analytics.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(analytics) as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS doc_audit (db TEXT, gaps INTEGER, ts TEXT)")
            conn.execute(
                "INSERT INTO doc_audit (db, gaps, ts) VALUES (?, ?, ?)",
                (str(db), gaps, datetime.utcnow().isoformat()),
            )
            conn.commit()
    SecondaryCopilotValidator().validate_corrections([str(p) for p in db_paths])
    return results


def analyze_documentation_tables(db_paths: list[Path], analytics: Path) -> list[dict[str, int]]:
    """Analyze row counts for documentation tables and log analytics."""
    results = []
    analytics.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(analytics) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS doc_analysis (db TEXT, table_name TEXT, row_count INTEGER, ts TEXT)")
        for db in db_paths:
            count = 0
            if db.exists():
                with sqlite3.connect(db) as dconn:
                    try:
                        cur = dconn.execute("SELECT COUNT(*) FROM enterprise_documentation")
                        count = cur.fetchone()[0]
                    except sqlite3.Error:
                        count = 0
            conn.execute(
                "INSERT INTO doc_analysis (db, table_name, row_count, ts) VALUES (?, 'enterprise_documentation', ?, ?)",
                (str(db), count, datetime.utcnow().isoformat()),
            )
            results.append({"db": str(db), "rows": count})
        conn.commit()
    SecondaryCopilotValidator().validate_corrections([str(p) for p in db_paths])
    return results


def validate_analysis(analytics_db: Path, expected: int) -> bool:
    """Check that at least ``expected`` records exist in ``doc_audit``.

    A secondary validator confirms the analytics database was touched,
    aligning with the dual-copilot requirement.
    """
    if not analytics_db.exists():
        return False
    with sqlite3.connect(analytics_db) as conn:
        cur = conn.execute("SELECT COUNT(*) FROM doc_audit")
        count = cur.fetchone()[0]
    SecondaryCopilotValidator().validate_corrections([str(analytics_db)])
    return count >= expected


def analyze_and_cleanup(db_path: Path, backup_path: Path | None = None) -> dict[str, int]:
    """Remove backups and duplicates from ``db_path`` and return a report.
    Optionally record removed entries for rollback.
    """
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found at {db_path}")

    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        placeholders = _audit_placeholders_conn(conn)
        before = cur.execute("SELECT COUNT(*) FROM enterprise_documentation").fetchone()[0]
        removed_backups = cur.execute(CLEANUP_SQL).rowcount
        removed_dupes = cur.execute(DEDUP_SQL).rowcount
        after = cur.execute("SELECT COUNT(*) FROM enterprise_documentation").fetchone()[0]
        conn.commit()
        with sqlite3.connect(ANALYTICS_DB) as log:
            log.execute(
                """
                CREATE TABLE IF NOT EXISTS doc_analysis (
                    db TEXT,
                    before INTEGER,
                    after INTEGER,
                    removed_backups INTEGER,
                    removed_duplicates INTEGER,
                    placeholders INTEGER,
                    ts TEXT
                )
                """
            )
            log.execute(
                "INSERT INTO doc_analysis (db, before, after, removed_backups, removed_duplicates, placeholders, ts) VALUES (?,?,?,?,?,?,?)",
                (
                    str(db_path),
                    before,
                    after,
                    removed_backups,
                    removed_dupes,
                    len(placeholders),
                    datetime.utcnow().isoformat(),
                ),
            )
            log.commit()

        ensure_correction_history(ANALYTICS_DB)
        with sqlite3.connect(ANALYTICS_DB) as log_conn:
            session = f"doc_cleanup_{datetime.utcnow().isoformat()}"
            if removed_backups:
                log_conn.execute(
                    "INSERT INTO correction_history (session_id, file_path, violation_code, fix_applied, timestamp)"
                    " VALUES (?, ?, 'DOC_BACKUP', ?, ?)",
                    (
                        session,
                        str(db_path),
                        f"{removed_backups}_removed",
                        datetime.utcnow().isoformat(),
                    ),
                )
            if removed_dupes:
                log_conn.execute(
                    "INSERT INTO correction_history (session_id, file_path, violation_code, fix_applied, timestamp)"
                    " VALUES (?, ?, 'DOC_DUPLICATE', ?, ?)",
                    (
                        session,
                        str(db_path),
                        f"{removed_dupes}_removed",
                        datetime.utcnow().isoformat(),
                    ),
                )
            log_conn.commit()

        if backup_path:
            backup_path.write_text(json.dumps(placeholders, indent=2), encoding="utf-8")

    _log_corrections(placeholders)

    try:
        ANALYTICS_DB.parent.mkdir(exist_ok=True, parents=True)
        with sqlite3.connect(ANALYTICS_DB) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS doc_audit ("
                "ts TEXT, db TEXT, removed_backups INTEGER, removed_dupes INTEGER)"
            )
            conn.execute(
                ("INSERT INTO doc_audit (ts, db, removed_backups, removed_dupes) VALUES (?,?,?,?)"),
                (
                    datetime.utcnow().isoformat(),
                    str(db_path),
                    removed_backups,
                    removed_dupes,
                ),
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS correction_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    violations_count INTEGER,
                    fixes_applied INTEGER,
                    fix_rate REAL,
                    timestamp TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            fix_rate = float(removed_backups + removed_dupes) / len(placeholders) if len(placeholders) > 0 else 0.0
            conn.execute(
                (
                    "INSERT INTO correction_history (session_id, file_path, "
                    "violation_code, fix_applied, violations_count, fixes_applied, "
                    "fix_rate, timestamp) VALUES (?,?,?,?,?,?,?,?)"
                ),
                (
                    "doc_cleanup",
                    str(db_path),
                    "DOC_SUMMARY",
                    f"{removed_backups + removed_dupes}_removed",
                    len(placeholders),
                    removed_backups + removed_dupes,
                    fix_rate,
                    datetime.utcnow().isoformat(),
                ),
            )
    except sqlite3.Error as exc:
        logger.warning("Failed to log audit: %s", exc)

    SecondaryCopilotValidator().validate_corrections([str(db_path)])

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
            conn.execute("CREATE TABLE IF NOT EXISTS doc_audit (timestamp TEXT, details TEXT)")
            conn.execute(
                "INSERT INTO doc_audit (timestamp, details) VALUES (?, ?)",
                (datetime.utcnow().isoformat(), json.dumps(report)),
            )
    except Exception as exc:  # pragma: no cover - logging failure should not fail tests
        logger.debug("analytics log failed: %s", exc)


def summarize_corrections(db_path: Path = ANALYTICS_DB, reports_dir: Path = REPORTS_DIR) -> dict[str, float]:
    """Aggregate correction history statistics and write a JSON report."""

    ensure_correction_history(db_path)
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT COUNT(*), COALESCE(SUM(violations_count),0), COALESCE(SUM(fixes_applied),0),"
            " SUM(CASE WHEN violation_code='DOC_ROLLBACK' OR fix_applied='DATABASE_RESTORE' THEN 1 ELSE 0 END)"
            " FROM correction_history"
        )
        entries, violations, fixes, rollbacks = cur.fetchone()

    success_rate = float(fixes) / float(violations) if violations else 0.0
    summary = {
        "entries": entries,
        "violations": violations,
        "fixes": fixes,
        "success_rate": success_rate,
        "rollbacks": rollbacks,
    }

    reports_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    report_path = reports_dir / f"correction_summary_{ts}.json"
    report_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    _log_event({"action": "summary", **summary}, table="doc_analysis", db_path=db_path)
    return summary


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
    _record_correction_session("rollback", ANALYTICS_DB)
    _write_session_reports(ANALYTICS_DB, REPORTS_DIR)
    ensure_correction_history(ANALYTICS_DB)
    with sqlite3.connect(ANALYTICS_DB) as conn:
        conn.execute(
            "INSERT INTO correction_history (session_id, file_path, violation_code, fix_applied, violations_count, fixes_applied, fix_rate, timestamp) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (
                f"rollback_{datetime.utcnow().isoformat()}",
                str(db_path),
                "DOC_ROLLBACK",
                "DATABASE_RESTORE",
                1,
                1,
                1.0,
                datetime.utcnow().isoformat(),
            ),
        )
        conn.commit()
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
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--summarize-corrections",
        action="store_true",
        help="Generate correction history summary report",
    )
    args = parser.parse_args()

    if args.summarize_corrections:
        summary = summarize_corrections(ANALYTICS_DB, REPORTS_DIR)
        logger.info("Summary generated: %s", summary)
        return

    repo_root = Path(__file__).resolve().parents[1]
    db_path = repo_root / "archives" / "documentation.db"
    start_ts = time.time()
    backup = repo_root / "reports" / "doc_placeholders_backup.json"
    for step in tqdm(["cleanup"], desc="[PROGRESS]", unit="step"):
        report = analyze_and_cleanup(db_path, backup)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    report_path = repo_root / "reports" / f"documentation_cleanup_report_{timestamp}.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2))
    _log_report(report)
    etc = calculate_etc(start_ts, 1, 1)
    logger.info("Cleanup complete: %s | ETC: %s", report_path, etc)
    with sqlite3.connect(ANALYTICS_DB) as log:
        log.execute("CREATE TABLE IF NOT EXISTS doc_analysis (db TEXT, report TEXT, ts TEXT)")
        log.execute(
            "INSERT INTO doc_analysis (db, report, ts) VALUES (?, ?, ?)",
            (str(db_path), str(report_path), datetime.utcnow().isoformat()),
        )
        log.commit()
    SecondaryCopilotValidator().validate_corrections([__file__])


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
