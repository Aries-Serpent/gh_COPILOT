#!/usr/bin/env python3
import importlib
import pytest

MODULES = [
    "critical_flake8_error_corrector",
    "database_first_flake8_compliance_scanner",
    "targeted_flake8_fixer",
    "scripts.visual_processing_compliance_validator",
]


@pytest.mark.parametrize("module_name", MODULES)
def test_main_passes_within_workspace(tmp_path, monkeypatch, module_name):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    (workspace / "example.py").write_text("print('hi')\n")
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    monkeypatch.chdir(workspace)
    module = importlib.import_module(module_name)
    assert module.main()


@pytest.mark.parametrize("module_name", MODULES)
def test_main_fails_outside_workspace(tmp_path, monkeypatch, module_name):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    (workspace / "example.py").write_text("print('hi')\n")
    outside = tmp_path / "outside"
    outside.mkdir()
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    monkeypatch.chdir(outside)
    module = importlib.import_module(module_name)
    assert module.main() is False
