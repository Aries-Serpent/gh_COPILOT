"""Tests for final validation logging with dual copilot orchestrator."""

from __future__ import annotations

from pathlib import Path

from enterprise_modules.compliance import run_final_validation
from scripts.validation import primary_copilot_executor


def test_final_validation_logging(tmp_path: Path, monkeypatch) -> None:
    """Ensure metrics capture failing primary paths and flake8 details."""

    bad_file = tmp_path / "bad.py"
    bad_file.write_text("def bad(:\n    pass\n")

    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")

    def fake_execute(self, phases, func):
        return 0, func()

    monkeypatch.setattr(
        primary_copilot_executor.PrimaryCopilotExecutor,
        "execute_with_monitoring",
        fake_execute,
    )

    def failing_primary() -> bool:
        return False

    primary_ok, validation_ok, metrics = run_final_validation(
        failing_primary, [str(bad_file)]
    )

    assert primary_ok is False
    assert validation_ok is False
    assert metrics["primary_success"] is False
    assert metrics["failed_files"] == [str(bad_file)]
    assert metrics["returncode"] != 0
