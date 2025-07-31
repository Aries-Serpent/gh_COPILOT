#!/usr/bin/env python3
"""
Tests for Script Database Validator

Enterprise Standards Compliance:
- Flake8/PEP 8 Compliant
- Focused testing for script-database validation functionality
"""

import hashlib
import tempfile
import sqlite3
import unittest
from pathlib import Path

from scripts.database.script_database_validator import ScriptDatabaseValidator


class TestScriptDatabaseValidator(unittest.TestCase):
    """Test script database validation functionality"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

        # Create test directories
        self.databases_dir = self.temp_path / "databases"
        self.databases_dir.mkdir()

        # Create test script database
        self.script_db_path = self.databases_dir / "script_generation.db"
        self._create_test_database()

        # Create test scripts
        self._create_test_scripts()

        self.validator = ScriptDatabaseValidator(self.temp_path)

    def _create_test_database(self):
        """Create test database with schema"""
        with sqlite3.connect(self.script_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE script_templates (
                    template_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT,
                    content TEXT NOT NULL,
                    quantum_hash TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def _create_test_scripts(self):
        """Create test script files"""
        # Script 1: In sync
        script1_content = "print('Hello World')\n"
        script1_path = self.temp_path / "test_script1.py"
        script1_path.write_text(script1_content)
        script1_hash = hashlib.sha256(script1_content.encode()).hexdigest()

        # Script 2: Out of sync (different content in DB)
        script2_content = "print('Hello World 2')\n"
        script2_path = self.temp_path / "test_script2.py"
        script2_path.write_text(script2_content)

        # Script 3: Missing from DB
        script3_content = "print('Hello World 3')\n"
        script3_path = self.temp_path / "test_script3.py"
        script3_path.write_text(script3_content)

        # Add scripts to database
        with sqlite3.connect(self.script_db_path) as conn:
            cursor = conn.cursor()

            # Script 1 - in sync
            cursor.execute(
                """
                INSERT INTO script_templates 
                (template_id, name, category, description, content, quantum_hash, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    "test1",
                    "test_script1.py",
                    "test",
                    "Test script 1",
                    script1_content,
                    script1_hash,
                    "2025-01-01",
                    "2025-01-01",
                ),
            )

            # Script 2 - out of sync (different content)
            cursor.execute(
                """
                INSERT INTO script_templates 
                (template_id, name, category, description, content, quantum_hash, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    "test2",
                    "test_script2.py",
                    "test",
                    "Test script 2",
                    "print('OLD CONTENT')",
                    "old_hash",
                    "2025-01-01",
                    "2025-01-01",
                ),
            )

            # Script 4 - in DB but not in repo
            cursor.execute(
                """
                INSERT INTO script_templates 
                (template_id, name, category, description, content, quantum_hash, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    "test4",
                    "missing_script.py",
                    "test",
                    "Missing script",
                    "print('Missing')",
                    "missing_hash",
                    "2025-01-01",
                    "2025-01-01",
                ),
            )

    def test_calculate_file_hash(self):
        """Test file hash calculation"""
        test_content = "test content"
        test_file = self.temp_path / "test_hash.py"
        test_file.write_text(test_content)

        expected_hash = hashlib.sha256(test_content.encode()).hexdigest()
        calculated_hash = self.validator.calculate_file_hash(test_file)

        self.assertEqual(calculated_hash, expected_hash)

    def test_get_repository_scripts(self):
        """Test repository script scanning"""
        scripts = self.validator.get_repository_scripts()

        # Should find 3 test scripts
        script_names = [Path(script).name for script in scripts.keys()]
        expected_scripts = ["test_script1.py", "test_script2.py", "test_script3.py"]

        for expected in expected_scripts:
            self.assertIn(expected, script_names)

        # Check that scripts have required metadata
        for script_data in scripts.values():
            self.assertIn("hash", script_data)
            self.assertIn("size", script_data)
            self.assertIn("modified", script_data)
            self.assertIn("extension", script_data)

    def test_get_database_scripts(self):
        """Test database script retrieval"""
        db_scripts = self.validator.get_database_scripts()

        # Should find 3 scripts in database
        self.assertEqual(len(db_scripts), 3)

        expected_scripts = ["test_script1.py", "test_script2.py", "missing_script.py"]
        for expected in expected_scripts:
            self.assertIn(expected, db_scripts)

        # Check metadata
        for script_data in db_scripts.values():
            self.assertIn("template_id", script_data)
            self.assertIn("database_hash", script_data)
            self.assertIn("content_hash", script_data)
            self.assertIn("created_at", script_data)

    def test_validate_script_sync(self):
        """Test script synchronization validation"""
        results = self.validator.validate_script_sync()

        # Check structure
        required_keys = [
            "timestamp",
            "total_repo_scripts",
            "total_db_scripts",
            "in_sync",
            "out_of_sync",
            "missing_from_db",
            "missing_from_repo",
            "hash_mismatches",
            "sync_percentage",
        ]
        for key in required_keys:
            self.assertIn(key, results)

        # Check counts
        self.assertEqual(results["total_repo_scripts"], 3)
        self.assertEqual(results["total_db_scripts"], 3)

        # test_script1.py should be in sync
        in_sync_scripts = [item["script"] for item in results["in_sync"]]
        self.assertTrue(any("test_script1.py" in script for script in in_sync_scripts))

        # test_script3.py should be missing from DB
        missing_from_db = [item["script"] for item in results["missing_from_db"]]
        self.assertTrue(any("test_script3.py" in script for script in missing_from_db))

        # test_script2.py should have hash mismatch
        hash_mismatches = [item["script"] for item in results["hash_mismatches"]]
        self.assertTrue(any("test_script2.py" in script for script in hash_mismatches))

        # missing_script.py should be missing from repo
        self.assertIn("missing_script.py", results["missing_from_repo"])

    def test_update_database_scripts(self):
        """Test database update functionality"""
        # Get missing scripts
        results = self.validator.validate_script_sync()
        missing_scripts = [item["script"] for item in results["missing_from_db"]]

        # Update database
        success = self.validator.update_database_scripts(missing_scripts)
        self.assertTrue(success)

        # Verify update
        new_results = self.validator.validate_script_sync()
        self.assertLess(len(new_results["missing_from_db"]), len(results["missing_from_db"]))

    def test_generate_validation_report(self):
        """Test report generation"""
        report = self.validator.generate_validation_report()

        # Check report structure
        self.assertIn("Script Database Validation Report", report)
        self.assertIn("Summary", report)
        self.assertIn("Synchronization Status", report)
        self.assertIn("Repository Scripts:", report)
        self.assertIn("Database Scripts:", report)

    def tearDown(self):
        """Clean up test environment"""
        import shutil

        shutil.rmtree(self.temp_dir)


if __name__ == "__main__":
    unittest.main()
