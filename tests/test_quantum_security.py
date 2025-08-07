from quantum.quantum_compliance_engine import QISKIT_AVAILABLE
from security.compliance_checker import ComplianceChecker


def test_quantum_security_interop() -> None:
    """Quantum components should coexist with security checks."""
    checker = ComplianceChecker()
    assert isinstance(QISKIT_AVAILABLE, bool)
    assert isinstance(checker.policy, dict)

