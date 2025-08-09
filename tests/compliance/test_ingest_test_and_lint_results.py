import json
import os
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from scripts.ingest_test_and_lint_results import _db, ingest


@pytest.fixture
def temp_workspace():
    with tempfile.TemporaryDirectory() as tmp:
        yield Path(tmp)


@pytest.fixture
def sample_ruff_data():
    return [{"code": "F401"}, {"code": "E302"}]


@pytest.fixture
def sample_pytest_data():
    return {"summary": {"total": 25, "passed": 20, "failed": 3}}


class TestDatabaseFunction:
    def test_db_default_workspace(self):
        with patch.dict(os.environ, {"GH_COPILOT_WORKSPACE": "/test/workspace"}):
            assert str(_db()) == "/test/workspace/databases/analytics.db"

    def test_db_explicit_workspace(self):
        assert str(_db("/custom/workspace")) == "/custom/workspace/databases/analytics.db"

    def test_db_fallback_cwd(self, monkeypatch):
        monkeypatch.delenv("GH_COPILOT_WORKSPACE", raising=False)
        monkeypatch.setattr(Path, "cwd", lambda: Path("/current/dir"))
        assert str(_db()) == "/current/dir/databases/analytics.db"


class TestIngest:
    def test_ingest_creates_db_and_inserts_metrics(
        self, temp_workspace, sample_ruff_data, sample_pytest_data
    ):
        ruff_json = temp_workspace / "ruff_report.json"
        ruff_json.write_text(json.dumps(sample_ruff_data), encoding="utf-8")
        pytest_json = temp_workspace / ".report.json"
        pytest_json.write_text(json.dumps(sample_pytest_data), encoding="utf-8")

        row_id = ingest(str(temp_workspace))

        analytics_db = temp_workspace / "databases" / "analytics.db"
        with sqlite3.connect(analytics_db) as conn:
            row = conn.execute(
                "SELECT ruff_issues, tests_passed, tests_failed, placeholders_open, placeholders_resolved "
                "FROM compliance_metrics_history WHERE id=?",
                (row_id,),
            ).fetchone()
        assert row == (2, 20, 3, None, None)

    def test_ingest_handles_missing_files(self, temp_workspace):
        row_id = ingest(str(temp_workspace))
        analytics_db = temp_workspace / "databases" / "analytics.db"
        with sqlite3.connect(analytics_db) as conn:
            row = conn.execute(
                "SELECT ruff_issues, tests_passed, tests_failed FROM compliance_metrics_history WHERE id=?",
                (row_id,),
            ).fetchone()
        assert row == (0, 0, 0)

    def test_ingest_malformed_json(self, temp_workspace):
        (temp_workspace / "ruff_report.json").write_text("{bad json", encoding="utf-8")
        (temp_workspace / ".report.json").write_text("{bad json", encoding="utf-8")
        row_id = ingest(str(temp_workspace))
        analytics_db = temp_workspace / "databases" / "analytics.db"
        with sqlite3.connect(analytics_db) as conn:
            row = conn.execute(
                "SELECT ruff_issues, tests_passed, tests_failed FROM compliance_metrics_history WHERE id=?",
                (row_id,),
            ).fetchone()
        assert row == (0, 0, 0)

    def test_ingest_custom_paths(
        self, temp_workspace, sample_ruff_data, sample_pytest_data
    ):
        custom_ruff = temp_workspace / "custom_ruff.json"
        custom_pytest = temp_workspace / "custom_pytest.json"
        custom_ruff.write_text(json.dumps(sample_ruff_data), encoding="utf-8")
        custom_pytest.write_text(json.dumps(sample_pytest_data), encoding="utf-8")
        row_id = ingest(
            str(temp_workspace), ruff_json=custom_ruff, pytest_json=custom_pytest
        )
        analytics_db = temp_workspace / "databases" / "analytics.db"
        with sqlite3.connect(analytics_db) as conn:
            row = conn.execute(
                "SELECT ruff_issues, tests_passed, tests_failed FROM compliance_metrics_history WHERE id=?",
                (row_id,),
            ).fetchone()
        assert row == (2, 20, 3)

