"""Tests for test and lint results ingestion script."""
from __future__ import annotations

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
    """Create a temporary workspace directory."""
    with tempfile.TemporaryDirectory() as tmp:
        workspace = Path(tmp)
        (workspace / "databases").mkdir()
        yield workspace


@pytest.fixture
def sample_ruff_data():
    """Sample ruff JSON output."""
    return [
        {
            "filename": "test.py",
            "line": 1,
            "column": 1,
            "rule": "F401",
            "message": "unused import",
            "severity": "error"
        },
        {
            "filename": "main.py", 
            "line": 10,
            "column": 5,
            "rule": "E302",
            "message": "expected 2 blank lines",
            "severity": "error"
        }
    ]


@pytest.fixture
def sample_pytest_data():
    """Sample pytest JSON output."""
    return {
        "summary": {
            "total": 25,
            "passed": 20,
            "failed": 3,
            "skipped": 2,
            "error": 0
        },
        "tests": [
            {"outcome": "passed", "nodeid": "test_example.py::test_function_1"},
            {"outcome": "passed", "nodeid": "test_example.py::test_function_2"},
            {"outcome": "failed", "nodeid": "test_example.py::test_function_3"}
        ]
    }


class TestDatabaseFunction:
    """Test database path resolution."""

    def test_db_default_workspace(self):
        """Test database path with default workspace."""
        with patch.dict(os.environ, {"GH_COPILOT_WORKSPACE": "/test/workspace"}):
            db_path = _db()
            assert str(db_path) == "/test/workspace/databases/analytics.db"

    def test_db_explicit_workspace(self):
        """Test database path with explicit workspace."""
        db_path = _db("/custom/workspace")
        assert str(db_path) == "/custom/workspace/databases/analytics.db"

    def test_db_fallback_cwd(self):
        """Test database path falls back to current directory."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("pathlib.Path.cwd", return_value=Path("/current/dir")):
                db_path = _db()
                assert str(db_path) == "/current/dir/databases/analytics.db"


class TestIngestionWithoutDatabase:
    """Test ingestion when database doesn't exist."""

    def test_ingest_missing_database(self, temp_workspace):
        """Test ingestion gracefully handles missing database."""
        # Remove the database directory
        (temp_workspace / "databases").rmdir()
        
        # Should not raise exception
        ingest(str(temp_workspace))
        assert True  # Test passes if no exception raised

    def test_ingest_missing_analytics_db(self, temp_workspace):
        """Test ingestion when analytics.db doesn't exist."""
        # Database directory exists but analytics.db doesn't
        
        # Should not raise exception
        ingest(str(temp_workspace))
        assert True  # Test passes if no exception raised


