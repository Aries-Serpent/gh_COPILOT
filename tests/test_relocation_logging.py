import importlib

import pytest


def test_relocation_logs_events(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(tmp_path.parent / "backups"))
    db_dir = tmp_path / "databases"
    db_dir.mkdir()
    (db_dir / "production.db").touch()
    (tmp_path / "logs").mkdir()

    called = []

    module = importlib.import_module("scripts.automation.enterprise_file_relocation_orchestrator")
    monkeypatch.setattr(module, "_log_event", lambda event, **_: called.append(event) or True)
    orch = module.EnterpriseFileRelocationOrchestrator()
    monkeypatch.setattr(orch, "secondary_validate", lambda: None, raising=False)
    monkeypatch.setattr(orch, "build_file_relocation_map", lambda: {})
    orch.execute_relocation_orchestration()
    assert any(e.get("event") == "relocation_start" for e in called)
    assert any(e.get("event") == "relocation_complete" for e in called)
