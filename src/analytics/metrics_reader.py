from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Dict, Any

DEFAULT_PANEL_MAP: Dict[str, str] = {
    "compliance": "code_quality_metrics",
    "tests": "test_run_stats",
    "lint": "ruff_issue_log",
    "placeholders": "placeholder_audit_snapshots",
}


def get_latest_panel_snapshot(panel: str, db_path: Path, test_mode: bool = False) -> Dict[str, Any]:
    """Return the most recent row for a given panel.

    Parameters
    ----------
    panel:
        Logical panel name such as ``"compliance"`` or ``"tests"``.
    db_path:
        Path to the analytics database.
    test_mode:
        When ``True`` the database will be opened with default read/write
        permissions so tests can create temporary schemas.

    Returns
    -------
    dict
        On success ``{"ok": True, "panel": panel, "table": table, "snapshot": row, "ts": ts, "source": "analytics.db"}``.
        On failure ``{"ok": False, "error": {"type": str, "message": str}}``.
    """

    panel_key = (panel or "").strip().lower()
    table = DEFAULT_PANEL_MAP.get(panel_key)
    if not table:
        return {"ok": False, "error": {"type": "UnknownPanel", "message": f"Unknown panel: {panel}"}}

    try:
        if test_mode:
            conn = sqlite3.connect(str(db_path))
        else:
            uri = f"file:{db_path.as_posix()}?mode=ro"
            conn = sqlite3.connect(uri, uri=True, timeout=5)
    except Exception as e:  # pragma: no cover - connection errors
        return {"ok": False, "error": {"type": e.__class__.__name__, "message": str(e)}}

    try:
        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
        if cur.fetchone() is None:
            return {
                "ok": False,
                "error": {"type": "MissingSchema", "message": f"Table {table} not found"},
            }

        cols = [r[1] for r in conn.execute(f"PRAGMA table_info({table});")]
        ts_col = next((c for c in ("ts", "timestamp", "created_at", "event_time") if c in cols), None)
        order_clause = ts_col if ts_col else "rowid"
        row = conn.execute(f"SELECT * FROM {table} ORDER BY {order_clause} DESC LIMIT 1;").fetchone()
        if row is None:
            return {"ok": True, "panel": panel_key, "table": table, "snapshot": None, "ts": ""}

        colnames = [c[1] for c in conn.execute(f"PRAGMA table_info({table});")]
        snapshot = dict(zip(colnames, row))
        ts_val = snapshot.get(ts_col, "") if ts_col else ""
        return {
            "ok": True,
            "panel": panel_key,
            "table": table,
            "snapshot": snapshot,
            "ts": str(ts_val),
            "source": "analytics.db",
        }
    except Exception as e:
        return {"ok": False, "error": {"type": e.__class__.__name__, "message": str(e)}}
    finally:
        conn.close()
