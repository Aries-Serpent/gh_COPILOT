import pytest

from quantum.providers.ionq_provider import IonQProvider
from quantum.framework.backend import QuantumBackend


@pytest.mark.skipif(not IonQProvider().is_available(), reason="IonQ SDK not available")
def test_get_backend_returns_quantum_backend():
    provider = IonQProvider()
    backend = provider.get_backend()
    assert isinstance(backend, QuantumBackend)
