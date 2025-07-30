from secondary_copilot_validator import SecondaryCopilotValidator


def test_secondary_validator_detects_flake8_error(tmp_path):
    bad_file = tmp_path / "bad.py"
    bad_file.write_text("import os\n\n\n")
    validator = SecondaryCopilotValidator()
    assert not validator.validate_corrections([str(bad_file)])
