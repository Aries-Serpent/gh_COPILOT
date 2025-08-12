import importlib.util
import pytest

from quantum.providers.ionq_provider import IonQProvider
from quantum.framework.backend import QuantumBackend


def test_ionq_provider_unavailable_without_env(monkeypatch):
    monkeypatch.delenv("IONQ_API_KEY", raising=False)
    provider = IonQProvider()
    assert provider.is_available() is False


@pytest.mark.skipif(
    importlib.util.find_spec("qiskit_ionq") is None,
    reason="IonQ SDK not available",
)
def test_get_backend_returns_quantum_backend(monkeypatch):
    monkeypatch.setenv("IONQ_API_KEY", "dummy")
    provider = IonQProvider()
    assert provider.is_available()
    backend = provider.get_backend()
    assert isinstance(backend, QuantumBackend)
