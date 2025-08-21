from pathlib import Path
from datetime import datetime, timezone
import json
import sys
import types

import pytest

if "pydantic" not in sys.modules:
    class BaseModel:
        def __init__(self, **data):
            for k, v in data.items():
                setattr(self, k, v)

        def model_dump(self):
            result = {}
            for k, v in self.__dict__.items():
                if isinstance(v, BaseModel):
                    result[k] = v.model_dump()
                elif isinstance(v, list):
                    result[k] = [i.model_dump() if isinstance(i, BaseModel) else i for i in v]
                else:
                    result[k] = v
            return result

        def model_dump_json(self):
            return json.dumps(self.model_dump())

        @classmethod
        def model_validate_json(cls, data: str):
            return cls(**json.loads(data))

    def Field(default_factory=None, default=None):
        if default is not None:
            return default
        if getattr(default_factory, "__name__", "") == "utcnow":
            return datetime.now(timezone.utc)
        return default_factory()

    pydantic_module = types.ModuleType("pydantic")
    pydantic_module.BaseModel = BaseModel
    pydantic_module.Field = Field
    sys.modules["pydantic"] = pydantic_module

from src.gh_copilot.compliance.dao import ComplianceDAO
from src.gh_copilot.compliance.models import ScoreInputs, ScoreSnapshot


@pytest.fixture
def populated_db(tmp_path: Path) -> Path:
    db = tmp_path / "analytics.db"
    dao = ComplianceDAO(db)
    with dao._conn() as c, c:
        c.execute(
            "CREATE TABLE score_snapshots (branch TEXT, score REAL, model_id TEXT, inputs_json TEXT, ts TEXT)"
        )
        c.execute("CREATE TABLE placeholder_tasks (status TEXT)")
    dao.ensure_views()
    return db


def test_latest_snapshot_none(populated_db: Path) -> None:
    dao = ComplianceDAO(populated_db)
    assert dao.latest_snapshot("main") is None


def test_compliance_summary_with_snapshot(populated_db: Path) -> None:
    dao = ComplianceDAO(populated_db)
    inputs = ScoreInputs(
        run_id="1",
        lint=0.8,
        tests=0.9,
        placeholders=1.0,
        sessions=1.0,
        model_id="m1",
    )
    snap = ScoreSnapshot(
        branch="main",
        score=0.85,
        model_id="m1",
        inputs=inputs,
        ts=datetime.now(timezone.utc),
    )
    with dao._conn() as c, c:
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
        c.execute("INSERT INTO placeholder_tasks VALUES ('open')")
    dao.invalidate_cache()
    summary = dao.compliance_summary("main")
    assert summary.score == 0.85
    assert summary.placeholders_open == 1
    # Cached call should not query again
    dao.latest_snapshot = lambda *_: (_ for _ in ()).throw(RuntimeError("cache miss"))  # type: ignore
    assert dao.compliance_summary("main") == summary


def test_compliance_summary_custom_target(populated_db: Path) -> None:
    dao = ComplianceDAO(populated_db)
    summary = dao.compliance_summary("dev", target_min_score=0.5)
    assert summary.gauges == []
    assert summary.score is None
