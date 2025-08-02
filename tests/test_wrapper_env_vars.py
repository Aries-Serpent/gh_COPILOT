import sys
import types
import pytest

from session_protocol_validator import main as spv_main

# Provide minimal stub modules so importing the wrapper does not fail
fake_qiskit = types.ModuleType("qiskit")
fake_qiskit.QuantumCircuit = object
sys.modules.setdefault("qiskit", fake_qiskit)
sys.modules.setdefault("qiskit.circuit", types.ModuleType("circuit"))
fake_library = types.ModuleType("library")
fake_library.QFT = object
sys.modules.setdefault("qiskit.circuit.library", fake_library)
sys.modules.setdefault("qiskit.circuit.library.templates", types.ModuleType("templates"))
fake_qi = types.ModuleType("quantum_info")
fake_qi.Statevector = object
sys.modules.setdefault("qiskit.quantum_info", fake_qi)

from quantum_database_search import cli as qds_cli


def test_session_protocol_requires_env(monkeypatch):
    monkeypatch.delenv("GH_COPILOT_WORKSPACE", raising=False)
    monkeypatch.delenv("GH_COPILOT_BACKUP_ROOT", raising=False)
    with pytest.raises(EnvironmentError):
        spv_main()


def test_quantum_search_requires_env(monkeypatch):
    monkeypatch.delenv("GH_COPILOT_WORKSPACE", raising=False)
    monkeypatch.delenv("GH_COPILOT_BACKUP_ROOT", raising=False)
    with pytest.raises(EnvironmentError):
        qds_cli()
