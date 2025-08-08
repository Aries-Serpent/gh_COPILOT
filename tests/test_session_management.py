import logging
from types import SimpleNamespace

import pytest

import unified_session_management_system as usm
from unified_session_management_system import ensure_no_zero_byte_files, finalize_session
import utils.validation_utils as validation_utils
from utils.validation_utils import _LOCK_DIR
import sys
import types
from utils import codex_log_db

_stub = types.ModuleType("correction_logger_and_rollback")
_stub.CorrectionLoggerRollback = object
sys.modules.setdefault("scripts.correction_logger_and_rollback", _stub)
import scripts
scripts.correction_logger_and_rollback = _stub
sys.modules["utils"].validation_utils = validation_utils

sk_stub = types.ModuleType("sklearn")
ensemble_stub = types.ModuleType("sklearn.ensemble")
ensemble_stub.IsolationForest = object
sk_stub.ensemble = ensemble_stub
sys.modules.setdefault("sklearn", sk_stub)
sys.modules.setdefault("sklearn.ensemble", ensemble_stub)


class DummyValidator:
    def __init__(self, *args, **kwargs):
        pass

    def validate_startup(self):
        return SimpleNamespace(is_success=True, errors=[], warnings=[])

    def validate_session_cleanup(self):
        return SimpleNamespace(is_success=True, errors=[], warnings=[])


def test_recursion_guard_on_start_session(monkeypatch, tmp_path):
    import scripts.utilities.unified_session_management_system as usms

    monkeypatch.setattr(
        "session_protocol_validator.SessionProtocolValidator", lambda *a, **k: DummyValidator()
    )
    monkeypatch.setattr(
        "utils.validation_utils.validate_enterprise_environment", lambda: True
    )
    monkeypatch.setattr("utils.validation_utils.detect_zero_byte_files", lambda p: [])
    system = usms.UnifiedSessionManagementSystem(workspace_root=str(tmp_path))
    lock_file = _LOCK_DIR / "_start.lock"
    lock_file.touch()
    with pytest.raises(RuntimeError):
        system.start_session()
    lock_file.unlink(missing_ok=True)


def test_ensure_no_zero_byte_files_detects(tmp_path):
    empty_file = tmp_path / "empty.txt"
    empty_file.touch()
    with pytest.raises(RuntimeError):
        with ensure_no_zero_byte_files(tmp_path, "s1"):
            pass


def test_lifecycle_logging(monkeypatch, tmp_path, caplog):
    import scripts.utilities.unified_session_management_system as usms

    monkeypatch.setattr(
        "session_protocol_validator.SessionProtocolValidator", lambda *a, **k: DummyValidator()
    )
    monkeypatch.setattr(
        "utils.validation_utils.validate_enterprise_environment", lambda: True
    )
    monkeypatch.setattr("utils.validation_utils.detect_zero_byte_files", lambda p: [])
    monkeypatch.setattr(usms, "push_metrics", lambda *a, **k: None)
    monkeypatch.setattr(usms, "log_backup_event", lambda *a, **k: None)
    monkeypatch.setattr(
        usms,
        "UnifiedDisasterRecoverySystem",
        lambda: SimpleNamespace(schedule_backups=lambda: None),
    )
    monkeypatch.setattr(
        usms.UnifiedSessionManagementSystem,
        "_scan_zero_byte_files",
        lambda self: [],
        raising=False,
    )
    monkeypatch.setattr(usms.UnifiedSessionManagementSystem, "_cleanup_zero_byte_files", lambda self: [])
    codex_db = tmp_path / "codex_log.db"
    monkeypatch.setattr(codex_log_db, "CODEX_LOG_DB", codex_db)
    system = usms.UnifiedSessionManagementSystem(workspace_root=str(tmp_path))
    with caplog.at_level(logging.INFO):
        system.start_session()
        system.end_session()
    assert any("Lifecycle start" in r.getMessage() for r in caplog.records)
    assert any("Lifecycle end" in r.getMessage() for r in caplog.records)
    codex_log_db.log_codex_action(system.session_id, "session_complete", "ok")
    assert codex_db.exists()


