import importlib
import importlib.util
import os
import sys
import types
from pathlib import Path

import pytest

# Create minimal "quantum" package to satisfy absolute imports without loading heavy dependencies
_quantum_pkg = types.ModuleType("quantum")
sys.modules.setdefault("quantum", _quantum_pkg)
_ibm_spec = importlib.util.spec_from_file_location(
    "ghc_quantum.ibm_backend", Path(__file__).resolve().parents[1] / "quantum/ibm_backend.py"
)
_ibm = importlib.util.module_from_spec(_ibm_spec)
_ibm_spec.loader.exec_module(_ibm)  # type: ignore[assignment]
sys.modules["ghc_quantum.ibm_backend"] = _ibm
_quantum_pkg.ibm_backend = _ibm

_spec = importlib.util.spec_from_file_location(
    "ghc_quantum.optimizers.quantum_optimizer",
    Path(__file__).resolve().parents[1] / "quantum/optimizers/quantum_optimizer.py",
)
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)  # type: ignore[assignment]
validate_workspace = _module.validate_workspace


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
    with pytest.raises(RuntimeError) as exc:
        validate_workspace()
    assert str(ws) in str(exc.value)


def test_validate_workspace_nested(tmp_path, monkeypatch):
    ws = tmp_path / "ws"
    bk = ws / "bk"
    ws.mkdir()
    bk.mkdir()
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(ws))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(bk))
    with pytest.raises(RuntimeError) as exc:
        validate_workspace()
    msg = str(exc.value)
    assert str(ws) in msg and str(bk) in msg


def test_validate_workspace_symlink(tmp_path, monkeypatch):
    ws, bk = _prepare_env(tmp_path, monkeypatch)
    (ws / "link").symlink_to(bk)
    with pytest.raises(RuntimeError) as exc:
        validate_workspace()
    msg = str(exc.value)
    assert "link" in msg and str(bk) in msg


def test_validate_workspace_symlink_to_workspace(tmp_path, monkeypatch):
    ws, bk = _prepare_env(tmp_path, monkeypatch)
    loop = ws / "loop"
    loop.symlink_to(ws)
    with pytest.raises(RuntimeError) as exc:
        validate_workspace()
    msg = str(exc.value)
    assert "loop" in msg and str(ws) in msg
    loop.unlink()


def test_validate_backup_symlink_to_workspace(tmp_path, monkeypatch):
    ws, bk = _prepare_env(tmp_path, monkeypatch)
    loop = bk / "loop"
    loop.symlink_to(ws)
    with pytest.raises(RuntimeError) as exc:
        validate_workspace()
    msg = str(exc.value)
    assert str(loop) in msg and str(ws) in msg
    loop.unlink()


def test_import_no_filesystem(monkeypatch, tmp_path):
    _prepare_env(tmp_path, monkeypatch)
    called = False

    def fake_walk(*args, **kwargs):
        nonlocal called
        called = True
        raise AssertionError("os.walk should not be called during import")

    monkeypatch.setattr(os, "walk", fake_walk)
    spec = importlib.util.spec_from_file_location(
        "quantum_optimizer_import",
        Path(__file__).resolve().parents[1] / "quantum/optimizers/quantum_optimizer.py",
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[assignment]
    assert called is False
