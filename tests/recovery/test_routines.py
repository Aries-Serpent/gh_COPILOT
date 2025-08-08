from __future__ import annotations

import sqlite3

from src.recovery import routines


def test_reconnect_database_retry():
    attempts: list[int] = []

    def factory() -> sqlite3.Connection:
        if len(attempts) < 2:
            attempts.append(1)
            raise RuntimeError("fail")
        return sqlite3.connect(":memory:")

    conn = routines.reconnect_database(factory, attempts=3, delay=0)
    assert isinstance(conn, sqlite3.Connection)
    assert len(attempts) == 2


def test_retry_sync_success_after_failures():
    calls: list[int] = []

    def action() -> str:
        if len(calls) < 1:
            calls.append(1)
            raise ValueError("boom")
        return "ok"

    assert routines.retry_sync(action, attempts=2, delay=0) == "ok"
    assert len(calls) == 1


def test_handle_alerts_triggers_recovery():
    models = {"m": (0.0, 1.0)}
    metrics = {"m": 5.0}  # z-score 5 -> anomaly

    conn = sqlite3.connect(":memory:")

    factory_calls: list[int] = []

    def factory() -> sqlite3.Connection:
        factory_calls.append(1)
        return sqlite3.connect(":memory:")

    sync_calls: list[int] = []

    def sync_action() -> None:
        sync_calls.append(1)

    result = routines.handle_alerts(models, metrics, [conn], factory, sync_action)
    assert result == {"reconnects": 1, "sync_retries": 1}
    assert len(factory_calls) == 1
    assert len(sync_calls) == 1


def test_restart_service_executes_callback():
    calls: list[int] = []

    def restart() -> None:
        calls.append(1)

    assert routines.restart_service(restart)
    assert calls == [1]


def test_revert_state_handles_error():
    def revert() -> None:
        raise RuntimeError("boom")

    assert routines.revert_state(revert) is False
