import pytest

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

