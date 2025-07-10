#!/usr/bin/env python3
"""
PIS SCRIPT DISCOVERY & POPULATION UTILITY
==========================================

Populates the script_tracking table with Python scripts found in the workspace.
This ensures the PIS framework has scripts to process during compliance scans.

AUTHOR: GitHub Copilot Enterprise System
VERSION: 1.0 (Script Population)
"""

import sqlite3
import hashlib

from pathlib import Path
from datetime import datetime


def populate_script_tracking():
    """Populate script_tracking table with discovered Python scripts."""
    try:
        print("DISCOVERING AND POPULATING PYTHON SCRIPTS...")

        # Connect to production database
        conn = sqlite3.connect('production.db')

        # Clear existing entries
        conn.execute("DELETE FROM script_tracking")

        # Discover Python scripts
        workspace_path = Path('.')
        scripts_found = 0

        for py_file in workspace_path.rglob("*.py"):
            try:
                file_path = str(py_file)

                # Skip certain directories for performance
                skip_patterns = ['__pycache__', '.git', 'venv', 'env', 'node_modules']
                if any(pattern in file_path for pattern in skip_patterns):
                    continue

                # Calculate file hash
                with open(py_file, 'rb') as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()

                # Get modification time
                mod_time = datetime.fromtimestamp(py_file.stat().st_mtime).isoformat()

                # Insert into script_tracking
                conn.execute("""
                    INSERT INTO script_tracking
                    (file_path, file_hash, last_modified, compliance_status)
                    VALUES (?, ?, ?, 'UNKNOWN')
                """, (file_path, file_hash, mod_time))

                scripts_found += 1
                if scripts_found % 10 == 0:
                    print(f"Processed {scripts_found} scripts...")

            except Exception as e:
                print(f"ERROR processing {py_file}: {e}")
                continue

        conn.commit()

        # Verify results
        cursor = conn.execute("SELECT COUNT(*) FROM script_tracking")
        count = cursor.fetchone()[0]

        print("SCRIPT POPULATION COMPLETE")
        print(f"Total scripts discovered: {scripts_found}")
        print(f"Total scripts in database: {count}")

        # Show sample entries
        cursor = conn.execute("SELECT file_path FROM script_tracking LIMIT 5")
        sample_scripts = [row[0] for row in cursor.fetchall()]

        print("\nSample scripts:")
        for script in sample_scripts:
            print(f"  - {script}")

        return True

    except Exception as e:
        print(f"SCRIPT POPULATION FAILED: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()


def main():
    """Main execution function."""
    print("PIS SCRIPT DISCOVERY & POPULATION UTILITY")
    print("=" * 60)

    if populate_script_tracking():
        print("=" * 60)
        print("READY FOR PIS FRAMEWORK EXECUTION")
        return 0
    else:
        print("=" * 60)
        print("SCRIPT POPULATION FAILED")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
