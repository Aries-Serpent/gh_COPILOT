from pathlib import Path
import pytest

pytest.importorskip("fastapi", minversion="0")

from src.gh_copilot.api import api_regenerate


def test_api_regenerate(monkeypatch, tmp_path):
    called = {}

    def fake_generate(kind: str, source_db: Path, out_dir: Path, analytics_db: Path, params: dict | None = None):
        out_dir.mkdir(exist_ok=True)
        out = out_dir / "out.txt"
        out.write_text("x")
        called["kind"] = kind
        return [out]

    monkeypatch.setattr(
        "gh_copilot.generation.generate_from_templates.generate", fake_generate
    )
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    resp = api_regenerate("docs")
    assert resp["written"]
    assert called["kind"] == "docs"
