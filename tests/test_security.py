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

