#!/usr/bin/env python3
"""
Enterprise Database Query Validation & Performance Testing Suite
==============================================================

DUAL COPILOT PATTERN - Database Query Validation and Performance Analysis
- Comprehensive connection testing with timeout handling
- Query performance testing with detailed timing metrics
- Data integrity validation using PRAGMA integrity_check
- Stress testing with rapid queries and transaction validation
- Enterprise-grade logging and audit trail
- JSON performance reports and metrics documentation

Testing Phases:
1. Connection Testing - Validate database accessibility and concurrent connections
2. Query Performance Testing - Measure SELECT, JOIN, and complex query performance
3. Data Integrity Validation - PRAGMA checks and constraint validation
4. Stress Testing - Rapid queries, transactions, and locking behavior
5. Performance Benchmarking - Comprehensive performance metrics and reporting

Enterprise Standards:
- All operations <1 second for query performance
- Zero data corruption tolerance
- Complete audit trail logging
- Visual progress indicators with tqdm
- Comprehensive error handling and recovery
- JSON format results for enterprise integration

Author: Enterprise Database Testing System
Version: 2.0.0 - Query Validation & Performance Testing
"""

import os
import sys
import sqlite3
import time
import threading
import json
import logging
import traceback
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager
import statistics
from tqdm import tqdm


