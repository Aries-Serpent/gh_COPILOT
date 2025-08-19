from __future__ import annotations

import pytest

from database_first_synchronization_engine import ConflictPolicy, TimestampConflictPolicy


def test_conflict_policy_is_abstract() -> None:
    with pytest.raises(TypeError):
        ConflictPolicy()  # type: ignore[abstract]


def test_timestamp_policy_picks_latest() -> None:
    policy = TimestampConflictPolicy()
    row_a = {"updated_at": 1, "value": "a"}
    row_b = {"updated_at": 2, "value": "b"}
    assert policy.resolve("tbl", row_a, row_b) == row_b
