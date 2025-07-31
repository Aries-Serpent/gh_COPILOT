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


def test_main_inserts_session(tmp_path, monkeypatch):
    temp_db = tmp_path / "production.db"
    shutil.copy(wsm.DB_PATH, temp_db)
    monkeypatch.setattr(wsm, "DB_PATH", temp_db)
    backup_root = tmp_path / "backups"
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(backup_root))
    dummy = DummyValidator()
    monkeypatch.setattr(wsm, "SecondaryCopilotValidator", lambda: dummy)
    orch = DummyOrchestrator()
    monkeypatch.setattr(
        wsm,
        "UnifiedWrapUpOrchestrator",
        lambda workspace_path=None: orch,
    )
    with sqlite3.connect(temp_db) as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM unified_wrapup_sessions")
        before = cur.fetchone()[0]
    wsm.main([])
    with sqlite3.connect(temp_db) as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM unified_wrapup_sessions")
        after = cur.fetchone()[0]
        cur.execute("SELECT compliance_score FROM unified_wrapup_sessions ORDER BY rowid DESC LIMIT 1")
        score = cur.fetchone()[0]
    assert after == before + 1
    assert abs(score - 1.0) < 1e-6
    assert dummy.called
    assert orch.called
    log_files = list((backup_root / "logs").glob("wlc_*.log"))
    assert log_files


def test_orchestrator_called(tmp_path, monkeypatch):
    temp_db = tmp_path / "production.db"
    shutil.copy(wsm.DB_PATH, temp_db)
    monkeypatch.setattr(wsm, "DB_PATH", temp_db)
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(tmp_path / "backups"))

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

    assert orch.called
    with sqlite3.connect(temp_db) as conn:
        cur = conn.cursor()
        cur.execute("SELECT compliance_score FROM unified_wrapup_sessions ORDER BY rowid DESC LIMIT 1")
        score = cur.fetchone()[0]
    assert abs(score - 0.42) < 1e-6


def test_session_error(tmp_path, monkeypatch):
    temp_db = tmp_path / "production.db"
    shutil.copy(wsm.DB_PATH, temp_db)
    monkeypatch.setattr(wsm, "DB_PATH", temp_db)
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(tmp_path / "backups"))

    class FailingOrchestrator:
        def __init__(self, workspace_path=None) -> None:
            pass

        def execute_unified_wrapup(self):
            raise RuntimeError("boom")

    monkeypatch.setattr(wsm, "UnifiedWrapUpOrchestrator", lambda workspace_path=None: FailingOrchestrator())

    with pytest.raises(RuntimeError):
        wsm.main([])

    with sqlite3.connect(temp_db) as conn:
        cur = conn.cursor()
        cur.execute("SELECT status, error_details FROM unified_wrapup_sessions ORDER BY rowid DESC LIMIT 1")
        status, error_details = cur.fetchone()

    assert status == "FAILED"
    assert "boom" in error_details


def test_run_session_inserts(tmp_path, monkeypatch):
    temp_db = tmp_path / "production.db"
    shutil.copy(wsm.DB_PATH, temp_db)
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    backup_root = tmp_path / "backups"
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(backup_root))
    monkeypatch.setattr(wsm, "SecondaryCopilotValidator", lambda: DummyValidator())
    monkeypatch.setattr(
        wsm,
        "UnifiedWrapUpOrchestrator",
        lambda workspace_path=None: DummyOrchestrator(),
    )
    with sqlite3.connect(temp_db) as conn:
        before = conn.execute("SELECT COUNT(*) FROM unified_wrapup_sessions").fetchone()[0]
    wsm.run_session(1, temp_db, False)
    with sqlite3.connect(temp_db) as conn:
        after = conn.execute("SELECT COUNT(*) FROM unified_wrapup_sessions").fetchone()[0]
    assert after == before + 1
    assert list((backup_root / "logs").glob("wlc_*.log"))


def test_missing_environment(monkeypatch):
    monkeypatch.delenv("GH_COPILOT_WORKSPACE", raising=False)
    monkeypatch.delenv("GH_COPILOT_BACKUP_ROOT", raising=False)
    with pytest.raises(EnvironmentError):
        wsm.run_session(1, wsm.DB_PATH, False)
