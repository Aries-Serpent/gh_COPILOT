"""Tests for quantum entry point gating and reproducibility."""

import pytest

from quantum.interfaces.quantum_api import execute_quantum_task


def test_quantum_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    """Feature flag prevents execution when disabled."""

    monkeypatch.setenv("QISKIT_IBM_TOKEN", "token")
    monkeypatch.setenv("QUANTUM_ENABLED", "0")

    with pytest.raises(RuntimeError):
        execute_quantum_task({"circuit": "x"})


def test_reproducible_results(monkeypatch: pytest.MonkeyPatch) -> None:
    """Simulator returns deterministic values for the same seed."""

    monkeypatch.setenv("QISKIT_IBM_TOKEN", "token")
    monkeypatch.setenv("QUANTUM_ENABLED", "1")

    task = {"circuit": "x", "seed": 42}
    r1 = execute_quantum_task(task)
    r2 = execute_quantum_task(task)

    assert r1["result"]["value"] == r2["result"]["value"]


def test_reproducible_changes_with_seed(monkeypatch: pytest.MonkeyPatch) -> None:
    """Different seeds should yield different simulated values."""

    monkeypatch.setenv("QISKIT_IBM_TOKEN", "token")
    monkeypatch.setenv("QUANTUM_ENABLED", "1")

    task1 = {"circuit": "x", "seed": 1}
    task2 = {"circuit": "x", "seed": 2}
    r1 = execute_quantum_task(task1)
    r2 = execute_quantum_task(task2)

    assert r1["result"]["value"] != r2["result"]["value"]

