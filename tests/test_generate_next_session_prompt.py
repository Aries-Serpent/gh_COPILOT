#!/usr/bin/env python3
from pathlib import Path

from tools.generate_next_session_prompt import generate_next_session_prompt
<<<<<<< HEAD
=======
import logging
>>>>>>> 072d1e7e (Nuclear fix: Complete repository rebuild - 2025-07-14 22:31:03)


def test_generate_next_session_prompt(tmp_path, monkeypatch):
    report = tmp_path / "session_validation_report_20250101_000000.json"
    report.write_text(
<<<<<<< HEAD
        "{\n"
=======
        '{\n'
>>>>>>> 072d1e7e (Nuclear fix: Complete repository rebuild - 2025-07-14 22:31:03)
        '  "overall_status": "FAILED",\n'
        '  "validation_results": {\n'
        '    "anti_recursion_compliance": false,\n'
        '    "enterprise_compliance": true\n'
<<<<<<< HEAD
        "  }\n"
        "}"
=======
        '  }\n'
        '}'
>>>>>>> 072d1e7e (Nuclear fix: Complete repository rebuild - 2025-07-14 22:31:03)
    )
    entropy = tmp_path / "NEXT_SESSION_ENTROPY_RESOLUTION.md"
    entropy.write_text("PRIORITY 1: Task A\n- fix issue A\n- fix issue B\n")
    monkeypatch.chdir(tmp_path)
<<<<<<< HEAD

    called = {"v": False}

    def dummy_validate(self, files):
        called["v"] = True
        return True

    monkeypatch.setattr(
        "secondary_copilot_validator.SecondaryCopilotValidator.validate_corrections",
        dummy_validate,
    )

    prompt = generate_next_session_prompt(Path("."))
=======
    prompt = generate_next_session_prompt(Path('.'))
>>>>>>> 072d1e7e (Nuclear fix: Complete repository rebuild - 2025-07-14 22:31:03)
    assert "Validation Status: FAILED" in prompt
    assert "anti_recursion_compliance" in prompt
    assert "fix issue A" in prompt
    assert "fix issue B" in prompt
<<<<<<< HEAD
    assert called["v"]
=======
>>>>>>> 072d1e7e (Nuclear fix: Complete repository rebuild - 2025-07-14 22:31:03)
