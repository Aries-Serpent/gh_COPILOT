"""Logging tests for the lightweight sync engine."""

import logging
import pytest
from src.sync.engine import Change, SyncEngine


def _change() -> Change:
    return Change(id="c", payload={}, timestamp=0.0)


def test_propagate_logs_start_and_end(caplog):
    engine = SyncEngine()
    engine.notify_change(_change())

    with caplog.at_level(logging.INFO, logger="sync"):
        engine.propagate(lambda _: None)

    assert caplog.messages == ["start", "end"]


def test_propagate_logs_error(caplog):
    engine = SyncEngine()
    engine.notify_change(_change())

    def send(_: Change) -> None:
        raise RuntimeError("boom")

    with caplog.at_level(logging.INFO, logger="sync"):
        with pytest.raises(RuntimeError):
            engine.propagate(send)

    assert caplog.messages == ["start", "error"]


def test_apply_remote_change_logs_start_and_end(caplog):
    engine = SyncEngine()
    change = _change()

    def apply(_: Change) -> None:
        return None

    with caplog.at_level(logging.INFO, logger="sync"):
        assert engine.apply_remote_change(change, apply)

    assert caplog.messages == ["start", "end"]


def test_apply_remote_change_logs_error(caplog):
    engine = SyncEngine()
    change = _change()

    def apply(_: Change) -> None:
        raise RuntimeError("boom")

    with caplog.at_level(logging.INFO, logger="sync"):
        with pytest.raises(RuntimeError):
            engine.apply_remote_change(change, apply)

    assert caplog.messages == ["start", "error"]

