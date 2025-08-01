from pathlib import Path
import shutil
import sqlite3

from scripts.ensure_enhanced_lessons_learned_table import (
    ensure_enhanced_lessons_learned_table,
    TABLE_NAME,
)


def test_table_created_when_missing(tmp_path):
    prod_src = Path("databases/production.db")
    ref_src = Path("databases/learning_monitor.db")

    prod_db = tmp_path / "production.db"
    ref_db = tmp_path / "learning_monitor.db"
    shutil.copy(prod_src, prod_db)
    shutil.copy(ref_src, ref_db)

    # Ensure table is absent
    with sqlite3.connect(prod_db) as conn:
        conn.execute(f"DROP TABLE IF EXISTS {TABLE_NAME}")

    assert ensure_enhanced_lessons_learned_table(prod_db, ref_db)

    with sqlite3.connect(prod_db) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name=?",
            (TABLE_NAME,),
        )
        prod_sql = cur.fetchone()[0]

    with sqlite3.connect(ref_db) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name=?",
            (TABLE_NAME,),
        )
        ref_sql = cur.fetchone()[0]

    assert prod_sql == ref_sql

