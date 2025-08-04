#!/usr/bin/env python3

from types import SimpleNamespace

from scripts.utilities.unified_session_management_system import (
    UnifiedSessionManagementSystem,
)
from session_protocol_validator import SessionProtocolValidator


def test_startup_detects_zero_byte(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    zero_file = tmp_path / "a.py"
    zero_file.write_text("")
    validator = SessionProtocolValidator()
    assert not validator.validate_startup().is_success


def test_unified_session_start_fails_with_zero_byte(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(tmp_path / "backups"))
    zero_file = tmp_path / "b.py"
    zero_file.write_text("")
    import scripts.utilities.unified_session_management_system as usms
    monkeypatch.setattr(usms, "UnifiedDisasterRecoverySystem", lambda: SimpleNamespace(schedule_backups=lambda: None))
    monkeypatch.setattr(usms, "log_backup_event", lambda *a, **k: None)
    mgr = UnifiedSessionManagementSystem()
    assert not mgr.start_session()


def test_unicode_workspace_path(tmp_path, monkeypatch):
    unicode_dir = tmp_path / "路径"
    unicode_dir.mkdir()
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(unicode_dir))
    validator = SessionProtocolValidator()
    assert validator.validate_startup().is_success


def test_comprehensive_validation_fails(monkeypatch):
    monkeypatch.setenv("MY_PASSWORD", "secret")
    monkeypatch.setenv("SESSION_TIMEOUT", "30")
    monkeypatch.setenv("USE_HTTPS", "0")
    validator = SessionProtocolValidator()
    result = validator.validate_comprehensive_session()
    assert result.is_failure


def test_unified_session_end_detects_zero_byte(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(tmp_path / "backups"))
    import scripts.utilities.unified_session_management_system as usms
    monkeypatch.setattr(usms, "UnifiedDisasterRecoverySystem", lambda: SimpleNamespace(schedule_backups=lambda: None))
    monkeypatch.setattr(usms, "log_backup_event", lambda *a, **k: None)
    mgr = UnifiedSessionManagementSystem()
    mgr.start_session()
    zero_file = tmp_path / "end.py"
    zero_file.write_text("")
    assert not mgr.end_session()
