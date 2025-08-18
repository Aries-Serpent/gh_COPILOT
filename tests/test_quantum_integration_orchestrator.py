import pytest
import sqlite3
import pytest

import quantum_integration_orchestrator as cli


@pytest.fixture(autouse=True)
def _sqlite_memory(monkeypatch):
    """Route sqlite3 connections to an in-memory database for tests."""
    orig = sqlite3.connect

    def _connect(*args, **kwargs):  # pragma: no cover - simple redirection
        return orig(":memory:")

    monkeypatch.setattr(sqlite3, "connect", _connect)

def test_cli_simulator(monkeypatch):
    """Ensure the CLI works with the simulator provider."""
    monkeypatch.setenv("GH_COPILOT_TEST_MODE", "1")
    backend = object()

    class DummyProvider:
        def get_backend(self):
            return backend

    monkeypatch.setattr("quantum.providers.get_provider", lambda name: DummyProvider())

    class DummyUtility:
        def __init__(self, *, backend=None):
            self.backend = backend

        def execute_utility(self) -> bool:
            return True

    monkeypatch.setattr(cli, "EnterpriseUtility", DummyUtility)
    assert cli.main(["--provider", "simulator"]) == 0


def test_cli_hardware_requires_token(monkeypatch):
    """Hardware provider without token should raise SystemExit."""
    monkeypatch.setenv("GH_COPILOT_TEST_MODE", "1")
    class DummyUtility:
        def __init__(self, *, backend=None):
            self.backend = backend

        def execute_utility(self) -> bool:
            return True

    monkeypatch.setattr(cli, "EnterpriseUtility", DummyUtility)
    with pytest.raises(SystemExit):
        cli.main(["--provider", "ibm"])


def test_cli_hardware(monkeypatch):
    """Hardware provider path executes when token is set."""
    monkeypatch.setenv("GH_COPILOT_TEST_MODE", "1")
    backend = object()

    class DummyProvider:
        def get_backend(self):
            return backend

    monkeypatch.setattr("quantum.providers.get_provider", lambda name: DummyProvider())
    monkeypatch.setenv("QISKIT_IBM_TOKEN", "token")

    class DummyUtility:
        def __init__(self, *, backend=None):
            self.backend = backend

        def execute_utility(self) -> bool:
            return True

    monkeypatch.setattr(cli, "EnterpriseUtility", DummyUtility)
    assert cli.main(["--provider", "ibm"]) == 0
