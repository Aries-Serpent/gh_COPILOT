import pytest

pytest.importorskip("fastapi", reason="FastAPI not installed")

from src.gh_copilot.api import api_regenerate, get_compliance


def test_api_regenerate_failure(monkeypatch, tmp_path):
    def boom(**kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(
        "gh_copilot.generation.generate_from_templates.generate",
        lambda *a, **k: boom(),
    )
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    with pytest.raises(RuntimeError):
        api_regenerate("docs")


def test_get_compliance_missing(monkeypatch):
    monkeypatch.setattr("src.gh_copilot.api._dao.fetch_score", lambda branch: None)
    resp = get_compliance("dev")
    assert resp == {"branch": "dev", "score": None}
