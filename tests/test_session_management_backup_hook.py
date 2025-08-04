"""Verify session management triggers disaster recovery backups."""

from __future__ import annotations

from types import SimpleNamespace

import scripts.utilities.unified_session_management_system as usms


class DummyValidator:
    def validate_startup(self):
        return SimpleNamespace(is_success=True, errors=[], warnings=[])

    def validate_session_cleanup(self):
        return SimpleNamespace(is_success=True, errors=[], warnings=[])


def test_session_start_triggers_backup(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "session_protocol_validator.SessionProtocolValidator", lambda *a, **k: DummyValidator()
    )
    monkeypatch.setattr(
        "utils.validation_utils.validate_enterprise_environment", lambda: True
    )
    monkeypatch.setattr(
        "utils.validation_utils.detect_zero_byte_files", lambda p: []
    )

    called: list[bool] = []

    class DummyOrchestrator:
        def __init__(self, *a, **k):
            pass

        def run_backup_cycle(self):
            called.append(True)
            return tmp_path / "dummy"

    monkeypatch.setattr(usms, "DisasterRecoveryOrchestrator", DummyOrchestrator)

    system = usms.UnifiedSessionManagementSystem(workspace_root=str(tmp_path))
    system.start_session()

    assert called


__all__ = ["test_session_start_triggers_backup"]

