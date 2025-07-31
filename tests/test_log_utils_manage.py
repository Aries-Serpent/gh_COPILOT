import logging
from utils.log_utils import (
    _clear_log,
    _list_events,
    ensure_tables,
    log_event,
    sse_event_stream,
    start_websocket_broadcast,
)


def test_list_and_clear(tmp_path, monkeypatch):
    monkeypatch.setenv("GH_COPILOT_TEST_MODE", "0")
    db = tmp_path / "events.db"
    ensure_tables(db, ["violation_logs"], test_mode=False)
    for i in range(3):
        log_event({"details": str(i)}, table="violation_logs", db_path=db)
    events = _list_events("violation_logs", db_path=db, order="ASC", test_mode=False)
    assert len(events) == 3
    assert events[0]["details"] == "0"
    assert _clear_log("violation_logs", db_path=db, test_mode=False)
    assert _list_events("violation_logs", db_path=db, test_mode=False) == []


def test_sse_category(tmp_path):
    db = tmp_path / "sse.db"
    ensure_tables(db, ["violation_logs"], test_mode=False)
    log_event({"details": "a"}, table="violation_logs", db_path=db)
    gen = sse_event_stream("violation_logs", db_path=db, poll_interval=0.01)
    first = next(gen)
    assert "event: violation_logs" in first
    assert "data:" in first


def test_websocket_broadcast_skips(monkeypatch, caplog):
    monkeypatch.setenv("LOG_WEBSOCKET_ENABLED", "1")
    import builtins as blt

    orig_import = blt.__import__

    def fake_import(name, *args, **kwargs):
        if name == "websockets":
            raise ImportError
        return orig_import(name, *args, **kwargs)

    monkeypatch.setattr(blt, "__import__", fake_import)
    with caplog.at_level(logging.WARNING):
        start_websocket_broadcast(port=8766)
    assert any("websockets package not available" in rec.getMessage() for rec in caplog.records)
    monkeypatch.setattr(blt, "__import__", orig_import)
