#!/usr/bin/env python3
import sqlite3
import subprocess
import sys
from pathlib import Path

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


def test_scheduler_cli(tmp_path):
    workspace = tmp_path / "ws"
    db_dir = workspace / "databases"
    db_dir.mkdir(parents=True)
    master = db_dir / "master.db"
    replica = db_dir / "replica.db"
    extra_replica = db_dir / "extra.db"
    log_db = db_dir / "enterprise_assets.db"
    for db in (master, replica, extra_replica, log_db):
        with sqlite3.connect(db) as conn:
            conn.execute("CREATE TABLE t (id INTEGER)")
            conn.execute("INSERT INTO t (id) VALUES (1)")

    list_file = workspace / "list.md"
    list_file.write_text(f"- {replica.name}\n")
    extra_file = workspace / "extra.md"
    extra_file.write_text(f"- {extra_replica.name}\n")

    subprocess.check_call(
        [
            sys.executable,
            str(Path(__file__).resolve().parents[1] / "scripts/database/database_sync_scheduler.py"),
            "--workspace",
            str(workspace),
            "--master",
            master.name,
            "--list-file",
            str(list_file),
            "--add-documentation-sync",
            str(extra_file),
            "--target",
            master.name,
        ]
    )

    for db in (replica, extra_replica):
        with sqlite3.connect(db) as conn:
            assert conn.execute("SELECT COUNT(*) FROM t").fetchone()[0] == 1
