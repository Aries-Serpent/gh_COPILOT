from __future__ import annotations
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

DEFAULT_TIMEOUT_S = 30


def _prime(conn: sqlite3.Connection, timeout_s: int) -> None:
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute(f"PRAGMA busy_timeout = {int(timeout_s * 1000)};")


def connect_wal(db: Path, timeout_s: int = DEFAULT_TIMEOUT_S) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db), timeout=timeout_s)
    _prime(conn, timeout_s)
    return conn


@contextmanager
def managed_connection(db: Path, timeout_s: int = DEFAULT_TIMEOUT_S) -> Iterator[sqlite3.Connection]:
    conn = connect_wal(db, timeout_s)
    try:
        yield conn
    finally:
        conn.close()
