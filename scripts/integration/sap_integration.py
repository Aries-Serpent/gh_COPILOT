#!/usr/bin/env python3
"""SAP integration data sync with retry and backoff.

Execution is gated by the ``SAP_INTEGRATION_ENABLED`` environment variable.
Authentication uses ``SAP_API_KEY`` and ``SAP_API_URL`` from the environment.
Each sync result is recorded in the ``integration_events`` table of
``analytics.db``.
"""

from __future__ import annotations

import os
import sqlite3
import time
from pathlib import Path
from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

DB_FILE = "analytics.db"


def _get_db(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS integration_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sync_id TEXT,
            timestamp TEXT,
            status TEXT,
            details TEXT
        )
        """
    )
    return conn


def sap_sync(
    sync_id: str,
    session: Optional[requests.Session] = None,
    db_path: Optional[Path] = None,
) -> Optional[dict]:
    """Synchronize data from SAP and log the result.

    Parameters
    ----------
    sync_id:
        Unique identifier for this sync attempt. Re-using the same ``sync_id``
        ensures idempotency.
    session:
        Optional ``requests.Session``. A session with retry/backoff is created
        when not provided.
    db_path:
        Optional override for the path to ``analytics.db``.
    """

    if os.environ.get("SAP_INTEGRATION_ENABLED") != "1":
        return None

    api_key = os.environ["SAP_API_KEY"]
    url = os.environ["SAP_API_URL"]

    session = session or requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    db_path = db_path or Path(os.environ.get("GH_COPILOT_WORKSPACE", ".")) / DB_FILE
    conn = _get_db(db_path)

    existing = conn.execute(
        "SELECT 1 FROM integration_events WHERE sync_id=? AND status='success' "
        "ORDER BY id DESC LIMIT 1",
        (sync_id,),
    ).fetchone()

    if existing:
        conn.execute(
            "INSERT INTO integration_events (sync_id, timestamp, status, details) "
            "VALUES (?, ?, ?, ?)",
            (sync_id, time.strftime("%Y-%m-%dT%H:%M:%SZ"), "skipped", "already synced"),
        )
        conn.commit()
        conn.close()
        return {"status": "skipped"}

    headers = {"Authorization": f"Bearer {api_key}", "Idempotency-Key": sync_id}
    try:
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        status = "success"
        details = data.get("detail", "")
    except Exception as exc:  # pragma: no cover - defensive
        data = None
        status = "failure"
        details = str(exc)

    conn.execute(
        "INSERT INTO integration_events (sync_id, timestamp, status, details) "
        "VALUES (?, ?, ?, ?)",
        (sync_id, time.strftime("%Y-%m-%dT%H:%M:%SZ"), status, details),
    )
    conn.commit()
    conn.close()
    return data


def main() -> int:
    """Run a single sync using the current timestamp as ``sync_id``."""

    sync_id = str(int(time.time()))
    sap_sync(sync_id)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

