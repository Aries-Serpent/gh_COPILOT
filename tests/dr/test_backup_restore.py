from __future__ import annotations

import json
import sqlite3

from dr.backup_orchestrator import BackupOrchestrator


def test_backup_and_restore(tmp_path, monkeypatch):
    backup_root = tmp_path / "backups"
    analytics_db = tmp_path / "analytics.db"
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(backup_root))
    monkeypatch.setenv("ANALYTICS_DB", str(analytics_db))

    target = tmp_path / "data.txt"
    target.write_text("original", encoding="utf-8")

    orchestrator = BackupOrchestrator(analytics_db=analytics_db)
    manifest = orchestrator.pre_op_backup([target])

    target.write_text("modified", encoding="utf-8")
    orchestrator.restore(manifest)

    assert target.read_text(encoding="utf-8") == "original"

    with sqlite3.connect(analytics_db) as conn:
        rows = conn.execute("SELECT target, backup FROM rollback_logs").fetchall()

    assert len(rows) == 2
    assert any(r[0] == str(target) for r in rows)

    data = json.loads(manifest.read_text(encoding="utf-8"))
    assert data[str(target)]
