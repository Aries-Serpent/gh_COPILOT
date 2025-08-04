import pytest

from security.compliance_checker import ComplianceChecker, ComplianceError


def test_run_checks_pass(monkeypatch):
    checker = ComplianceChecker(threshold=0)
    monkeypatch.setattr(checker, "validate_environment", lambda: {"compliance_status": "FULL"})
    assert checker.run_checks() is True


def test_run_checks_threshold(monkeypatch):
    checker = ComplianceChecker(threshold=0)
    monkeypatch.setattr(checker, "validate_environment", lambda: {"compliance_status": "FULL"})
    checker.register_rule(lambda: False)
    with pytest.raises(ComplianceError):
        checker.run_checks()


def test_validate_operation_logs(monkeypatch):
    monkeypatch.setattr(
        "security.compliance_checker.validate_enterprise_operation",
        lambda **kwargs: False,
    )
    checker = ComplianceChecker()
    monkeypatch.setattr(checker, "validate_environment", lambda: {"compliance_status": "FULL"})
    assert checker.validate_operation(path="/tmp") is False
    assert "operation_policy_violation" in checker.events


def test_run_checks_triggers_backup(monkeypatch, tmp_path):
    events = []
    workspace = tmp_path / "ws"
    workspace.mkdir()
    backup_root = tmp_path / "backup"
    backup_root.mkdir()
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(backup_root))

    class DummySystem:
        def __init__(self, *_):
            pass

        def schedule_backups(self):
            return backup_root / "b.txt"

    monkeypatch.setattr(
        "unified_disaster_recovery_system.UnifiedDisasterRecoverySystem",
        DummySystem,
    )
    monkeypatch.setattr(
        "unified_disaster_recovery_system.log_backup_event",
        lambda event, details=None: events.append((event, details)),
    )

    checker = ComplianceChecker(threshold=0)
    monkeypatch.setattr(checker, "validate_environment", lambda: {"compliance_status": "NONE"})

    with pytest.raises(ComplianceError):
        checker.run_checks()

    assert any(evt[0] == "compliance_violation" for evt in events)
