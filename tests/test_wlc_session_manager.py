import shutil
import sqlite3

import scripts.wlc_session_manager as wsm


class DummyValidator:
    def __init__(self, logger=None):
        self.called = False

    def validate_corrections(self, files):
        self.called = True
        return True


def test_main_inserts_session(tmp_path, monkeypatch):
    temp_db = tmp_path / "production.db"
    shutil.copy(wsm.DB_PATH, temp_db)
    monkeypatch.setattr(wsm, "DB_PATH", temp_db)
    backup_root = tmp_path / "backups"
    monkeypatch.setenv("GH_COPILOT_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("GH_COPILOT_BACKUP_ROOT", str(backup_root))
    dummy = DummyValidator()
    monkeypatch.setattr(wsm, "SecondaryCopilotValidator", lambda: dummy)
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
    assert dummy.called
    log_files = list((backup_root / "logs").glob("wlc_*.log"))
    assert log_files
