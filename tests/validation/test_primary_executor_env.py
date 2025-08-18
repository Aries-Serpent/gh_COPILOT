import logging

from scripts.validation.primary_copilot_executor import PrimaryCopilotExecutor


def test_validate_environment_compliance_passes(tmp_path, monkeypatch, caplog):
    """PrimaryCopilotExecutor.validate_environment_compliance succeeds on clean workspace."""

    # Point to a temporary workspace with no forbidden folders
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("GH_COPILOT_DISABLE_VALIDATION", "1")

    executor = PrimaryCopilotExecutor("dummy")

    with caplog.at_level(logging.INFO):
        executor.validate_environment_compliance()

    assert "ENVIRONMENT COMPLIANCE VALIDATED" in caplog.text

