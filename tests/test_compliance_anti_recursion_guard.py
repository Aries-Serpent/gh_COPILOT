import os
import threading
import time

import pytest

from enterprise_modules.compliance import anti_recursion_guard, MAX_RECURSION_DEPTH


def test_guard_aborts_on_nested_directories(tmp_path):
    """The guard aborts when recursion depth exceeds the limit."""

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


def test_guard_aborts_on_duplicate_pid():
    """Concurrent invocation by the same PID triggers early abort."""

    @anti_recursion_guard
    def slow_call():
        time.sleep(0.2)

    t = threading.Thread(target=slow_call)
    t.start()
    time.sleep(0.05)
    with pytest.raises(RuntimeError):
        slow_call()
    t.join()


def test_guard_allows_single_invocation():
    """Single invocation proceeds normally and records parent-child PID."""

    @anti_recursion_guard
    def hello():
        return "ok"

    assert hello() == "ok"


def test_guard_aborts_on_pid_loop():
    """Artificial parent/child PID loop triggers early abort."""

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
