import pytest
from contextlib import contextmanager
from pathlib import Path

from security.compliance_checker import ComplianceChecker, ComplianceError


def test_run_checks_pass(monkeypatch):
    checker = ComplianceChecker(threshold=0)
    monkeypatch.setattr(
        checker, "validate_environment", lambda: {"compliance_status": "FULL"}
    )
    assert checker.run_checks() is True


def test_run_checks_threshold(monkeypatch):
    checker = ComplianceChecker(threshold=0)
    monkeypatch.setattr(
        checker, "validate_environment", lambda: {"compliance_status": "FULL"}
    )
    checker.register_rule(lambda: False)
    with pytest.raises(ComplianceError):
        checker.run_checks()


def test_validate_operation_logs(monkeypatch):
    monkeypatch.setattr(
        "security.compliance_checker.validate_enterprise_operation",
        lambda **kwargs: False,
    )
    checker = ComplianceChecker()
    monkeypatch.setattr(
        checker, "validate_environment", lambda: {"compliance_status": "FULL"}
    )
    assert checker.validate_operation(path="/tmp") is False
    assert "operation_policy_violation" in checker.events


def test_pre_deployment_validation_schedules_backup(monkeypatch, tmp_path: Path) -> None:
    checker = ComplianceChecker(threshold=0)
    monkeypatch.setattr(checker, "run_checks", lambda: True)

    state: dict[str, str] = {}

    class DummySystem:
        def __init__(self, workspace_path: str) -> None:
            pass

        def schedule_backups(self) -> None:
            state["backup"] = "done"

    @contextmanager
    def fake_cm(_path: Path):
        yield

    monkeypatch.setattr(
        "security.compliance_checker.UnifiedDisasterRecoverySystem", DummySystem
    )
    monkeypatch.setattr(
        "security.compliance_checker.ensure_no_zero_byte_files", fake_cm
    )
    monkeypatch.setattr(
        "security.compliance_checker.prevent_recursion", lambda f: f
    )
    monkeypatch.setattr(
        "security.compliance_checker.log_backup_event", lambda e, details=None: state.setdefault("event", e)
    )

    assert checker.pre_deployment_validation(workspace=tmp_path) is True
    assert state.get("backup") == "done"
    assert state.get("event") == "pre_deployment_backup"

