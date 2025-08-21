import os
import sqlite3
import threading
import time
import tempfile


def test_busy_timeout_reduces_lock_errors(monkeypatch):
    monkeypatch.setenv("BUSY_TIMEOUT_MS", "1000")

    with tempfile.NamedTemporaryFile(suffix=".db", delete=True) as tmp:
        db_path = tmp.name

        writer = sqlite3.connect(db_path, timeout=0)
        wc = writer.cursor()
        wc.execute("CREATE TABLE IF NOT EXISTS t(x)")
        writer.commit()

        rw = sqlite3.connect(db_path, timeout=0)
        rc = rw.cursor()
        rc.execute(f"PRAGMA busy_timeout={os.getenv('BUSY_TIMEOUT_MS')}")

        def hold_lock():
            w2 = sqlite3.connect(db_path, timeout=0)
            c2 = w2.cursor()
            c2.execute("BEGIN IMMEDIATE")
            c2.execute("INSERT INTO t(x) VALUES(1)")
            time.sleep(0.5)
            w2.commit()
            w2.close()

        th = threading.Thread(target=hold_lock)
        th.start()
        time.sleep(0.1)

        failed = False
        try:
            rc.execute("INSERT INTO t(x) VALUES(2)")
            rw.commit()
        except sqlite3.OperationalError as e:
            failed = "locked" in str(e).lower()

        th.join()
        rw.close()
        writer.close()

        assert failed is False
