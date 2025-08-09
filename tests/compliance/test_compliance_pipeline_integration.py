"""Integration tests for complete compliance pipeline."""
from __future__ import annotations

import json
import sqlite3
import tempfile
import time
from pathlib import Path

import pytest

from scripts.compliance.update_compliance_metrics import update_compliance_metrics
from scripts.ingest_test_and_lint_results import ingest
from session.session_lifecycle_metrics import end_session, start_session


@pytest.fixture
def temp_workspace():
    """Create a temporary workspace directory."""
    with tempfile.TemporaryDirectory() as tmp:
        workspace = Path(tmp)
        (workspace / "databases").mkdir()
        yield workspace


@pytest.fixture
def sample_compliance_data():
    """Sample data for complete compliance pipeline test."""
    return {
        "ruff_data": [
            {"filename": "test1.py", "rule": "F401", "message": "unused import"},
            {"filename": "test2.py", "rule": "E302", "message": "expected 2 blank lines"},
            {"filename": "test3.py", "rule": "W503", "message": "line break before binary operator"}
        ],
        "pytest_data": {
            "summary": {
                "total": 50,
                "passed": 45,
                "failed": 3,
                "skipped": 2,
                "error": 0
            }
        },
        "placeholder_data": {
            "open_count": 8,
            "resolved_count": 22
        }
    }


