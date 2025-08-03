import importlib


def test_placeholder_modules_importable():
    modules = [
        "scripts.quantum_placeholders.quantum_annealing",
        "scripts.quantum_placeholders.quantum_superposition_search",
        "scripts.quantum_placeholders.quantum_entanglement_correction",
    ]
    for name in modules:
        mod = importlib.import_module(name)
        assert mod is not None
