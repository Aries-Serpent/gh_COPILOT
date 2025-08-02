import importlib
import os
import sys

import pytest

from quantum.optimizers.quantum_optimizer import validate_workspace


def _prepare_env(tmp_path, monkeypatch):
    ws = tmp_path / "ws"
    bk = tmp_path / "bk"
    ws.mkdir()
    bk.mkdir()
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(ws))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(bk))
    return ws, bk


def test_validate_workspace_valid(tmp_path, monkeypatch):
    _prepare_env(tmp_path, monkeypatch)
    assert validate_workspace() is True


def test_validate_workspace_same_path(tmp_path, monkeypatch):
    ws = tmp_path / "same"
    ws.mkdir()
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(ws))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(ws))
    with pytest.raises(RuntimeError):
        validate_workspace()


def test_validate_workspace_nested(tmp_path, monkeypatch):
    ws = tmp_path / "ws"
    bk = ws / "bk"
    ws.mkdir()
    bk.mkdir()
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(ws))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(bk))
    with pytest.raises(RuntimeError):
        validate_workspace()


def test_validate_workspace_symlink(tmp_path, monkeypatch):
    ws, bk = _prepare_env(tmp_path, monkeypatch)
    (ws / "link").symlink_to(bk)
    with pytest.raises(RuntimeError):
        validate_workspace()


def test_import_no_filesystem(monkeypatch, tmp_path):
    ws, bk = _prepare_env(tmp_path, monkeypatch)
    called = False

    def fake_walk(*args, **kwargs):
        nonlocal called
        called = True
        raise AssertionError("os.walk should not be called during import")

    monkeypatch.setattr(os, "walk", fake_walk)
    sys.modules.pop("quantum.optimizers.quantum_optimizer", None)
    importlib.import_module("quantum.optimizers.quantum_optimizer")
    assert called is False
