import importlib


def test_qiskit_and_qml_import():
    qiskit = importlib.import_module("qiskit")
    qml = importlib.import_module("qiskit_machine_learning")

    assert hasattr(qiskit, "QuantumCircuit")
    assert hasattr(qml, "__version__")
