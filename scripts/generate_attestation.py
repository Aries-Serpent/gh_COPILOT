#!/usr/bin/env python3
"""Generate quarterly governance attestation and commit it."""
from __future__ import annotations

import sqlite3
import subprocess
from datetime import datetime
from pathlib import Path

DB_PATH = Path("databases/analytics.db")
DOCS_DIR = Path("docs/governance")


def _current_quarter(now: datetime) -> tuple[int, int]:
    quarter = (now.month - 1) // 3 + 1
    return now.year, quarter


def _fetch_rows(start: datetime, end: datetime) -> list[tuple[str, str, datetime]]:
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        cur.execute(
            "CREATE TABLE IF NOT EXISTS governance_checks (\"check\" TEXT, status TEXT, timestamp TEXT)"
        )
        cur.execute('SELECT "check", status, timestamp FROM governance_checks')
        rows = []
        for check, status, ts in cur.fetchall():
            ts_dt = datetime.fromisoformat(ts)
            if start <= ts_dt < end:
                rows.append((check, status, ts_dt))
    finally:
        conn.close()
    return rows


def _generate_file(year: int, quarter: int, rows: list[tuple[str, str, datetime]]) -> Path:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    path = DOCS_DIR / f"attestation_{year}_Q{quarter}.md"
    with path.open("w", encoding="utf-8") as f:
        f.write(f"# Governance Attestation {year} Q{quarter}\n\n")
        for check, status, ts in rows:
            f.write(f"- {ts.isoformat()} – {check}: {status}\n")
    return path


def _commit(path: Path) -> None:
    subprocess.run(["git", "add", str(path)], check=True)
    msg = f"docs: add governance attestation {path.stem}"
    subprocess.run(["git", "commit", "-m", msg], check=True)


def main() -> None:
    now = datetime.utcnow()
    year, quarter = _current_quarter(now)
    start_month = (quarter - 1) * 3 + 1
    start = datetime(year, start_month, 1)
    end_year = year + (1 if quarter == 4 else 0)
    end_month = ((start_month + 2) % 12) + 1
    end = datetime(end_year, end_month, 1)
    rows = _fetch_rows(start, end)
    path = _generate_file(year, quarter, rows)
    _commit(path)


if __name__ == "__main__":
    main()
