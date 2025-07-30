import types
import pytest
from quantum.orchestration import executor as qexec
from quantum.orchestration.executor import QuantumExecutor
from quantum.orchestration.registry import register_algorithm
from quantum.algorithms.base import QuantumAlgorithmBase

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

@pytest.mark.skipif(not hasattr(qexec, "IBMProvider"), reason="IBMProvider unavailable")
def test_hardware_backend(monkeypatch):
    monkeypatch.setattr(qexec, "IBMProvider", lambda: MockProvider())
    exec_ = QuantumExecutor(use_hardware=True, backend_name="mock")
    result = exec_.execute_algorithm("dummy_test")
    assert result["success"]
    assert exec_.use_hardware


@pytest.mark.skipif(not hasattr(qexec, "IBMProvider"), reason="IBMProvider unavailable")
def test_hardware_fallback(monkeypatch):
    def bad_provider():
        raise RuntimeError("no access")
    monkeypatch.setattr(qexec, "IBMProvider", bad_provider)
    exec_ = QuantumExecutor(use_hardware=True, backend_name="mock")
    assert exec_.use_hardware is False
    result = exec_.execute_algorithm("dummy_test")
    assert result["success"]

