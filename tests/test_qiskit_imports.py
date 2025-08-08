#!/usr/bin/env python3
import importlib
<<<<<<< HEAD
=======
import logging
>>>>>>> 072d1e7e (Nuclear fix: Complete repository rebuild - 2025-07-14 22:31:03)


def test_qiskit_and_qml_import():
    qiskit = importlib.import_module("qiskit")
    qml = importlib.import_module("qiskit_machine_learning")

    assert hasattr(qiskit, "QuantumCircuit")
    assert hasattr(qml, "__version__")
