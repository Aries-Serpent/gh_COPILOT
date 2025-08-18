import sqlite3


def test_complex_join():
    conn = sqlite3.connect(':memory:')
    conn.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)')
    conn.execute('CREATE TABLE orders (id INTEGER PRIMARY KEY, user_id INTEGER, item TEXT)')
    conn.executemany('INSERT INTO users(id, name) VALUES (?, ?)', [(1, 'a'), (2, 'b')])
    conn.executemany(
        'INSERT INTO orders(id, user_id, item) VALUES (?, ?, ?)',
        [(1, 1, 'x'), (2, 2, 'y'), (3, 1, 'z')],
    )
    rows = conn.execute(
        'SELECT users.name, orders.item FROM users '\
        'JOIN orders ON users.id = orders.user_id ORDER BY orders.id'
    ).fetchall()
    assert rows == [('a', 'x'), ('b', 'y'), ('a', 'z')]


def test_transaction_rollback_on_failure():
    conn = sqlite3.connect(':memory:')
    conn.execute('CREATE TABLE items (id INTEGER PRIMARY KEY, value TEXT UNIQUE)')
    conn.execute('INSERT INTO items(id, value) VALUES (1, "a")')
    conn.commit()
    try:
        with conn:
            conn.execute('INSERT INTO items(id, value) VALUES (2, "b")')
            conn.execute('INSERT INTO items(id, value) VALUES (3, "a")')
    except sqlite3.IntegrityError:
        pass
    rows = conn.execute('SELECT id, value FROM items ORDER BY id').fetchall()
    assert rows == [(1, 'a')]
