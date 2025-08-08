"""Tests for codex_log_db utilities."""

import importlib.util
import sqlite3
import sys
import types
from pathlib import Path


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    assert spec and spec.loader
    spec.loader.exec_module(module)
    sys.modules[name] = module
    return module


BASE = Path(__file__).resolve().parent.parent / "utils"
utils_pkg = types.ModuleType("utils")
sys.modules["utils"] = utils_pkg
_load("utils.cross_platform_paths", BASE / "cross_platform_paths.py")
codex_log_db = _load("utils.codex_log_db", BASE / "codex_log_db.py")
codex_log_cursor = codex_log_db.codex_log_cursor
log_codex_start = codex_log_db.log_codex_start
log_codex_end = codex_log_db.log_codex_end


def test_init_db_creates_codex_actions(tmp_path, monkeypatch):
    db_file = tmp_path / "codex_log.db"
    monkeypatch.setattr(codex_log_db, "CODEX_LOG_DB", db_file)
    codex_log_db.init_db()
    assert db_file.exists()
    with sqlite3.connect(db_file) as conn:
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='codex_actions'"
        )
        assert cursor.fetchone() is not None


def test_log_codex_action_inserts_row(tmp_path, monkeypatch):
    db_file = tmp_path / "codex_log.db"
    monkeypatch.setattr(codex_log_db, "CODEX_LOG_DB", db_file)
    codex_log_db.log_codex_action("s1", "act", "stmt", "meta")
    with sqlite3.connect(db_file) as conn:
        rows = conn.execute(
            "SELECT session_id, action, statement, metadata FROM codex_actions"
        ).fetchall()
    assert rows == [("s1", "act", "stmt", "meta")]


def test_log_codex_start_end(tmp_path, monkeypatch):
    db_dir = tmp_path / "databases"
    db_dir.mkdir()
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))

    log_codex_start("s1")
    log_codex_end("s1", "done")

    conn = sqlite3.connect(db_dir / "codex_log.db")
    rows = conn.execute("SELECT session_id, event, summary FROM codex_log").fetchall()
    conn.close()

    assert rows == [("s1", "start", ""), ("s1", "end", "done")]


def test_codex_log_cursor_batch(tmp_path, monkeypatch):
    db_dir = tmp_path / "databases"
    db_dir.mkdir()
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))

    with codex_log_cursor() as cursor:
        cursor.executemany(
            "INSERT INTO codex_log (session_id, event, summary, ts) VALUES (?, ?, ?, ?)",
            [
                ("a", "start", "", "t1"),
                ("a", "log", "m1", "t2"),
                ("b", "log", "m2", "t3"),
            ],
        )

    conn = sqlite3.connect(db_dir / "codex_log.db")
    count = conn.execute("SELECT COUNT(*) FROM codex_log").fetchone()[0]
    conn.close()
    assert count == 3

