import pytest
import database_driven_flake8_corrector_functional as mod
from database_driven_flake8_corrector_functional import DatabaseDrivenFlake8CorrectorFunctional
from pathlib import PureWindowsPath


def test_validate_workspace_detects_recursion(tmp_path):
    nested = tmp_path / tmp_path.name
    nested.mkdir()
    corrector = DatabaseDrivenFlake8CorrectorFunctional(workspace_path=str(tmp_path))
    with pytest.raises(RuntimeError):
        corrector.validate_workspace()


def test_windows_paths_sanitized(monkeypatch):
    class DummyPath(PureWindowsPath):
        @classmethod
        def cwd(cls):
            return PureWindowsPath("C:\\Temp")

    monkeypatch.setattr(mod.os, "name", "nt", raising=False)
    monkeypatch.setattr(mod, "Path", DummyPath)
    path = "C:\\Temp\\proj"
    corrector = DatabaseDrivenFlake8CorrectorFunctional(workspace_path=path, db_path="C:\\Temp\\db.sqlite")
    assert isinstance(corrector.workspace_path, PureWindowsPath)
    assert corrector.workspace_path.as_posix() == "C:/Temp/proj"
    assert isinstance(corrector.db_path, PureWindowsPath)
