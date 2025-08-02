import shutil
import sqlite3

import pytest

import scripts.wlc_session_manager as wsm


class DummyValidator:
    def __init__(self, logger=None):
        self.called = False

    def validate_corrections(self, files):
        self.called = True
        return True


class DummyOrchestrator:
    def __init__(self):
        self.called = False

    def execute_unified_wrapup(self):
        self.called = True
        return type("R", (), {"compliance_score": 100.0})()


def test_main_skips_side_effects_with_test_mode(tmp_path, monkeypatch):
    temp_db = tmp_path / "production.db"
    shutil.copy(wsm.DB_PATH, temp_db)
    monkeypatch.setattr(wsm, "DB_PATH", temp_db)
    backup_root = tmp_path / "backups"
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(backup_root))
    monkeypatch.setenv("TEST_MODE", "1")
    dummy = DummyValidator()
    monkeypatch.setattr(wsm, "SecondaryCopilotValidator", lambda: dummy)
    orch = DummyOrchestrator()
    monkeypatch.setattr(
        wsm,
        "UnifiedWrapUpOrchestrator",
        lambda workspace_path=None: orch,
    )
    with sqlite3.connect(temp_db) as conn:
        before = conn.execute("SELECT COUNT(*) FROM unified_wrapup_sessions").fetchone()[0]
    wsm.main([])
    with sqlite3.connect(temp_db) as conn:
        after = conn.execute("SELECT COUNT(*) FROM unified_wrapup_sessions").fetchone()[0]
    assert after == before
    assert not dummy.called
    assert not orch.called
    assert not list((backup_root / "logs").glob("wlc_*.log"))


def test_orchestrator_skipped_in_test_mode(tmp_path, monkeypatch):
    temp_db = tmp_path / "production.db"
    shutil.copy(wsm.DB_PATH, temp_db)
    monkeypatch.setattr(wsm, "DB_PATH", temp_db)
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(tmp_path / "backups"))
    monkeypatch.setenv("TEST_MODE", "1")

    class DummyOrchestrator:
        def __init__(self, workspace_path=None) -> None:
            self.called = False

        def execute_unified_wrapup(self):
            self.called = True
            return type("R", (), {"compliance_score": 42.0})()

    orch = DummyOrchestrator()
    monkeypatch.setattr(
        wsm,
        "UnifiedWrapUpOrchestrator",
        lambda workspace_path=None: orch,
    )

    dummy = DummyValidator()
    monkeypatch.setattr(wsm, "SecondaryCopilotValidator", lambda: dummy)

    wsm.main([])
    assert not orch.called


def test_session_error_skipped_in_test_mode(tmp_path, monkeypatch):
    temp_db = tmp_path / "production.db"
    shutil.copy(wsm.DB_PATH, temp_db)
    monkeypatch.setattr(wsm, "DB_PATH", temp_db)
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(tmp_path / "backups"))
    monkeypatch.setenv("TEST_MODE", "1")

    class FailingOrchestrator:
        def __init__(self, workspace_path=None) -> None:
            pass

        def execute_unified_wrapup(self):
            raise RuntimeError("boom")

    monkeypatch.setattr(wsm, "UnifiedWrapUpOrchestrator", lambda workspace_path=None: FailingOrchestrator())
    wsm.main([])  # should not raise


def test_session_persists_lesson_skipped(tmp_path, monkeypatch):
    temp_db = tmp_path / "production.db"
    shutil.copy(wsm.DB_PATH, temp_db)
    monkeypatch.setattr(wsm, "DB_PATH", temp_db)
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(tmp_path / "backups"))
    monkeypatch.setenv("TEST_MODE", "1")
    stored = {}
    monkeypatch.setattr(wsm, "store_lesson", lambda **kw: stored.update(kw))
    wsm.run_session(1, temp_db, False, run_orchestrator=False)
    assert stored == {}


def test_missing_environment(monkeypatch):
    monkeypatch.delenv("GH_COPILOT_WORKSPACE", raising=False)
    monkeypatch.delenv("GH_COPILOT_BACKUP_ROOT", raising=False)
    monkeypatch.setenv("TEST_MODE", "1")
    with pytest.raises(EnvironmentError):
        wsm.run_session(1, wsm.DB_PATH, False)