class TestRuffIngestion:
    """Test ruff results ingestion."""

    def test_ingest_ruff_json_success(self, temp_workspace, sample_ruff_data):
        """Test successful ruff JSON ingestion."""
        analytics_db = temp_workspace / "databases" / "analytics.db"
        ruff_json = temp_workspace / "ruff_report.json"
        
        # Create analytics database
        with sqlite3.connect(analytics_db) as conn:
            pass
        
        # Create ruff JSON file
        ruff_json.write_text(json.dumps(sample_ruff_data), encoding="utf-8")
        
        # Ingest data
        ingest(str(temp_workspace))
        
        # Verify data was inserted
        with sqlite3.connect(analytics_db) as conn:
            cur = conn.execute("SELECT issues FROM ruff_issue_log ORDER BY run_timestamp DESC LIMIT 1")
            row = cur.fetchone()
            assert row is not None
            assert row[0] == 2  # Two issues in sample data

    def test_ingest_ruff_object_format(self, temp_workspace):
        """Test ruff ingestion with object format."""
        analytics_db = temp_workspace / "databases" / "analytics.db"
        ruff_json = temp_workspace / "ruff_report.json"
        
        # Create analytics database
        with sqlite3.connect(analytics_db) as conn:
            pass
        
        # Create ruff JSON file with object format
        ruff_data = {"issue_count": 5, "other_field": "value"}
        ruff_json.write_text(json.dumps(ruff_data), encoding="utf-8")
        
        # Ingest data
        ingest(str(temp_workspace))
        
        # Verify data was inserted
        with sqlite3.connect(analytics_db) as conn:
            cur = conn.execute("SELECT issues FROM ruff_issue_log ORDER BY run_timestamp DESC LIMIT 1")
            row = cur.fetchone()
            assert row is not None
            assert row[0] == 5

    def test_ingest_ruff_malformed_json(self, temp_workspace):
        """Test ruff ingestion handles malformed JSON."""
        analytics_db = temp_workspace / "databases" / "analytics.db"
        ruff_json = temp_workspace / "ruff_report.json"
        
        # Create analytics database
        with sqlite3.connect(analytics_db) as conn:
            pass
        
        # Create malformed JSON file
        ruff_json.write_text("{ invalid json", encoding="utf-8")
        
        # Ingest data (should handle error gracefully)
        ingest(str(temp_workspace))
        
        # Verify 0 issues were recorded
        with sqlite3.connect(analytics_db) as conn:
            cur = conn.execute("SELECT issues FROM ruff_issue_log ORDER BY run_timestamp DESC LIMIT 1")
            row = cur.fetchone()
            assert row is not None
            assert row[0] == 0

    def test_ingest_ruff_missing_file(self, temp_workspace):
        """Test ruff ingestion when JSON file doesn't exist."""
        analytics_db = temp_workspace / "databases" / "analytics.db"
        
        # Create analytics database
        with sqlite3.connect(analytics_db) as conn:
            pass
        
        # Ingest data (no ruff file exists)
        ingest(str(temp_workspace))
        
        # Verify no ruff data was inserted
        with sqlite3.connect(analytics_db) as conn:
            cur = conn.execute("SELECT COUNT(*) FROM ruff_issue_log")
            count = cur.fetchone()[0]
            assert count == 0

    def test_ingest_custom_ruff_path(self, temp_workspace, sample_ruff_data):
        """Test ruff ingestion with custom file path."""
        analytics_db = temp_workspace / "databases" / "analytics.db"
        custom_ruff = temp_workspace / "custom_ruff.json"
        
        # Create analytics database
        with sqlite3.connect(analytics_db) as conn:
            pass
        
        # Create custom ruff JSON file
        custom_ruff.write_text(json.dumps(sample_ruff_data), encoding="utf-8")
        
        # Ingest data with custom path
        ingest(str(temp_workspace), ruff_json=custom_ruff)
        
        # Verify data was inserted
        with sqlite3.connect(analytics_db) as conn:
            cur = conn.execute("SELECT issues FROM ruff_issue_log ORDER BY run_timestamp DESC LIMIT 1")
            row = cur.fetchone()
            assert row is not None
            assert row[0] == 2


