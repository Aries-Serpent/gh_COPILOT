from security.compliance_checker import ComplianceChecker


def test_compliance_policy_loaded() -> None:
    """ComplianceChecker should load the security policy."""
    checker = ComplianceChecker()
    assert isinstance(checker.policy, dict)

