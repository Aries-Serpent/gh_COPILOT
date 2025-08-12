#!/usr/bin/env python3
"""Tests for quantum_optimization module."""

import logging
from typing import Any, Dict, List


from ghc_quantum.quantum_optimization import EnterpriseUtility


class DummyTqdm:
    """Minimal tqdm replacement for testing."""

    def __init__(self, *args: Any, total: int, desc: str, leave: bool = False, **kwargs: Any) -> None:
        self.total = total
        self.desc = desc
        self.leave = leave
        self.updates = 0
        self.postfixes: List[Dict[str, str]] = []

    def __enter__(self) -> "DummyTqdm":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        pass

    def update(self, n: int = 1) -> None:
        self.updates += n

    def set_postfix(self, data: Dict[str, str]) -> None:
        self.postfixes.append(data)


def test_progress_logging(monkeypatch, caplog):
    """Ensure progress and PID are logged with tqdm integration."""

    bars: List[DummyTqdm] = []

    def dummy_tqdm(*args: Any, **kwargs: Any) -> DummyTqdm:
        bar = DummyTqdm(*args, **kwargs)
        bars.append(bar)
        return bar

    monkeypatch.setattr("ghc_quantum.quantum_optimization.tqdm", dummy_tqdm)
    monkeypatch.setattr("ghc_quantum.quantum_optimization.os.getpid", lambda: 1234)

    util = EnterpriseUtility()

    with caplog.at_level(logging.INFO):
        assert util.execute_utility(iterations=3) is True

    assert bars and bars[0].updates == 3
    assert len(bars[0].postfixes) == 3
    assert any("PID: 1234" in rec.getMessage() for rec in caplog.records)
    step_logs = [rec for rec in caplog.records if "Step" in rec.getMessage()]
    assert len(step_logs) == 3
