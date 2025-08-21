import asyncio
from builtins import anext
from datetime import datetime, timezone
from pathlib import Path
import os
import sqlite3
import tempfile

import pytest

pytest.importorskip("fastapi", reason="FastAPI not installed")
pytest.importorskip("starlette", reason="Starlette not installed")

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
            inputs = ScoreInputs(
                run_id="1", lint=1, tests=1, placeholders=1, sessions=1, model_id="m1"
            )
            snap = ScoreSnapshot(
                branch="main",
                score=0.9,
                model_id="m1",
                inputs=inputs,
                ts=datetime.now(timezone.utc),
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
    return dao


def test_health_endpoint() -> None:
    assert api.health() == {"ok": True}


def test_get_compliance_summary_no_snapshot(tmp_path: Path, monkeypatch) -> None:
    dao = _setup_db(tmp_path, with_snapshot=False)
    monkeypatch.setattr(api, "_dao", dao)
    resp = api.get_compliance_summary()
    data = resp.body.decode()
    assert '"score": null' in data
    assert '"placeholders_open": 0' in data


def test_get_compliance_summary_with_snapshot(tmp_path: Path, monkeypatch) -> None:
    dao = _setup_db(tmp_path, with_snapshot=True)
    with dao._conn() as c, c:
        c.execute("INSERT INTO placeholder_tasks VALUES ('open')")
    dao.invalidate_cache()
    monkeypatch.setattr(api, "_dao", dao)
    resp = api.get_compliance_summary(min_score=0.5)
    data = resp.body.decode()
    assert '"score": 0.9' in data
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
