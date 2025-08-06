import os
import sqlite3
from pathlib import Path

import pytest

from enterprise_modules.compliance import anti_recursion_guard, MAX_RECURSION_DEPTH


def _fetch_logs(db: Path) -> list[tuple[str, int, int]]:
    with sqlite3.connect(db) as conn:
        return conn.execute(
            "SELECT path, pid, depth FROM recursion_pid_log"
        ).fetchall()


def test_guard_logs_pid(monkeypatch, tmp_path):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    db = tmp_path / "databases" / "analytics.db"

    @anti_recursion_guard
    def wrapped(path: Path) -> str:
        return "ok"

    assert wrapped(tmp_path) == "ok"
    logs = _fetch_logs(db)
    assert any(
        row[1] == os.getpid() and "wrapped/entry" in row[0] and row[2] == 1
        for row in logs
    )


def test_guard_aborts_on_nested_directories(monkeypatch, tmp_path):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    current = tmp_path
    for i in range(MAX_RECURSION_DEPTH + 1):
        current = current / f"lvl{i}"
        current.mkdir()

    @anti_recursion_guard
    def walk(path: Path) -> None:
        for child in path.iterdir():
            if child.is_dir():
                walk(child)

    with pytest.raises(RuntimeError):
        walk(tmp_path)

