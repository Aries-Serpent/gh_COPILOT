from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Dict, Any

from utils.logging_utils import setup_enterprise_logging, log_enterprise_operation


def sync_databases(source: str | Path, target: str | Path) -> None:
    """Synchronize SQLite databases.

    Copies tables, inserting new rows, updating existing ones when the source
    row has a newer ``updated_at`` timestamp, and deleting rows missing from
    the source. Decisions are logged via enterprise logging.
    """
    setup_enterprise_logging()
    source_path = Path(source)
    target_path = Path(target)
    log_enterprise_operation("sync_databases", "INFO", f"{source_path} -> {target_path}")

    with sqlite3.connect(source_path) as src, sqlite3.connect(target_path) as tgt:
        src.row_factory = sqlite3.Row
        tgt.row_factory = sqlite3.Row

        tables = [r[0] for r in src.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        for table in tables:
            schema = src.execute(
                "SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table,)
            ).fetchone()[0]
            if not tgt.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,)
            ).fetchone():
                tgt.execute(schema)
                log_enterprise_operation("create_table", "INFO", table)

            src_rows: Dict[Any, Dict[str, Any]] = {
                row["id"]: dict(row) for row in src.execute(f"SELECT * FROM {table}")
            }
            tgt_rows: Dict[Any, Dict[str, Any]] = {
                row["id"]: dict(row) for row in tgt.execute(f"SELECT * FROM {table}")
            }

            for pk, srow in src_rows.items():
                if pk not in tgt_rows:
                    cols = ", ".join(srow.keys())
                    placeholders = ", ".join("?" for _ in srow)
                    tgt.execute(
                        f"INSERT INTO {table} ({cols}) VALUES ({placeholders})",
                        tuple(srow.values()),
                    )
                    log_enterprise_operation("insert", "INFO", f"{table}:{pk}")
                    continue

                trow = tgt_rows[pk]
                src_ts = srow.get("updated_at") or srow.get("modified_at")
                tgt_ts = trow.get("updated_at") or trow.get("modified_at")
                if src_ts and tgt_ts and src_ts > tgt_ts:
                    cols = [c for c in srow.keys() if c != "id"]
                    assignments = ", ".join(f"{c}=?" for c in cols)
                    values = [srow[c] for c in cols] + [pk]
                    tgt.execute(
                        f"UPDATE {table} SET {assignments} WHERE id=?", values
                    )
                    log_enterprise_operation("update", "INFO", f"{table}:{pk}")
                else:
                    log_enterprise_operation("conflict_skip", "INFO", f"{table}:{pk}")

            for pk in set(tgt_rows) - set(src_rows):
                tgt.execute(f"DELETE FROM {table} WHERE id=?", (pk,))
                log_enterprise_operation("delete", "INFO", f"{table}:{pk}")
        tgt.commit()
