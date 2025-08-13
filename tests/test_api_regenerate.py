from fastapi.testclient import TestClient
from pathlib import Path
from src.gh_copilot.api import app


def test_api_regenerate(monkeypatch, tmp_path):
    called = {}

    def fake_generate(kind: str, source_db: Path, out_dir: Path, analytics_db: Path, params: dict | None = None):
        out = out_dir / "out.txt"
        out.write_text("x")
        called["kind"] = kind
        return [out]

    monkeypatch.setattr(
        "gh_copilot.generation.generate_from_templates.generate", fake_generate
    )
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    client = TestClient(app)
    resp = client.post("/api/v1/regenerate/docs")
    assert resp.status_code == 200
    assert resp.json()["written"]
    assert called["kind"] == "docs"
