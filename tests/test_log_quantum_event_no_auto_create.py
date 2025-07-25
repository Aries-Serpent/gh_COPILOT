import quantum_algorithm_library_expansion as qale


def test_log_quantum_event_does_not_create_db(tmp_path, monkeypatch):
    db = tmp_path / "analytics.db"
    monkeypatch.setattr(qale, "ANALYTICS_DB", db)

    if db.exists():
        db.unlink()

    qale.log_quantum_event("test", "desc")
    assert not db.exists(), "analytics.db should not be created automatically"

