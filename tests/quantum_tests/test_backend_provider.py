import pytest

from ghc_quantum.utils import backend_provider


class DummyBackend:
    pass


class DummyProvider:
    def __init__(self, token=None):
        self.token = token

    def get_backend(self, name):
        return DummyBackend()


@pytest.mark.skipif(backend_provider.Aer is None, reason="Qiskit not available")
def test_get_backend_uses_provider(monkeypatch):
    monkeypatch.setattr(backend_provider, "IBMProvider", lambda token=None: DummyProvider(token))
    backend = backend_provider.get_backend("dummy", use_hardware=True, token="abc")
    assert isinstance(backend, DummyBackend)


@pytest.mark.skipif(backend_provider.Aer is None, reason="Qiskit not available")
def test_get_backend_token_forwarded(monkeypatch):
    captured = {}

    def provider_factory(token=None):
        captured["token"] = token
        return DummyProvider(token)

    monkeypatch.setattr(backend_provider, "IBMProvider", provider_factory)
    backend_provider.get_backend("dummy", use_hardware=True, token="secret")
    assert captured["token"] == "secret"


@pytest.mark.skipif(backend_provider.Aer is None, reason="Qiskit not available")
def test_get_backend_falls_back(monkeypatch):
    monkeypatch.setattr(backend_provider, "IBMProvider", None)
    backend = backend_provider.get_backend(use_hardware=True)
    assert backend is not None
