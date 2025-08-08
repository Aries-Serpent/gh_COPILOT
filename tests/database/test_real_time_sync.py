import sqlite3
import threading
import time

from src.database.engine import Engine


def _setup_db(path):
    conn = sqlite3.connect(path)
    conn.execute(
        "CREATE TABLE items(id INTEGER PRIMARY KEY, value TEXT, updated_at REAL)"
    )
    conn.commit()
    conn.close()


def test_real_time_sync_concurrent_updates(tmp_path):
    db_a = tmp_path / "a.db"
    db_b = tmp_path / "b.db"
    _setup_db(db_a)
    _setup_db(db_b)

    engine_a = Engine(db_a)
    engine_b = Engine(db_b)
    engine_a.install_triggers("items")
    engine_b.install_triggers("items")

    events_a = []
    events_b = []
    engine_a.stream.register(lambda op, tbl, row: events_a.append((op, row["value"])))
    engine_b.stream.register(lambda op, tbl, row: events_b.append((op, row["value"])))

    def update_a():
        with engine_a.conn:
            engine_a.conn.execute(
                "INSERT INTO items(id, value, updated_at) VALUES (1, 'A1', 1)"
            )

    def update_b():
        time.sleep(0.1)
        with engine_b.conn:
            engine_b.conn.execute(
                "INSERT INTO items(id, value, updated_at) VALUES (1, 'B1', 2)"
            )

    t1 = threading.Thread(target=update_a)
    t2 = threading.Thread(target=update_b)
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    engine_a.sync_with(engine_b)

    with engine_a.conn:
        value_a = engine_a.conn.execute(
            "SELECT value FROM items WHERE id=1"
        ).fetchone()[0]
    with engine_b.conn:
        value_b = engine_b.conn.execute(
            "SELECT value FROM items WHERE id=1"
        ).fetchone()[0]

    assert value_a == "B1"
    assert value_b == "B1"
    assert any(op == "insert" for op, _ in events_a)
    assert any(op == "insert" for op, _ in events_b)

