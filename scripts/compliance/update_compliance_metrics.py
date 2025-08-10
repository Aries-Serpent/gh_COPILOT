"""Compliance Metrics Updater (composite score persistence).

Composite score formula:
    L = max(0, 100 - ruff_issues)
    T = (tests_passed / tests_total) * 100
    P = (placeholders_resolved / (placeholders_open + placeholders_resolved)) * 100
    composite = 0.3*L + 0.5*T + 0.2*P

Data sources (optional tables – treated as 0/100 defaults if absent):
    ruff_issue_log(issues)
    test_run_stats(passed, total)
    placeholder_audit_snapshots(timestamp, open_count, resolved_count)

Writes to analytics.db: compliance_metrics_history (and legacy compliance_scores)
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import os
import sqlite3
import time

from scripts.code_placeholder_audit import get_latest_placeholder_snapshot

__all__ = [
    "update_compliance_metrics",
    "ComplianceComponents",
    "_ensure_metrics_table",
    "fetch_recent_compliance",
]


@dataclass
class ComplianceComponents:
    ruff_issues: int
    tests_passed: int
    tests_total: int
    placeholders_open: int
    placeholders_resolved: int


def _connect(db: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db))
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


def _table_exists(conn: sqlite3.Connection, name: str) -> bool:
    cur = conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=? LIMIT 1", (name,))
    return cur.fetchone() is not None


def _ensure_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS compliance_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp INTEGER NOT NULL,
            L REAL NOT NULL,
            T REAL NOT NULL,
            P REAL NOT NULL,
            composite REAL NOT NULL,
            ruff_issues INTEGER NOT NULL,
            tests_passed INTEGER NOT NULL,
            tests_total INTEGER NOT NULL,
            placeholders_open INTEGER NOT NULL,
            placeholders_resolved INTEGER NOT NULL
        )
        """
    )


