#!/usr/bin/env python3
import sqlite3

from scripts.database.database_sync_scheduler import synchronize_databases
from scripts.database.unified_database_initializer import initialize_database


def test_synchronize_databases(tmp_path):
    master = tmp_path / "master.db"
    replica = tmp_path / "replica.db"
    log_db = tmp_path / "enterprise_assets.db"
    initialize_database(log_db)
    with sqlite3.connect(master) as conn:
        conn.execute("CREATE TABLE t (id INTEGER)")
        conn.execute("INSERT INTO t (id) VALUES (1)")
    synchronize_databases(master, [replica], log_db=log_db)
    with sqlite3.connect(replica) as conn:
        cur = conn.execute("SELECT COUNT(*) FROM t")
        assert cur.fetchone()[0] == 1
    with sqlite3.connect(log_db) as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM cross_database_sync_operations"
        ).fetchone()[0]
    assert count >= 2
