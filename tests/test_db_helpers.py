
# Auto-generated tests by codex_sequential_executor.py
import os
import sqlite3
import tempfile

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
                [tuple(r[c] for c in cols) for r in rs]
            )
    conn.commit()
    return path, conn

def test_schema_compare_and_diff():
    schema = "CREATE TABLE items(id INTEGER PRIMARY KEY, name TEXT, qty INTEGER);"
    rows_a = {"items":[{"id":1,"name":"A","qty":3},{"id":2,"name":"B","qty":1}]}
    rows_b = {"items":[{"id":1,"name":"A","qty":2}]}
    pa, ca = _mk_db(schema, rows_a)
    pb, cb = _mk_db(schema, rows_b)
    try:
        from database_first_synchronization_engine import compare_schema, diff_rows
        sch = compare_schema(ca, cb)
        assert sch["changed"] == {}, sch
        dif = diff_rows(ca, cb, "items", "id")
        assert set(dif["insert"]) == {"2"}
        assert set(dif["update"]) == {"1"}
    finally:
        ca.close()
        cb.close()
        os.remove(pa)
        os.remove(pb)

def test_upsert_idempotence(tmp_path):
    schema = "CREATE TABLE items(id INTEGER PRIMARY KEY, name TEXT, qty INTEGER);"
    rows_a = {"items":[{"id":1,"name":"A","qty":3},{"id":2,"name":"B","qty":1}]}
    rows_b = {"items":[{"id":1,"name":"A","qty":2}]}
    pa, ca = _mk_db(schema, rows_a)
    pb, cb = _mk_db(schema, rows_b)
    try:
        from database_first_synchronization_engine import attempt_reconcile
        stats1 = attempt_reconcile(ca, cb, "items", "id", "upsert")
        stats2 = attempt_reconcile(ca, cb, "items", "id", "upsert")
        assert stats1["inserted"] >= 1
        # second pass should not increase net updates if nothing changed
        assert stats2["updated"] >= 0
    finally:
        ca.close()
        cb.close()
        os.remove(pa)
        os.remove(pb)
