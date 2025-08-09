"""Tests for session lifecycle metrics module."""
from __future__ import annotations

import os
import sqlite3
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from session.session_lifecycle_metrics import _db, _ensure, end_session, start_session


@pytest.fixture
def temp_workspace():
    """Create a temporary workspace directory."""
    with tempfile.TemporaryDirectory() as tmp:
        workspace = Path(tmp)
        (workspace / "databases").mkdir()
        yield workspace


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


class TestTableEnsure:
    """Test table creation logic."""

    def test_ensure_creates_table(self, temp_workspace):
        """Test that _ensure creates session_lifecycle table."""
        analytics_db = temp_workspace / "databases" / "analytics.db"
        
        with sqlite3.connect(analytics_db) as conn:
            _ensure(conn)
            
            # Verify table exists
            cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='session_lifecycle'")
            assert cur.fetchone() is not None
            
            # Verify table schema
            cur = conn.execute("PRAGMA table_info(session_lifecycle)")
            columns = {row[1]: row[2] for row in cur.fetchall()}
            
            expected_columns = {
                "session_id": "TEXT",
                "start_ts": "INTEGER",
                "end_ts": "INTEGER",
                "duration_seconds": "REAL",
                "zero_byte_violations": "INTEGER",
                "recursion_flags": "INTEGER",
                "status": "TEXT"
            }
            
            for col, expected_type in expected_columns.items():
                assert col in columns
                assert columns[col] == expected_type

    def test_ensure_table_already_exists(self, temp_workspace):
        """Test that _ensure works when table already exists."""
        analytics_db = temp_workspace / "databases" / "analytics.db"
        
        with sqlite3.connect(analytics_db) as conn:
            # Create table manually first
            conn.execute("""CREATE TABLE session_lifecycle (
                session_id TEXT PRIMARY KEY,
                start_ts INTEGER NOT NULL,
                end_ts INTEGER,
                duration_seconds REAL,
                zero_byte_violations INTEGER DEFAULT 0,
                recursion_flags INTEGER DEFAULT 0,
                status TEXT DEFAULT 'running'
            )""")
            
            # _ensure should not fail
            _ensure(conn)
            
            # Table should still exist
            cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='session_lifecycle'")
            assert cur.fetchone() is not None


class TestStartSession:
    """Test session start functionality."""

    def test_start_session_success(self, temp_workspace):
        """Test successful session start."""
        analytics_db = temp_workspace / "databases" / "analytics.db"
        
        # Create analytics database
        with sqlite3.connect(analytics_db) as conn:
            pass
        
        session_id = "test_session_123"
        start_time = time.time()
        
        # Start session
        start_session(session_id, workspace=str(temp_workspace))
        
        # Verify session was recorded
        with sqlite3.connect(analytics_db) as conn:
            cur = conn.execute("SELECT session_id, start_ts, status FROM session_lifecycle WHERE session_id = ?", (session_id,))
            row = cur.fetchone()
            
            assert row is not None
            assert row[0] == session_id
            assert abs(row[1] - start_time) < 5  # Within 5 seconds
            assert row[2] == "running"

    def test_start_session_replace_existing(self, temp_workspace):
        """Test starting session replaces existing session with same ID."""
        analytics_db = temp_workspace / "databases" / "analytics.db"
        
        # Create analytics database
        with sqlite3.connect(analytics_db) as conn:
            pass
        
        session_id = "test_session_123"
        
        # Start session twice
        start_session(session_id, workspace=str(temp_workspace))
        time.sleep(0.1)  # Small delay
        start_session(session_id, workspace=str(temp_workspace))
        
        # Verify only one record exists
        with sqlite3.connect(analytics_db) as conn:
            cur = conn.execute("SELECT COUNT(*) FROM session_lifecycle WHERE session_id = ?", (session_id,))
            count = cur.fetchone()[0]
            assert count == 1

    def test_start_session_missing_database(self, temp_workspace):
        """Test start_session handles missing database gracefully."""
        # Remove the database file
        (temp_workspace / "databases").rmdir()
        
        # Should not raise exception
        start_session("test_session", workspace=str(temp_workspace))
        assert True  # Test passes if no exception raised

    def test_start_session_default_workspace(self):
        """Test start_session with default workspace."""
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            (workspace / "databases").mkdir()
            analytics_db = workspace / "databases" / "analytics.db"
            
            # Create analytics database
            with sqlite3.connect(analytics_db) as conn:
                pass
            
            with patch.dict(os.environ, {"GH_COPILOT_WORKSPACE": str(workspace)}):
                start_session("test_session")
                
                # Verify session was recorded
                with sqlite3.connect(analytics_db) as conn:
                    cur = conn.execute("SELECT session_id FROM session_lifecycle WHERE session_id = ?", ("test_session",))
                    row = cur.fetchone()
                    assert row is not None