class TestCompleteCompliancePipeline:
    """Test the complete compliance pipeline end-to-end."""

    def test_full_pipeline_integration(self, temp_workspace, sample_compliance_data):
        """Test complete pipeline from ingestion to scoring."""
        analytics_db = temp_workspace / "databases" / "analytics.db"
        ruff_json = temp_workspace / "ruff_report.json"
        pytest_json = temp_workspace / ".report.json"
        
        # Step 1: Create analytics database
        with sqlite3.connect(analytics_db) as conn:
            pass
        
        # Step 2: Create sample data files
        ruff_json.write_text(json.dumps(sample_compliance_data["ruff_data"]), encoding="utf-8")
        pytest_json.write_text(json.dumps(sample_compliance_data["pytest_data"]), encoding="utf-8")
        
        # Step 3: Simulate placeholder audit results
        with sqlite3.connect(analytics_db) as conn:
            conn.execute("CREATE TABLE placeholder_audit_snapshots (id INTEGER, open_count INTEGER, resolved_count INTEGER)")
            conn.execute("INSERT INTO placeholder_audit_snapshots VALUES (1, ?, ?)", 
                        (sample_compliance_data["placeholder_data"]["open_count"],
                         sample_compliance_data["placeholder_data"]["resolved_count"]))
            conn.commit()
        
        # Step 4: Ingest test and lint results
        ingest(str(temp_workspace))
        
        # Step 5: Update compliance metrics
        composite_score = update_compliance_metrics(str(temp_workspace))
        
        # Step 6: Verify complete pipeline results
        assert 0.0 <= composite_score <= 100.0
        
        # Verify all tables were created and populated
        with sqlite3.connect(analytics_db) as conn:
            # Check ruff_issue_log
            cur = conn.execute("SELECT issues FROM ruff_issue_log ORDER BY run_timestamp DESC LIMIT 1")
            ruff_row = cur.fetchone()
            assert ruff_row is not None
            assert ruff_row[0] == 3  # Three issues in sample data
            
            # Check test_run_stats
            cur = conn.execute("SELECT passed, total FROM test_run_stats ORDER BY run_timestamp DESC LIMIT 1")
            test_row = cur.fetchone()
            assert test_row is not None
            assert test_row[0] == 45  # passed
            assert test_row[1] == 50  # total
            
            # Check compliance_scores legacy table
            cur = conn.execute("SELECT L, T, P, composite FROM compliance_scores ORDER BY id DESC LIMIT 1")
            score_row = cur.fetchone()
            assert score_row is not None

            L, T, P, composite = score_row
            assert L == 97.0  # max(0, 100-3)
            assert T == 90.0  # 45/50 * 100
            assert P == pytest.approx(73.33, abs=0.1)  # 22/30 * 100
            assert composite == pytest.approx(88.77, abs=0.1)  # 0.3*97 + 0.5*90 + 0.2*73.33

            # Check unified history table
            cur = conn.execute(
                "SELECT composite_score FROM compliance_metrics_history ORDER BY id DESC LIMIT 1"
            )
            assert cur.fetchone() is not None

    def test_pipeline_with_session_tracking(self, temp_workspace, sample_compliance_data):
        """Test pipeline integration with session lifecycle tracking."""
        analytics_db = temp_workspace / "databases" / "analytics.db"
        ruff_json = temp_workspace / "ruff_report.json"
        pytest_json = temp_workspace / ".report.json"
        
        # Create analytics database
        with sqlite3.connect(analytics_db) as conn:
            pass
        
        session_id = "compliance_pipeline_test_session"
        
        # Start session tracking
        start_session(session_id, workspace=str(temp_workspace))
        
        # Create test data files
        ruff_json.write_text(json.dumps(sample_compliance_data["ruff_data"]), encoding="utf-8")
        pytest_json.write_text(json.dumps(sample_compliance_data["pytest_data"]), encoding="utf-8")
        
        # Add placeholder data
        with sqlite3.connect(analytics_db) as conn:
            conn.execute("CREATE TABLE placeholder_audit_snapshots (id INTEGER, open_count INTEGER, resolved_count INTEGER)")
            conn.execute("INSERT INTO placeholder_audit_snapshots VALUES (1, ?, ?)", 
                        (sample_compliance_data["placeholder_data"]["open_count"],
                         sample_compliance_data["placeholder_data"]["resolved_count"]))
            conn.commit()
        
        # Run pipeline
        ingest(str(temp_workspace))
        composite_score = update_compliance_metrics(str(temp_workspace))
        
        # End session tracking
        end_session(session_id, status="success", workspace=str(temp_workspace))
        
        # Verify session was tracked
        with sqlite3.connect(analytics_db) as conn:
            cur = conn.execute("SELECT session_id, status, duration_seconds FROM session_lifecycle WHERE session_id = ?", (session_id,))
            session_row = cur.fetchone()
            assert session_row is not None
            assert session_row[0] == session_id
            assert session_row[1] == "success"
            assert session_row[2] >= 0  # Duration may be near zero in tests
        
        # Verify compliance score was calculated
        assert composite_score > 0

    def test_multiple_pipeline_runs(self, temp_workspace, sample_compliance_data):
        """Test multiple runs of the compliance pipeline."""
        analytics_db = temp_workspace / "databases" / "analytics.db"
        ruff_json = temp_workspace / "ruff_report.json"
        pytest_json = temp_workspace / ".report.json"
        
        # Create analytics database
        with sqlite3.connect(analytics_db) as conn:
            pass
        
        # Add placeholder data once
        with sqlite3.connect(analytics_db) as conn:
            conn.execute("CREATE TABLE placeholder_audit_snapshots (id INTEGER, open_count INTEGER, resolved_count INTEGER)")
            conn.execute("INSERT INTO placeholder_audit_snapshots VALUES (1, ?, ?)", 
                        (sample_compliance_data["placeholder_data"]["open_count"],
                         sample_compliance_data["placeholder_data"]["resolved_count"]))
            conn.commit()
        
        scores = []
        
        # Run pipeline multiple times with different data
        for run in range(3):
            # Modify ruff issues for each run
            modified_ruff_data = sample_compliance_data["ruff_data"][:run+1]  # 1, 2, 3 issues
            ruff_json.write_text(json.dumps(modified_ruff_data), encoding="utf-8")
            pytest_json.write_text(json.dumps(sample_compliance_data["pytest_data"]), encoding="utf-8")
            
            # Run pipeline
            ingest(str(temp_workspace))
            score = update_compliance_metrics(str(temp_workspace))
            scores.append(score)
            
            time.sleep(0.1)  # Small delay between runs
        
        # Verify scores decreased as issues increased
        assert len(scores) == 3
        assert scores[0] > scores[1] > scores[2]  # Scores should decrease
        
        # Verify all runs were recorded
        with sqlite3.connect(analytics_db) as conn:
            # Check multiple ruff entries
            cur = conn.execute("SELECT COUNT(*) FROM ruff_issue_log")
            ruff_count = cur.fetchone()[0]
            assert ruff_count == 3
            
            # Check multiple compliance score entries
            cur = conn.execute("SELECT COUNT(*) FROM compliance_scores")
            score_count = cur.fetchone()[0]
            assert score_count == 6

    def test_pipeline_with_missing_data(self, temp_workspace):
        """Test pipeline behavior with missing or incomplete data."""
        analytics_db = temp_workspace / "databases" / "analytics.db"
        
        # Create analytics database
        with sqlite3.connect(analytics_db) as conn:
            pass
        
        # Run pipeline with no data files (should use defaults)
        ingest(str(temp_workspace))
        score = update_compliance_metrics(str(temp_workspace))
        
        # Should get default score (no issues, no tests, placeholders unresolved)
        # L = 100 (no ruff issues), T = 0 (no tests), P = 0 (no placeholder scan)
        # composite = 0.3*100 + 0.5*0 + 0.2*0 = 30
        assert score == 30.0
        
        # Verify data was recorded with zeros
        with sqlite3.connect(analytics_db) as conn:
            cur = conn.execute("SELECT L, T, P, composite FROM compliance_scores ORDER BY id DESC LIMIT 1")
            row = cur.fetchone()
            assert row is not None
            assert row[0] == 100.0  # L
            assert row[1] == 0.0    # T
            assert row[2] == 0.0    # P
            assert row[3] == 30.0   # composite

    def test_pipeline_error_recovery(self, temp_workspace):
        """Test pipeline behavior with malformed data."""
        analytics_db = temp_workspace / "databases" / "analytics.db"
        ruff_json = temp_workspace / "ruff_report.json"
        pytest_json = temp_workspace / ".report.json"
        
        # Create analytics database
        with sqlite3.connect(analytics_db) as conn:
            pass
        
        # Create malformed JSON files
        ruff_json.write_text("{ invalid json", encoding="utf-8")
        pytest_json.write_text("{ also invalid", encoding="utf-8")
        
        # Pipeline should handle errors gracefully
        ingest(str(temp_workspace))
        score = update_compliance_metrics(str(temp_workspace))
        
        # Should still produce a score using default values
        assert 0.0 <= score <= 100.0
        
        # Verify zero values were recorded for malformed data
        with sqlite3.connect(analytics_db) as conn:
            cur = conn.execute("SELECT issues FROM ruff_issue_log ORDER BY run_timestamp DESC LIMIT 1")
            ruff_row = cur.fetchone()
            assert ruff_row is not None
            assert ruff_row[0] == 0  # Zero issues due to malformed JSON
            
            cur = conn.execute("SELECT passed, total FROM test_run_stats ORDER BY run_timestamp DESC LIMIT 1")
            test_row = cur.fetchone()
            assert test_row is not None
            assert test_row[0] == 0  # Zero passed due to malformed JSON
            assert test_row[1] == 0  # Zero total due to malformed JSON


