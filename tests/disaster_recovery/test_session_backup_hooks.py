"""Ensure session wrap-up hooks create backups and log compliance events."""

from __future__ import annotations

import sqlite3

from scripts import wlc_session_manager
from utils.logging_utils import ANALYTICS_DB, log_session_event


def test_session_backup_hooks(monkeypatch, tmp_path):
    """Simulate a session wrap-up and verify backup and logging hooks."""

    backup_root = tmp_path / "backups"
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(backup_root))

    # Simulate wrap-up: create a log file under the backup root
    log_file = wlc_session_manager.setup_logging(verbose=False)
    assert log_file.exists()
    assert backup_root in log_file.parents

    # Record a compliance event in analytics.db
    session_id = "wrap-up-test"
    monkeypatch.setattr(
        "utils.logging_utils.validate_enterprise_operation", lambda *a, **k: True
    )
    monkeypatch.setattr(
        "enterprise_modules.database_utils.validate_enterprise_operation",
        lambda *a, **k: True,
    )
    assert log_session_event(session_id, "wrap_up")

    with sqlite3.connect(ANALYTICS_DB) as conn:
        rows = conn.execute(
            "SELECT event FROM session_history WHERE session_id=?",
            (session_id,),
        ).fetchall()

    assert ("wrap_up",) in rows

