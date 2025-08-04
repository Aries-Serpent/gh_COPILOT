"""Import tests for quantum placeholder modules."""

import importlib
from importlib import import_module
from typing import Any, Sequence

import pytest


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


@pytest.mark.parametrize(
    "module, func, args",
    [
        (
            "scripts.quantum_placeholders.quantum_placeholder_algorithm",
            "simulate_quantum_process",
            ([1],),
        ),
        (
            "scripts.quantum_placeholders.quantum_annealing",
            "run_quantum_annealing",
            ([1.0],),
        ),
        (
            "scripts.quantum_placeholders.quantum_superposition_search",
            "run_quantum_superposition_search",
            (1,),
        ),
        (
            "scripts.quantum_placeholders.quantum_entanglement_correction",
            "run_entanglement_correction",
            tuple(),
        ),
    ],
)
def test_placeholders_error_in_production(
    monkeypatch, module: str, func: str, args: Sequence[Any]
) -> None:
    monkeypatch.setenv("GH_COPILOT_ENV", "production")
    mod = import_module(module)
    with pytest.raises(RuntimeError, match="should not be used in production"):
        getattr(mod, func)(*args)

