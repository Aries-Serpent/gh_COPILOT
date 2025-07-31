import sqlite3
from pathlib import Path

from tools.cleanup import cleanup_obsolete_entries


def test_cleanup_obsolete_entries(tmp_path: Path, monkeypatch) -> None:
    db = tmp_path / "test.db"
    with sqlite3.connect(db) as conn:
        conn.execute("CREATE TABLE obsolete_table(id INTEGER)")
        conn.executemany("INSERT INTO obsolete_table(id) VALUES (?)", [(1,), (2,)])

    called = {"v": False}

    def dummy_validate(self, files):
        called["v"] = True
        return True

    monkeypatch.setattr(
        "secondary_copilot_validator.SecondaryCopilotValidator.validate_corrections",
        dummy_validate,
    )

    deleted, valid = cleanup_obsolete_entries(db)

    assert deleted == 2
    assert valid

    with sqlite3.connect(db) as conn:
        remaining = conn.execute("SELECT COUNT(*) FROM obsolete_table").fetchone()[0]
    assert remaining == 0
    assert called["v"]
