import sqlite3


from database_sync_scheduler import synchronize_databases


def test_synchronize_databases(tmp_path):
    master = tmp_path / "master.db"
    replica = tmp_path / "replica.db"
    with sqlite3.connect(master) as conn:
        conn.execute("CREATE TABLE t (id INTEGER)")
        conn.execute("INSERT INTO t (id) VALUES (1)")
    synchronize_databases(master, [replica])
    with sqlite3.connect(replica) as conn:
        cur = conn.execute("SELECT COUNT(*) FROM t")
        assert cur.fetchone()[0] == 1