class TestAPIEndpointIntegration:
    """Test integration with API endpoints."""

    def test_compliance_scores_api_data(self, temp_workspace, sample_compliance_data):
        """Test that compliance scores API would return expected data."""
        analytics_db = temp_workspace / "databases" / "analytics.db"
        ruff_json = temp_workspace / "ruff_report.json"
        pytest_json = temp_workspace / ".report.json"
        
        # Create analytics database
        with sqlite3.connect(analytics_db) as conn:
            pass
        
        # Setup test data
        ruff_json.write_text(json.dumps(sample_compliance_data["ruff_data"]), encoding="utf-8")
        pytest_json.write_text(json.dumps(sample_compliance_data["pytest_data"]), encoding="utf-8")
        
        # Add placeholder data
        with sqlite3.connect(analytics_db) as conn:
            conn.execute("CREATE TABLE placeholder_audit_snapshots (id INTEGER, open_count INTEGER, resolved_count INTEGER)")
            conn.execute("INSERT INTO placeholder_audit_snapshots VALUES (1, ?, ?)", 
                        (sample_compliance_data["placeholder_data"]["open_count"],
                         sample_compliance_data["placeholder_data"]["resolved_count"]))
            conn.commit()
        
        # Run pipeline multiple times to create history
        for i in range(5):
            ingest(str(temp_workspace))
            update_compliance_metrics(str(temp_workspace))
            time.sleep(0.1)
        
        # Simulate API endpoint query
        with sqlite3.connect(analytics_db) as conn:
            cur = conn.execute("SELECT timestamp, composite FROM compliance_scores ORDER BY id DESC LIMIT 50")
            api_data = [{"timestamp": r[0], "composite": r[1]} for r in cur.fetchall()]
        
        # Verify API data structure (two entries per run)
        assert len(api_data) == 10
        for entry in api_data:
            assert "timestamp" in entry
            assert "composite" in entry
            assert isinstance(entry["timestamp"], int)
            assert isinstance(entry["composite"], (int, float))
            assert 0 <= entry["composite"] <= 100

    def test_refresh_compliance_workflow(self, temp_workspace, sample_compliance_data):
        """Test the refresh compliance workflow."""
        analytics_db = temp_workspace / "databases" / "analytics.db"
        ruff_json = temp_workspace / "ruff_report.json"
        pytest_json = temp_workspace / ".report.json"
        
        # Create analytics database
        with sqlite3.connect(analytics_db) as conn:
            pass
        
        # Initial setup
        ruff_json.write_text(json.dumps(sample_compliance_data["ruff_data"]), encoding="utf-8")
        pytest_json.write_text(json.dumps(sample_compliance_data["pytest_data"]), encoding="utf-8")
        
        # Add placeholder data
        with sqlite3.connect(analytics_db) as conn:
            conn.execute("CREATE TABLE placeholder_audit_snapshots (id INTEGER, open_count INTEGER, resolved_count INTEGER)")
            conn.execute("INSERT INTO placeholder_audit_snapshots VALUES (1, ?, ?)", 
                        (sample_compliance_data["placeholder_data"]["open_count"],
                         sample_compliance_data["placeholder_data"]["resolved_count"]))
            conn.commit()
        
        # Run initial ingestion
        ingest(str(temp_workspace))
        
        # Simulate refresh compliance API call
        initial_score = update_compliance_metrics(str(temp_workspace))
        
        # Modify data to simulate changes
        improved_ruff_data = sample_compliance_data["ruff_data"][:1]  # Fewer issues
        ruff_json.write_text(json.dumps(improved_ruff_data), encoding="utf-8")
        
        improved_pytest_data = {
            "summary": {
                "total": 50,
                "passed": 48,  # More tests passing
                "failed": 2,
                "skipped": 0
            }
        }
        pytest_json.write_text(json.dumps(improved_pytest_data), encoding="utf-8")
        
        # Run refresh workflow
        ingest(str(temp_workspace))
        updated_score = update_compliance_metrics(str(temp_workspace))
        
        # Score should improve
        assert updated_score > initial_score
        
        # Verify both scores are recorded
        with sqlite3.connect(analytics_db) as conn:
            cur = conn.execute("SELECT COUNT(*) FROM compliance_scores")
            count = cur.fetchone()[0]
            assert count == 4


