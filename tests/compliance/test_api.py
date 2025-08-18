import asyncio
from builtins import anext
from pathlib import Path
import json
import os
import sys
import types
import tempfile
import sqlite3

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

    def Field(default_factory=None, default=None):  # noqa: D401 - simple stub
        return default if default is not None else default_factory()

    pydantic_module = types.ModuleType("pydantic")
    pydantic_module.BaseModel = BaseModel
    pydantic_module.Field = Field
    sys.modules["pydantic"] = pydantic_module

if "starlette" not in sys.modules:
    class JSONResponse:  # minimal stub
        def __init__(self, content):
            self.body = json.dumps(content).encode()

    class StreamingResponse:  # minimal stub
        def __init__(self, gen, media_type="text/event-stream"):
            self.gen = gen

    starlette_responses = types.ModuleType("starlette.responses")
    starlette_responses.JSONResponse = JSONResponse
    starlette_responses.StreamingResponse = StreamingResponse
    sys.modules["starlette"] = types.ModuleType("starlette")
    sys.modules["starlette.responses"] = starlette_responses

    class FastAPI:  # minimal stub for routing decorators
        def __init__(self, **_):
            pass

        def get(self, _path):
            def decorator(func):
                return func
            return decorator

    def Query(default=None):
        return default

    fastapi_module = types.ModuleType("fastapi")
    fastapi_module.FastAPI = FastAPI
    fastapi_module.Query = Query
    sys.modules["fastapi"] = fastapi_module

tmp_db = tempfile.NamedTemporaryFile(delete=False)
with sqlite3.connect(tmp_db.name) as _conn:
    _conn.execute(
        "CREATE TABLE score_snapshots (branch TEXT, score REAL, model_id TEXT, inputs_json TEXT, ts TEXT)"
    )
    _conn.execute("CREATE TABLE placeholder_tasks (status TEXT)")
os.environ["GH_COPILOT_ANALYTICS_DB"] = tmp_db.name

from src.gh_copilot.compliance import api
from src.gh_copilot.compliance.dao import ComplianceDAO
from src.gh_copilot.compliance.models import ScoreInputs, ScoreSnapshot


def _setup_db(tmp_path: Path, with_snapshot: bool = False) -> ComplianceDAO:
    db = tmp_path / "analytics.db"
    dao = ComplianceDAO(db)
    with dao._conn() as c, c:
        c.execute(
            "CREATE TABLE score_snapshots (branch TEXT, score REAL, model_id TEXT, inputs_json TEXT, ts TEXT)"
        )
        c.execute("CREATE TABLE placeholder_tasks (status TEXT)")
        if with_snapshot:
            inputs = ScoreInputs(run_id="1", lint=1, tests=1, placeholders=1, sessions=1, model_id="m1")
            snap = ScoreSnapshot(branch="main", score=0.9, model_id="m1", inputs=inputs)
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
    return dao


def test_health_endpoint() -> None:
    assert api.health() == {"ok": True}


def test_get_compliance_summary_no_snapshot(tmp_path: Path, monkeypatch) -> None:
    dao = _setup_db(tmp_path, with_snapshot=False)
    monkeypatch.setattr(api, "_dao", dao)
    resp = api.get_compliance_summary()
    data = resp.body.decode()
    assert "\"score\": null" in data
    assert "\"placeholders_open\": 0" in data


def test_get_compliance_summary_with_snapshot(tmp_path: Path, monkeypatch) -> None:
    dao = _setup_db(tmp_path, with_snapshot=True)
    with dao._conn() as c, c:
        c.execute("INSERT INTO placeholder_tasks VALUES ('open')")
    dao.invalidate_cache()
    monkeypatch.setattr(api, "_dao", dao)
    resp = api.get_compliance_summary(min_score=0.5)
    data = resp.body.decode()
    assert "\"score\": 0.9" in data
    assert "0.5" in data


def test_sse_event_stream(tmp_path: Path, monkeypatch) -> None:
    dao = _setup_db(tmp_path, with_snapshot=True)
    monkeypatch.setattr(api, "_dao", dao)
    gen = api._sse_event_stream("main", None)
    first = asyncio.run(anext(gen))
    assert first.startswith(b"data:")
    ping = asyncio.run(anext(gen))
    assert ping == b": ping\n\n"


def test_sse_event_stream_no_snapshot(tmp_path: Path, monkeypatch) -> None:
    dao = _setup_db(tmp_path, with_snapshot=False)
    monkeypatch.setattr(api, "_dao", dao)
    gen = api._sse_event_stream("dev", None)
    first = asyncio.run(anext(gen))
    assert first.startswith(b"data:")
    ping = asyncio.run(anext(gen))
    assert ping == b": ping\n\n"