class TestPytestIngestion:
    """Test pytest results ingestion."""

    def test_ingest_pytest_json_success(self, temp_workspace, sample_pytest_data):
        """Test successful pytest JSON ingestion."""
        analytics_db = temp_workspace / "databases" / "analytics.db"
        pytest_json = temp_workspace / ".report.json"
        
        # Create analytics database
        with sqlite3.connect(analytics_db) as conn:
            pass
        
        # Create pytest JSON file
        pytest_json.write_text(json.dumps(sample_pytest_data), encoding="utf-8")
        
        # Ingest data
        ingest(str(temp_workspace))
        
        # Verify data was inserted
        with sqlite3.connect(analytics_db) as conn:
            cur = conn.execute("SELECT passed, total FROM test_run_stats ORDER BY run_timestamp DESC LIMIT 1")
            row = cur.fetchone()
            assert row is not None
            assert row[0] == 20  # passed
            assert row[1] == 25  # total

    def test_ingest_pytest_malformed_json(self, temp_workspace):
        """Test pytest ingestion handles malformed JSON."""
        analytics_db = temp_workspace / "databases" / "analytics.db"
        pytest_json = temp_workspace / ".report.json"
        
        # Create analytics database
        with sqlite3.connect(analytics_db) as conn:
            pass
        
        # Create malformed JSON file
        pytest_json.write_text("{ invalid: json }", encoding="utf-8")
        
        # Ingest data (should handle error gracefully)
        ingest(str(temp_workspace))
        
        # Verify 0 values were recorded
        with sqlite3.connect(analytics_db) as conn:
            cur = conn.execute("SELECT passed, total FROM test_run_stats ORDER BY run_timestamp DESC LIMIT 1")
            row = cur.fetchone()
            assert row is not None
            assert row[0] == 0  # passed
            assert row[1] == 0  # total

    def test_ingest_pytest_missing_summary(self, temp_workspace):
        """Test pytest ingestion when summary is missing."""
        analytics_db = temp_workspace / "databases" / "analytics.db"
        pytest_json = temp_workspace / ".report.json"
        
        # Create analytics database
        with sqlite3.connect(analytics_db) as conn:
            pass
        
        # Create pytest JSON without summary
        pytest_data = {"tests": []}
        pytest_json.write_text(json.dumps(pytest_data), encoding="utf-8")
        
        # Ingest data
        ingest(str(temp_workspace))
        
        # Verify 0 values were recorded
        with sqlite3.connect(analytics_db) as conn:
            cur = conn.execute("SELECT passed, total FROM test_run_stats ORDER BY run_timestamp DESC LIMIT 1")
            row = cur.fetchone()
            assert row is not None
            assert row[0] == 0  # passed
            assert row[1] == 0  # total

    def test_ingest_pytest_missing_file(self, temp_workspace):
        """Test pytest ingestion when JSON file doesn't exist."""
        analytics_db = temp_workspace / "databases" / "analytics.db"
        
        # Create analytics database
        with sqlite3.connect(analytics_db) as conn:
            pass
        
        # Ingest data (no pytest file exists)
        ingest(str(temp_workspace))
        
        # Verify no pytest data was inserted
        with sqlite3.connect(analytics_db) as conn:
            cur = conn.execute("SELECT COUNT(*) FROM test_run_stats")
            count = cur.fetchone()[0]
            assert count == 0

    def test_ingest_custom_pytest_path(self, temp_workspace, sample_pytest_data):
        """Test pytest ingestion with custom file path."""
        analytics_db = temp_workspace / "databases" / "analytics.db"
        custom_pytest = temp_workspace / "custom_report.json"
        
        # Create analytics database
        with sqlite3.connect(analytics_db) as conn:
            pass
        
        # Create custom pytest JSON file
        custom_pytest.write_text(json.dumps(sample_pytest_data), encoding="utf-8")
        
        # Ingest data with custom path
        ingest(str(temp_workspace), pytest_json=custom_pytest)
        
        # Verify data was inserted
        with sqlite3.connect(analytics_db) as conn:
            cur = conn.execute("SELECT passed, total FROM test_run_stats ORDER BY run_timestamp DESC LIMIT 1")
            row = cur.fetchone()
            assert row is not None
            assert row[0] == 20  # passed
            assert row[1] == 25  # total


class TestCombinedIngestion:
    """Test ingestion of both ruff and pytest data."""

    def test_ingest_both_sources(self, temp_workspace, sample_ruff_data, sample_pytest_data):
        """Test ingestion from both ruff and pytest sources."""
        analytics_db = temp_workspace / "databases" / "analytics.db"
        ruff_json = temp_workspace / "ruff_report.json"
        pytest_json = temp_workspace / ".report.json"
        
        # Create analytics database
        with sqlite3.connect(analytics_db) as conn:
            pass
        
        # Create both JSON files
        ruff_json.write_text(json.dumps(sample_ruff_data), encoding="utf-8")
        pytest_json.write_text(json.dumps(sample_pytest_data), encoding="utf-8")
        
        # Ingest data
        ingest(str(temp_workspace))
        
        # Verify both tables have data
        with sqlite3.connect(analytics_db) as conn:
            # Check ruff data
            cur = conn.execute("SELECT issues FROM ruff_issue_log ORDER BY run_timestamp DESC LIMIT 1")
            ruff_row = cur.fetchone()
            assert ruff_row is not None
            assert ruff_row[0] == 2
            
            # Check pytest data
            cur = conn.execute("SELECT passed, total FROM test_run_stats ORDER BY run_timestamp DESC LIMIT 1")
            pytest_row = cur.fetchone()
            assert pytest_row is not None
            assert pytest_row[0] == 20
            assert pytest_row[1] == 25

    def test_multiple_ingestion_runs(self, temp_workspace, sample_ruff_data):
        """Test multiple ingestion runs accumulate data."""
        analytics_db = temp_workspace / "databases" / "analytics.db"
        ruff_json = temp_workspace / "ruff_report.json"
        
        # Create analytics database
        with sqlite3.connect(analytics_db) as conn:
            pass
        
        # Create ruff JSON file
        ruff_json.write_text(json.dumps(sample_ruff_data), encoding="utf-8")
        
        # Run ingestion multiple times
        ingest(str(temp_workspace))
        ingest(str(temp_workspace))
        ingest(str(temp_workspace))
        
        # Verify multiple records were created
        with sqlite3.connect(analytics_db) as conn:
            cur = conn.execute("SELECT COUNT(*) FROM ruff_issue_log")
            count = cur.fetchone()[0]
            assert count == 3  # Three ingestion runs


