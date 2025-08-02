import os
import sys

from quantum.cli import executor_cli


class DummyExecutor:
    def __init__(self, use_hardware: bool, backend_name: str):
        self.init_args = {"use_hardware": use_hardware, "backend_name": backend_name}
        self.backend = type("B", (), {"name": backend_name})()
        # Simulate hardware availability based on flag
        self.use_hardware = use_hardware


def test_cli_parses_token_and_backend(monkeypatch, capsys):
    called = {}

    def fake_executor(**kwargs):
        called.update(kwargs)
        return DummyExecutor(**kwargs)

    monkeypatch.setattr(executor_cli, "QuantumExecutor", fake_executor)
    monkeypatch.setattr(
        sys,
        "argv",
        ["prog", "--use-hardware", "--token", "TEST", "--backend", "ibm_test"],
    )

    executor_cli.main()
    out = capsys.readouterr().out
    assert "ibm_test" in out
    assert called == {"use_hardware": True, "backend_name": "ibm_test"}
    assert os.getenv("QISKIT_IBM_TOKEN") == "TEST"


def test_cli_fallback_without_token(monkeypatch, capsys):
    def fake_executor(**kwargs):
        # Hardware request but mark unavailable
        exec_ = DummyExecutor(**kwargs)
        exec_.use_hardware = False
        return exec_

    monkeypatch.delenv("QISKIT_IBM_TOKEN", raising=False)
    monkeypatch.setattr(executor_cli, "QuantumExecutor", fake_executor)
    monkeypatch.setattr(sys, "argv", ["prog", "--use-hardware"])

    executor_cli.main()
    out = capsys.readouterr().out
    assert "using simulator" in out
    assert "hardware=False" in out