def test_metrics_and_recovery(monkeypatch, tmp_path):
    import scripts.utilities.unified_session_management_system as usms

    class FailingValidator(DummyValidator):
        def validate_startup(self):  # type: ignore[override]
            return SimpleNamespace(is_success=False, errors=["e"], warnings=[])

    monkeypatch.setattr(
        "session_protocol_validator.SessionProtocolValidator", lambda *a, **k: FailingValidator()
    )
    monkeypatch.setattr(
        "utils.validation_utils.validate_enterprise_environment", lambda: True
    )
    monkeypatch.setattr("utils.validation_utils.detect_zero_byte_files", lambda p: [])

    metrics: dict[str, float] = {}
    monkeypatch.setattr(usms, "push_metrics", lambda m, *, db_path=None, session_id=None: metrics.update(m))
    events: list[str] = []

    def fake_log_backup_event(event, details=None):
        events.append(event)

    monkeypatch.setattr(usms, "log_backup_event", fake_log_backup_event)

    class FakeDRS:
        def schedule_backups(self):
            events.append("scheduled")

    monkeypatch.setattr(usms, "UnifiedDisasterRecoverySystem", FakeDRS)

    class FakeCLR:
        def __init__(self, analytics_db):
            pass

        def log_violation(self, message: str) -> None:  # pragma: no cover - simple record
            events.append("violation")

        def auto_rollback(self, target, backup_path=None) -> None:  # pragma: no cover
            events.append("rollback")

    monkeypatch.setattr(
        "scripts.correction_logger_and_rollback.CorrectionLoggerRollback", FakeCLR
    )
    monkeypatch.setattr(usms, "CorrectionLoggerRollback", FakeCLR)
    monkeypatch.setattr(
        usms.UnifiedSessionManagementSystem,
        "_scan_zero_byte_files",
        lambda self: [],
        raising=False,
    )
    monkeypatch.setattr(usms.UnifiedSessionManagementSystem, "_cleanup_zero_byte_files", lambda self: [])

    system = usms.UnifiedSessionManagementSystem(workspace_root=str(tmp_path))
    assert not system.start_session()
    assert "session_start_failure" in events
    assert "rollback" in events
    assert metrics["validator_success"] == 0.0
    assert metrics["zero_byte_files"] == 0.0


def test_zero_byte_logging(tmp_path, monkeypatch):
    db_file = tmp_path / "analytics.db"
    monkeypatch.setattr(usm, "ANALYTICS_DB", db_file)
    empty = tmp_path / "empty.txt"
    empty.touch()
    with pytest.raises(RuntimeError):
        with ensure_no_zero_byte_files(tmp_path, "s1"):
            pass
    import sqlite3
    with sqlite3.connect(db_file) as conn:
        rows = conn.execute("SELECT path, phase FROM zero_byte_files").fetchall()
    assert rows and rows[0][0].endswith("empty.txt") and rows[0][1] == "before"


def test_finalize_session_records_hash(tmp_path, monkeypatch):
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    (log_dir / "session.log").write_text("hello")
    db_file = tmp_path / "analytics.db"
    monkeypatch.setattr(usm, "ANALYTICS_DB", db_file)
    digest = finalize_session(log_dir)
    import sqlite3
    with sqlite3.connect(db_file) as conn:
        stored = conn.execute("SELECT hash FROM session_hashes").fetchone()[0]
    assert stored == digest


def test_finalize_session_recursion_guard(tmp_path):
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    (log_dir / "session.log").write_text("data")
    lock_file = _LOCK_DIR / "finalize_session.lock"
    lock_file.touch()
    with pytest.raises(RuntimeError):
        finalize_session(log_dir)
    lock_file.unlink(missing_ok=True)


def test_finalize_session_empty_log(tmp_path, monkeypatch):
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    (log_dir / "session.log").touch()
    db_file = tmp_path / "analytics.db"
    monkeypatch.setattr(usm, "ANALYTICS_DB", db_file)
    with pytest.raises(RuntimeError):
        finalize_session(log_dir)
