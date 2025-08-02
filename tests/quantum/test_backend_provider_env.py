import pytest

from quantum.utils import backend_provider


class DummyBackend:
    pass


class DummyProvider:
    def __init__(self, token=None):
        if token != "token":
            raise RuntimeError("missing token")

    def get_backend(self, name):
        return DummyBackend()


@pytest.mark.skipif(backend_provider.Aer is None, reason="Qiskit not available")
def test_env_override_enables_hardware(monkeypatch):
    monkeypatch.setenv("QISKIT_IBM_TOKEN", "token")
    monkeypatch.setenv("QUANTUM_USE_HARDWARE", "1")
    monkeypatch.setattr(backend_provider, "IBMProvider", DummyProvider)
    backend = backend_provider.get_backend("dummy")
    assert isinstance(backend, DummyBackend)


@pytest.mark.skipif(backend_provider.Aer is None, reason="Qiskit not available")
def test_env_override_disables_hardware(monkeypatch):
    monkeypatch.setenv("QISKIT_IBM_TOKEN", "token")
    monkeypatch.setenv("QUANTUM_USE_HARDWARE", "0")
    monkeypatch.setattr(backend_provider, "IBMProvider", DummyProvider)
    backend = backend_provider.get_backend("dummy")
    from qiskit import Aer as _Aer

    assert backend == _Aer.get_backend("qasm_simulator")
