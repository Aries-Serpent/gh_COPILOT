import sqlite3
import threading
import time

from db.engine.sync import SyncEngine


def test_bidirectional_concurrent_sync():
    """Concurrent inserts and updates are propagated both ways."""
    src = sqlite3.connect(":memory:", check_same_thread=False)
    dst = sqlite3.connect(":memory:", check_same_thread=False)

    src.execute("CREATE TABLE items (id INTEGER PRIMARY KEY, value TEXT)")
    dst.execute("CREATE TABLE items (id INTEGER PRIMARY KEY, value TEXT)")

    engine = SyncEngine(src, dst, "items")

    def insert_values(conn: sqlite3.Connection, start: int, end: int) -> None:
        for i in range(start, end):
            conn.execute("INSERT INTO items (id, value) VALUES (?, ?)", (i, f"v{i}"))
            conn.commit()
            time.sleep(0.01)

    t1 = threading.Thread(target=insert_values, args=(src, 1, 4))
    t2 = threading.Thread(target=insert_values, args=(dst, 4, 7))
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    time.sleep(0.2)

    expected = [(i, f"v{i}") for i in range(1, 7)]
    assert sorted(src.execute("SELECT id, value FROM items").fetchall()) == expected
    assert sorted(dst.execute("SELECT id, value FROM items").fetchall()) == expected

    def update_values(conn: sqlite3.Connection, updates):
        for row_id, value in updates:
            conn.execute("UPDATE items SET value=? WHERE id=?", (value, row_id))
            conn.commit()
            time.sleep(0.01)

    t3 = threading.Thread(target=update_values, args=(src, [(1, "a1"), (2, "a2")]))
    t4 = threading.Thread(target=update_values, args=(dst, [(4, "b4"), (5, "b5")]))
    t3.start()
    t4.start()
    t3.join()
    t4.join()

    # Allow some time for the background worker to propagate updates.
    for _ in range(20):
        if (
            dst.execute("SELECT value FROM items WHERE id=1").fetchone()[0] == "a1"
            and src.execute("SELECT value FROM items WHERE id=4").fetchone()[0] == "b4"
        ):
            break
        time.sleep(0.1)

    assert dst.execute("SELECT value FROM items WHERE id=1").fetchone()[0] == "a1"
    assert src.execute("SELECT value FROM items WHERE id=4").fetchone()[0] == "b4"

    engine.stop()
