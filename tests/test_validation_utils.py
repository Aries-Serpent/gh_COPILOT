import time
from threading import Thread

import pytest
import utils.validation_utils as validation_utils

from utils.validation_utils import (
    anti_recursion_guard,
    run_dual_copilot_validation,
)


def test_anti_recursion_guard_prevents_recursion():
    calls = []

    @anti_recursion_guard
    def recurse(n: int) -> int:
        calls.append(n)
        if n > 0:
            recurse(n - 1)
        return len(calls)

    with pytest.raises(RuntimeError):
        recurse(1)


def test_anti_recursion_guard_cleans_lock_on_concurrent_invocation():
    calls = []

    @anti_recursion_guard
    def slow() -> None:
        calls.append("run")
        time.sleep(0.1)

    thread = Thread(target=slow)
    thread.start()
    time.sleep(0.02)
    with pytest.raises(RuntimeError):
        slow()
    thread.join()

    lock_file = validation_utils._LOCK_DIR / f"{slow.__name__}.lock"
    assert not lock_file.exists()


def test_run_dual_copilot_validation_executes_both():
    order = []

    def primary() -> bool:
        order.append("primary")
        return True

    def secondary() -> bool:
        order.append("secondary")
        return True

    assert run_dual_copilot_validation(primary, secondary) is True
    assert order == ["primary", "secondary"]


def test_dual_copilot_runs_secondary_even_if_primary_fails():
    order = []

    def primary() -> bool:
        order.append("primary")
        return False

    def secondary() -> bool:
        order.append("secondary")
        return True

    assert run_dual_copilot_validation(primary, secondary) is False
    assert order == ["primary", "secondary"]
