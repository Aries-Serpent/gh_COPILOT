import pytest

from unified_session_management_system import prevent_recursion


def test_prevent_recursion_allows_single_call():
    @prevent_recursion
    def add_one(x: int) -> int:
        return x + 1

    assert add_one(1) == 2


def test_prevent_recursion_blocks_recursive_call():
    @prevent_recursion
    def recurse(n: int) -> int:
        return 0 if n == 0 else recurse(n - 1)

    with pytest.raises(RuntimeError):
        recurse(1)
