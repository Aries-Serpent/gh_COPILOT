import os
from pathlib import Path

import pytest

from template_engine import db_first_code_generator as dbgen
from template_engine.db_first_code_generator import DBFirstCodeGenerator
from utils import log_utils


os.environ.setdefault("GH_COPILOT_DISABLE_VALIDATION", "1")


def test_generation_idempotent_and_logged(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    analytics_dir = tmp_path / "databases"
    analytics_dir.mkdir()
    analytics = analytics_dir / "analytics.db"
    gen = DBFirstCodeGenerator(
        production_db=tmp_path / "production.db",
        documentation_db=tmp_path / "documentation.db",
        template_db=tmp_path / "templates.db",
        analytics_db=analytics,
    )
    monkeypatch.setattr(dbgen, "validate_no_recursive_folders", lambda: None)

    # Ensure artifact does not exist prior to generation
    import hashlib

    stub_hash = hashlib.sha256("print('hello')".encode()).hexdigest()
    existing = Path(stub_hash + ".py")
    if existing.exists():
        existing.unlink()

    # Simplify template processing
    gen.select_best_template = lambda *_: "print('hello')"
    monkeypatch.setattr(dbgen, "apply_tokens", lambda t, *_: t)
    monkeypatch.setattr(dbgen, "remove_unused_tokens", lambda s, **_: s)

    events: list[tuple[str, dict]] = []
    orig_log = log_utils._log_event

    def fake_log(event: dict, *, table: str, db_path: Path, **kwargs: object) -> bool:
        events.append((table, event))
        return orig_log(event, table=table, db_path=db_path, **kwargs)

    monkeypatch.setattr(log_utils, "_log_event", fake_log)
    monkeypatch.setattr(dbgen, "_log_event", fake_log)

    path1 = gen.generate_integration_ready_code("Obj")
    mtime = path1.stat().st_mtime
    path2 = gen.generate_integration_ready_code("Obj")

    assert path1 == path2
    assert path2.stat().st_mtime == mtime

    gen_events = [e for t, e in events if t == "generator_events"]
    corr_events = [e for t, e in events if t == "correction_logs"]

    assert any(e.get("event") == "integration_ready_generated" for e in gen_events)
    assert any(e.get("event") == "artifact_exists" for e in gen_events)
    assert all(
        e.get("hash") for e in gen_events if e.get("event") in {"integration_ready_generated", "artifact_exists"}
    )
    assert all(
        e.get("timestamp") for e in gen_events if e.get("event") in {"integration_ready_generated", "artifact_exists"}
    )

    assert any(e.get("event") == "code_generated" for e in corr_events)
    assert any(e.get("event") == "artifact_exists" for e in corr_events)