class TestTableCreation:
    """Test table creation logic."""

    def test_creates_ruff_table(self, temp_workspace):
        """Test that ruff_issue_log table is created."""
        analytics_db = temp_workspace / "databases" / "analytics.db"
        
        # Create analytics database
        with sqlite3.connect(analytics_db) as conn:
            pass
        
        # Ingest (should create tables)
        ingest(str(temp_workspace))
        
        # Verify table exists with correct schema
        with sqlite3.connect(analytics_db) as conn:
            cur = conn.execute("PRAGMA table_info(ruff_issue_log)")
            columns = {row[1]: row[2] for row in cur.fetchall()}
            
            assert "run_timestamp" in columns
            assert "issues" in columns
            assert columns["run_timestamp"] == "INTEGER"
            assert columns["issues"] == "INTEGER"

    def test_creates_test_stats_table(self, temp_workspace):
        """Test that test_run_stats table is created."""
        analytics_db = temp_workspace / "databases" / "analytics.db"
        
        # Create analytics database
        with sqlite3.connect(analytics_db) as conn:
            pass
        
        # Ingest (should create tables)
        ingest(str(temp_workspace))
        
        # Verify table exists with correct schema
        with sqlite3.connect(analytics_db) as conn:
            cur = conn.execute("PRAGMA table_info(test_run_stats)")
            columns = {row[1]: row[2] for row in cur.fetchall()}
            
            assert "run_timestamp" in columns
            assert "passed" in columns
            assert "total" in columns
            assert columns["run_timestamp"] == "INTEGER"
            assert columns["passed"] == "INTEGER"
            assert columns["total"] == "INTEGER"


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_ruff_list(self, temp_workspace):
        """Test ruff ingestion with empty list."""
        analytics_db = temp_workspace / "databases" / "analytics.db"
        ruff_json = temp_workspace / "ruff_report.json"
        
        # Create analytics database
        with sqlite3.connect(analytics_db) as conn:
            pass
        
        # Create empty ruff JSON file
        ruff_json.write_text("[]", encoding="utf-8")
        
        # Ingest data
        ingest(str(temp_workspace))
        
        # Verify 0 issues were recorded
        with sqlite3.connect(analytics_db) as conn:
            cur = conn.execute("SELECT issues FROM ruff_issue_log ORDER BY run_timestamp DESC LIMIT 1")
            row = cur.fetchone()
            assert row is not None
            assert row[0] == 0

    def test_zero_test_totals(self, temp_workspace):
        """Test pytest ingestion with zero test totals."""
        analytics_db = temp_workspace / "databases" / "analytics.db"
        pytest_json = temp_workspace / ".report.json"
        
        # Create analytics database
        with sqlite3.connect(analytics_db) as conn:
            pass
        
        # Create pytest JSON with zero totals
        pytest_data = {"summary": {"total": 0, "passed": 0}}
        pytest_json.write_text(json.dumps(pytest_data), encoding="utf-8")
        
        # Ingest data
        ingest(str(temp_workspace))
        
        # Verify zero values were recorded
        with sqlite3.connect(analytics_db) as conn:
            cur = conn.execute("SELECT passed, total FROM test_run_stats ORDER BY run_timestamp DESC LIMIT 1")
            row = cur.fetchone()
            assert row is not None
            assert row[0] == 0
            assert row[1] == 0

    def test_unicode_handling(self, temp_workspace):
        """Test handling of unicode characters in JSON."""
        analytics_db = temp_workspace / "databases" / "analytics.db"
        ruff_json = temp_workspace / "ruff_report.json"
        
        # Create analytics database
        with sqlite3.connect(analytics_db) as conn:
            pass
        
        # Create ruff JSON with unicode
        ruff_data = [{"filename": "tëst.py", "message": "ërror"}]
        ruff_json.write_text(json.dumps(ruff_data), encoding="utf-8")
        
        # Ingest data (should handle unicode gracefully)
        ingest(str(temp_workspace))
        
        # Verify data was recorded
        with sqlite3.connect(analytics_db) as conn:
            cur = conn.execute("SELECT issues FROM ruff_issue_log ORDER BY run_timestamp DESC LIMIT 1")
            row = cur.fetchone()
            assert row is not None
            assert row[0] == 1
