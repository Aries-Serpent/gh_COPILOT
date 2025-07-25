"""Template synchronization utilities."""
from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

from utils.log_utils import _log_event

ANALYTICS_DB = Path(os.getenv("GH_COPILOT_WORKSPACE", ".")) / "databases" / "analytics.db"

__all__ = ["synchronize_templates"]


def _fetch_templates(conn: sqlite3.Connection) -> List[Tuple[str, str]]:
    """Return all templates from a connection."""
    cur = conn.execute("SELECT name, template_content FROM templates")
    return cur.fetchall()


def _has_templates_table(conn: sqlite3.Connection) -> bool:
    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='templates'"
    )
    return cur.fetchone() is not None


def synchronize_templates(databases: Iterable[Path]) -> None:
    """Synchronize templates across multiple SQLite databases.

    Parameters
    ----------
    databases:
        Iterable of database paths each expected to contain a ``templates`` table.

    Templates with empty content are ignored. All insertions occur inside
    transactions. On any error, all databases are rolled back and an entry is
    recorded in ``audit_log``. Each processed template is logged to ``sync_events``.
    """
    paths = [Path(db) for db in databases]
    conns = []
    try:
        for path in paths:
            con = sqlite3.connect(path)
            con.row_factory = sqlite3.Row
            con.execute("BEGIN")
            conns.append(con)

        templates: Dict[str, str] = {}
        events: List[Tuple[str, bool]] = []
        for con in conns:
            if _has_templates_table(con):
                for name, content in _fetch_templates(con):
                    events.append((name, bool(content)))
                    if content:
                        templates[name] = content

        for name, is_valid in events:
            status = "template_sync" if is_valid else "template_invalid"
            _log_event({"template": name, "event": status}, table="sync_events", db_path=ANALYTICS_DB)

        for name, content in templates.items():
            for con, path in zip(conns, paths):
                if not _has_templates_table(con):
                    raise RuntimeError(f"missing templates table: {path}")
                con.execute(
                    "INSERT OR REPLACE INTO templates (name, template_content) VALUES (?, ?)",
                    (name, content),
                )

        for con in conns:
            con.commit()
    except Exception as exc:
        for con in conns:
            con.rollback()
        _log_event(
            {"description": f"sync failed: {exc}"}, table="audit_log", db_path=ANALYTICS_DB
        )
    finally:
        for con in conns:
            con.close()
