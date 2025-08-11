import pytest

from scripts.quantum_placeholders.quantum_annealing import run_quantum_annealing
from scripts.quantum_placeholders.quantum_superposition_search import run_quantum_superposition_search
from scripts.quantum_placeholders.quantum_entanglement_correction import run_entanglement_correction


def test_quantum_annealing_simulation():
    try:
        counts = run_quantum_annealing([1, -1])
    except FileNotFoundError:  # pragma: no cover - optional placeholder data
        pytest.skip("annealing data unavailable")
    assert counts == {"01": 1024}


def test_superposition_search_probabilities():
    try:
        probs = run_quantum_superposition_search(2)
    except FileNotFoundError:  # pragma: no cover - optional placeholder data
        pytest.skip("superposition data unavailable")
    assert pytest.approx(sum(probs.values()), rel=1e-9) == 1.0
    assert all(pytest.approx(p, rel=1e-9) == 0.25 for p in probs.values())


def test_entanglement_correction():
    try:
        counts = run_entanglement_correction()
    except FileNotFoundError:  # pragma: no cover - optional placeholder data
        pytest.skip("entanglement data unavailable")
    assert counts == {"00": 1024}


def test_hardware_flag_graceful_fallback():
    try:
        counts = run_quantum_annealing([1], use_hardware=True)
    except FileNotFoundError:  # pragma: no cover - optional placeholder data
        pytest.skip("annealing data unavailable")
    # Should still return simulation results even without hardware access
    assert sum(counts.values()) == 1024
