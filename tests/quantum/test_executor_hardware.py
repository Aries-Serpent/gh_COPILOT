import pytest
from quantum.orchestration.executor import QuantumExecutor
from quantum.orchestration.registry import register_algorithm
from quantum.algorithms.base import QuantumAlgorithmBase
from quantum.utils import backend_provider

pytestmark = pytest.mark.skipif(
    backend_provider.Aer is None, reason="Qiskit not available"
)


class DummyAlgo(QuantumAlgorithmBase):
    def __init__(self):
        super().__init__(None)
        self.backend = None
        self.flag = False

    def set_backend(self, backend, use_hardware: bool = False):
        self.backend = backend
        self.flag = use_hardware

    def get_algorithm_name(self) -> str:
        return "Dummy"

    def execute_algorithm(self) -> bool:
        return True


register_algorithm("dummy_test", DummyAlgo)


class MockBackend:
    def run(self, circ):
        class Result:
            def result(self):
                return None

        return Result()


class MockProvider:
    def get_backend(self, name):
        return MockBackend()


def test_missing_token_fallback(monkeypatch):
    monkeypatch.setattr(backend_provider, "_load_provider", lambda: None)
    exec_ = QuantumExecutor(use_hardware=True, backend_name="mock")
    assert exec_.use_hardware is False


def test_hardware_execution(monkeypatch):
    backend = MockBackend()

    class Provider:
        def get_backend(self, name):
            return backend

    monkeypatch.setattr(backend_provider, "_load_provider", lambda: Provider())
    exec_ = QuantumExecutor(use_hardware=True, backend_name="mock")
    result = exec_.execute_algorithm("dummy_test")
    assert result["success"]
    assert exec_.use_hardware
