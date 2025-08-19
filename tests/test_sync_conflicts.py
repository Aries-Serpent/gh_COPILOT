import os
import sqlite3
import tempfile

from database_first_synchronization_engine import SyncManager, LastWriteWinsPolicy


def _mk_db(schema_sql, rows):
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.executescript(schema_sql)
    for t, rs in rows.items():
        if rs:
            cols = rs[0].keys()
            cur.executemany(
                f"INSERT INTO {t} ({','.join(cols)}) VALUES ({','.join(['?']*len(cols))})",
                [tuple(r[c] for c in cols) for r in rs],
            )
    conn.commit()
    conn.close()
    return path


def test_conflicting_rows_synchronize(tmp_path):
    schema = (
        "CREATE TABLE items(" "id INTEGER PRIMARY KEY, name TEXT, updated_at INTEGER);"
    )
    db_a = _mk_db(schema, {"items": [{"id": 1, "name": "old", "updated_at": 1}]})
    db_b = _mk_db(schema, {"items": [{"id": 1, "name": "new", "updated_at": 2}]})
    fd, analytics = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    sqlite3.connect(analytics).close()

    try:
        manager = SyncManager(analytics_db=analytics)
        manager.sync(db_a, db_b, policy=LastWriteWinsPolicy())
        with sqlite3.connect(db_a) as ca, sqlite3.connect(db_b) as cb:
            name_a = ca.execute("SELECT name FROM items WHERE id=1").fetchone()[0]
            name_b = cb.execute("SELECT name FROM items WHERE id=1").fetchone()[0]
        assert name_a == name_b == "new"
    finally:
        os.remove(db_a)
        os.remove(db_b)
        os.remove(analytics)

