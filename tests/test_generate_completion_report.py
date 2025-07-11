import logging
from datetime import datetime, timedelta
from pathlib import Path

from database_first_windows_compatible_flake8_corrector import \
    DatabaseFirstFlake8Corrector


def test_generate_completion_report_logs_once(tmp_path, caplog):
    """Ensure completion report is logged once with summary stats."""
    workspace = tmp_path
    (workspace / "databases").mkdir()

    caplog.set_level(logging.INFO)
    corrector = DatabaseFirstFlake8Corrector(workspace_path=str(workspace))

    start_time = datetime.now() - timedelta(seconds=5)
    with caplog.at_level(logging.INFO):
        corrector.generate_completion_report(start_time)

    messages = [record.message for record in caplog.records]

    assert messages.count("[COMPLETE] DATABASE-FIRST FLAKE8 CORRECTION COMPLETE") == 1
    assert any("Files Processed" in m for m in messages)