class TestEndSession:
    """Test session end functionality."""

    def test_end_session_success(self, temp_workspace):
        """Test successful session end."""
        analytics_db = temp_workspace / "databases" / "analytics.db"
        
        # Create analytics database
        with sqlite3.connect(analytics_db) as conn:
            pass
        
        session_id = "test_session_123"
        
        # Start and end session
        start_session(session_id, workspace=str(temp_workspace))
        time.sleep(0.1)  # Small delay to ensure different timestamps
        end_session(
            session_id,
            zero_byte_violations=2,
            recursion_flags=1,
            status="success",
            workspace=str(temp_workspace)
        )
        
        # Verify session was updated
        with sqlite3.connect(analytics_db) as conn:
            cur = conn.execute("""
                SELECT session_id, start_ts, end_ts, duration_seconds, 
                       zero_byte_violations, recursion_flags, status 
                FROM session_lifecycle WHERE session_id = ?
            """, (session_id,))
            row = cur.fetchone()
            
            assert row is not None
            assert row[0] == session_id
            assert row[1] is not None  # start_ts
            assert row[2] is not None  # end_ts
            assert row[3] > 0  # duration_seconds should be positive
            assert row[4] == 2  # zero_byte_violations
            assert row[5] == 1  # recursion_flags
            assert row[6] == "success"  # status

    def test_end_session_without_start(self, temp_workspace):
        """Test ending session that was never started."""
        analytics_db = temp_workspace / "databases" / "analytics.db"
        
        # Create analytics database
        with sqlite3.connect(analytics_db) as conn:
            pass
        
        session_id = "nonexistent_session"
        end_time = time.time()
        
        # End session without starting
        end_session(session_id, workspace=str(temp_workspace))
        
        # Verify session was created with current time as start
        with sqlite3.connect(analytics_db) as conn:
            cur = conn.execute("""
                SELECT session_id, start_ts, end_ts, duration_seconds, status 
                FROM session_lifecycle WHERE session_id = ?
            """, (session_id,))
            row = cur.fetchone()
            
            assert row is not None
            assert row[0] == session_id
            assert abs(row[1] - end_time) < 5  # start_ts close to end_time
            assert row[2] is not None  # end_ts
            assert row[3] >= 0  # duration_seconds should be non-negative
            assert row[4] == "success"  # default status

    def test_end_session_custom_status(self, temp_workspace):
        """Test ending session with custom status."""
        analytics_db = temp_workspace / "databases" / "analytics.db"
        
        # Create analytics database
        with sqlite3.connect(analytics_db) as conn:
            pass
        
        session_id = "test_session_123"
        
        # Start and end session with custom status
        start_session(session_id, workspace=str(temp_workspace))
        end_session(
            session_id,
            status="failed",
            workspace=str(temp_workspace)
        )
        
        # Verify custom status was recorded
        with sqlite3.connect(analytics_db) as conn:
            cur = conn.execute("SELECT status FROM session_lifecycle WHERE session_id = ?", (session_id,))
            row = cur.fetchone()
            assert row is not None
            assert row[0] == "failed"

    def test_end_session_missing_database(self, temp_workspace):
        """Test end_session handles missing database gracefully."""
        # Remove the database file
        (temp_workspace / "databases").rmdir()
        
        # Should not raise exception
        end_session("test_session", workspace=str(temp_workspace))
        assert True  # Test passes if no exception raised

    def test_end_session_default_workspace(self):
        """Test end_session with default workspace."""
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            (workspace / "databases").mkdir()
            analytics_db = workspace / "databases" / "analytics.db"
            
            # Create analytics database
            with sqlite3.connect(analytics_db) as conn:
                pass
            
            with patch.dict(os.environ, {"GH_COPILOT_WORKSPACE": str(workspace)}):
                start_session("test_session")
                end_session("test_session")
                
                # Verify session was updated
                with sqlite3.connect(analytics_db) as conn:
                    cur = conn.execute("SELECT status FROM session_lifecycle WHERE session_id = ?", ("test_session",))
                    row = cur.fetchone()
                    assert row is not None
                    assert row[0] == "success"