class EnterpriseDatabaseQueryValidator:
    """Enterprise-grade database query validation and performance testing system"""

    def __init__(self, databases_path: Optional[str] = None):
        self.workspace_path = Path(os.getcwd())
        self.databases_path = Path(]
            databases_path) if databases_path else self.workspace_path / "databases"
        self.test_results_dir = self.workspace_path / "database_test_results"

        # Ensure test results directory exists
        self.test_results_dir.mkdir(exist_ok=True)

        # Setup enterprise logging
        self.log_path = self.test_results_dir
            / f"database_query_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        logging.basicConfig(]
            format = '%(asctime)s - %(levelname)s - %(message)s',
            handlers = [
                logging.FileHandler(str(self.log_path)),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

        # CRITICAL: Anti-recursion validation at start
        self.validate_workspace_integrity()

        # Test configuration
        self.max_concurrent_connections = 5
        self.stress_test_iterations = 100
        self.query_timeout_seconds = 1.0  # Enterprise requirement: <1 second
        self.transaction_timeout_seconds = 5.0

        # Test results tracking
        self.test_session = {
            "session_id": f"DB_TEST_{int(time.time())}",
            "start_time": datetime.now().isoformat(),
            "workspace_path": str(self.workspace_path),
            "databases_path": str(self.databases_path),
            "test_configuration": {},
            "databases_discovered": [],
            "connection_tests": {},
            "performance_tests": {},
            "integrity_tests": {},
            "stress_tests": {},
            "overall_results": {},
            "errors": []
        }

        self.logger.info(
            "[LAUNCH] ENTERPRISE DATABASE QUERY VALIDATOR INITIALIZED")
        self.logger.info(f"Session ID: {self.test_session['session_id']}")
        self.logger.info(f"Start Time: {self.test_session['start_time']}")
        self.logger.info(f"Process ID: {os.getpid()}")
        self.logger.info(f"Databases Path: {self.databases_path}")
        self.logger.info(f"Test Results Path: {self.test_results_dir}")

    def validate_workspace_integrity(self) -> bool:
        """CRITICAL: Validate workspace integrity and prevent recursive operations"""
        try:
            current_path = Path(os.getcwd())

            # Check for recursive backup folders in workspace
            backup_patterns = ["_backup_*", "*_backup", "backup_*"]
            for pattern in backup_patterns:
                backup_dirs = list(current_path.glob(pattern))
                if len(backup_dirs) > 5:  # Allow some backups but prevent excessive recursion
                    self.logger.warning(
                        f"[WARNING] Multiple backup directories detected: {len(backup_dirs)}")

            # Validate proper environment root usage
            if "temp" in str(current_path).lower() and "C:" in str(current_path):
                raise RuntimeError(]
                    "CRITICAL: Invalid E:\\gh_COPILOT	emp usage detected")

            return True

        except Exception as e:
            self.logger.error(
                f"[ERROR] WORKSPACE INTEGRITY VALIDATION FAILED: {e}")
            return False

    def discover_databases(self) -> List[Path]:
        """Discover all database files in the databases directory"""
        self.logger.info("[SEARCH] DISCOVERING DATABASE FILES")

        if not self.databases_path.exists():
            error_msg = f"Databases directory does not exist: {self.databases_path}"
            self.logger.error(error_msg)
            self.test_session["errors"].append(error_msg)
            return []

        database_files = list(self.databases_path.glob("*.db"))
        self.test_session["databases_discovered"] = [
            str(db) for db in database_files]

        self.logger.info(
            f"[BAR_CHART] DISCOVERED {len(database_files)} DATABASE FILES")
        for db_file in database_files:
            self.logger.info(
                f"  - {db_file.name} ({db_file.stat().st_size:,} bytes)")

        return database_files

    @ contextmanager
    def database_connection(self, db_path: Path, timeout: float=30.0):
        """Context manager for database connections with timeout"""
        conn = None
        try:
            conn = sqlite3.connect(str(db_path), timeout=timeout)
            conn.row_factory = sqlite3.Row
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()

    def test_database_connection(self, db_path: Path) -> Dict[str, Any]:
        """Test basic database connection and accessibility"""
        test_result = {
            "file_size": db_path.stat().st_size,
            "accessible": False,
            "connection_time": 0.0,
            "sqlite_version": None,
            "page_size": None,
            "encoding": None,
            "errors": []
        }

        try:
            start_time = time.perf_counter()

            with self.database_connection(db_path, timeout=self.query_timeout_seconds) as conn:
                # Test basic connectivity
                cursor = conn.cursor()

                # Get SQLite version
                cursor.execute("SELECT sqlite_version()")
                test_result["sqlite_version"] = cursor.fetchone()[0]

                # Get database info
                cursor.execute("PRAGMA page_size")
                test_result["page_size"] = cursor.fetchone()[0]

                cursor.execute("PRAGMA encoding")
                test_result["encoding"] = cursor.fetchone()[0]

                test_result["accessible"] = True
                test_result["connection_time"] = time.perf_counter()
                    - start_time

        except Exception as e:
            error_msg = f"Connection test failed for {db_path.name}: {e}"
            test_result["errors"].append(error_msg)
            self.logger.error(error_msg)

        return test_result

    def test_concurrent_connections(self, db_path: Path) -> Dict[str, Any]:
        """Test concurrent database connections"""
        test_result = {
            "connection_times": [],
            "errors": []
        }

        def connect_test(connection_id: int) -> Tuple[int, float, Optional[str]]:
            try:
                start_time = time.perf_counter()
                with self.database_connection(db_path, timeout=self.query_timeout_seconds) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT 1")
                    result = cursor.fetchone()[0]
                    connection_time = time.perf_counter() - start_time
                    return connection_id, connection_time, None
            except Exception as e:
                return connection_id, 0.0, str(e)

        try:
            with ThreadPoolExecutor(max_workers=self.max_concurrent_connections) as executor:
                futures = [executor.submit(connect_test, i) for i in range(]
                    self.max_concurrent_connections)]

                for future in as_completed(futures):
                    conn_id, conn_time, error = future.result()
                    if error:
                        test_result["errors"].append(]
                            f"Connection {conn_id}: {error}")
                    else:
                        test_result["successful_connections"] += 1
                        test_result["connection_times"].append(conn_time)

        except Exception as e:
            error_msg = f"Concurrent connection test failed for {db_path.name}: {e}"
            test_result["errors"].append(error_msg)
            self.logger.error(error_msg)

        return test_result

    def test_query_performance(self, db_path: Path) -> Dict[str, Any]:
        """Test query performance for basic and complex operations"""
        test_result = {
            "query_tests": {},
            "performance_metrics": {},
            "errors": []
        }

        try:
            with self.database_connection(db_path, timeout=self.query_timeout_seconds * 2) as conn:
                cursor = conn.cursor()

                # Get table list
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                test_result["tables_found"] = len(tables)

                if not tables:
                    test_result["errors"].append("No tables found in database")
                    return test_result

                query_times = [

                # Test basic SELECT queries on each table
                for table in tables:
                    table_tests = {
                        "select_count": {"time": 0.0, "result": 0, "success": False},
                        "select_limit": {"time": 0.0, "rows": 0, "success": False},
                        "select_all_columns": {"time": 0.0, "columns": 0, "success": False}
                    }

                    try:
                        # Test COUNT query
                        start_time = time.perf_counter()
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        count_result = cursor.fetchone()[0]
                        count_time = time.perf_counter() - start_time

                        table_tests["select_count"] = {
                        }
                        query_times.append(count_time)

                        # Test LIMIT query
                        start_time = time.perf_counter()
                        cursor.execute(f"SELECT * FROM {table} LIMIT 5")
                        limit_results = cursor.fetchall()
                        limit_time = time.perf_counter() - start_time

                        table_tests["select_limit"] = {
                            "rows": len(limit_results),
                            "success": True
                        }
                        query_times.append(limit_time)

                        # Test column info query
                        start_time = time.perf_counter()
                        cursor.execute(f"PRAGMA table_info({table})")
                        columns = cursor.fetchall()
                        column_time = time.perf_counter() - start_time

                        table_tests["select_all_columns"] = {
                            "columns": len(columns),
                            "success": True
                        }
                        query_times.append(column_time)

                    except Exception as e:
                        error_msg = f"Query test failed for table {table}: {e}"
                        test_result["errors"].append(error_msg)

                    test_result["query_tests"][table] = table_tests

                # Calculate performance metrics
                if query_times:
                    test_result["performance_metrics"] = {
                        "total_queries": len(query_times),
                        "average_time": statistics.mean(query_times),
                        "median_time": statistics.median(query_times),
                        "min_time": min(query_times),
                        "max_time": max(query_times),
                        "std_deviation": statistics.stdev(query_times) if len(query_times) > 1 else 0.0,
                        "queries_under_1s": sum(1 for t in query_times if t < 1.0),
                        "performance_grade": "PASS" if max(query_times) < self.query_timeout_seconds else "FAIL"
                    }

        except Exception as e:
            error_msg = f"Query performance test failed for {db_path.name}: {e}"
            test_result["errors"].append(error_msg)
            self.logger.error(error_msg)

        return test_result

    def test_data_integrity(self, db_path: Path) -> Dict[str, Any]:
        """Test database data integrity using PRAGMA checks"""
        test_result = {
            "integrity_check": {"passed": False, "result": "", "time": 0.0},
            "foreign_key_check": {"passed": False, "violations": [], "time": 0.0},
            "quick_check": {"passed": False, "result": "", "time": 0.0},
            "schema_validation": {"passed": False, "tables": 0, "indexes": 0, "time": 0.0},
            "errors": []
        }

        try:
            with self.database_connection(db_path, timeout=self.query_timeout_seconds * 3) as conn:
                cursor = conn.cursor()

                # PRAGMA integrity_check
                try:
                    start_time = time.perf_counter()
                    cursor.execute("PRAGMA integrity_check")
                    integrity_result = cursor.fetchone()[0]
                    integrity_time = time.perf_counter() - start_time

                    test_result["integrity_check"] = {
                    }
                except Exception as e:
                    test_result["errors"].append(]
                        f"Integrity check failed: {e}")

                # PRAGMA foreign_key_check
                try:
                    start_time = time.perf_counter()
                    cursor.execute("PRAGMA foreign_key_check")
                    fk_violations = cursor.fetchall()
                    fk_time = time.perf_counter() - start_time

                    test_result["foreign_key_check"] = {
                        "passed": len(fk_violations) == 0,
                        "violations": [dict(row) for row in fk_violations],
                        "time": fk_time
                    }
                except Exception as e:
                    test_result["errors"].append(]
                        f"Foreign key check failed: {e}")

                # PRAGMA quick_check
                try:
                    start_time = time.perf_counter()
                    cursor.execute("PRAGMA quick_check")
                    quick_result = cursor.fetchone()[0]
                    quick_time = time.perf_counter() - start_time

                    test_result["quick_check"] = {
                    }
                except Exception as e:
                    test_result["errors"].append(f"Quick check failed: {e}")

                # Schema validation
                try:
                    start_time = time.perf_counter()

                    # Count tables
                    cursor.execute(
                        "SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                    table_count = cursor.fetchone()[0]

                    # Count indexes
                    cursor.execute(
                        "SELECT COUNT(*) FROM sqlite_master WHERE type='index'")
                    index_count = cursor.fetchone()[0]

                    schema_time = time.perf_counter() - start_time

                    test_result["schema_validation"] = {
                    }
                except Exception as e:
                    test_result["errors"].append(]
                        f"Schema validation failed: {e}")

        except Exception as e:
            error_msg = f"Data integrity test failed for {db_path.name}: {e}"
            test_result["errors"].append(error_msg)
            self.logger.error(error_msg)

        return test_result

    def test_database_stress(self, db_path: Path) -> Dict[str, Any]:
        """Perform stress testing with rapid queries and transactions"""
        test_result = {
            "rapid_queries": {"completed": 0, "failed": 0, "total_time": 0.0, "avg_time": 0.0},
            "transaction_test": {"success": False, "rollback_success": False, "time": 0.0},
            "concurrent_stress": {"threads": 3, "completed": 0, "failed": 0, "total_time": 0.0},
            "errors": []
        }

        try:
            with self.database_connection(db_path, timeout=self.transaction_timeout_seconds * 2) as conn:
                cursor = conn.cursor()

                # Get a table for testing
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' LIMIT 1")
                table_result = cursor.fetchone()
                if not table_result:
                    test_result["errors"].append(]
                        "No tables available for stress testing")
                    return test_result

                test_table = table_result[0]

                # Rapid query stress test
                self.logger.info(
                    f"[PROCESSING] STRESS TESTING: Rapid queries on {db_path.name}")

                start_time = time.perf_counter()
                completed_queries = 0
                failed_queries = 0

                with tqdm(total=self.stress_test_iterations, desc=f"Stress Test {db_path.name}") as pbar:
                    for i in range(self.stress_test_iterations):
                        try:
                            cursor.execute(
                                f"SELECT COUNT(*) FROM {test_table}")
                            result = cursor.fetchone()
                            completed_queries += 1
                        except Exception as e:
                            failed_queries += 1
                            if failed_queries < 5:  # Log first few errors only
                                test_result["errors"].append(]
                                    f"Rapid query {i} failed: {e}")

                        pbar.update(1)

                total_time = time.perf_counter() - start_time

                test_result["rapid_queries"] = {
                }

                # Transaction stress test
                try:
                    start_time = time.perf_counter()

                    # Test transaction with rollback
                    conn.execute("BEGIN TRANSACTION")

                    # Create temporary table for testing
                    conn.execute(]
                        "CREATE TEMPORARY TABLE stress_test (id INTEGER, value TEXT)")
                    conn.execute(]
                        "INSERT INTO stress_test (id, value) VALUES (1, 'test')")

                    # Test rollback
                    conn.execute("ROLLBACK")

                    # Verify rollback worked
                    try:
                        cursor.execute("SELECT COUNT(*) FROM stress_test")
                        rollback_failed = True
                    except:
                        rollback_failed = False  # Table should not exist after rollback

                    transaction_time = time.perf_counter() - start_time

                    test_result["transaction_test"] = {
                    }

                except Exception as e:
                    test_result["errors"].append(]
                        f"Transaction test failed: {e}")

                # Concurrent stress test
                def concurrent_query_test(thread_id: int) -> Tuple[int, int, float]:
                    """Run concurrent queries from separate thread"""
                    try:
                        with self.database_connection(db_path, timeout=self.query_timeout_seconds) as thread_conn:
                            thread_cursor = thread_conn.cursor()
                            completed = 0
                            failed = 0
                            start = time.perf_counter()

                            for _ in range(10):  # 10 queries per thread
                                try:
                                    thread_cursor.execute(
                                        f"SELECT COUNT(*) FROM {test_table}")
                                    thread_cursor.fetchone()
                                    completed += 1
                                except:
                                    failed += 1

                            return completed, failed, time.perf_counter() - start
                    except Exception:
                        return 0, 10, 0.0

                try:
                    concurrent_start = time.perf_counter()
                    with ThreadPoolExecutor(max_workers=3) as executor:
                        futures = [
                            concurrent_query_test, i) for i in range(3)]

                        total_completed = 0
                        total_failed = 0

                        for future in as_completed(futures):
                            completed, failed, _ = future.result()
                            total_completed += completed
                            total_failed += failed

                    concurrent_time = time.perf_counter() - concurrent_start

                    test_result["concurrent_stress"] = {
                    }

                except Exception as e:
                    test_result["errors"].append(]
                        f"Concurrent stress test failed: {e}")

        except Exception as e:
            error_msg = f"Stress test failed for {db_path.name}: {e}"
            test_result["errors"].append(error_msg)
            self.logger.error(error_msg)

        return test_result

    def run_comprehensive_testing(self) -> Dict[str, Any]:
        """Execute complete database query validation and performance testing suite"""
        self.logger.info(
            "[LAUNCH] STARTING COMPREHENSIVE DATABASE QUERY VALIDATION")
        self.logger.info(f"Session: {self.test_session['session_id']}")
        self.logger.info(
            f"Testing Configuration: {self.max_concurrent_connections} concurrent, {self.stress_test_iterations} stress iterations")

        # Phase 1: Discover databases
        databases = self.discover_databases()
        if not databases:
            self.logger.error(
                "[ERROR] NO DATABASES FOUND - TESTING CANNOT PROCEED")
            return self.test_session

        total_tests = len(databases) * 4  # 4 test phases per database

        with tqdm(total=total_tests, desc="Database Testing Progress") as main_pbar:

            # Phase 2: Connection Testing
            self.logger.info("[CHAIN] PHASE 1: CONNECTION TESTING")
            for db_path in databases:
                self.logger.info(f"Testing connections for {db_path.name}")

                # Basic connection test
                connection_result = self.test_database_connection(db_path)

                # Concurrent connection test
                concurrent_result = self.test_concurrent_connections(db_path)

                self.test_session["connection_tests"][db_path.name] = {
                }

                main_pbar.update(1)

            # Phase 3: Query Performance Testing
            self.logger.info("[POWER] PHASE 2: QUERY PERFORMANCE TESTING")
            for db_path in databases:
                self.logger.info(f"Performance testing {db_path.name}")

                performance_result = self.test_query_performance(db_path)
                self.test_session["performance_tests"][db_path.name] = performance_result

                main_pbar.update(1)

            # Phase 4: Data Integrity Testing
            self.logger.info("[SHIELD] PHASE 3: DATA INTEGRITY VALIDATION")
            for db_path in databases:
                self.logger.info(f"Integrity validation for {db_path.name}")

                integrity_result = self.test_data_integrity(db_path)
                self.test_session["integrity_tests"][db_path.name] = integrity_result

                main_pbar.update(1)

            # Phase 5: Stress Testing
            self.logger.info("[?] PHASE 4: STRESS TESTING")
            for db_path in databases:
                self.logger.info(f"Stress testing {db_path.name}")

                stress_result = self.test_database_stress(db_path)
                self.test_session["stress_tests"][db_path.name] = stress_result

                main_pbar.update(1)

        # Generate overall results
        self.generate_overall_results()

        # Save test results
        results_file = self.save_test_results()

        self.logger.info("[SUCCESS] COMPREHENSIVE DATABASE TESTING COMPLETED")
        self.logger.info(f"Results saved to: {results_file}")

        return self.test_session

    def generate_overall_results(self):
        """Generate overall test results and summary"""
        self.logger.info("[BAR_CHART] GENERATING OVERALL TEST RESULTS")

        overall = {
                "total_databases": len(self.test_session["databases_discovered"]),
                "databases_accessible": 0,
                "databases_performance_pass": 0,
                "databases_integrity_pass": 0,
                "databases_stress_pass": 0,
                "overall_pass": 0
            },
            "performance_summary": {]
                "fastest_query_time": float('inf'),'
                "slowest_query_time": 0.0,
                "average_query_time": 0.0,
                "total_queries_executed": 0,
                "queries_under_1s": 0,
                "performance_grade": "UNKNOWN"
            },
            "integrity_summary": {},
            "stress_summary": {},
            "recommendations": []
        }

        all_query_times = [
        total_queries = 0
        queries_under_1s = 0

        # Analyze connection tests
        for db_name, results in self.test_session["connection_tests"].items():
            if results["basic_connection"]["accessible"]:
                overall["test_summary"]["databases_accessible"] += 1

        # Analyze performance tests
        for db_name, results in self.test_session["performance_tests"].items():
            if results.get("performance_metrics"):
                metrics = results["performance_metrics"]
                if metrics.get("performance_grade") == "PASS":
                    overall["test_summary"]["databases_performance_pass"] += 1

                # Collect timing data
                total_queries += metrics.get("total_queries", 0)
                queries_under_1s += metrics.get("queries_under_1s", 0)

                if metrics.get("min_time", 0) < overall["performance_summary"]["fastest_query_time"]:
                    overall["performance_summary"]["fastest_query_time"] = metrics["min_time"]

                if metrics.get("max_time", 0) > overall["performance_summary"]["slowest_query_time"]:
                    overall["performance_summary"]["slowest_query_time"] = metrics["max_time"]

                all_query_times.extend([metrics.get("average_time", 0)])

        # Calculate performance summary
        if all_query_times:
            overall["performance_summary"]["average_query_time"] = statistics.mean(]
                all_query_times)
            overall["performance_summary"]["total_queries_executed"] = total_queries
            overall["performance_summary"]["queries_under_1s"] = queries_under_1s

            if overall["performance_summary"]["slowest_query_time"] < self.query_timeout_seconds:
                overall["performance_summary"]["performance_grade"] = "PASS"
            else:
                overall["performance_summary"]["performance_grade"] = "FAIL"

        # Analyze integrity tests
        for db_name, results in self.test_session["integrity_tests"].items():
            integrity_pass = True
            fk_violations = 0

            if not results.get("integrity_check", {}).get("passed", False):
                integrity_pass = False

            if not results.get("quick_check", {}).get("passed", False):
                integrity_pass = False

            fk_check = results.get("foreign_key_check", {})
            if fk_check.get("violations"):
                fk_violations = len(fk_check["violations"])
                overall["integrity_summary"]["total_foreign_key_violations"] += fk_violations
                if fk_violations > 0:
                    integrity_pass = False

            if integrity_pass:
                overall["integrity_summary"]["databases_passed_all_checks"] += 1
            else:
                overall["integrity_summary"]["databases_with_integrity_issues"] += 1

        # Analyze stress tests
        total_stress_completed = 0
        total_stress_failed = 0
        concurrent_success = 0

        for db_name, results in self.test_session["stress_tests"].items():
            rapid_queries = results.get("rapid_queries", {})
            total_stress_completed += rapid_queries.get("completed", 0)
            total_stress_failed += rapid_queries.get("failed", 0)

            concurrent = results.get("concurrent_stress", {})
            if concurrent.get("failed", 0) == 0:
                concurrent_success += 1

        overall["stress_summary"]["total_stress_queries"] = total_stress_completed + \
            total_stress_failed
        overall["stress_summary"]["total_stress_failures"] = total_stress_failed
        overall["stress_summary"]["concurrent_test_success"] = concurrent_success

        if total_stress_completed + total_stress_failed > 0:
            overall["stress_summary"]["stress_success_rate"] = total_stress_completed / \
                (total_stress_completed + total_stress_failed)

        # Calculate overall pass count
        for db_name in self.test_session["connection_tests"].keys():
            db_pass = (]
                self.test_session["connection_tests"][db_name]["basic_connection"]["accessible"] and
                self.test_session["performance_tests"][db_name].get("performance_metrics", {}).get("performance_grade") == "PASS" and
                db_name not in [db for db, result in self.test_session["integrity_tests"].items()
                                if not result.get("integrity_check", {}).get("passed", False)] and
                self.test_session["stress_tests"][db_name].get(]
                    "rapid_queries", {}).get("failed", 1) == 0
            )
            if db_pass:
                overall["test_summary"]["overall_pass"] += 1

        # Generate recommendations
        if overall["performance_summary"]["performance_grade"] == "FAIL":
            overall["recommendations"].append(]
                "CRITICAL: Some queries exceed 1-second performance requirement")

        if overall["integrity_summary"]["databases_with_integrity_issues"] > 0:
            overall["recommendations"].append(]
                "WARNING: Database integrity issues detected - review integrity test results")

        if overall["stress_summary"]["stress_success_rate"] < 0.95:
            overall["recommendations"].append(]
                "PERFORMANCE: Stress test success rate below 95% - investigate database stability")

        if overall["test_summary"]["overall_pass"] == overall["test_summary"]["total_databases"]:
            overall["recommendations"].append(]
                "SUCCESS: All databases pass enterprise validation requirements")

        # Update test session
        self.test_session["overall_results"] = overall
        self.test_session["end_time"] = datetime.now().isoformat()

        # Log summary
        self.logger.info("=" * 80)
        self.logger.info("[BAR_CHART] COMPREHENSIVE DATABASE TESTING SUMMARY")
        self.logger.info("=" * 80)
        self.logger.info(
            f"Total Databases Tested: {overall['test_summary']['total_databases']}")
        self.logger.info(
            f"Databases Accessible: {overall['test_summary']['databases_accessible']}")
        self.logger.info(
            f"Performance Pass: {overall['test_summary']['databases_performance_pass']}")
        self.logger.info(
            f"Integrity Pass: {overall['test_summary']['databases_integrity_pass']}")
        self.logger.info(
            f"Overall Pass: {overall['test_summary']['overall_pass']}")
        self.logger.info(
            f"Performance Grade: {overall['performance_summary']['performance_grade']}")
        self.logger.info(
            f"Average Query Time: {overall['performance_summary']['average_query_time']:.4f}s")
        self.logger.info(
            f"Stress Success Rate: {overall['stress_summary']['stress_success_rate']:.2%}")

        for recommendation in overall["recommendations"]:
            self.logger.info(f"[LIGHTBULB] {recommendation}")

        self.logger.info("=" * 80)

    def save_test_results(self) -> str:
        """Save comprehensive test results to JSON file"""
        results_file = self.test_results_dir / \
            f"database_query_validation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(]
                          ensure_ascii=False, default=str)

            self.logger.info(
                f"[STORAGE] Test results saved to: {results_file}")
            return str(results_file)

        except Exception as e:
            error_msg = f"Failed to save test results: {e}"
            self.logger.error(error_msg)
            self.test_session["errors"].append(error_msg)
            return ""


