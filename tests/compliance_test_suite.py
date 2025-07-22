"""Basic compliance test suite for linting and cross-platform checks."""
from __future__ import annotations

import subprocess
from pathlib import Path


def test_ruff() -> None:
    result = subprocess.run(["ruff", "check", str(Path(__file__).parent.parent)], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
