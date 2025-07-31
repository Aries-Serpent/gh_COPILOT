#!/usr/bin/env python3
from pathlib import Path

import pytest

from scripts.database.database_first_windows_compatible_flake8_corrector import \
    DatabaseFirstFlake8Corrector


def test_flake8_scan_handles_non_ascii(tmp_path):
    pytest.importorskip("flake8")
    workspace = tmp_path / "路径"
    workspace.mkdir()
    (workspace / "example.py").write_text("print('hi')  \n")

    corrector = DatabaseFirstFlake8Corrector(workspace_path=str(workspace))
    violations = corrector.run_flake8_scan()
    assert isinstance(violations, list)


def test_flake8_scan_handles_unc_non_ascii(tmp_path):
    """Ensure Flake8 runs with UNC paths containing non-ASCII characters."""
    pytest.importorskip("flake8")
    workspace = tmp_path / "路径"
    workspace.mkdir()
    (workspace / "example.py").write_text("print('hi')  \n")

    unc_path = Path("//" + workspace.as_posix().lstrip("/"))
    corrector = DatabaseFirstFlake8Corrector(workspace_path=str(unc_path))
    violations = corrector.run_flake8_scan()
    assert isinstance(violations, list)
