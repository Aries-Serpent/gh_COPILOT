import shutil
import sqlite3

import scripts.wlc_session_manager as wsm


def test_main_inserts_session(tmp_path, monkeypatch):
    temp_db = tmp_path / "production.db"
    shutil.copy(wsm.DB_PATH, temp_db)
    monkeypatch.setattr(wsm, "DB_PATH", temp_db)
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(tmp_path / "backups"))
    with sqlite3.connect(temp_db) as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM unified_wrapup_sessions")
        before = cur.fetchone()[0]
    wsm.main()
    with sqlite3.connect(temp_db) as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM unified_wrapup_sessions")
        after = cur.fetchone()[0]
        cur.execute(
            "SELECT compliance_score FROM unified_wrapup_sessions ORDER BY rowid DESC LIMIT 1"
        )
        score = cur.fetchone()[0]
    assert after == before + 1
    assert abs(score - 1.0) < 1e-6
