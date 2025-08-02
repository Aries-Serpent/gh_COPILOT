#!/usr/bin/env python3
"""
Limited Script Sync Test - Validates functionality with a small subset of scripts
"""

import tempfile
import sqlite3
from pathlib import Path
from db_tools.script_database_validator import ScriptDatabaseValidator


def test_limited_sync():
    """Test synchronization with a limited set of scripts"""
    print("Testing script database synchronization with limited scope...")

    # Create a temporary test environment
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        databases_dir = temp_path / "databases"
        databases_dir.mkdir()

        # Create test database
        script_db_path = databases_dir / "script_generation.db"
        with sqlite3.connect(script_db_path) as conn:
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

        # Create a few test scripts
        test_scripts = {
            "test1.py": 'print("Test 1")\n',
            "test2.py": 'print("Test 2")\nprint("More code")\n',
            "test3.py": '#!/usr/bin/env python3\nprint("Test 3")\n',
        }

        for script_name, content in test_scripts.items():
            script_path = temp_path / script_name
            script_path.write_text(content)

        # Initialize validator
        validator = ScriptDatabaseValidator(temp_path)

        # Test 1: Initial validation (should show all missing)
        print("\n1. Initial Validation:")
        results = validator.validate_script_sync()
        print(f"   Repository scripts: {results['total_repo_scripts']}")
        print(f"   Database scripts: {results['total_db_scripts']}")
        print(f"   Missing from DB: {len(results['missing_from_db'])}")
        print(f"   Sync percentage: {results['sync_percentage']:.2f}%")

        # Test 2: Update database with missing scripts
        print("\n2. Synchronizing scripts...")
        missing_scripts = [item["script"] for item in results["missing_from_db"]]
        success = validator.update_database_scripts(missing_scripts)
        print(f"   Update successful: {success}")

        # Test 3: Post-sync validation (should show improved sync)
        print("\n3. Post-sync Validation:")
        results = validator.validate_script_sync()
        print(f"   Repository scripts: {results['total_repo_scripts']}")
        print(f"   Database scripts: {results['total_db_scripts']}")
        print(f"   Scripts in sync: {len(results['in_sync'])}")
        print(f"   Missing from DB: {len(results['missing_from_db'])}")
        print(f"   Sync percentage: {results['sync_percentage']:.2f}%")

        # Test 4: Generate validation report
        print("\n4. Generating validation report...")
        report = validator.generate_validation_report()
        report_lines = report.split("\n")
        print("   Report preview:")
        for line in report_lines[:15]:  # Show first 15 lines
            print(f"   {line}")

        print("\n✓ Limited sync test completed successfully!")
        return results["sync_percentage"] > 90


if __name__ == "__main__":
    success = test_limited_sync()
    print(f"\nTest result: {'PASSED' if success else 'FAILED'}")
