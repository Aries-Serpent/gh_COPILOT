import pytest

from scripts.quantum_placeholders.quantum_annealing import run_quantum_annealing
from scripts.quantum_placeholders.quantum_superposition_search import run_quantum_superposition_search
from scripts.quantum_placeholders.quantum_entanglement_correction import run_entanglement_correction


def test_quantum_annealing_simulation():
    counts = run_quantum_annealing([1, -1])
    assert counts == {"01": 1024}


def test_superposition_search_probabilities():
    probs = run_quantum_superposition_search(2)
    assert pytest.approx(sum(probs.values()), rel=1e-9) == 1.0
    assert all(pytest.approx(p, rel=1e-9) == 0.25 for p in probs.values())


def test_entanglement_correction():
    counts = run_entanglement_correction()
    assert counts == {"00": 1024}


def test_hardware_flag_graceful_fallback():
    counts = run_quantum_annealing([1], use_hardware=True)
    # Should still return simulation results even without hardware access
    assert sum(counts.values()) == 1024
