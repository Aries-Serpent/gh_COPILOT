import sqlite3
from contextlib import contextmanager

import scripts.wlc_session_manager as wsm
import utils.codex_log_db as codex_db_mod
from utils.lessons_learned_integrator import extract_lessons_from_codex_logs


def test_extract_lessons_from_codex_logs(tmp_path):
    db = tmp_path / "codex_log.db"
    with sqlite3.connect(db) as conn:
        conn.execute(
            "CREATE TABLE codex_actions (session_id TEXT, action TEXT, statement TEXT, ts TEXT, metadata TEXT)"
        )
        conn.execute(
            "INSERT INTO codex_actions VALUES (?,?,?,?,?)",
            ("s1", "end", "Error: Be concise", "2024-01-01T00:00:00Z", ""),
        )
    lessons = extract_lessons_from_codex_logs(db)
    assert lessons == [
        {
            "description": "Error: Be concise",
            "source": "codex_log",
            "timestamp": "2024-01-01T00:00:00Z",
            "validation_status": "pending",
            "tags": "error",
        }
    ]


def test_run_session_stores_codex_lessons(tmp_path, monkeypatch):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    backup_root = tmp_path / "backup"
    backup_root.mkdir()
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(workspace))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(backup_root))
    monkeypatch.delenv("TEST_MODE", raising=False)

    codex_db = workspace / "databases" / "codex_log.db"
    codex_db.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(codex_db) as conn:
        conn.execute(
            "CREATE TABLE codex_actions (session_id TEXT, action TEXT, statement TEXT, ts TEXT, metadata TEXT)"
        )
        conn.execute(
            "INSERT INTO codex_actions VALUES (?,?,?,?,?)",
            ("s1", "end", "Warning: Review results", "2024-01-02T00:00:00Z", ""),
        )
    monkeypatch.setattr(codex_db_mod, "CODEX_LOG_DB", codex_db)

    @contextmanager
    def dummy_no_zero(path, session_id):
        yield

    monkeypatch.setattr(wsm, "ensure_no_zero_byte_files", dummy_no_zero)

    class DummyOrchestrator:
        def __init__(self, workspace_path=None):
            pass

        def execute_unified_wrapup(self):
            return type("R", (), {"compliance_score": 100.0})()

    monkeypatch.setattr(wsm, "UnifiedWrapUpOrchestrator", DummyOrchestrator)

    class DummyValidator:
        def validate_corrections(self, files):
            return True

    monkeypatch.setattr(wsm, "SecondaryCopilotValidator", lambda: DummyValidator())
    monkeypatch.setattr(wsm, "validate_environment", lambda: True)

    stored = []

    def fake_store_lesson(description, source, timestamp, validation_status, *, tags=None, db_path=None):
        stored.append(
            {
                "description": description,
                "source": source,
                "timestamp": timestamp,
                "validation_status": validation_status,
                "tags": tags,
            }
        )

    monkeypatch.setattr(wsm, "store_lesson", fake_store_lesson)

    session_db = workspace / "databases" / "session.db"
    wsm.run_session(0, session_db, False, run_orchestrator=False)

    assert any(lesson["description"] == "Warning: Review results" for lesson in stored)
