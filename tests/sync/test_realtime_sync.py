from src.sync.engine import Change, SyncEngine


def test_change_listener_and_queue():
    engine = SyncEngine()
    heard = []
    engine.register_listener(lambda c: heard.append(c))
    change = Change(id="1", payload={"x": 1}, timestamp=0.0)
    engine.notify_change(change)
    assert heard == [change]
    assert list(engine.outgoing) == [change]


def test_outgoing_queue_propagation():
    engine = SyncEngine()
    change = Change(id="2", payload={}, timestamp=0.0)
    engine.notify_change(change)
    sent = []
    engine.propagate(lambda c: sent.append(c))
    assert sent == [change]
    assert not engine.outgoing


def test_remote_change_idempotency_and_conflict():
    engine = SyncEngine()
    applied = []
    change = Change(id="3", payload={}, timestamp=0.0)

    def apply(c: Change) -> None:
        applied.append(c)

    assert engine.apply_remote_change(change, apply)
    assert applied == [change]
    assert not engine.apply_remote_change(change, apply)
    assert applied == [change]

    change2 = Change(id="4", payload={}, timestamp=0.0)

    def conflict_detector(_: Change) -> bool:
        return True

    assert not engine.apply_remote_change(change2, apply, conflict_detector)
    assert change2 not in applied
    assert not engine.apply_remote_change(change2, apply, conflict_detector)
