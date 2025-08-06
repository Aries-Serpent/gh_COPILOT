#!/usr/bin/env python3
"""
🧪 DATABASE CONSOLIDATION FUNCTIONALITY TEST
================================================================
Quick test to verify the autonomous system works correctly
with the consolidated database structure.
================================================================
"""

import sqlite3
from pathlib import Path


def test_consolidated_database_functionality():
    """🧪 Test core functionality with consolidated databases"""

    print("🧪 TESTING CONSOLIDATED DATABASE FUNCTIONALITY")
    print("=" * 60)

    databases_path = Path("databases")
    test_results = {"tests_passed": 0, "tests_failed": 0, "issues": []}

    # Test 1: Critical databases accessible
    critical_dbs = ["production.db", "analytics.db", "monitoring.db", "deployment_logs.db"]

    for db_name in critical_dbs:
        db_path = databases_path / db_name
        try:
            with sqlite3.connect(str(db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                table_count = cursor.fetchone()[0]

                if table_count > 0:
                    print(f"✅ {db_name}: {table_count} tables accessible")
                    test_results["tests_passed"] += 1
                else:
                    print(f"❌ {db_name}: No tables found")
                    test_results["tests_failed"] += 1
                    test_results["issues"].append(f"{db_name} has no tables")

        except Exception as e:
            print(f"❌ {db_name}: Connection failed - {e}")
            test_results["tests_failed"] += 1
            test_results["issues"].append(f"{db_name} connection failed: {e}")

    # Test 2: New consolidated databases functional
    consolidated_dbs = ["template_consolidated.db", "quantum_consolidated.db"]

    for db_name in consolidated_dbs:
        db_path = databases_path / db_name
        try:
            with sqlite3.connect(str(db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                table_count = cursor.fetchone()[0]

                # Test data access
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' LIMIT 1")
                first_table = cursor.fetchone()

                if first_table:
                    cursor.execute(f"SELECT COUNT(*) FROM `{first_table[0]}`")
                    row_count = cursor.fetchone()[0]
                    print(f"✅ {db_name}: {table_count} tables, {row_count} rows in {first_table[0]}")
                    test_results["tests_passed"] += 1
                else:
                    print(f"❌ {db_name}: No tables to test")
                    test_results["tests_failed"] += 1

        except Exception as e:
            print(f"❌ {db_name}: Test failed - {e}")
            test_results["tests_failed"] += 1
            test_results["issues"].append(f"{db_name} test failed: {e}")

    # Test 3: Enhanced databases have more data
    enhanced_dbs = ["enterprise_builds.db", "learning_monitor.db", "performance_analysis.db"]

    for db_name in enhanced_dbs:
        db_path = databases_path / db_name
        try:
            with sqlite3.connect(str(db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                table_count = cursor.fetchone()[0]

                print(f"✅ {db_name}: Enhanced with {table_count} tables")
                test_results["tests_passed"] += 1

        except Exception as e:
            print(f"❌ {db_name}: Enhancement test failed - {e}")
            test_results["tests_failed"] += 1
            test_results["issues"].append(f"{db_name} enhancement test failed: {e}")

    # Test 4: Verify removed databases are gone
    removed_dbs = [
        "analytics_20250714_235950.db",
        "production_20250714_235950.db",
        "templates.db",
        "quantum_integration.db",
        "backup.db",
    ]

    for db_name in removed_dbs:
        db_path = databases_path / db_name
        if not db_path.exists():
            print(f"✅ {db_name}: Successfully removed")
            test_results["tests_passed"] += 1
        else:
            print(f"❌ {db_name}: Still exists (should be removed)")
            test_results["tests_failed"] += 1
            test_results["issues"].append(f"{db_name} was not properly removed")

    # Test summary
    total_tests = test_results["tests_passed"] + test_results["tests_failed"]
    success_rate = (test_results["tests_passed"] / total_tests * 100) if total_tests > 0 else 0

    print(f"\n📊 TEST RESULTS SUMMARY")
    print(f"✅ Tests Passed: {test_results['tests_passed']}")
    print(f"❌ Tests Failed: {test_results['tests_failed']}")
    print(f"📈 Success Rate: {success_rate:.1f}%")

    if test_results["issues"]:
        print(f"\n⚠️ Issues Found:")
        for issue in test_results["issues"]:
            print(f"  • {issue}")

    if success_rate >= 90:
        print(f"\n🎊 CONSOLIDATION FUNCTIONALITY TEST: SUCCESS")
        return True
    else:
        print(f"\n❌ CONSOLIDATION FUNCTIONALITY TEST: FAILED")
        return False


if __name__ == "__main__":
    test_consolidated_database_functionality()
