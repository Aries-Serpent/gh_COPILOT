"""Tests for zero-byte file detection and logging."""

from pathlib import Path
import sqlite3

import pytest

import unified_session_management_system as usms


def _setup_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    db = tmp_path / "analytics.db"
    monkeypatch.setattr(usms, "ANALYTICS_DB", db)
    return db


def _fetch_records(db: Path) -> list[tuple[str, str, str]]:
    with sqlite3.connect(db) as conn:
        return list(
            conn.execute("SELECT path, session_id, phase FROM zero_byte_files")
        )


def test_zero_byte_file_before_block(tmp_path, monkeypatch):
    db = _setup_db(tmp_path, monkeypatch)
    zero_file = tmp_path / "empty.txt"
    zero_file.touch()

    with pytest.raises(RuntimeError):
        with usms.ensure_no_zero_byte_files(tmp_path, "sess1"):
            pass

    records = _fetch_records(db)
    assert (str(zero_file), "sess1", "before") in records


def test_zero_byte_file_after_block(tmp_path, monkeypatch):
    db = _setup_db(tmp_path, monkeypatch)
    target = tmp_path / "later.txt"

    with pytest.raises(RuntimeError):
        with usms.ensure_no_zero_byte_files(tmp_path, "sess2"):
            target.touch()

    records = _fetch_records(db)
    assert (str(target), "sess2", "after") in records

