#!/usr/bin/env python3
"""
Quick Database Query Tool
========================
Query all databases in the codebase to show structure and sample data
"""
import sqlite3
import os
from pathlib import Path


def query_database(db_path):
    """Query a single database and return its structure and sample data"""
    results = {
       'tables': {},
        'status': 'success',
        'error': None
    }

        try:
    conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get all user tables (excluding sqlite_ tables)
        cursor.execute(
    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        table_names = [row[0] for row in cursor.fetchall()]

        for table_name in table_names:
            # Get row count
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]

            # Get column info
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [col[1] for col in cursor.fetchall()]

            # Get sample data (first 2 rows)
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 2")
            sample_data = cursor.fetchall()

            results['tables'][table_name] = {
    }

        conn.close()

        except Exception as e:
    results['status'] = 'error'
        results['error'] = str(e)

        return results


    def main():
    databases_dir = Path('databases')

    if not databases_dir.exists():
    print("[ERROR] databases directory not found")
        return

    print("[SEARCH] QUICK DATABASE QUERY RESULTS")
    print("=" * 60)

    for db_file in sorted(databases_dir.glob('*.db')):
    result = query_database(db_file)

        print(f"\n[BAR_CHART] {result['name']}")
        print("-" * 40)

        if result['status'] == 'error':
    print(f"[ERROR] Error: {result['error']}")
            continue

        if not result['tables']:
    print("[NOTES] No user tables found")
            continue

        for table_name, table_info in result['tables'].items():
    print(f"[CLIPBOARD] Table: {table_name}")
            print(f"   Records: {table_info['row_count']}")
            print(
    f"   Columns: {', '.join(table_info['columns'][:5])}{'...' if len(table_info['columns']) > 5 else ''}")

            if table_info['sample_data']:
    print(
    f"   Sample: {str(table_info['sample_data'][0])[:80]}...")
            print()


    if __name__ == "__main__":
    main()
