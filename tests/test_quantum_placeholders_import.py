"""Tests for quantum placeholder modules."""

from scripts.quantum_placeholders import quantum_placeholder_algorithm


def test_simulate_quantum_process_round_trip():
    data = [1, 2, 3]
    assert quantum_placeholder_algorithm.simulate_quantum_process(data) == data
