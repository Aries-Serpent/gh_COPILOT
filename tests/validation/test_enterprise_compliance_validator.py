from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from validation.enterprise_compliance_validator import (
    EnterpriseComplianceValidator,
)
import secondary_copilot_validator as wrapper


def _setup_db(path: Path) -> None:
    with sqlite3.connect(path) as conn:
        conn.execute(
            "CREATE TABLE ruff_issue_log(run_timestamp INTEGER, issues INTEGER)"
        )
        conn.executemany(
            "INSERT INTO ruff_issue_log(run_timestamp, issues) VALUES(?, ?)",
            [(1, 5), (2, 7)],
        )
        conn.execute(
            "CREATE TABLE test_run_stats(run_timestamp INTEGER, passed INTEGER, total INTEGER)"
        )
        conn.executemany(
            "INSERT INTO test_run_stats(run_timestamp, passed, total) VALUES(?, ?, ?)",
            [(1, 8, 10), (2, 9, 12)],
        )
        conn.execute(
            "CREATE TABLE todo_fixme_tracking(id INTEGER PRIMARY KEY, status TEXT)"
        )
        conn.executemany(
            "INSERT INTO todo_fixme_tracking(status) VALUES (?)",
            [("open",), ("resolved",)],
        )
        conn.execute(
            "CREATE TABLE session_lifecycle(session_id TEXT, status TEXT)"
        )
        conn.executemany(
            "INSERT INTO session_lifecycle(session_id, status) VALUES (?, ?)",
            [("a", "success"), ("b", "failed")],
        )


def test_evaluate_success(tmp_path: Path) -> None:
    db = tmp_path / "analytics.db"
    _setup_db(db)
    validator = EnterpriseComplianceValidator(db)
    metrics = validator.evaluate()
    assert metrics["lint_issues"] == 7
    assert metrics["tests_passed"] == 9
    assert metrics["tests_failed"] == 3
    assert metrics["placeholders_open"] == 1
    assert metrics["placeholders_resolved"] == 1
    assert metrics["composite_score"] > 0
    with sqlite3.connect(db) as conn:
        cur = conn.execute(
            "SELECT COUNT(*) FROM enterprise_compliance_scores"
        )
        assert cur.fetchone()[0] == 1


def test_missing_database(tmp_path: Path) -> None:
    db = tmp_path / "missing.db"
    validator = EnterpriseComplianceValidator(db)
    with pytest.raises(FileNotFoundError):
        validator.evaluate()


def test_wrapper_function(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    db = tmp_path / "analytics.db"
    _setup_db(db)

    def _factory() -> EnterpriseComplianceValidator:
        return EnterpriseComplianceValidator(db)

    monkeypatch.setattr(wrapper, "EnterpriseComplianceValidator", _factory)
    score = wrapper.record_compliance_metrics()
    assert score > 0


def test_fetch_latest_order_by(tmp_path: Path) -> None:
    db = tmp_path / "analytics.db"
    with sqlite3.connect(db) as conn:
        conn.execute("CREATE TABLE table_a(ts INTEGER, val INTEGER)")
        conn.executemany(
            "INSERT INTO table_a(ts, val) VALUES(?, ?)",
            [(1, 10), (3, 30), (2, 20)],
        )
        conn.execute("CREATE TABLE table_b(val INTEGER, ts INTEGER)")
        conn.executemany(
            "INSERT INTO table_b(val, ts) VALUES(?, ?)",
            [(100, 1), (200, 2)],
        )
    validator = EnterpriseComplianceValidator(db)
    with sqlite3.connect(db) as conn:
        cur = conn.cursor()
        latest_a, = validator._fetch_latest(cur, "table_a", "val", order_by="ts")
        latest_b, = validator._fetch_latest(cur, "table_b", "val", order_by="ts")
    assert latest_a == 30
    assert latest_b == 200

