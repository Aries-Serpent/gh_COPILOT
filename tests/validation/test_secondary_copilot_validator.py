import subprocess

from secondary_copilot_validator import SecondaryCopilotValidator


def test_missing_flake8(monkeypatch):
    def _missing_flake8(*args, **kwargs):
        raise FileNotFoundError

    monkeypatch.setattr(subprocess, "run", _missing_flake8)
    validator = SecondaryCopilotValidator()
    assert validator.validate_corrections(["dummy.py"]) is False
    assert validator.metrics["returncode"] == -1