def main():
    """Main execution function for database query validation"""
    print("Enterprise Database Query Validation & Performance Testing Suite")
    print("================================================================")

    # Check workspace path
    databases_path = None
    if len(sys.argv) > 1:
        databases_path = sys.argv[1]

    # Initialize validator
    try:
        validator = EnterpriseDatabaseQueryValidator(databases_path)

        # Run comprehensive testing
        test_results = validator.run_comprehensive_testing()

        # Determine success
        overall_results = test_results.get("overall_results", {})
        test_summary = overall_results.get("test_summary", {})

        total_databases = test_summary.get("total_databases", 0)
        overall_pass = test_summary.get("overall_pass", 0)

        if overall_pass == total_databases and total_databases > 0:
            print(
                "\n[SUCCESS] ALL DATABASES PASSED ENTERPRISE VALIDATION REQUIREMENTS")
            print(
                f"[TARGET] Success Rate: {overall_pass}/{total_databases} (100%)")
            return 0
        else:
            print(f"\n[WARNING] VALIDATION COMPLETED WITH ISSUES")
            print(
                f"[TARGET] Success Rate: {overall_pass}/{total_databases} ({overall_pass/total_databases*100 if total_databases > 0 else 0:.1f}%)")
            return 1

    except Exception as e:
        print(f"\n[ERROR] CRITICAL ERROR IN DATABASE VALIDATION: {e}")
        traceback.print_exc()
        return 2


if __name__ == "__main__":
    sys.exit(main())
