"""Ensure hardware providers respect feature flags and default to simulators."""

import importlib
import types
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]

# Create a minimal ``quantum`` package to avoid heavy imports from ``quantum.__init__``
quantum_pkg = types.ModuleType("quantum")
quantum_pkg.__path__ = [str(REPO_ROOT / "quantum")]
sys.modules.setdefault("quantum", quantum_pkg)

providers_pkg = types.ModuleType("quantum.providers")
providers_pkg.__path__ = [str(REPO_ROOT / "quantum" / "providers")]
sys.modules.setdefault("quantum.providers", providers_pkg)

framework_pkg = types.ModuleType("quantum.framework")
framework_pkg.__path__ = [str(REPO_ROOT / "quantum" / "framework")]
sys.modules.setdefault("quantum.framework", framework_pkg)

SimulatorBackend = importlib.import_module("quantum.framework.backend").SimulatorBackend
IBMBackendProvider = importlib.import_module("quantum.providers.ibm_provider").IBMBackendProvider
IonQProvider = importlib.import_module("quantum.providers.ionq_provider").IonQProvider
DWaveProvider = importlib.import_module("quantum.providers.dwave_provider").DWaveProvider


def test_ibm_provider_flag_disabled(monkeypatch):
    monkeypatch.setenv("QISKIT_IBM_TOKEN", "token")
    provider = IBMBackendProvider()
    assert provider.is_available() is False
    assert isinstance(provider.get_backend(), SimulatorBackend)


def test_ionq_provider_flag_disabled(monkeypatch):
    monkeypatch.setenv("IONQ_API_KEY", "token")
    provider = IonQProvider()
    assert provider.is_available() is False
    assert isinstance(provider.get_backend(), SimulatorBackend)


def test_dwave_provider_flag_disabled(monkeypatch):
    monkeypatch.setenv("DWAVE_API_TOKEN", "token")
    provider = DWaveProvider()
    assert provider.is_available() is False
    assert isinstance(provider.get_backend(), SimulatorBackend)
