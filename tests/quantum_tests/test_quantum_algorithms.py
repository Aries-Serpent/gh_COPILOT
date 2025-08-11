"""Tests for basic quantum algorithm helpers."""

from quantum_algorithms_functional import run_quantum_fourier_transform


def test_qft_returns_statevector() -> None:
    """Running the QFT on a simple state returns the correct length."""
    result = run_quantum_fourier_transform([1, 0])
    assert len(result) == 2

