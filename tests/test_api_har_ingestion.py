from fastapi.testclient import TestClient
from pathlib import Path
from src.gh_copilot.api import app


def test_api_ingest_har(monkeypatch, tmp_path):
    called = {}

    def fake_ingest(workspace: Path, har_dir: Path | None = None) -> None:  # pragma: no cover - stub
        called["workspace"] = workspace

    monkeypatch.setattr(
        "scripts.database.har_ingestor.ingest_har_entries", fake_ingest
    )
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    client = TestClient(app)
    resp = client.post("/api/v1/ingest-har")
    assert resp.status_code == 200
    assert resp.json() == {"ok": True}
    assert Path(called["workspace"]) == tmp_path
