"""Tests for compliance metrics updater script."""
from __future__ import annotations

import os
import sqlite3
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from scripts.compliance.update_compliance_metrics import (
    ComplianceComponents,
    _compute,
    _connect,
    _ensure_table,
    _ensure_metrics_table,
    _fetch_components,
    _table_exists,
    fetch_recent_compliance,
    update_compliance_metrics,
)


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        yield Path(tmp.name)
    Path(tmp.name).unlink(missing_ok=True)


@pytest.fixture
def temp_workspace():
    """Create a temporary workspace directory."""
    with tempfile.TemporaryDirectory() as tmp:
        workspace = Path(tmp)
        (workspace / "databases").mkdir()
        yield workspace


class TestComplianceComponents:
    """Test ComplianceComponents dataclass."""

    def test_compliance_components_creation(self):
        """Test ComplianceComponents dataclass initialization."""
        comp = ComplianceComponents(
            ruff_issues=5,
            tests_passed=18,
            tests_total=20,
            placeholders_open=10,
            placeholders_resolved=15
        )
        assert comp.ruff_issues == 5
        assert comp.tests_passed == 18
        assert comp.tests_total == 20
        assert comp.placeholders_open == 10
        assert comp.placeholders_resolved == 15


class TestDatabaseFunctions:
    """Test database utility functions."""

    def test_connect(self, temp_db):
        """Test database connection."""
        conn = _connect(temp_db)
        assert isinstance(conn, sqlite3.Connection)
        conn.close()

    def test_table_exists_false(self, temp_db):
        """Test table_exists returns False for non-existent table."""
        with _connect(temp_db) as conn:
            assert not _table_exists(conn, "nonexistent_table")

    def test_table_exists_true(self, temp_db):
        """Test table_exists returns True for existing table."""
        with _connect(temp_db) as conn:
            conn.execute("CREATE TABLE test_table (id INTEGER)")
            assert _table_exists(conn, "test_table")

    def test_ensure_table(self, temp_db):
        """Test compliance_scores table creation."""
        with _connect(temp_db) as conn:
            _ensure_table(conn)
            assert _table_exists(conn, "compliance_scores")
            
            # Verify table structure
            cur = conn.execute("PRAGMA table_info(compliance_scores)")
            columns = {row[1]: row[2] for row in cur.fetchall()}
            
            expected_columns = {
                "id": "INTEGER",
                "timestamp": "INTEGER",
                "L": "REAL",
                "T": "REAL", 
                "P": "REAL",
                "composite": "REAL",
                "ruff_issues": "INTEGER",
                "tests_passed": "INTEGER",
                "tests_total": "INTEGER",
                "placeholders_open": "INTEGER",
                "placeholders_resolved": "INTEGER"
            }
            
            for col, type_name in expected_columns.items():
                assert col in columns
                assert columns[col] == type_name

    def test_ensure_metrics_table(self, temp_db):
        """Test compliance_metrics_history table creation."""
        with _connect(temp_db) as conn:
            _ensure_metrics_table(conn)
            assert _table_exists(conn, "compliance_metrics_history")


class TestComponentFetching:
    """Test component data fetching from database."""

    def test_fetch_components_empty_db(self, temp_db):
        """Test fetching components from empty database."""
        with _connect(temp_db) as conn:
            comp = _fetch_components(conn)
            assert comp.ruff_issues == 0
            assert comp.tests_passed == 0
            assert comp.tests_total == 0
            assert comp.placeholders_open == 0
            assert comp.placeholders_resolved == 0

    def test_fetch_components_with_data(self, temp_db):
        """Test fetching components from populated database."""
        with _connect(temp_db) as conn:
            # Create tables and insert test data
            conn.execute("CREATE TABLE ruff_issue_log (issues INTEGER)")
            conn.execute("INSERT INTO ruff_issue_log VALUES (5)")
            conn.execute("INSERT INTO ruff_issue_log VALUES (3)")
            
            conn.execute("CREATE TABLE test_run_stats (passed INTEGER, total INTEGER)")
            conn.execute("INSERT INTO test_run_stats VALUES (18, 20)")
            conn.execute("INSERT INTO test_run_stats VALUES (15, 18)")
            
            conn.execute(
                "CREATE TABLE placeholder_audit_snapshots (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp INTEGER, open_count INTEGER, resolved_count INTEGER)"
            )
            conn.execute(
                "INSERT INTO placeholder_audit_snapshots(timestamp, open_count, resolved_count) VALUES (1, 10, 15)"
            )
            conn.execute(
                "INSERT INTO placeholder_audit_snapshots(timestamp, open_count, resolved_count) VALUES (2, 8, 18)"
            )
            
            comp = _fetch_components(conn)
            assert comp.ruff_issues == 8  # Sum of issues
            assert comp.tests_passed == 33  # Sum of passed
            assert comp.tests_total == 38   # Sum of total
            assert comp.placeholders_open == 8    # Latest open count
            assert comp.placeholders_resolved == 18  # Latest resolved count

    def test_fetch_components_missing_tables(self, temp_db):
        """Test fetching components when some tables are missing."""
        with _connect(temp_db) as conn:
            # Only create ruff_issue_log
            conn.execute("CREATE TABLE ruff_issue_log (issues INTEGER)")
            conn.execute("INSERT INTO ruff_issue_log VALUES (3)")
            
            comp = _fetch_components(conn)
            assert comp.ruff_issues == 3
            assert comp.tests_passed == 0
            assert comp.tests_total == 0
            assert comp.placeholders_open == 0
            assert comp.placeholders_resolved == 0


