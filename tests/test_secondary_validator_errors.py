from secondary_copilot_validator import SecondaryCopilotValidator


def test_secondary_validator_detects_flake8_error(tmp_path):
    bad_file = tmp_path / "bad.py"
    bad_file.write_text("import os\n\n\n")
    validator = SecondaryCopilotValidator()
    assert not validator.validate_corrections([str(bad_file)])


def test_secondary_validator_handles_missing_flake8(monkeypatch):
    import scripts.validation.secondary_copilot_validator as scv

    validator = scv.SecondaryCopilotValidator()

    def fake_run(*_args, **_kwargs):
        raise FileNotFoundError

    monkeypatch.setattr(scv.subprocess, "run", fake_run)
    assert validator.validate_corrections(["dummy.py"]) is False