class TestPerformanceAndScale:
    """Test performance and scalability aspects."""

    def test_large_dataset_handling(self, temp_workspace):
        """Test pipeline with large datasets."""
        analytics_db = temp_workspace / "databases" / "analytics.db"
        ruff_json = temp_workspace / "ruff_report.json"
        pytest_json = temp_workspace / ".report.json"
        
        # Create analytics database
        with sqlite3.connect(analytics_db) as conn:
            pass
        
        # Create large datasets
        large_ruff_data = [
            {"filename": f"test{i}.py", "rule": "F401", "message": f"error {i}"}
            for i in range(1000)  # 1000 ruff issues
        ]
        
        large_pytest_data = {
            "summary": {
                "total": 5000,
                "passed": 4800,
                "failed": 150,
                "skipped": 50
            }
        }
        
        ruff_json.write_text(json.dumps(large_ruff_data), encoding="utf-8")
        pytest_json.write_text(json.dumps(large_pytest_data), encoding="utf-8")
        
        # Add placeholder data
        with sqlite3.connect(analytics_db) as conn:
            conn.execute("CREATE TABLE placeholder_audit_snapshots (id INTEGER, open_count INTEGER, resolved_count INTEGER)")
            conn.execute("INSERT INTO placeholder_audit_snapshots VALUES (1, 50, 500)")
            conn.commit()
        
        # Measure execution time
        start_time = time.time()
        ingest(str(temp_workspace))
        score = update_compliance_metrics(str(temp_workspace))
        end_time = time.time()
        
        # Should complete within reasonable time
        execution_time = end_time - start_time
        assert execution_time < 5.0  # Should complete within 5 seconds
        
        # Verify correct score calculation
        assert 0.0 <= score <= 100.0
        
        # Verify data was processed correctly
        with sqlite3.connect(analytics_db) as conn:
            cur = conn.execute("SELECT issues FROM ruff_issue_log ORDER BY run_timestamp DESC LIMIT 1")
            ruff_row = cur.fetchone()
            assert ruff_row[0] == 1000  # All 1000 issues recorded
            
            cur = conn.execute("SELECT passed, total FROM test_run_stats ORDER BY run_timestamp DESC LIMIT 1")
            test_row = cur.fetchone()
            assert test_row[0] == 4800  # All passed tests recorded
            assert test_row[1] == 5000  # All total tests recorded
