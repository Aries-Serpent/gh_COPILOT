import pathlib
import sqlite3

import importlib.util

UDRS_PATH = pathlib.Path("unified_disaster_recovery_system.py")

spec = importlib.util.spec_from_file_location("udrs", UDRS_PATH)
udrs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(udrs)  # type: ignore


def test_backup_and_verify(tmp_path):
    src = tmp_path / "data"
    dest = tmp_path / "backup"
    db = tmp_path / "analytics.db"

    src.mkdir()
    (src / "file.txt").write_text("hello")

    logger = udrs.AnalyticsLogger(str(db))
    assert udrs._dr_create_backup(str(src), str(dest), logger)
    assert udrs._dr_verify_backup(str(dest), logger)
    assert (dest / "file.txt").exists()

    con = sqlite3.connect(db)
    with con:
        count = con.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    assert count >= 2


def test_restore_and_rollback(tmp_path):
    original = tmp_path / "original"
    backup = tmp_path / "backup"
    dest = tmp_path / "dest"
    db = tmp_path / "analytics.db"

    original.mkdir()
    (original / "a.txt").write_text("A")

    logger = udrs.AnalyticsLogger(str(db))
    assert udrs._dr_create_backup(str(original), str(backup), logger)

    dest.mkdir()
    (dest / "a.txt").write_text("DIFF")

    assert udrs._dr_restore_from_backup(str(backup), str(dest), logger)
    assert (dest / "a.txt").read_text() == "A"

    (dest / "a.txt").write_text("BROKEN")
    assert udrs._dr_rollback(str(backup), str(dest), logger)
    assert (dest / "a.txt").read_text() == "A"

