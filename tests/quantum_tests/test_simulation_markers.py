import logging
import pytest
import shutil

from quantum.utils.backend_provider import get_backend
from quantum.algorithms.hardware_aware import HardwareAwareAlgorithm
from quantum.quantum_compliance_engine import QuantumComplianceEngine, WORKSPACE_ROOT
import quantum.quantum_compliance_engine as qce


def test_get_backend_warns_when_aer_missing(monkeypatch):
    """get_backend raises when Qiskit's Aer is absent."""
    monkeypatch.setattr("quantum.utils.backend_provider.Aer", None)
    # Combine: use the most informative ImportError message ("mock" preferred for clarity)
    monkeypatch.setattr(
        "quantum.utils.backend_provider._AER_IMPORT_ERROR",
        ImportError("mock"),
        raising=False,
    )
    with pytest.raises(ImportError):
        get_backend()


def test_hardware_aware_algorithm_warns_no_backend(monkeypatch, caplog):
    """HardwareAwareAlgorithm emits a warning when no backend is available."""
    monkeypatch.setattr(
        "quantum.algorithms.hardware_aware.get_backend", lambda **_: None
    )
    algo = HardwareAwareAlgorithm(use_hardware=True)
    with caplog.at_level(logging.WARNING):
        result = algo.execute_algorithm()
    assert result is False
    assert any(
        "No backend available" in rec.message or "Qiskit not available" in rec.message
        for rec in caplog.records
    )


@pytest.mark.skip("requires full quantum compliance environment")
def test_compliance_engine_warns_without_qiskit(monkeypatch, caplog):
    """_quantum_field_redundancy warns and returns classical score when Qiskit is missing."""
    # Use the newer import style and also handle workspace cleanup
    monkeypatch.setattr(qce, "validate_no_recursive_folders", lambda: None)
    shutil.rmtree(WORKSPACE_ROOT / "tmp", ignore_errors=True)
    engine = QuantumComplianceEngine()
    monkeypatch.setattr("quantum.quantum_compliance_engine.QISKIT_AVAILABLE", False)
    with caplog.at_level(logging.WARNING):
        with pytest.raises(RuntimeError):
            engine._quantum_field_redundancy(0.5)
    assert any("Qiskit not available" in rec.message for rec in caplog.records)