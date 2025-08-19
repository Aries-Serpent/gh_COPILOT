"""Tests for `scripts/wlc_session_manager.py`."""

from __future__ import annotations

import importlib.util
import sqlite3
from pathlib import Path

import logging


MODULE_PATH = Path(__file__).resolve().parents[2] / "scripts" / "wlc_session_manager.py"
spec = importlib.util.spec_from_file_location("wlc_session_manager", MODULE_PATH)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

initialize_database = module.initialize_database


def _has_table(db: Path) -> bool:
    conn = sqlite3.connect(db)
    try:
        cur = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='unified_wrapup_sessions'"
        )
        return cur.fetchone() is not None
    finally:
        conn.close()


def test_initialize_database_creates_file(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("TEST_MODE", raising=False)
    db = tmp_path / "session.db"
    initialize_database(db)
    assert db.exists()
    assert _has_table(db)


def test_initialize_database_handles_corruption(tmp_path: Path, monkeypatch, caplog) -> None:  # noqa: ANN001
    monkeypatch.delenv("TEST_MODE", raising=False)
    db = tmp_path / "session.db"
    db.write_text("not a database")
    with caplog.at_level(logging.WARNING):
        initialize_database(db)
    assert _has_table(db)
    backup = db.with_suffix(db.suffix + ".corrupt")
    assert backup.exists()
    assert any("corrupted" in record.message for record in caplog.records)

