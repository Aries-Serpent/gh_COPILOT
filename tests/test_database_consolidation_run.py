import logging
import sqlite3
from pathlib import Path

from scripts.database import database_consolidation_migration as dcm


def test_run_dual_validation(tmp_path: Path, monkeypatch, caplog) -> None:
    db_dir = tmp_path / "databases"
    db_dir.mkdir()
    target = db_dir / "analytics.db"
    with sqlite3.connect(target):
        pass
    for name in dcm.ANALYTICS_SOURCES:
        src = db_dir / name
        with sqlite3.connect(src) as conn:
            conn.execute("CREATE TABLE t (id INTEGER)")
            conn.execute("INSERT INTO t (id) VALUES (1)")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(dcm, "ensure_db_reference", lambda path: True)
    monkeypatch.setattr(dcm, "validate_enterprise_operation", lambda path=None: True)

    class DummyValidator:
        def __init__(self, logger=None):
            pass

        def validate_corrections(self, files):
            logging.info("SECONDARY validation executed")
            return True

    monkeypatch.setattr(dcm, "SecondaryCopilotValidator", DummyValidator)
    caplog.set_level(logging.INFO)
    dcm.run()
    logs = caplog.text
    assert "PRIMARY VALIDATION" in logs
    assert "SECONDARY validation executed" in logs
