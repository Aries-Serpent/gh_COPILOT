"""Basic integration test for the placeholder audit script."""

from __future__ import annotations

from pathlib import Path

import os

import pytest

audit_module = pytest.importorskip("scripts.code_placeholder_audit")
main = audit_module.main


def test_placeholder_audit_clean_workspace(tmp_path):
    """The audit should succeed when no placeholders are present."""

    os.environ["GH_COPILOT_DISABLE_VALIDATION"] = "1"

    test_file: Path = tmp_path / "clean.py"
    test_file.write_text("print('hi')\n", encoding="utf-8")

    assert main(
        workspace_path=str(tmp_path),
        analytics_db=str(tmp_path / "analytics.db"),
        production_db=str(tmp_path / "production.db"),
        dashboard_dir=str(tmp_path / "dashboard"),
        simulate=True,
    )

