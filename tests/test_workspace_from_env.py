
from database_purification_engine import DatabasePurificationEngine


def test_engine_uses_env_var(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    engine = DatabasePurificationEngine()
    assert engine.workspace_path == tmp_path
