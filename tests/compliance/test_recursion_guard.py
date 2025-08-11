import os
import sqlite3

import enterprise_modules.compliance as comp


def test_pid_tracking_and_cleanup(monkeypatch, tmp_path):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    comp._PID_PARENTS.clear()
    comp._PID_CHILDREN.clear()

    @comp.anti_recursion_guard
    def sample():
        pid = os.getpid()
        ppid = os.getppid()
        assert comp._PID_PARENTS[pid] == ppid
        assert pid in comp._PID_CHILDREN[ppid]
        return "ok"

    assert sample() == "ok"
    pid = os.getpid()
    ppid = os.getppid()
    assert pid not in comp._PID_PARENTS
    assert ppid not in comp._PID_CHILDREN or pid not in comp._PID_CHILDREN[ppid]


def test_detect_recursion_records_parent_pid(monkeypatch, tmp_path):
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    assert comp._detect_recursion(tmp_path) is False
    db = tmp_path / "databases" / "analytics.db"
    with sqlite3.connect(db) as conn:
        parents = [row[0] for row in conn.execute("SELECT parent_pid FROM recursion_pid_log").fetchall()]
    assert parents and all(p == os.getppid() for p in parents)
