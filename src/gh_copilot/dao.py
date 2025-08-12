from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Protocol

from .models import PlaceholderTask, ScoreInputs, ScoreModel, ScoreSnapshot


class AnalyticsDAO(Protocol):
    def log_placeholder(self, task: PlaceholderTask) -> None: ...
    def fetch_placeholders(
        self,
        status: str = "open",
        limit: int = 1000,
    ) -> list[PlaceholderTask]: ...
    def store_score_inputs(self, inputs: ScoreInputs) -> None: ...
    def fetch_active_model(self, branch: str) -> ScoreModel: ...
    def store_score_snapshot(self, snap: ScoreSnapshot) -> None: ...
    def fetch_score(self, branch: str) -> ScoreSnapshot | None: ...


PRAGMAS = (
    "PRAGMA journal_mode=WAL;",
    "PRAGMA synchronous=NORMAL;",
    "PRAGMA foreign_keys=ON;",
)


def get_conn(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    for p in PRAGMAS:
        conn.execute(p)
    return conn


class SQLiteAnalyticsDAO:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path

    @contextmanager
    def _conn(self) -> Iterator[sqlite3.Connection]:
        conn = get_conn(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def log_placeholder(self, task: PlaceholderTask) -> None:
        with self._conn() as conn:
            with conn:
                conn.execute(
                    """
                    INSERT INTO placeholder_tasks(file, line, kind, sha, ts, status)
                    VALUES (?, ?, ?, ?, ?, 'open')
                    """,
                    (task.file, task.line, task.kind.value, task.sha, task.ts.isoformat()),
                )

    def fetch_placeholders(self, status: str = "open", limit: int = 1000) -> list[PlaceholderTask]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT file, line, kind, sha, ts FROM placeholder_tasks WHERE status=? ORDER BY ts DESC LIMIT ?",
                (status, limit),
            ).fetchall()
        return [
            PlaceholderTask(
                file=r["file"],
                line=r["line"],
                kind=r["kind"],
                sha=r["sha"],
                ts=datetime.fromisoformat(r["ts"]),
            )  # type: ignore[arg-type]
            for r in rows
        ]

    def store_score_inputs(self, inputs: ScoreInputs) -> None:
        with self._conn() as conn:
            with conn:
                conn.execute(
                    """
                    INSERT INTO score_inputs(run_id, lint, tests, placeholders, sessions, model_id, ts)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        inputs.run_id,
                        inputs.lint,
                        inputs.tests,
                        inputs.placeholders,
                        inputs.sessions,
                        inputs.model_id,
                        inputs.ts.isoformat(),
                    ),
                )

    def fetch_active_model(self, branch: str) -> ScoreModel:
        # Simple defaulting by branch; extend with a real selector
        min_score = 0.90 if branch == "main" else 0.80
        with self._conn() as conn:
            row = conn.execute(
                "SELECT model_id, weights_json, min_score, effective_from FROM compliance_models ORDER BY effective_from DESC LIMIT 1",
            ).fetchone()
        if row:
            import json

            weights = json.loads(row["weights_json"])  # {lint, tests, placeholders, sessions}
            return ScoreModel(
                model_id=row["model_id"],
                lint=weights.get("lint", 0.30),
                tests=weights.get("tests", 0.40),
                placeholders=weights.get("placeholders", 0.20),
                sessions=weights.get("sessions", 0.10),
                min_score=min_score,
                effective_from=datetime.fromisoformat(row["effective_from"]),
            )
        return ScoreModel(model_id="default", effective_from=datetime.utcnow(), min_score=min_score)

    def store_score_snapshot(self, snap: ScoreSnapshot) -> None:
        with self._conn() as conn:
            with conn:
                conn.execute(
                    """
                    INSERT INTO score_snapshots(branch, score, model_id, inputs_json, ts)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        snap.branch,
                        snap.score,
                        snap.model_id,
                        snap.inputs.model_dump_json(),
                        snap.ts.isoformat(),
                    ),
                )

    def fetch_score(self, branch: str) -> ScoreSnapshot | None:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT score, model_id, inputs_json, ts FROM score_snapshots WHERE branch=? ORDER BY ts DESC LIMIT 1",
                (branch,),
            ).fetchone()
        if not row:
            return None

        from .models import ScoreInputs, ScoreSnapshot

        inputs = ScoreInputs.model_validate_json(row["inputs_json"])  # type: ignore[arg-type]
        return ScoreSnapshot(
            branch=branch,
            score=row["score"],
            model_id=row["model_id"],
            inputs=inputs,
            ts=datetime.fromisoformat(row["ts"]),
        )
