import pytest

qiskit = pytest.importorskip("qiskit")
from qiskit import QuantumCircuit


def test_simulator_import():
    try:
        from qiskit import Aer
    except Exception:  # pragma: no cover - environment-dependent
        pytest.skip("Qiskit Aer is not available")

    qc = QuantumCircuit(1, 1)
    qc.x(0)
    qc.measure(0, 0)

    backend = Aer.get_backend("qasm_simulator")
    result = backend.run(qc, shots=1).result()
    counts = result.get_counts()
    assert counts == {"1": 1}
