from security.compliance_checker import ComplianceChecker


def test_compliance_policy_loaded() -> None:
    """ComplianceChecker should load the security policy."""
    checker = ComplianceChecker()
    assert isinstance(checker.policy, dict)


def test_environment_validation_returns_dict() -> None:
    """validate_environment should return a result dictionary."""
    checker = ComplianceChecker()
    result = checker.validate_environment()
    assert isinstance(result, dict)


def test_policy_contains_rules_key() -> None:
    """Security policy should define security controls."""
    checker = ComplianceChecker()
    assert "security_controls" in checker.policy

