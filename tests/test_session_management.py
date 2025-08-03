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
    system = usms.UnifiedSessionManagementSystem(workspace_root=str(tmp_path))
    with caplog.at_level(logging.INFO):
        system.start_session()
        system.end_session()
    assert any("Lifecycle start" in r.getMessage() for r in caplog.records)
    assert any("Lifecycle end" in r.getMessage() for r in caplog.records)
