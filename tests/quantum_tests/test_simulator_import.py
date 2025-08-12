import pytest

pytest.importorskip("qiskit")
pytest.importorskip("qiskit_aer")
from qiskit import QuantumCircuit
from qiskit_aer import Aer


def test_simulator_import_and_run():
    circuit = QuantumCircuit(1, 1)
    circuit.h(0)
    circuit.measure(0, 0)
    backend = Aer.get_backend("aer_simulator")
    result = backend.run(circuit, shots=1).result()
    counts = result.get_counts()
    assert counts
