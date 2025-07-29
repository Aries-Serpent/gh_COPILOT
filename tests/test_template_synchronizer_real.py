import sqlite3
from pathlib import Path

from template_engine import template_synchronizer


def create_db(path: Path, templates: dict[str, str]) -> None:
    with sqlite3.connect(path) as conn:
        conn.execute("CREATE TABLE templates (name TEXT PRIMARY KEY, template_content TEXT)")
        conn.executemany(
            "INSERT INTO templates (name, template_content) VALUES (?, ?)",
            list(templates.items()),
        )


def test_synchronize_templates_real(tmp_path: Path, monkeypatch) -> None:
    db_a = tmp_path / "a.db"
    db_b = tmp_path / "b.db"
    analytics = tmp_path / "analytics.db"
    create_db(db_a, {"t1": "foo"})
    create_db(db_b, {})
    monkeypatch.setattr(template_synchronizer, "ANALYTICS_DB", analytics)
    synced = template_synchronizer.synchronize_templates_real([db_a, db_b])
    assert synced == 2

    with sqlite3.connect(db_b) as conn:
        rows = conn.execute("SELECT name, template_content FROM templates ORDER BY name").fetchall()
        assert rows == [("t1", "foo")]

    with sqlite3.connect(analytics) as conn:
        count = conn.execute("SELECT COUNT(*) FROM sync_events_log").fetchone()[0]
        assert count >= 3


class DummyValidator:
    def __init__(self):
        self.called = False

    def validate_corrections(self, files):
        self.called = True
        return True


def test_validator_called(tmp_path: Path, monkeypatch) -> None:
    db_a = tmp_path / "a.db"
    db_b = tmp_path / "b.db"
    analytics = tmp_path / "analytics.db"
    create_db(db_a, {"t1": "foo"})
    create_db(db_b, {})
    monkeypatch.setattr(template_synchronizer, "ANALYTICS_DB", analytics)
    dummy = DummyValidator()
    monkeypatch.setattr(template_synchronizer, "SecondaryCopilotValidator", lambda: dummy)
    template_synchronizer.synchronize_templates_real([db_a, db_b])
    assert dummy.called


def test_validator_failure(tmp_path: Path, monkeypatch) -> None:
    class FailValidator(DummyValidator):
        def validate_corrections(self, files):
            self.called = True
            return False

    db_a = tmp_path / "a.db"
    db_b = tmp_path / "b.db"
    analytics = tmp_path / "analytics.db"
    create_db(db_a, {"t1": "foo"})
    create_db(db_b, {})
    monkeypatch.setattr(template_synchronizer, "ANALYTICS_DB", analytics)
    dummy = FailValidator()
    monkeypatch.setattr(template_synchronizer, "SecondaryCopilotValidator", lambda: dummy)
    template_synchronizer.synchronize_templates_real([db_a, db_b])
    assert dummy.called
