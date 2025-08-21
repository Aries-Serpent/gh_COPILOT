from pathlib import Path
import pytest

pytest.importorskip("fastapi", reason="FastAPI not installed")

from src.gh_copilot.api import api_ingest


def test_api_ingest(monkeypatch, tmp_path):
    called = {}

    def fake_ingest(
        workspace: Path, har_dir: Path | None = None
    ) -> None:  # pragma: no cover - stub
        called["workspace"] = workspace

    monkeypatch.setattr("scripts.database.har_ingestor.ingest_har_entries", fake_ingest)
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    resp = api_ingest("har")
    assert resp == {"ok": True}
    assert Path(called["workspace"]) == tmp_path
