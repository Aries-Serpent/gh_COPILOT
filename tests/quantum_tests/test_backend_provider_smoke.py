"""Ensure backend_provider falls back to simulator and Qiskit is available."""

from qiskit import QuantumCircuit

from ghc_quantum.utils.backend_provider import get_backend


def test_backend_provider_simulator() -> None:
    """Verify the simulator backend is returned by default."""
    QuantumCircuit(1)
    backend = get_backend()
    assert backend.name == "qasm_simulator"

