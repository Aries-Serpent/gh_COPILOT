import pytest

from utils.validation_utils import anti_recursion_guard, run_dual_copilot_validation


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
