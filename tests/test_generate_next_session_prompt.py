#!/usr/bin/env python3
from pathlib import Path

from tools.generate_next_session_prompt import generate_next_session_prompt


def test_generate_next_session_prompt(tmp_path, monkeypatch):
    report = tmp_path / "session_validation_report_20250101_000000.json"
    report.write_text(
        "{\n"
        '  "overall_status": "FAILED",\n'
        '  "validation_results": {\n'
        '    "anti_recursion_compliance": false,\n'
        '    "enterprise_compliance": true\n'
        "  }\n"
        "}"
    )
    entropy = tmp_path / "NEXT_SESSION_ENTROPY_RESOLUTION.md"
    entropy.write_text("PRIORITY 1: Task A\n- fix issue A\n- fix issue B\n")
    monkeypatch.chdir(tmp_path)

    called = {"v": False}

    def dummy_validate(self, files):
        called["v"] = True
        return True

    monkeypatch.setattr(
        "secondary_copilot_validator.SecondaryCopilotValidator.validate_corrections",
        dummy_validate,
    )

    prompt = generate_next_session_prompt(Path("."))
    assert "Validation Status: FAILED" in prompt
    assert "anti_recursion_compliance" in prompt
    assert "fix issue A" in prompt
    assert "fix issue B" in prompt
    assert called["v"]
