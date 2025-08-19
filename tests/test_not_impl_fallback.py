from __future__ import annotations

import logging

from codex_sequential_executor import _not_impl


def test_not_impl_returns_input_and_logs(caplog) -> None:
    with caplog.at_level(logging.WARNING):
        result = _not_impl("missing", example_input=42)
    assert result == 42
    assert "missing" in caplog.text
