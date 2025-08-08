import pytest

from pathlib import Path

import scripts.wlc_session_manager as wsm
from unified_session_management_system import prevent_recursion
import subprocess


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


def test_main_skips_side_effects_with_test_mode(unified_wrapup_session_db, tmp_path, monkeypatch):
    monkeypatch.setattr(wsm, "DB_PATH", unified_wrapup_session_db)
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
    with wsm.get_connection(unified_wrapup_session_db) as conn:
        before = conn.execute("SELECT COUNT(*) FROM unified_wrapup_sessions").fetchone()[0]
    wsm.main([])
    with wsm.get_connection(unified_wrapup_session_db) as conn:
        after = conn.execute("SELECT COUNT(*) FROM unified_wrapup_sessions").fetchone()[0]
    assert after == before
    assert not dummy.called
    assert not orch.called


def test_orchestrator_called(unified_wrapup_session_db, tmp_path, monkeypatch):
    monkeypatch.setattr(wsm, "DB_PATH", unified_wrapup_session_db)
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    backup_root = tmp_path / "backups"
    backup_root.mkdir()
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(backup_root))
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

    with wsm.get_connection(unified_wrapup_session_db) as conn:
        before = conn.execute("SELECT COUNT(*) FROM unified_wrapup_sessions").fetchone()[0]
    wsm.main([])
    with wsm.get_connection(unified_wrapup_session_db) as conn:
        after = conn.execute("SELECT COUNT(*) FROM unified_wrapup_sessions").fetchone()[0]

    assert after == before
    assert not orch.called
    assert not dummy.called


def test_session_error_skipped_in_test_mode(unified_wrapup_session_db, tmp_path, monkeypatch):
    monkeypatch.setattr(wsm, "DB_PATH", unified_wrapup_session_db)
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(tmp_path / "backups"))
    monkeypatch.setenv("TEST_MODE", "1")

    class FailingOrchestrator:
        def __init__(self, workspace_path=None) -> None:
            pass

        def execute_unified_wrapup(self):
            raise RuntimeError("boom")

    monkeypatch.setattr(wsm, "UnifiedWrapUpOrchestrator", lambda workspace_path=None: FailingOrchestrator())

    with wsm.get_connection(unified_wrapup_session_db) as conn:
        before = conn.execute("SELECT COUNT(*) FROM unified_wrapup_sessions").fetchone()[0]
    wsm.main([])
    with wsm.get_connection(unified_wrapup_session_db) as conn:
        after = conn.execute("SELECT COUNT(*) FROM unified_wrapup_sessions").fetchone()[0]

    assert after == before


def test_session_persists_lesson_skipped(unified_wrapup_session_db, tmp_path, monkeypatch):
    monkeypatch.setattr(wsm, "DB_PATH", unified_wrapup_session_db)
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(tmp_path / "backups"))
    monkeypatch.setenv("TEST_MODE", "1")
    stored = {}
    monkeypatch.setattr(wsm, "store_lesson", lambda **kw: stored.update(kw))
    wsm.run_session(1, unified_wrapup_session_db, False, run_orchestrator=False)
    assert stored == {}


def test_missing_environment(monkeypatch):
    monkeypatch.delenv("GH_COPILOT_WORKSPACE", raising=False)
    monkeypatch.delenv("GH_COPILOT_BACKUP_ROOT", raising=False)
    monkeypatch.delenv("TEST_MODE", raising=False)
    with pytest.raises(EnvironmentError):
        wsm.run_session(1, wsm.DB_PATH, False)


def test_internal_backup_root_invalid(tmp_path, monkeypatch):
    """Ensure backup root inside workspace triggers EnvironmentError."""
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    backup_root = tmp_path / "backups"
    backup_root.mkdir()
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(backup_root))
    monkeypatch.delenv("TEST_MODE", raising=False)
    with pytest.raises(EnvironmentError):
        wsm.validate_environment()


def test_backup_logging_records_entry(tmp_path, monkeypatch):
    """Execute utility and confirm rollback log entry recorded."""
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    backup_root = tmp_path.parent / "backups"
    backup_root.mkdir()
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(backup_root))
    analytics_db = tmp_path / "databases" / "analytics.db"
    analytics_db.parent.mkdir(parents=True, exist_ok=True)
    analytics_db.touch()
    from session_management_consolidation_executor import EnterpriseUtility

    util = EnterpriseUtility(str(tmp_path))
    util.execute_utility()

    import sqlite3

    with sqlite3.connect(analytics_db) as conn:
        rows = conn.execute("SELECT target, backup FROM rollback_logs").fetchall()
    assert rows
    assert Path(rows[0][1]).parent == backup_root


def test_prevent_recursion_blocks_nested_calls():
    calls: list[int] = []

    @prevent_recursion
    def recurse(depth: int = 0) -> None:
        calls.append(depth)
        if depth == 0:
            recurse(depth + 1)

    with pytest.raises(RuntimeError):
        recurse()
    assert calls == [0]


def test_run_session_creates_and_stages_codex_db(tmp_path, monkeypatch):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    backup_root = tmp_path / "backup"
    backup_root.mkdir()
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(backup_root))
    monkeypatch.delenv("TEST_MODE", raising=False)

    subprocess.run(["git", "init"], cwd=workspace, check=True, capture_output=True)

    import utils.codex_log_db as cldb
    monkeypatch.setattr(cldb, "CODEX_LOG_DB", workspace / "databases" / "codex_log.db")
    monkeypatch.setattr(
        cldb, "CODEX_SESSION_LOG_DB", workspace / "databases" / "codex_session_logs.db"
    )

    monkeypatch.setattr(wsm, "SecondaryCopilotValidator", lambda: DummyValidator())
    from contextlib import contextmanager

    @contextmanager
    def _no_zero_byte(_path=None, _session_id=None):
        yield

    monkeypatch.setattr(wsm, "ensure_no_zero_byte_files", _no_zero_byte)
    monkeypatch.setattr(wsm, "extract_lessons_from_codex_logs", lambda db: [])
    monkeypatch.setattr(wsm, "store_lesson", lambda **kw: None)
    monkeypatch.setattr(wsm, "_zero_byte_count", lambda session_id: 0)
    class _DummyOrchestrator:
        def __init__(self, workspace_path=None):
            pass

        def execute_unified_wrapup(self):
            return type("R", (), {"compliance_score": 100.0})()

    monkeypatch.setattr(wsm, "UnifiedWrapUpOrchestrator", _DummyOrchestrator)

    wsm.run_session(1, workspace / "production.db", False, run_orchestrator=False)

    codex_db = workspace / "databases" / "codex_log.db"
    assert codex_db.exists()
    ls_output = subprocess.run(
        ["git", "ls-files", "--stage", str(codex_db.relative_to(workspace))],
        cwd=workspace,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    assert ls_output.strip()
