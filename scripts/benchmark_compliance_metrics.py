"""Benchmark compliance summary calculations.

This script populates a temporary SQLite database with many score snapshots
and measures the time to compute compliance summaries repeatedly with and
without memoization.
"""
from __future__ import annotations

from pathlib import Path
from time import perf_counter
import json
import sys

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

import types

if "pydantic" not in sys.modules:
    class BaseModel:
        def __init__(self, **data):
            for k, v in data.items():
                setattr(self, k, v)

        def model_dump(self):
            return self.__dict__.copy()

        def model_dump_json(self):
            return json.dumps(self.model_dump())

        @classmethod
        def model_validate_json(cls, data: str):
            return cls(**json.loads(data))

    def Field(default_factory=None, default=None):
        return default if default is not None else default_factory()

    pydantic_module = types.ModuleType("pydantic")
    pydantic_module.BaseModel = BaseModel
    pydantic_module.Field = Field
    sys.modules["pydantic"] = pydantic_module

from gh_copilot.compliance.dao import ComplianceDAO
from gh_copilot.compliance.models import ScoreInputs, ScoreSnapshot

DB_PATH = Path("/tmp/compliance_benchmark.db")


def _prepare_db(records: int = 5000) -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()
    inputs = ScoreInputs(
        run_id="r1",
        lint=0.9,
        tests=0.8,
        placeholders=0.7,
        sessions=1.0,
        model_id="m1",
    )
    dao = ComplianceDAO(DB_PATH)
    with dao._conn() as c, c:
        c.execute(
            "CREATE TABLE score_snapshots (branch TEXT, score REAL, model_id TEXT, inputs_json TEXT, ts TEXT)"
        )
        c.execute(
            "CREATE TABLE placeholder_tasks (status TEXT)"
        )
        for _ in range(records):
            snap = ScoreSnapshot(
                branch="main",
                score=0.8,
                model_id="m1",
                inputs=inputs,
            )
            c.execute(
                "INSERT INTO score_snapshots VALUES (?, ?, ?, ?, ?)",
                (
                    snap.branch,
                    snap.score,
                    snap.model_id,
                    snap.inputs.model_dump_json(),
                    snap.ts.isoformat(),
                ),
            )
    dao.ensure_views()


def benchmark(iterations: int = 1000) -> tuple[float, float]:
    dao = ComplianceDAO(DB_PATH)
    start = perf_counter()
    for _ in range(iterations):
        dao.invalidate_cache()
        dao.compliance_summary("main")
    uncached = perf_counter() - start

    dao.invalidate_cache()
    dao.compliance_summary("main")  # prime cache
    start = perf_counter()
    for _ in range(iterations):
        dao.compliance_summary("main")
    cached = perf_counter() - start
    return uncached, cached


if __name__ == "__main__":  # pragma: no cover - manual benchmark
    _prepare_db()
    uncached, cached = benchmark()
    print(f"uncached: {uncached:.3f}s, cached: {cached:.3f}s")
