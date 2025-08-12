from qiskit import QuantumCircuit

from ghc_quantum.utils.backend_provider import get_backend


def test_qiskit_simulator_backend():
    backend = get_backend()
    assert backend.name == 'qasm_simulator'
    circuit = QuantumCircuit(1, 1)
    assert circuit.num_qubits == 1