class TestScoreComputation:
    """Test score computation logic."""

    def test_compute_perfect_scores(self):
        """Test computation with perfect scores."""
        comp = ComplianceComponents(
            ruff_issues=0,
            tests_passed=20,
            tests_total=20,
            placeholders_open=0,
            placeholders_resolved=10
        )
        L, T, P, composite = _compute(comp)
        
        assert L == 100.0  # No ruff issues
        assert T == 100.0  # All tests passed
        assert P == 100.0  # No open placeholders
        assert composite == 100.0  # Perfect composite

    def test_compute_zero_scores(self):
        """Test computation with poor scores."""
        comp = ComplianceComponents(
            ruff_issues=150,
            tests_passed=0,
            tests_total=20,
            placeholders_open=10,
            placeholders_resolved=0
        )
        L, T, P, composite = _compute(comp)
        
        assert L == 0.0   # Max(0, 100-150)
        assert T == 0.0   # 0/20 tests passed
        assert P == 0.0   # 0 resolved placeholders
        assert composite == 0.0  # 0.3*0 + 0.5*0 + 0.2*0

    def test_compute_mixed_scores(self):
        """Test computation with mixed scores."""
        comp = ComplianceComponents(
            ruff_issues=20,
            tests_passed=16,
            tests_total=20,
            placeholders_open=4,
            placeholders_resolved=6
        )
        L, T, P, composite = _compute(comp)
        
        assert L == 80.0  # 100-20
        assert T == 80.0  # 16/20 * 100
        assert P == 60.0  # 6/10 * 100
        assert composite == pytest.approx(76.0)  # 0.3*80 + 0.5*80 + 0.2*60

    def test_compute_no_tests(self):
        """Test computation when no tests exist."""
        comp = ComplianceComponents(
            ruff_issues=5,
            tests_passed=0,
            tests_total=0,
            placeholders_open=2,
            placeholders_resolved=8
        )
        L, T, P, composite = _compute(comp)
        
        assert L == 95.0  # 100-5
        assert T == 0.0   # No tests to evaluate
        assert P == 80.0  # 8/10 * 100
        assert composite == pytest.approx(44.5)  # 0.3*95 + 0.5*0 + 0.2*80

    def test_compute_no_placeholders(self):
        """Test computation when no placeholders exist."""
        comp = ComplianceComponents(
            ruff_issues=10,
            tests_passed=18,
            tests_total=20,
            placeholders_open=0,
            placeholders_resolved=0
        )
        L, T, P, composite = _compute(comp)
        
        assert L == 90.0   # 100-10
        assert T == 90.0   # 18/20 * 100
        assert P == 0.0  # No placeholders => placeholder score 0
        assert composite == pytest.approx(72.0)  # 0.3*90 + 0.5*90 + 0.2*0


