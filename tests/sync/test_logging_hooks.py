from __future__ import annotations

import pytest

from src.sync.engine import Change, SyncEngine


def test_propagate_logging(tmp_path) -> None:
    events: list[tuple[str, dict]] = []
    engine = SyncEngine(log_hook=lambda e, ctx: events.append((e, ctx)))
    change = Change(id="1", payload={}, timestamp=0.0)
    engine.notify_change(change)
    engine.propagate(lambda c: None)
    assert events[0][0] == "propagate.start"
    assert events[-1][0] == "propagate.end"
    assert events[-1][1].get("sent") == 1


def test_propagate_logging_error() -> None:
    events: list[tuple[str, dict]] = []
    engine = SyncEngine(log_hook=lambda e, ctx: events.append((e, ctx)))
    change = Change(id="1", payload={}, timestamp=0.0)
    engine.notify_change(change)

    def send(_: Change) -> None:  # pragma: no cover - raised for logging
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError):
        engine.propagate(send)
    assert any(e == "propagate.error" for e, _ in events)


def test_apply_logging() -> None:
    events: list[tuple[str, dict]] = []
    engine = SyncEngine(log_hook=lambda e, ctx: events.append((e, ctx)))
    change = Change(id="1", payload={}, timestamp=0.0)

    def apply(_: Change) -> None:
        pass

    assert engine.apply_remote_change(change, apply)
    assert events[0][0] == "apply.start"
    assert events[-1][0] == "apply.end"
    assert events[-1][1].get("status") == "applied"


def test_apply_logging_error() -> None:
    events: list[tuple[str, dict]] = []
    engine = SyncEngine(log_hook=lambda e, ctx: events.append((e, ctx)))
    change = Change(id="1", payload={}, timestamp=0.0)

    def apply(_: Change) -> None:  # pragma: no cover - raised for logging
        raise ValueError("bad")

    with pytest.raises(ValueError):
        engine.apply_remote_change(change, apply)
    assert any(e == "apply.error" for e, _ in events)

