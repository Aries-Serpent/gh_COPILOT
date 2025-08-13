from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Iterable

from .models import ComplianceSummary, GaugeBreakdown, ScoreInputs, ScoreSnapshot

PRAGMAS: tuple[str, ...] = (
    "PRAGMA journal_mode=WAL;",
    "PRAGMA synchronous=NORMAL;",
    "PRAGMA foreign_keys=ON;",
)


def get_conn(db_path: Path, timeout: float = 30.0) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, timeout=timeout)
    conn.row_factory = sqlite3.Row
    for p in PRAGMAS:
        conn.execute(p)
    conn.execute(f"PRAGMA busy_timeout = {int(timeout * 1000)}")
    return conn


class ComplianceDAO:
    """Read-optimized DAO for compliance summary and gauges."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path

    @contextmanager
    def _conn(self) -> Iterable[sqlite3.Connection]:
        c = get_conn(self.db_path)
        try:
            yield c
        finally:
            c.close()

    def ensure_views(self) -> None:
        """Create views if missing."""
        with self._conn() as c, c:
            c.executescript(
                """
                CREATE VIEW IF NOT EXISTS vw_latest_snapshot AS
                SELECT s1.*
                FROM score_snapshots s1
                JOIN (
                    SELECT branch, MAX(ts) AS max_ts
                    FROM score_snapshots
                    GROUP BY branch
                ) s2 ON s1.branch = s2.branch AND s1.ts = s2.max_ts;

                CREATE VIEW IF NOT EXISTS vw_placeholders_open AS
                SELECT COUNT(*) AS open_count
                FROM placeholder_tasks
                WHERE status = 'open';
                """
            )

    def latest_snapshot(self, branch: str) -> ScoreSnapshot | None:
        with self._conn() as c:
            row = c.execute(
                "SELECT branch, score, model_id, inputs_json, ts FROM vw_latest_snapshot WHERE branch=?",
                (branch,),
            ).fetchone()
        if not row:
            return None
        inputs = ScoreInputs.model_validate_json(row["inputs_json"])  # pydantic v2
        return ScoreSnapshot(
            branch=row["branch"],
            score=float(row["score"]),
            model_id=row["model_id"],
            inputs=inputs,
            ts=datetime.fromisoformat(row["ts"]),
        )

    def open_placeholders(self) -> int:
        with self._conn() as c:
            row = c.execute("SELECT open_count FROM vw_placeholders_open").fetchone()
        return int(row["open_count"]) if row else 0

    def compliance_summary(self, branch: str, target_min_score: float | None = None) -> ComplianceSummary:
        snap = self.latest_snapshot(branch)
        placeholders_open = self.open_placeholders()
        if snap is None:
            return ComplianceSummary(branch=branch, score=None, placeholders_open=placeholders_open, gauges=[])
        target = target_min_score if target_min_score is not None else (0.90 if branch == "main" else 0.80)
        gauges = [
            GaugeBreakdown(name="compliance_score", value=snap.score, target=target),
            GaugeBreakdown(name="open_placeholders", value=float(placeholders_open), target=0.0),
        ]
        return ComplianceSummary(
            branch=branch,
            score=snap.score,
            model_id=snap.model_id,
            placeholders_open=placeholders_open,
            gauges=gauges,
        )
