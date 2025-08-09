"""Compliance Metrics Updater (composite score persistence).

Composite score formula:
    L = max(0, 100 - ruff_issues)
    T = (tests_passed / tests_total) * 100
    P = (placeholders_resolved / (placeholders_open + placeholders_resolved)) * 100
    composite = 0.3*L + 0.5*T + 0.2*P

Data sources (optional tables – treated as 0/100 defaults if absent):
    ruff_issue_log(issues)
    test_run_stats(passed, total)
    placeholder_audit_snapshots(open_count, resolved_count)

Writes to analytics.db: compliance_scores
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple
import os, sqlite3, time

__all__ = ["update_compliance_metrics", "ComplianceComponents"]


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


def _fetch_components(conn: sqlite3.Connection) -> ComplianceComponents:
    if _table_exists(conn, "ruff_issue_log"):
        ruff_issues = conn.execute("SELECT COALESCE(SUM(issues),0) FROM ruff_issue_log").fetchone()[0]
    else:
        ruff_issues = 0
    if _table_exists(conn, "test_run_stats"):
        tests_passed, tests_total = conn.execute(
            "SELECT COALESCE(SUM(passed),0), COALESCE(SUM(total),0) FROM test_run_stats"
        ).fetchone()
    else:
        tests_passed, tests_total = 0, 0
    if _table_exists(conn, "placeholder_audit_snapshots"):
        placeholders_open, placeholders_resolved = conn.execute(
            "SELECT COALESCE(open_count,0), COALESCE(resolved_count,0) FROM placeholder_audit_snapshots ORDER BY id DESC LIMIT 1"
        ).fetchone()
    else:
        placeholders_open, placeholders_resolved = 0, 0
    return ComplianceComponents(int(ruff_issues or 0), int(tests_passed or 0), int(tests_total or 0), int(placeholders_open or 0), int(placeholders_resolved or 0))


def _compute(c: ComplianceComponents) -> Tuple[float, float, float, float]:
    L = max(0.0, 100.0 - float(c.ruff_issues))
    T = (float(c.tests_passed) / c.tests_total * 100.0) if c.tests_total else 0.0
    denom = c.placeholders_open + c.placeholders_resolved
    P = (float(c.placeholders_resolved) / denom * 100.0) if denom else 100.0
    composite = 0.3 * L + 0.5 * T + 0.2 * P
    return L, T, P, composite


def update_compliance_metrics(workspace: Optional[str] = None, db_path: Optional[Path] = None) -> float:
    ws = Path(workspace or os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
    analytics_db = db_path or ws / "databases" / "analytics.db"
    if not analytics_db.exists():  # pragma: no cover
        raise FileNotFoundError(f"analytics.db not found: {analytics_db}")
    if "backup" in str(ws).lower():  # safety
        raise RuntimeError("Refusing to run inside backup directory")
    with _connect(analytics_db) as conn:
        _ensure_table(conn)
        comp = _fetch_components(conn)
        L, T, P, composite = _compute(comp)
        conn.execute(
            """
            INSERT INTO compliance_scores
            (timestamp, L, T, P, composite, ruff_issues, tests_passed, tests_total, placeholders_open, placeholders_resolved)
            VALUES (?,?,?,?,?,?,?,?,?,?)
            """,
            (int(time.time()), L, T, P, composite, comp.ruff_issues, comp.tests_passed, comp.tests_total, comp.placeholders_open, comp.placeholders_resolved),
        )
        conn.commit()
        return composite


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
