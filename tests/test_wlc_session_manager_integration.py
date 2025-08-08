"""Integration tests for ``wlc_session_manager``."""

from contextlib import contextmanager
from pathlib import Path
import sys
import types


class DummyTqdm(list):
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def update(self, *args, **kwargs):
        return None


def _tqdm(iterable=None, *args, **kwargs):
    return DummyTqdm(iterable or [])


sys.modules.setdefault("tqdm", types.SimpleNamespace(tqdm=_tqdm))
sys.modules.setdefault("psutil", types.SimpleNamespace())

from scripts import wlc_session_manager
from utils import codex_log_db


def _dummy_result():
    class Result:
        compliance_score = 100.0

    return Result()


def test_run_session_creates_and_stages_db(tmp_path, monkeypatch):
    """Running a session should create and stage the Codex log DB."""

    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(tmp_path / "backup"))
    monkeypatch.setenv("TEST", "1")
    monkeypatch.setenv("TEST_MODE", "0")

    db_file = tmp_path / "codex_log.db"
    session_file = tmp_path / "codex_session_logs.db"
    monkeypatch.setattr(codex_log_db, "CODEX_LOG_DB", db_file)
    monkeypatch.setattr(codex_log_db, "CODEX_SESSION_LOG_DB", session_file)

    # Stub out heavy dependencies
    monkeypatch.setattr(wlc_session_manager, "validate_environment", lambda: True)
    monkeypatch.setattr(wlc_session_manager, "setup_logging", lambda verbose: tmp_path / "log.txt")

    class DummyValidator:
        def validate_corrections(self, files):
            return None

    monkeypatch.setattr(wlc_session_manager, "SecondaryCopilotValidator", DummyValidator)

    class DummyOrchestrator:
        def __init__(self, *args, **kwargs):
            pass

        def execute_unified_wrapup(self):
            return _dummy_result()

    monkeypatch.setattr(wlc_session_manager, "UnifiedWrapUpOrchestrator", DummyOrchestrator)
    monkeypatch.setattr(wlc_session_manager, "extract_lessons_from_codex_logs", lambda db: [])
    monkeypatch.setattr(wlc_session_manager, "store_lesson", lambda **kw: None)

    @contextmanager
    def dummy_zero_byte(_path, _session_id):
        yield

    monkeypatch.setattr(wlc_session_manager, "ensure_no_zero_byte_files", dummy_zero_byte)

    calls: list[list[str]] = []

    def fake_run(cmd, cwd=None, check=False):
        calls.append(cmd)
        class Result:
            returncode = 0
        return Result()

    monkeypatch.setattr(codex_log_db.subprocess, "run", fake_run)

    wlc_session_manager.run_session(1, tmp_path / "prod.db", verbose=False)

    assert db_file.exists()
    assert session_file.exists()
    assert any(
        cmd[:2] == ["git", "add"]
        and str(Path(cmd[-2])) == str(db_file.relative_to(tmp_path))
        and str(Path(cmd[-1])) == str(session_file.relative_to(tmp_path))
        for cmd in calls
    )

