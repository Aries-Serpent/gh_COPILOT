from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Iterator

PRAGMAS = ("PRAGMA journal_mode=WAL;", "PRAGMA synchronous=NORMAL;", "PRAGMA foreign_keys=ON;", "PRAGMA busy_timeout=10000;")

def get_conn(db: Path) -> sqlite3.Connection:
    c = sqlite3.connect(db)
    c.row_factory = sqlite3.Row
    for p in PRAGMAS:
        c.execute(p)
    return c

class GenerationDAO:
    def __init__(self, analytics_db: Path): self.analytics_db = analytics_db
    @contextmanager
    def _conn(self) -> Iterator[sqlite3.Connection]:
        c = get_conn(self.analytics_db)
        try:
            yield c
        finally:
            c.close()

    def log_event(self, kind: str, source: str, target_path: str, template_id: str|None, inputs: dict) -> None:
        with self._conn() as c, c:
            c.execute(
                "INSERT INTO generation_events(kind, source, target_path, template_id, inputs_json, ts) VALUES (?,?,?,?,?,?)",
                (kind, source, target_path, template_id, json.dumps(inputs), datetime.utcnow().isoformat()),
            )
