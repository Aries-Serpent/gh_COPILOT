import json
import sqlite3

from scripts.disaster_recovery import run_restore_drill


def test_run_restore_drill_generates_report(tmp_path, monkeypatch):
    db_path = tmp_path / "analytics.db"
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE rollback_logs (target TEXT, backup TEXT, timestamp TEXT)")
    backup = tmp_path / "backup.sqlite"
    backup.write_text("data")
    conn.execute(
        "INSERT INTO rollback_logs VALUES (?, ?, ?)",
        ("db.sqlite", str(backup), "2024-01-01T00:00:00"),
    )
    conn.commit()
    conn.close()

    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(tmp_path))
    monkeypatch.setattr(run_restore_drill, "validate_enterprise_operation", lambda: None)

    called = {}

    def fake_update(payload):
        called["payload"] = payload

    monkeypatch.setattr(run_restore_drill, "_update_dashboard", fake_update)

    report = run_restore_drill.run_restore_drill(db_path, sample_size=1)
    data = json.loads(report.read_text())

    assert data["sampled"][0]["restored"] is True
    assert called["payload"]["drill_sampled"] == 1
