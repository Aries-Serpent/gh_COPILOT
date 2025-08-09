"""Test configuration and fixtures for compliance tests."""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def analytics_db_schema():
    """Define the expected analytics database schema."""
    return {
        "compliance_scores": {
            "columns": {
                "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
                "timestamp": "INTEGER NOT NULL",
                "L": "REAL NOT NULL",
                "T": "REAL NOT NULL", 
                "P": "REAL NOT NULL",
                "composite": "REAL NOT NULL",
                "ruff_issues": "INTEGER NOT NULL",
                "tests_passed": "INTEGER NOT NULL",
                "tests_total": "INTEGER NOT NULL",
                "placeholders_open": "INTEGER NOT NULL",
                "placeholders_resolved": "INTEGER NOT NULL"
            }
        },
        "ruff_issue_log": {
            "columns": {
                "run_timestamp": "INTEGER DEFAULT (STRFTIME('%s','now'))",
                "issues": "INTEGER"
            }
        },
        "test_run_stats": {
            "columns": {
                "run_timestamp": "INTEGER DEFAULT (STRFTIME('%s','now'))",
                "passed": "INTEGER",
                "total": "INTEGER"
            }
        },
        "session_lifecycle": {
            "columns": {
                "session_id": "TEXT PRIMARY KEY",
                "start_ts": "INTEGER NOT NULL",
                "end_ts": "INTEGER",
                "duration_seconds": "REAL",
                "zero_byte_violations": "INTEGER DEFAULT 0",
                "recursion_flags": "INTEGER DEFAULT 0",
                "status": "TEXT DEFAULT 'running'"
            }
        },
        "placeholder_audit_snapshots": {
            "columns": {
                "id": "INTEGER",
                "open_count": "INTEGER",
                "resolved_count": "INTEGER"
            }
        }
    }


@pytest.fixture
def verify_schema():
    """Fixture to verify database schema matches expectations."""
    def _verify_schema(db_path: Path, expected_schema: dict):
        """Verify database schema matches expected structure."""
        with sqlite3.connect(db_path) as conn:
            for table_name, table_info in expected_schema.items():
                # Check if table exists
                cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
                assert cur.fetchone() is not None, f"Table {table_name} does not exist"
                
                # Check columns
                cur = conn.execute(f"PRAGMA table_info({table_name})")
                actual_columns = {row[1]: row[2] for row in cur.fetchall()}
                
                for col_name, col_type in table_info["columns"].items():
                    if col_name in actual_columns:
                        # Basic type checking (SQLite is flexible with types)
                        expected_base_type = col_type.split()[0].upper()
                        actual_base_type = actual_columns[col_name].upper()
                        
                        # Allow some flexibility in type matching
                        if expected_base_type in ["INTEGER", "INT"]:
                            assert actual_base_type in ["INTEGER", "INT"], f"Column {col_name} type mismatch"
                        elif expected_base_type == "REAL":
                            assert actual_base_type in ["REAL", "NUMERIC"], f"Column {col_name} type mismatch"
                        elif expected_base_type == "TEXT":
                            assert actual_base_type in ["TEXT", "VARCHAR"], f"Column {col_name} type mismatch"
    
    return _verify_schema


@pytest.fixture
def sample_test_data():
    """Provide consistent test data across tests."""
    return {
        "ruff_minimal": [
            {"filename": "test.py", "rule": "F401", "message": "unused import"}
        ],
        "ruff_multiple": [
            {"filename": "test1.py", "rule": "F401", "message": "unused import"},
            {"filename": "test2.py", "rule": "E302", "message": "expected 2 blank lines"},
            {"filename": "test3.py", "rule": "W503", "message": "line break before binary operator"}
        ],
        "pytest_perfect": {
            "summary": {"total": 20, "passed": 20, "failed": 0, "skipped": 0}
        },
        "pytest_good": {
            "summary": {"total": 25, "passed": 22, "failed": 2, "skipped": 1}
        },
        "pytest_poor": {
            "summary": {"total": 30, "passed": 15, "failed": 10, "skipped": 5}
        },
        "placeholders_none": {"open_count": 0, "resolved_count": 10},
        "placeholders_some": {"open_count": 5, "resolved_count": 15},
        "placeholders_many": {"open_count": 20, "resolved_count": 5}
    }


@pytest.fixture
def expected_scores():
    """Provide expected scores for different data combinations."""
    return {
        "perfect": 100.0,  # L=100, T=100, P=100
        "no_tests": 50.0,  # L=100, T=0, P=100
        "no_placeholders": 50.0,  # L=0, T=0, P=100
        "all_zeros": 20.0,  # L=0, T=0, P=0
    }


@pytest.fixture
def compliance_test_config():
    """Configuration for compliance testing."""
    return {
        "timeout_seconds": 30,
        "max_file_size_mb": 100,
        "score_tolerance": 0.1,
        "timestamp_tolerance_seconds": 60
    }


def pytest_configure(config):
    """Configure pytest for compliance tests."""
    # Add custom markers
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
    config.addinivalue_line("markers", "compliance: marks tests as compliance-related")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names."""
    for item in items:
        # Mark integration tests
        if "integration" in item.nodeid or "pipeline" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        
        # Mark slow tests
        if "large_dataset" in item.nodeid or "performance" in item.nodeid:
            item.add_marker(pytest.mark.slow)
        
        # Mark all tests in compliance directory as compliance tests
        if "compliance" in str(item.fspath):
            item.add_marker(pytest.mark.compliance)
        
        # Mark unit tests (anything not integration)
        if not any(marker.name == "integration" for marker in item.iter_markers()):
            item.add_marker(pytest.mark.unit)
