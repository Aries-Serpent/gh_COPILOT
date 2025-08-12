"""Tests for VQE and phase estimation demos with hardware fallback."""

import pytest

from ghc_quantum.algorithms import phase_estimation_demo, vqe_demo
from ghc_quantum.utils import backend_provider


class _FailingProvider:
    def __init__(self, *args, **kwargs):  # pragma: no cover - dummy
        raise RuntimeError("no provider")


def test_vqe_demo_falls_back(monkeypatch):
    monkeypatch.setattr(backend_provider, "IBMProvider", _FailingProvider)
    sim = vqe_demo.run_vqe_demo(use_hardware=False)
    fallback = vqe_demo.run_vqe_demo(use_hardware=True)
    assert sim is not None and pytest.approx(sim, rel=1e-6) == fallback


def test_phase_estimation_demo_falls_back(monkeypatch):
    monkeypatch.setattr(backend_provider, "IBMProvider", _FailingProvider)
    sim = phase_estimation_demo.run_phase_estimation_demo(use_hardware=False)
    fallback = phase_estimation_demo.run_phase_estimation_demo(use_hardware=True)
    assert sim == fallback
    assert sim in {"001", "100"}  # bit order may vary

