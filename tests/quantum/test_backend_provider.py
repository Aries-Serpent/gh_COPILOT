import pytest

from quantum.utils import backend_provider


class DummyBackend:
    pass


class DummyProvider:
    def get_backend(self, name):
        return DummyBackend()


@pytest.mark.skipif(backend_provider.Aer is None, reason="Qiskit not available")
def test_get_backend_uses_provider(monkeypatch):
    monkeypatch.setattr(backend_provider, "IBMProvider", lambda: DummyProvider())
    backend = backend_provider.get_backend("dummy", use_hardware=True)
    assert isinstance(backend, DummyBackend)


@pytest.mark.skipif(backend_provider.Aer is None, reason="Qiskit not available")
def test_get_backend_falls_back(monkeypatch):
    monkeypatch.setattr(backend_provider, "IBMProvider", None)
    backend = backend_provider.get_backend(use_hardware=True)
    assert backend is not None
