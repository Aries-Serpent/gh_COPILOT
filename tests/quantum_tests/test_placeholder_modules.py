"""Deterministic behavior checks for quantum placeholder modules."""

from __future__ import annotations

from scripts.quantum_placeholders import (
    quantum_annealing,
    quantum_entanglement_correction,
    quantum_placeholder_algorithm,
    quantum_superposition_search,
)


def test_placeholder_algorithm_deterministic() -> None:
    data = [1, 2, 3]
    assert quantum_placeholder_algorithm.simulate_quantum_process(data) == data


def test_quantum_annealing_deterministic(monkeypatch) -> None:
    monkeypatch.setattr(quantum_annealing, "QISKIT_AVAILABLE", False)
    monkeypatch.setattr(quantum_annealing, "log_quantum_audit", lambda *a, **k: None)
    assert quantum_annealing.run_quantum_annealing([0.5, -0.5]) == {"01": 1024}


def test_entanglement_correction_deterministic(monkeypatch) -> None:
    monkeypatch.setattr(quantum_entanglement_correction, "QISKIT_AVAILABLE", False)
    monkeypatch.setattr(
        quantum_entanglement_correction, "log_quantum_audit", lambda *a, **k: None
    )
    assert quantum_entanglement_correction.run_entanglement_correction() == {
        "00": 1024
    }


def test_superposition_search_deterministic(monkeypatch) -> None:
    monkeypatch.setattr(quantum_superposition_search, "QISKIT_AVAILABLE", False)
    monkeypatch.setattr(
        quantum_superposition_search, "log_quantum_audit", lambda *a, **k: None
    )
    expected = {"00": 0.25, "01": 0.25, "10": 0.25, "11": 0.25}
    assert quantum_superposition_search.run_quantum_superposition_search(2) == expected

