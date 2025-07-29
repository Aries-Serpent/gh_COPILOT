"""Tests for :mod:`archive.consolidated_scripts.enterprise_database_driven_documentation_manager`."""

import logging
import os
import sqlite3
from datetime import datetime
from pathlib import Path

from archive.consolidated_scripts.enterprise_database_driven_documentation_manager import (
    DocumentationManager,
    dual_validate,
)


def test_dual_copilot_validation(tmp_path: Path, monkeypatch, caplog) -> None:
    """Validate DUAL COPILOT pattern for documentation rendering."""

    # Visual processing indicator start
    start = datetime.now()
    print("PROCESS STARTED: test_dual_copilot_validation")
    print(f"Start Time: {start.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Process ID: {os.getpid()}")

    # Setup temporary databases
    prod_db = tmp_path / "production.db"
    analytics_db = tmp_path / "databases" / "analytics.db"
    analytics_db.parent.mkdir(parents=True, exist_ok=True)
    completion_db = tmp_path / "template_completion.db"

    with sqlite3.connect(prod_db) as conn:
        conn.execute("CREATE TABLE documentation (title TEXT, content TEXT, compliance_score INTEGER)")
        conn.execute("INSERT INTO documentation VALUES ('Doc1', 'content', 75)")

    with sqlite3.connect(completion_db) as conn:
        conn.execute("CREATE TABLE templates (template_content TEXT)")
        conn.execute("INSERT INTO templates VALUES ('{content}')")

    with sqlite3.connect(analytics_db) as conn:
        conn.execute("CREATE TABLE ml_pattern_optimization (replacement_template TEXT)")
        conn.execute("INSERT INTO ml_pattern_optimization VALUES ('{content}')")

    # Ensure environment variables are set for compliance
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(tmp_path / "backups"))

    # Provide our custom manager to ``dual_validate``
    manager = DocumentationManager(
        database=prod_db,
        analytics_db=analytics_db,
        completion_db=completion_db,
    )
    monkeypatch.setattr(
        "archive.consolidated_scripts.enterprise_database_driven_documentation_manager.DocumentationManager",
        lambda: manager,
    )

    with caplog.at_level(logging.INFO):
        assert dual_validate(), "Primary render step failed"

    assert any("Simulated analytics.db log event" in rec.getMessage() for rec in caplog.records)

    # Visual processing indicator end
    duration = (datetime.now() - start).total_seconds()
    print(f"TEST COMPLETED: test_dual_copilot_validation in {duration:.2f}s")


def test_render_logs_missing_table(tmp_path: Path, monkeypatch, caplog) -> None:
    """Ensure missing documentation table logs a warning and returns 0."""

    prod_db = tmp_path / "production.db"
    analytics_db = tmp_path / "databases" / "analytics.db"
    analytics_db.parent.mkdir(parents=True, exist_ok=True)
    completion_db = tmp_path / "template_completion.db"
    prod_db.touch()
    with sqlite3.connect(analytics_db) as conn:
        conn.execute("CREATE TABLE render_events (event TEXT)")
        conn.execute("CREATE TABLE ml_pattern_optimization (replacement_template TEXT)")

    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(tmp_path / "backups"))

    manager = DocumentationManager(
        database=prod_db,
        analytics_db=analytics_db,
        completion_db=completion_db,
    )
    caplog.set_level(logging.WARNING)
    result = manager.render()
    assert result == 0
    assert any("Failed to read documentation table" in rec.getMessage() for rec in caplog.records)
