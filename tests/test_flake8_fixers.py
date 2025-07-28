#!/usr/bin/env python3
"""Tests for simple flake8 fixers."""

from scripts.utilities.targeted_flake8_fixer import EnterpriseFlake8Corrector
from scripts.utilities.critical_flake8_error_corrector import EnterpriseFlake8Corrector as CriticalCorrector


def _write_bad_file(path):
    path.write_text("print('hi')  \n", encoding="utf-8")


def test_targeted_correct_file(tmp_path):
    bad = tmp_path / "bad.py"
    _write_bad_file(bad)
    fixer = EnterpriseFlake8Corrector(workspace_path=str(tmp_path))
    changed = fixer.correct_file(str(bad))
    assert changed
    assert bad.read_text(encoding="utf-8") == "print('hi')\n"


def test_critical_correct_file(tmp_path):
    bad = tmp_path / "bad.py"
    _write_bad_file(bad)
    fixer = CriticalCorrector(workspace_path=str(tmp_path))
    changed = fixer.correct_file(str(bad))
    assert changed
    assert bad.read_text(encoding="utf-8") == "print('hi')\n"
