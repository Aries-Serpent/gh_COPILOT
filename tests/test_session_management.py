import logging
from types import SimpleNamespace

import pytest

from unified_session_management_system import ensure_no_zero_byte_files
from utils.validation_utils import _LOCK_DIR


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
        with ensure_no_zero_byte_files(tmp_path):
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
    system = usms.UnifiedSessionManagementSystem(workspace_root=str(tmp_path))
    with caplog.at_level(logging.INFO):
        system.start_session()
        system.end_session()
    assert any("Lifecycle start" in r.getMessage() for r in caplog.records)
    assert any("Lifecycle end" in r.getMessage() for r in caplog.records)


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

    system = usms.UnifiedSessionManagementSystem(workspace_root=str(tmp_path))
    assert not system.start_session()
    assert "session_start_failure" in events
    assert "rollback" in events
    assert metrics["validator_success"] == 0.0
    assert metrics["zero_byte_files"] == 0.0
