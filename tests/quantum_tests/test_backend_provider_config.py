import pytest

from ghc_quantum.utils import backend_provider


class DummyBackend:
    pass


class DummyProvider:
    def get_backend(self, name):
        return DummyBackend()


@pytest.mark.skipif(backend_provider.Aer is None, reason="Qiskit not available")
def test_env_var_enables_hardware(monkeypatch):
    monkeypatch.setenv("QUANTUM_USE_HARDWARE", "1")
    monkeypatch.setattr(backend_provider, "IBMProvider", lambda: DummyProvider())
    backend = backend_provider.get_backend()
    assert isinstance(backend, DummyBackend)


@pytest.mark.skipif(backend_provider.Aer is None, reason="Qiskit not available")
def test_env_var_defaults_to_simulator(monkeypatch):
    monkeypatch.delenv("QUANTUM_USE_HARDWARE", raising=False)
    monkeypatch.setattr(backend_provider, "IBMProvider", lambda: DummyProvider())
    backend = backend_provider.get_backend()
    from qiskit_aer import Aer as _Aer

    assert backend.name == _Aer.get_backend("qasm_simulator").name

