from __future__ import annotations

import sqlite3
import os
from datetime import datetime
from pathlib import Path

from tqdm import tqdm

DB_PATH = Path('databases/production.db')
DOCS_DIR = Path('docs')
TEMPLATE_DIR = Path('template_engine/templates')


def init_databases() -> None:
    if not DB_PATH.exists():
        conn = sqlite3.connect(DB_PATH)
        conn.execute('CREATE TABLE IF NOT EXISTS logs(id INTEGER PRIMARY KEY, message TEXT)')
        conn.commit()
        conn.close()


def ingest_assets() -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    for path in tqdm(list(DOCS_DIR.rglob('*.md')) + list(TEMPLATE_DIR.rglob('*.tpl'))):
        cur.execute('INSERT INTO logs(message) VALUES (?)', (f"ingested {path}",))
    conn.commit()
    conn.close()


def run_audit() -> None:
    os.system('python scripts/code_placeholder_audit.py')


if __name__ == '__main__':
    start = datetime.now()
    init_databases()
    ingest_assets()
    run_audit()
    print(f"Automation finished in {(datetime.now()-start).total_seconds()}s")
