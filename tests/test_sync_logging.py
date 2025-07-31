import sqlite3
from pathlib import Path
from template_engine import template_synchronizer


def create_db(path: Path) -> None:
    with sqlite3.connect(path) as conn:
        conn.execute("CREATE TABLE templates (name TEXT PRIMARY KEY, template_content TEXT)")
        conn.execute("INSERT INTO templates VALUES ('t', 'x')")


def test_sync_logs_violation_and_rollback(tmp_path, monkeypatch):
    db = tmp_path / "a.db"
    create_db(db)
    analytics = tmp_path / "analytics.db"
    monkeypatch.setattr(template_synchronizer, "ANALYTICS_DB", analytics)
    events = []
    monkeypatch.setattr(
        template_synchronizer, "log_event_simulation", lambda evt, **kw: events.append((kw.get("table"), evt))
    )
    monkeypatch.setattr(template_synchronizer, "_compliance_check", lambda *_: False)
    template_synchronizer.synchronize_templates_real([db])
    assert any(t == "violation_logs" for t, _ in events)
    assert any(t == "rollback_logs" for t, _ in events)
