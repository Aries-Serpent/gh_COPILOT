from pathlib import Path


def test_main_invokes_helpers(monkeypatch, tmp_path):
    import scripts.database.har_ingestor as hi

    calls: list[str] = []

    monkeypatch.setattr(hi, "_log_event", lambda *a, **k: None)
    monkeypatch.setattr(
        hi.compliance,
        "validate_enterprise_operation",
        lambda *a, **k: calls.append("validate") or True,
    )
    monkeypatch.setattr(
        hi.compliance,
        "enforce_anti_recursion",
        lambda *a, **k: calls.append("enforce") or True,
    )
    monkeypatch.setattr(
        hi.compliance,
        "log_sync_operation",
        lambda *a, **k: calls.append("sync") or None,
        raising=False,
    )
    monkeypatch.setattr(
        hi.compliance,
        "log_event",
        lambda *a, **k: calls.append("event") or None,
        raising=False,
    )

    class DummyRes:
        inserted = skipped = errors = 0

    monkeypatch.setattr(hi, "ingest_har_entries", lambda *a, **k: DummyRes())

    hi.main(db=tmp_path / "db.sqlite", path=[tmp_path])

    assert {"validate", "enforce", "sync", "event"}.issubset(set(calls))

