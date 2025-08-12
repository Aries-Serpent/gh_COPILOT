from ghc_quantum.quantum_compliance_engine import QISKIT_AVAILABLE
from security.compliance_checker import ComplianceChecker


def test_quantum_security_interop() -> None:
    """Quantum components should coexist with security checks."""
    checker = ComplianceChecker()
    assert isinstance(QISKIT_AVAILABLE, bool)
    assert isinstance(checker.policy, dict)


def test_validate_operation_returns_bool() -> None:
    """validate_operation should return a boolean result."""
    checker = ComplianceChecker()
    assert isinstance(checker.validate_operation(command="echo"), bool)


def test_validate_environment_contains_status() -> None:
    """validate_environment should include a compliance status."""
    result = ComplianceChecker().validate_environment()
    assert "compliance_status" in result

