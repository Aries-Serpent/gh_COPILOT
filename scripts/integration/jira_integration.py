#!/usr/bin/env python3
"""Jira ticket management with retry/backoff and idempotency.

Execution is gated by the ``JIRA_INTEGRATION_ENABLED`` environment variable.
Authentication uses ``JIRA_API_TOKEN`` and ``JIRA_API_URL`` from the
environment. Each operation is recorded in the ``integration_events`` table of
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
        """,
    )
    return conn


def jira_create_ticket(
    ticket_id: str,
    fields: dict,
    session: Optional[requests.Session] = None,
    db_path: Optional[Path] = None,
) -> Optional[dict]:
    """Create a Jira ticket and log the result.

    ``ticket_id`` is used as an idempotency key. Re-using the same
    ``ticket_id`` ensures only one API call is issued for successful creates.
    """

    if os.environ.get("JIRA_INTEGRATION_ENABLED") != "1":
        return None

    token = os.environ["JIRA_API_TOKEN"]
    base_url = os.environ["JIRA_API_URL"]

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
        (ticket_id,),
    ).fetchone()

    if existing:
        conn.execute(
            "INSERT INTO integration_events (sync_id, timestamp, status, details) "
            "VALUES (?, ?, ?, ?)",
            (ticket_id, time.strftime("%Y-%m-%dT%H:%M:%SZ"), "skipped", "already created"),
        )
        conn.commit()
        conn.close()
        return {"status": "skipped"}

    headers = {
        "Authorization": f"Bearer {token}",
        "Idempotency-Key": ticket_id,
    }
    url = f"{base_url}/rest/api/2/issue"

    try:
        response = session.post(url, json={"fields": fields}, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        status = "success"
        details = data.get("key", "")
    except Exception as exc:  # pragma: no cover - defensive
        data = None
        status = "failure"
        details = str(exc)

    conn.execute(
        "INSERT INTO integration_events (sync_id, timestamp, status, details) "
        "VALUES (?, ?, ?, ?)",
        (ticket_id, time.strftime("%Y-%m-%dT%H:%M:%SZ"), status, details),
    )
    conn.commit()
    conn.close()
    return data


def jira_update_ticket(
    ticket_key: str,
    fields: dict,
    session: Optional[requests.Session] = None,
    db_path: Optional[Path] = None,
) -> Optional[dict]:
    """Update a Jira ticket and log the operation."""

    if os.environ.get("JIRA_INTEGRATION_ENABLED") != "1":
        return None

    token = os.environ["JIRA_API_TOKEN"]
    base_url = os.environ["JIRA_API_URL"]

    session = session or requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    db_path = db_path or Path(os.environ.get("GH_COPILOT_WORKSPACE", ".")) / DB_FILE
    conn = _get_db(db_path)

    headers = {"Authorization": f"Bearer {token}"}
    url = f"{base_url}/rest/api/2/issue/{ticket_key}"

    try:
        response = session.put(url, json={"fields": fields}, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json() if response.content else {}
        status = "success"
        details = data.get("key", "")
    except Exception as exc:  # pragma: no cover - defensive
        data = None
        status = "failure"
        details = str(exc)

    conn.execute(
        "INSERT INTO integration_events (sync_id, timestamp, status, details) "
        "VALUES (?, ?, ?, ?)",
        (
            f"update-{ticket_key}",
            time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            status,
            details,
        ),
    )
    conn.commit()
    conn.close()
    return data


def main() -> int:  # pragma: no cover
    """Placeholder main entrypoint."""
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

