import pytest

from quantum.orchestration.executor import QuantumExecutor
from quantum.orchestration import executor as qexec


@pytest.mark.skipif(
    (not qexec.QISKIT_AVAILABLE) or (qexec.Aer is None),
    reason="Qiskit not available",
)
def test_teleportation_runs():
    exec_ = QuantumExecutor()
    result = exec_.execute_algorithm("teleportation")
    assert result["success"]
