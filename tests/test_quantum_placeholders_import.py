"""Tests for quantum placeholder modules."""

import pytest

from scripts.quantum_placeholders import quantum_placeholder_algorithm


def test_simulate_quantum_process_round_trip():
    data = [1, 2, 3]
    assert quantum_placeholder_algorithm.simulate_quantum_process(data) == data


def test_placeholder_raises_in_production(monkeypatch):
    monkeypatch.setenv("GH_COPILOT_ENV", "production")
    with pytest.raises(RuntimeError, match="should not be used in production"):
        quantum_placeholder_algorithm.simulate_quantum_process([1])
