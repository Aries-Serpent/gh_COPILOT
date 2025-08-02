import sys

import json

from quantum.cli import token_setup


def test_token_setup_writes_config(tmp_path, monkeypatch):
    cfg = tmp_path / "qiskit.json"
    monkeypatch.setattr(token_setup, "CONFIG_PATH", cfg)

    captured = {}

    def fake_init_ibm_backend(token=None, backend_name=None, enforce_hardware=False):
        captured["token"] = token
        return object(), True

    monkeypatch.setattr(token_setup, "init_ibm_backend", fake_init_ibm_backend)
    monkeypatch.setenv("IBM_BACKEND", "ibmq_qasm_simulator")
    monkeypatch.setattr(sys, "argv", ["token_setup", "--token", "ABC", "--save", "--use-hardware"])
    token_setup.main()

    assert json.loads(cfg.read_text())["QISKIT_IBM_TOKEN"] == "ABC"
    assert cfg.stat().st_mode & 0o777 == 0o600
    assert captured["token"] == "ABC"
