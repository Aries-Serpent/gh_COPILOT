"""Tests for advanced quantum algorithms."""

import pytest

from ghc_quantum.advanced_quantum_algorithms import (
    QISKIT_AVAILABLE,
    grover_search_qiskit,
    phase_estimation_qiskit,
)

pytestmark = pytest.mark.skipif(not QISKIT_AVAILABLE, reason="qiskit not available")


def test_grover_search_qiskit():
    assert grover_search_qiskit("11") == "11"


def test_phase_estimation_qiskit():
    estimate = phase_estimation_qiskit(0.125, precision=3)
    assert abs(estimate - 0.125) < 0.01
