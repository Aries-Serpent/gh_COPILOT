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
        conn.execute(
            "INSERT INTO ruff_issue_log(run_timestamp, issues) VALUES(1, 5)"
        )
        conn.execute(
            "CREATE TABLE test_run_stats(run_timestamp INTEGER, passed INTEGER, total INTEGER)"
        )
        conn.execute(
            "INSERT INTO test_run_stats(run_timestamp, passed, total) VALUES(1, 8, 10)"
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
    assert metrics["lint_issues"] == 5
    assert metrics["tests_passed"] == 8
    assert metrics["tests_failed"] == 2
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

