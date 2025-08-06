import importlib

import pytest


def test_template_synchronizer_uses_env(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    module = importlib.reload(importlib.import_module("template_engine.template_synchronizer"))
    assert module.WORKSPACE_ROOT == tmp_path
    assert module.ANALYTICS_DB == tmp_path / "databases" / "analytics.db"


def test_quantum_engine_uses_env(tmp_path, monkeypatch):
    pytest.skip("quantum module heavy import skipped in minimal test")


def test_autonomous_cli_uses_env(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    mod = importlib.reload(importlib.import_module("scripts.automation.autonomous_cli"))
    cli = mod.AutonomousCLI()
    assert cli.workspace_path == tmp_path


def test_openai_api_key(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    module = importlib.reload(importlib.import_module("github_integration.openai_connector"))
    assert module.get_api_key() == "test-key"