class TestSessionLifecycle:
    """Test complete session lifecycle scenarios."""

    def test_multiple_sessions(self, temp_workspace):
        """Test multiple concurrent sessions."""
        analytics_db = temp_workspace / "databases" / "analytics.db"
        
        # Create analytics database
        with sqlite3.connect(analytics_db) as conn:
            pass
        
        # Start multiple sessions
        sessions = ["session_1", "session_2", "session_3"]
        for session_id in sessions:
            start_session(session_id, workspace=str(temp_workspace))
        
        # End sessions with different outcomes
        end_session(sessions[0], status="success", workspace=str(temp_workspace))
        end_session(sessions[1], status="failed", recursion_flags=1, workspace=str(temp_workspace))
        end_session(sessions[2], zero_byte_violations=3, workspace=str(temp_workspace))
        
        # Verify all sessions were recorded
        with sqlite3.connect(analytics_db) as conn:
            cur = conn.execute("SELECT COUNT(*) FROM session_lifecycle")
            count = cur.fetchone()[0]
            assert count == 3
            
            # Verify different statuses
            cur = conn.execute("SELECT session_id, status FROM session_lifecycle ORDER BY session_id")
            rows = cur.fetchall()
            assert rows[0][1] == "success"    # session_1
            assert rows[1][1] == "failed"     # session_2
            assert rows[2][1] == "success"    # session_3 (default)

    def test_session_duration_calculation(self, temp_workspace):
        """Test session duration is calculated correctly."""
        analytics_db = temp_workspace / "databases" / "analytics.db"
        
        # Create analytics database
        with sqlite3.connect(analytics_db) as conn:
            pass
        
        session_id = "test_session_123"
        
        # Start session
        start_session(session_id, workspace=str(temp_workspace))
        
        # Wait a known duration
        time.sleep(0.2)  # 200ms
        
        # End session
        end_session(session_id, workspace=str(temp_workspace))
        
        # Verify duration is reasonable
        with sqlite3.connect(analytics_db) as conn:
            cur = conn.execute("SELECT duration_seconds FROM session_lifecycle WHERE session_id = ?", (session_id,))
            duration = cur.fetchone()[0]
            
            assert duration >= 0.1  # At least 100ms
            assert duration <= 1.0   # Less than 1 second

    def test_default_parameter_values(self, temp_workspace):
        """Test default parameter values."""
        analytics_db = temp_workspace / "databases" / "analytics.db"
        
        # Create analytics database
        with sqlite3.connect(analytics_db) as conn:
            pass
        
        session_id = "test_session_123"
        
        # Start and end session with defaults
        start_session(session_id, workspace=str(temp_workspace))
        end_session(session_id, workspace=str(temp_workspace))
        
        # Verify default values
        with sqlite3.connect(analytics_db) as conn:
            cur = conn.execute("""
                SELECT zero_byte_violations, recursion_flags, status 
                FROM session_lifecycle WHERE session_id = ?
            """, (session_id,))
            row = cur.fetchone()
            
            assert row[0] == 0  # zero_byte_violations default
            assert row[1] == 0  # recursion_flags default
            assert row[2] == "success"  # status default


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_very_long_session_id(self, temp_workspace):
        """Test with very long session ID."""
        analytics_db = temp_workspace / "databases" / "analytics.db"
        
        # Create analytics database
        with sqlite3.connect(analytics_db) as conn:
            pass
        
        # Use very long session ID
        session_id = "a" * 1000
        
        start_session(session_id, workspace=str(temp_workspace))
        end_session(session_id, workspace=str(temp_workspace))
        
        # Verify session was recorded
        with sqlite3.connect(analytics_db) as conn:
            cur = conn.execute("SELECT session_id FROM session_lifecycle WHERE session_id = ?", (session_id,))
            row = cur.fetchone()
            assert row is not None
            assert row[0] == session_id

    def test_special_characters_in_session_id(self, temp_workspace):
        """Test with special characters in session ID."""
        analytics_db = temp_workspace / "databases" / "analytics.db"
        
        # Create analytics database
        with sqlite3.connect(analytics_db) as conn:
            pass
        
        # Use session ID with special characters
        session_id = "session-123_test@domain.com"
        
        start_session(session_id, workspace=str(temp_workspace))
        end_session(session_id, workspace=str(temp_workspace))
        
        # Verify session was recorded
        with sqlite3.connect(analytics_db) as conn:
            cur = conn.execute("SELECT session_id FROM session_lifecycle WHERE session_id = ?", (session_id,))
            row = cur.fetchone()
            assert row is not None
            assert row[0] == session_id

    def test_negative_violation_counts(self, temp_workspace):
        """Test with negative violation counts."""
        analytics_db = temp_workspace / "databases" / "analytics.db"
        
        # Create analytics database
        with sqlite3.connect(analytics_db) as conn:
            pass
        
        session_id = "test_session_123"
        
        start_session(session_id, workspace=str(temp_workspace))
        end_session(
            session_id,
            zero_byte_violations=-5,
            recursion_flags=-2,
            workspace=str(temp_workspace)
        )
        
        # Verify values were recorded (database allows negative values)
        with sqlite3.connect(analytics_db) as conn:
            cur = conn.execute("""
                SELECT zero_byte_violations, recursion_flags 
                FROM session_lifecycle WHERE session_id = ?
            """, (session_id,))
            row = cur.fetchone()
            assert row[0] == -5
            assert row[1] == -2

    def test_unicode_session_id(self, temp_workspace):
        """Test with unicode characters in session ID."""
        analytics_db = temp_workspace / "databases" / "analytics.db"
        
        # Create analytics database
        with sqlite3.connect(analytics_db) as conn:
            pass
        
        # Use session ID with unicode characters
        session_id = "session_测试_ëxample"
        
        start_session(session_id, workspace=str(temp_workspace))
        end_session(session_id, workspace=str(temp_workspace))
        
        # Verify session was recorded
        with sqlite3.connect(analytics_db) as conn:
            cur = conn.execute("SELECT session_id FROM session_lifecycle WHERE session_id = ?", (session_id,))
            row = cur.fetchone()
            assert row is not None
            assert row[0] == session_id
