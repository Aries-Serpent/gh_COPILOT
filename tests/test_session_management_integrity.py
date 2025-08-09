import pytest
import unified_session_management_system as usm
from unified_session_management_system import prevent_recursion


def test_prevent_recursion_allows_single_call():
    @prevent_recursion
    def add_one(x: int) -> int:
        return x + 1

    assert add_one(1) == 2


def test_prevent_recursion_blocks_recursive_call(monkeypatch):
    monkeypatch.setattr(usm, "record_codex_action", lambda *a, **k: None)

    @prevent_recursion
    def recurse(n: int) -> int:
        return 0 if n == 0 else recurse(n - 1)

    with pytest.raises(RuntimeError):
        recurse(1)


def test_prevent_recursion_logs(monkeypatch):
    calls = []
    monkeypatch.setattr(
        usm, "record_codex_action", lambda *args: calls.append(args)
    )

    @usm.prevent_recursion
    def recurse(n: int = 0) -> None:
        if n == 0:
            recurse(n + 1)

    with pytest.raises(RuntimeError):
        recurse()
    assert any(a[1] == "anti_recursion_triggered" for a in calls)
