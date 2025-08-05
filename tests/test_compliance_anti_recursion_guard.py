import os
import threading
import time

import pytest

from enterprise_modules.compliance import anti_recursion_guard, MAX_RECURSION_DEPTH


def test_guard_aborts_on_nested_directories(monkeypatch, tmp_path):
    """The guard aborts when recursion depth exceeds the limit."""

    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    current = tmp_path
    for i in range(MAX_RECURSION_DEPTH + 1):
        current = current / f"lvl{i}"
        current.mkdir()

    @anti_recursion_guard
    def walk(path):
        for child in path.iterdir():
            if child.is_dir():
                walk(child)

    with pytest.raises(RuntimeError):
        walk(tmp_path)


def test_guard_aborts_on_duplicate_pid(monkeypatch, tmp_path):
    """Concurrent invocation by the same PID triggers early abort."""

    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))

    @anti_recursion_guard
    def slow_call():
        time.sleep(0.2)

    t = threading.Thread(target=slow_call)
    t.start()
    time.sleep(0.05)
    with pytest.raises(RuntimeError):
        slow_call()
    t.join()


def test_guard_allows_single_invocation(monkeypatch, tmp_path):
    """Single invocation proceeds normally and records parent-child PID."""

    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    db = tmp_path / "databases" / "analytics.db"

    @anti_recursion_guard
    def hello():
        return "ok"

    assert hello() == "ok"
    import sqlite3
    with sqlite3.connect(db) as conn:
        rows = conn.execute(
            "SELECT path, pid, depth FROM recursion_pid_log"
        ).fetchall()
    assert any("hello/entry" in r[0] and r[2] == 1 for r in rows)


def test_guard_aborts_on_pid_loop(monkeypatch, tmp_path):
    """Artificial parent/child PID loop triggers early abort."""

    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))

    @anti_recursion_guard
    def invoke():
        return True

    import enterprise_modules.compliance as comp

    parent = os.getppid()
    comp._PID_PARENTS[parent] = os.getpid()
    try:
        with pytest.raises(RuntimeError):
            invoke()
    finally:
        comp._PID_PARENTS.pop(parent, None)
