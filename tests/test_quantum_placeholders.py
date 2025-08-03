"""Import tests for quantum placeholder modules."""

import importlib


def test_quantum_placeholders_importable():
    modules = [
        "scripts.quantum_placeholders.quantum_annealing",
        "scripts.quantum_placeholders.quantum_superposition_search",
        "scripts.quantum_placeholders.quantum_entanglement_correction",
        "scripts.quantum_placeholders.quantum_placeholder_algorithm",
    ]
    for name in modules:
        mod = importlib.import_module(name)
        assert mod is not None