class TestUpdateComplianceMetrics:
    """Test main update function."""

    def test_update_compliance_metrics_success(self, temp_workspace):
        """Test successful compliance metrics update."""
        analytics_db = temp_workspace / "databases" / "analytics.db"
        
        # Create analytics database with test data
        with _connect(analytics_db) as conn:
            conn.execute("CREATE TABLE ruff_issue_log (issues INTEGER)")
            conn.execute("INSERT INTO ruff_issue_log VALUES (5)")
            
            conn.execute("CREATE TABLE test_run_stats (passed INTEGER, total INTEGER)")
            conn.execute("INSERT INTO test_run_stats VALUES (18, 20)")
            
            conn.execute(
                "CREATE TABLE placeholder_audit_snapshots (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp INTEGER, open_count INTEGER, resolved_count INTEGER)"
            )
            conn.execute(
                "INSERT INTO placeholder_audit_snapshots(timestamp, open_count, resolved_count) VALUES (1, 2, 8)"
            )
        
        # Update metrics
        score = update_compliance_metrics(str(temp_workspace))
        
        # Verify score is reasonable
        assert 0.0 <= score <= 100.0
        
        # Verify data was written to compliance_scores table
        with _connect(analytics_db) as conn:
            # Use the most complete and robust checks from both sides of the conflict:
            cur = conn.execute("SELECT * FROM compliance_scores ORDER BY id DESC LIMIT 1")
            row = cur.fetchone()
            assert row is not None

            # Verify timestamp is recent
            timestamp = row[1]
            assert abs(timestamp - time.time()) < 60  # Within last minute

            # Verify composite score matches
            composite = row[5]
            assert composite == score

    def test_update_compliance_metrics_missing_db(self, temp_workspace):
        """Test update when analytics database doesn't exist."""
        with pytest.raises(FileNotFoundError):
            update_compliance_metrics(str(temp_workspace))

    def test_update_compliance_metrics_backup_rejection(self, temp_workspace):
        """Test update rejects backup directory."""
        backup_workspace = temp_workspace / "backup_workspace" 
        backup_workspace.mkdir()
        (backup_workspace / "databases").mkdir()
        analytics_db = backup_workspace / "databases" / "analytics.db"
        analytics_db.touch()
        
        with pytest.raises(RuntimeError, match="backup directory"):
            update_compliance_metrics(str(backup_workspace))

    @patch.dict(os.environ, {"GH_COPILOT_WORKSPACE": "/tmp/test_workspace"})
    def test_update_compliance_metrics_env_workspace(self):
        """Test update uses environment variable for workspace."""
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            (workspace / "databases").mkdir()
            analytics_db = workspace / "databases" / "analytics.db"
            
            # Create minimal database
            with _connect(analytics_db) as conn:
                pass  # Empty db, should use defaults
            
            with patch.dict(os.environ, {"GH_COPILOT_WORKSPACE": str(workspace)}):
                score = update_compliance_metrics()
                assert score == 30.0  # Expected default score with placeholder penalty

    def test_update_compliance_metrics_custom_db_path(self, temp_workspace):
        """Test update with custom database path."""
        custom_db = temp_workspace / "custom.db"
        
        # Create custom database
        with _connect(custom_db) as conn:
            pass  # Empty db
        
        score = update_compliance_metrics(str(temp_workspace), custom_db)
        assert score == 30.0  # Expected default score with placeholder penalty


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_null_values_in_database(self, temp_db):
        """Test handling of NULL values in database."""
        with _connect(temp_db) as conn:
            conn.execute("CREATE TABLE ruff_issue_log (issues INTEGER)")
            conn.execute("INSERT INTO ruff_issue_log VALUES (NULL)")
            
            comp = _fetch_components(conn)
        assert comp.ruff_issues == 0  # NULL should be treated as 0

    def test_fetch_recent_compliance(self, temp_workspace):
        """fetch_recent_compliance returns inserted rows from history table."""
        analytics_db = temp_workspace / "databases" / "analytics.db"
        with sqlite3.connect(analytics_db) as conn:
            _ensure_metrics_table(conn)
            conn.execute(
                "INSERT INTO compliance_metrics_history (ts, ruff_issues, tests_passed, tests_total, placeholders_open, placeholders_resolved, lint_score, test_score, placeholder_score, composite_score, source, meta_json) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                (1, 1, 1, 1, 0, 0, 99.0, 100.0, 0.0, 50.0, "test", None),
            )
            conn.commit()
        rows = fetch_recent_compliance(workspace=str(temp_workspace))
        assert rows and rows[0]["composite"] == 50.0

    def test_very_large_values(self):
        """Test computation with very large values."""
        comp = ComplianceComponents(
            ruff_issues=999999,
            tests_passed=1000000,
            tests_total=1000000,
            placeholders_open=0,
            placeholders_resolved=1000000
        )
        L, T, P, composite = _compute(comp)
        
        assert L == 0.0     # Should be clamped to 0
        assert T == 100.0   # Perfect test score
        assert P == 100.0   # Perfect placeholder score
        assert composite == 70.0  # 0.3*0 + 0.5*100 + 0.2*100

    def test_negative_values(self):
        """Test computation handles negative values gracefully."""
        comp = ComplianceComponents(
            ruff_issues=-5,  # Should be treated as 0 issues
            tests_passed=-1, # Invalid but handled
            tests_total=10,
            placeholders_open=5,
            placeholders_resolved=3
        )
        L, T, P, composite = _compute(comp)
        
        # Negative ruff issue counts are clamped to 100%
        assert L == 100.0
