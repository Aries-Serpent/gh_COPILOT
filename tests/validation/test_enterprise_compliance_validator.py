from __future__ import annotations

import sqlite3
import sys
import types
from importlib import util
from pathlib import Path

import pytest

# Load the module directly to avoid executing ``validation.__init__`` which has
# heavy dependencies not required for these tests.
MODULE_PATH = Path(__file__).resolve().parents[2] / "validation" / "enterprise_compliance_validator.py"
spec = util.spec_from_file_location("validation.enterprise_compliance_validator", MODULE_PATH)
validator_module = util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(validator_module)
EnterpriseComplianceValidator = validator_module.EnterpriseComplianceValidator

# Provide a lightweight ``validation`` package so modules importing
# ``validation.enterprise_compliance_validator`` resolve to our loaded module.
validation_pkg = types.ModuleType("validation")
validation_pkg.enterprise_compliance_validator = validator_module
sys.modules.setdefault("validation", validation_pkg)
sys.modules.setdefault("validation.enterprise_compliance_validator", validator_module)

import secondary_copilot_validator as wrapper


def _setup_db(path: Path) -> None:
    with sqlite3.connect(path) as conn:
        conn.execute(
            "CREATE TABLE ruff_issue_log(run_timestamp INTEGER, issues INTEGER)"
        )
        conn.executemany(
            "INSERT INTO ruff_issue_log(run_timestamp, issues) VALUES(?, ?)",
            [(1, 5), (2, 4)],
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
    assert metrics["lint_issues"] == 4
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
        cur = conn.cursor()
        # Table where a manual ``id`` column does not align with ``rowid``
        cur.execute("CREATE TABLE sample(id INTEGER, value INTEGER)")
        cur.executemany(
            "INSERT INTO sample(id, value) VALUES (?, ?)", [(2, 10), (1, 20)]
        )

        # Table with separate timestamp column inserted out of order
        cur.execute(
            "CREATE TABLE sample_ts(id INTEGER PRIMARY KEY, ts INTEGER, value INTEGER)"
        )
        cur.executemany(
            "INSERT INTO sample_ts(id, ts, value) VALUES (?, ?, ?)",
            [(1, 2, 100), (2, 1, 200)],
        )
        validator = EnterpriseComplianceValidator(db)

        # Default ordering uses rowid (insertion order)
        assert validator._fetch_latest(cur, "sample", "value") == (20,)
        # Ordering by primary key retrieves the highest id regardless of insertion order
        assert (
            validator._fetch_latest(cur, "sample", "value", order_by="id") == (10,)
        )

        # Without specifying, rowid returns the last inserted timestamp value
        assert validator._fetch_latest(cur, "sample_ts", "value") == (200,)
        # Using the timestamp column retrieves the logically latest row
        assert (
            validator._fetch_latest(cur, "sample_ts", "value", order_by="ts")
            == (100,)
        )

