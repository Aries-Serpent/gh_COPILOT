"""Smoke tests for the simulator backend provider."""

import pytest

pytest.importorskip("qiskit")

from quantum.utils import backend_provider


def test_simulator_backend_available():
    backend = backend_provider.get_backend(use_hardware=False)
    assert backend is not None

