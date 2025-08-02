"""Verify WLC sessions persist lessons and load them on subsequent runs."""

from __future__ import annotations

import logging


class DummyOrchestrator:
    """Minimal orchestrator stub returning a perfect score."""

    def __init__(self, workspace_path: str) -> None:  # pragma: no cover - simple init
        self.workspace_path = workspace_path

    def execute_unified_wrapup(self):  # pragma: no cover - simple return
        class Result:
            compliance_score = 100

        return Result()


def test_lessons_persist_and_load(tmp_path, monkeypatch, caplog):
    workspace = tmp_path / "workspace"
    backup = tmp_path / "backup"
    workspace.mkdir()
    backup.mkdir()
    (workspace / "databases").mkdir()

    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(backup))
    monkeypatch.delenv("TEST_MODE", raising=False)

    from scripts import wlc_session_manager
    monkeypatch.setattr(
        wlc_session_manager, "UnifiedWrapUpOrchestrator", DummyOrchestrator
    )
    from scripts.wlc_session_manager import run_session
    from utils.lessons_learned_integrator import load_lessons

    prod_db = workspace / "databases" / "production.db"
    lessons_db = workspace / "databases" / "learning_monitor.db"

    caplog.set_level(logging.INFO, logger="scripts.wlc_session_manager")

    run_session(steps=0, db_path=prod_db, verbose=False)
    lessons = load_lessons(lessons_db)
    assert lessons, "first run persisted a lesson"

    caplog.clear()
    run_session(steps=0, db_path=prod_db, verbose=False)
    assert any("Lesson applied" in rec.message for rec in caplog.records)