def _ensure_metrics_table(conn: sqlite3.Connection) -> None:
    """Ensure the unified compliance metrics history table exists."""
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS compliance_metrics_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts INTEGER,
            ruff_issues INTEGER,
            tests_passed INTEGER,
            tests_total INTEGER,
            placeholders_open INTEGER,
            placeholders_resolved INTEGER,
            lint_score REAL,
            test_score REAL,
            placeholder_score REAL,
            composite_score REAL,
            source TEXT,
            meta_json TEXT
        )
        """
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_compliance_metrics_history_ts ON compliance_metrics_history(ts DESC)"
    )


def _fetch_components(conn: sqlite3.Connection) -> ComplianceComponents:
    if _table_exists(conn, "ruff_issue_log"):
        try:
            ruff_issues = conn.execute(
                "SELECT COALESCE(issues,0) FROM ruff_issue_log ORDER BY run_timestamp DESC LIMIT 1"
            ).fetchone()[0]
        except sqlite3.OperationalError:
            ruff_issues = conn.execute(
                "SELECT COALESCE(issues,0) FROM ruff_issue_log ORDER BY rowid DESC LIMIT 1"
            ).fetchone()[0]
    else:
        ruff_issues = 0
    if _table_exists(conn, "test_run_stats"):
        try:
            tests_passed, tests_total = conn.execute(
                """
                SELECT COALESCE(passed,0), COALESCE(total,0)
                FROM test_run_stats ORDER BY run_timestamp DESC LIMIT 1
                """
            ).fetchone()
        except sqlite3.OperationalError:
            tests_passed, tests_total = conn.execute(
                """
                SELECT COALESCE(passed,0), COALESCE(total,0)
                FROM test_run_stats ORDER BY rowid DESC LIMIT 1
                """
            ).fetchone()
    else:
        tests_passed, tests_total = 0, 0
    # Use the most robust, compatible approach for placeholder audit snapshots
    placeholders_open, placeholders_resolved = get_latest_placeholder_snapshot(conn)
    return ComplianceComponents(
        int(ruff_issues or 0),
        int(tests_passed or 0),
        int(tests_total or 0),
        int(placeholders_open or 0),
        int(placeholders_resolved or 0),
    )


def _compute(c: ComplianceComponents) -> Tuple[float, float, float, float]:
    L = min(100.0, max(0.0, 100.0 - float(c.ruff_issues)))
    T = (float(c.tests_passed) / c.tests_total * 100.0) if c.tests_total else 0.0
    denom = c.placeholders_open + c.placeholders_resolved
    placeholder_score = (
        float(c.placeholders_resolved) / denom * 100.0
        if denom
        else 0.0
    )
    composite = 0.3 * L + 0.5 * T + 0.2 * placeholder_score
    return L, T, placeholder_score, composite


def update_compliance_metrics(workspace: Optional[str] = None, db_path: Optional[Path] = None) -> float:
    ws = Path(workspace or os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
    analytics_db = db_path or ws / "databases" / "analytics.db"
    if not analytics_db.exists():  # pragma: no cover
        raise FileNotFoundError(f"analytics.db not found: {analytics_db}")
    if "backup" in str(ws).lower():  # safety
        raise RuntimeError("Refusing to run inside backup directory")
    with _connect(analytics_db) as conn:
        _ensure_table(conn)
        _ensure_metrics_table(conn)
        comp = _fetch_components(conn)
        L, T, placeholder_score, composite = _compute(comp)
        ts = int(time.time())
        # Write to unified history table
        conn.execute(
            """
            INSERT INTO compliance_metrics_history (
                ts, ruff_issues, tests_passed, tests_total,
                placeholders_open, placeholders_resolved,
                lint_score, test_score, placeholder_score,
                composite_score, source, meta_json
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                ts,
                comp.ruff_issues,
                comp.tests_passed,
                comp.tests_total,
                comp.placeholders_open,
                comp.placeholders_resolved,
                L,
                T,
                placeholder_score,
                composite,
                "update_compliance",
                None,
            ),
        )
        # Write to legacy table for backward compatibility
        conn.execute(
            """
            INSERT INTO compliance_scores (
                timestamp, L, T, P, composite,
                ruff_issues, tests_passed, tests_total,
                placeholders_open, placeholders_resolved
            ) VALUES (?,?,?,?,?,?,?,?,?,?)
            """,
            (
                ts,
                L,
                T,
                placeholder_score,
                composite,
                comp.ruff_issues,
                comp.tests_passed,
                comp.tests_total,
                comp.placeholders_open,
                comp.placeholders_resolved,
            ),
        )
        conn.commit()
        return composite


def fetch_recent_compliance(
    limit: int = 20,
    workspace: Optional[str] = None,
    db_path: Optional[Path] = None,
) -> List[Dict[str, float]]:
    """Return recent compliance metrics from the unified history table."""
    ws = Path(workspace or os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
    analytics_db = db_path or ws / "databases" / "analytics.db"
    rows: List[Dict[str, float]] = []
    if not analytics_db.exists():
        return rows
    with _connect(analytics_db) as conn:
        _ensure_metrics_table(conn)
        cur = conn.execute(
            """
            SELECT ts, composite_score, lint_score, test_score, placeholder_score
            FROM compliance_metrics_history ORDER BY ts DESC LIMIT ?
            """,
            (limit,),
        )
        for ts, comp, l_score, t_score, p_score in cur.fetchall():
            rows.append(
                {
                    "timestamp": ts,
                    "composite": comp,
                    "lint_score": l_score,
                    "test_score": t_score,
                    "placeholder_score": p_score,
                }
            )
    return rows


def _cli():  # pragma: no cover
    import argparse
    p = argparse.ArgumentParser(description="Update composite compliance metrics")
    p.add_argument("--workspace", type=str, default=None)
    p.add_argument("--db", type=str, default=None)
    a = p.parse_args()
    score = update_compliance_metrics(a.workspace, Path(a.db) if a.db else None)
    print(f"Composite compliance score recorded: {score:.2f}")


if __name__ == "__main__":  # pragma: no cover
    _cli()
