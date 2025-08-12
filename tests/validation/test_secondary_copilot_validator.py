import subprocess

import pytest

from scripts.validation.secondary_copilot_validator import SecondaryCopilotValidator


def test_missing_flake8(monkeypatch: pytest.MonkeyPatch) -> None:
    validator = SecondaryCopilotValidator()

    def _missing_flake8(*args, **kwargs):
        raise FileNotFoundError("flake8 not found")

    monkeypatch.setattr(subprocess, "run", _missing_flake8)
    assert validator.validate_corrections(["dummy.py"]) is False

