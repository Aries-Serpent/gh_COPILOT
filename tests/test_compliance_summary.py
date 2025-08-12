from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sqlite3

from gh_copilot.compliance.dao import ComplianceDAO
from gh_copilot.compliance.models import ScoreInputs


def seed_minimal(db: Path) -> None:
    con = sqlite3.connect(db)
    con.executescript(
        """
        PRAGMA foreign_keys=ON;
        CREATE TABLE IF NOT EXISTS score_snapshots (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          branch TEXT NOT NULL,
          score REAL NOT NULL,
          model_id TEXT NOT NULL,
          inputs_json TEXT NOT NULL,
          ts TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS placeholder_tasks (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          file TEXT NOT NULL,
          line INTEGER NOT NULL,
          kind TEXT NOT NULL,
          sha TEXT,
          ts TEXT NOT NULL,
          status TEXT NOT NULL DEFAULT 'open'
        );
        """
    )
    con.commit()
    con.close()


def test_summary_without_data(tmp_path: Path) -> None:
    db = tmp_path / "analytics.db"
    seed_minimal(db)
    dao = ComplianceDAO(db)
    dao.ensure_views()

    s = dao.compliance_summary("main")
    assert s.score is None
    assert s.placeholders_open == 0
    assert s.gauges == []


def test_summary_with_snapshot_and_placeholder(tmp_path: Path) -> None:
    db = tmp_path / "analytics.db"
    seed_minimal(db)

    con = sqlite3.connect(db)
    inputs = ScoreInputs(
        run_id="t1", lint=0.9, tests=0.9, placeholders=0.9, sessions=0.9, model_id="main-default"
    )
    con.execute(
        "INSERT INTO score_snapshots(branch, score, model_id, inputs_json, ts) VALUES (?,?,?,?,?)",
        ("main", 0.92, "main-default", inputs.model_dump_json(), datetime.utcnow().isoformat()),
    )
    con.execute(
        "INSERT INTO placeholder_tasks(file, line, kind, sha, ts, status) VALUES (?,?,?,?,?, 'open')",
        ("a.py", 1, "TODO", "deadbeef", datetime.utcnow().isoformat()),
    )
    con.commit()
    con.close()

    dao = ComplianceDAO(db)
    dao.ensure_views()

    s = dao.compliance_summary("main")
    assert s.score == 0.92
    assert s.placeholders_open == 1
    assert any(g.name == "compliance_score" for g in s.gauges)
    assert any(g.name == "open_placeholders" for g in s.gauges)

