import sys
import types
from pathlib import Path
import pytest

from scripts.session.session_protocol_validator import main as spv_main

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

_quantum_pkg = types.ModuleType("quantum")
_quantum_pkg.__path__ = [str(Path(__file__).resolve().parents[1] / "quantum")]
sys.modules.setdefault("quantum", _quantum_pkg)
algorithms_stub = types.ModuleType("quantum.algorithms")
algorithms_stub.QuantumEncryptedCommunication = type(
    "QuantumEncryptedCommunication",
    (),
    {"encrypt_message": lambda self, m: m, "decrypt_message": lambda self, m: m},
)
sys.modules.setdefault("quantum.algorithms", algorithms_stub)

from archive.legacy_root_scripts.quantum.quantum_database_search import cli as qds_cli


def test_session_protocol_requires_env(monkeypatch):
    monkeypatch.delenv("GH_COPILOT_WORKSPACE", raising=False)
    monkeypatch.delenv("GH_COPILOT_BACKUP_ROOT", raising=False)
    assert spv_main() is False


def test_quantum_search_requires_env(monkeypatch):
    monkeypatch.delenv("GH_COPILOT_WORKSPACE", raising=False)
    monkeypatch.delenv("GH_COPILOT_BACKUP_ROOT", raising=False)
    with pytest.raises(EnvironmentError):
        qds_cli()
