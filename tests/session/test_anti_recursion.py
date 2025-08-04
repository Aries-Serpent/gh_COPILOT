import pytest
from scripts.session.anti_recursion_enforcer import (
    AntiRecursionEnforcer,
    anti_recursion_guard,
)


def test_decorator_blocks_on_recursion(monkeypatch):
    calls = []

    def fake_enforce(self, current_pid=None):
        calls.append("check")
        raise RuntimeError("recursion")

    monkeypatch.setattr(
        AntiRecursionEnforcer,
        "enforce_no_recursion",
        fake_enforce,
    )

    @anti_recursion_guard
    def wrapped():
        calls.append("run")

    with pytest.raises(RuntimeError):
        wrapped()
    assert calls == ["check"]


def test_decorator_allows_single_call(monkeypatch):
    calls = []

    def fake_enforce(self, current_pid=None):
        calls.append("check")

    monkeypatch.setattr(
        AntiRecursionEnforcer,
        "enforce_no_recursion",
        fake_enforce,
    )

    @anti_recursion_guard
    def wrapped():
        calls.append("run")
        return "ok"

    assert wrapped() == "ok"
    assert calls == ["check", "run"]


def test_decorator_prevents_reentrancy():
    @anti_recursion_guard
    def recur():
        recur()

    with pytest.raises(RuntimeError):
        recur()
