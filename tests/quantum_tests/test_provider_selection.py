from __future__ import annotations

from quantum.framework import QuantumExecutor, SimulatorBackend
from quantum.providers import ibm_provider
from quantum.framework.backend import QuantumBackend


class _DummyBackend(QuantumBackend):
    def run(self, circuit, **kwargs):  # pragma: no cover - simple stub
        return {"dummy": True}


def test_env_selects_simulator(monkeypatch):
    monkeypatch.setenv("QUANTUM_PROVIDER", "simulator")
    exec_ = QuantumExecutor()
    assert isinstance(exec_.backend, SimulatorBackend)
    assert exec_.use_hardware is False


def test_env_requests_ibm_but_falls_back(monkeypatch):
    monkeypatch.setenv("QUANTUM_PROVIDER", "ibm")
    monkeypatch.setattr(
        ibm_provider.IBMBackendProvider, "is_available", lambda self: False
    )
    exec_ = QuantumExecutor()
    assert isinstance(exec_.backend, SimulatorBackend)
    assert exec_.use_hardware is False


def test_ibm_selected_when_available(monkeypatch):
    monkeypatch.setenv("QUANTUM_PROVIDER", "ibm")

    def _avail(self):
        return True

    def _get(self):
        return _DummyBackend()

    monkeypatch.setattr(ibm_provider.IBMBackendProvider, "is_available", _avail)
    monkeypatch.setattr(ibm_provider.IBMBackendProvider, "get_backend", _get)

    exec_ = QuantumExecutor()
    assert isinstance(exec_.backend, _DummyBackend)
    assert exec_.use_hardware is True


def test_feature_flag_disables_providers(monkeypatch):
    monkeypatch.setenv("QUANTUM_PROVIDER", "ibm")
    monkeypatch.setenv("ENABLE_QUANTUM_PROVIDERS", "0")
    monkeypatch.setattr(ibm_provider.IBMBackendProvider, "is_available", lambda self: True)
    monkeypatch.setattr(ibm_provider.IBMBackendProvider, "get_backend", lambda self: _DummyBackend())
    exec_ = QuantumExecutor()
    assert isinstance(exec_.backend, SimulatorBackend)
    assert exec_.use_hardware is False

