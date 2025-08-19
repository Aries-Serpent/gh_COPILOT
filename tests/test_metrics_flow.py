import sqlite3
import pytest


def _build_db(path):
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE IF NOT EXISTS metrics(metric TEXT, value REAL)")
    con.execute("INSERT INTO metrics(metric, value) VALUES ('total_errors', 0)")
    con.execute("INSERT INTO metrics(metric, value) VALUES ('critical_alerts', 0)")
    con.commit()
    con.close()


def test_no_halt(tmp_path):
    db = tmp_path / "ok.db"
    _build_db(str(db))
    con = sqlite3.connect(str(db))
    con.row_factory = sqlite3.Row
    cur = con.execute("SELECT metric, value FROM metrics")
    metrics = {r['metric']: float(r['value']) for r in cur.fetchall()}
    con.close()
    assert not any(v >= 1.0 for v in metrics.values())


def test_halt(tmp_path):
    db = tmp_path / "bad.db"
    _build_db(str(db))
    con = sqlite3.connect(str(db))
    con.execute("UPDATE metrics SET value=2 WHERE metric='total_errors'")
    con.commit()
    con.close()
    con = sqlite3.connect(str(db))
    cur = con.execute("SELECT metric, value FROM metrics")
    metrics = {r[0]: float(r[1]) for r in cur.fetchall()}
    con.close()
    assert metrics['total_errors'] >= 1.0

