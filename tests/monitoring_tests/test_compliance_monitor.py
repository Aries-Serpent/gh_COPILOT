"""Tests for compliance monitoring alerts."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from ghc_monitoring import compliance_monitor
from notifications import email, webhook


def _write_score(db: Path, score: float) -> None:
    conn = sqlite3.connect(db)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS compliance_scores (timestamp REAL, composite_score REAL)"
    )
    conn.execute("DELETE FROM compliance_scores")
    conn.execute("INSERT INTO compliance_scores VALUES (0, ?)", (score,))
    conn.commit()
    conn.close()


def test_alerts_triggered(tmp_path, monkeypatch):
    db = tmp_path / "analytics.db"
    _write_score(db, 0.5)

    messages = []

    monkeypatch.setattr(email, "send_alert", lambda m: messages.append(("email", m)))
    monkeypatch.setattr(webhook, "send_alert", lambda m: messages.append(("webhook", m)))

    compliance_monitor.check_compliance(db)

    assert ("email", "Compliance score below threshold: 0.50") in messages
    assert ("webhook", "Compliance score below threshold: 0.50") in messages
