#!/usr/bin/env python3
from pathlib import Path
from builds.production.builds.artifacts.validation.github_copilot_instruction_set_validator import EnterpriseUtility


def test_instruction_validator_pass(tmp_path):
    workspace = Path(tmp_path)
    copilot_dir = workspace / "copilot"
    copilot_dir.mkdir()
    instructions = copilot_dir / "copilot-instructions.md"
    instructions.write_text("Dual Copilot\nVisual Processing Indicators")

    util = EnterpriseUtility(str(workspace))
    assert util.perform_utility_function() is True


def test_instruction_validator_fail(tmp_path):
    workspace = Path(tmp_path)
    copilot_dir = workspace / "copilot"
    copilot_dir.mkdir()
    instructions = copilot_dir / "copilot-instructions.md"
    instructions.write_text("Just some text")

    util = EnterpriseUtility(str(workspace))
    assert util.perform_utility_function() is False
