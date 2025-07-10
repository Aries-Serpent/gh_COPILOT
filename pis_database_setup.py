#!/usr/bin/env python3
"""
PIS DATABASE SETUP & REPAIR UTILITY
===================================

Ensures all required database tables exist for PIS framework execution.
Fixes missing tables and repairs database schema issues.

AUTHOR: GitHub Copilot Enterprise System
VERSION: 1.0 (Database Setup)
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime


def setup_analytics_database():
    """Setup/repair analytics database with all required tables."""
    try:
        print("🔧 SETTING UP ANALYTICS DATABASE...")

        analytics_db_path = Path("analytics.db")
        conn = sqlite3.connect(str(analytics_db_path))

        # Create compliance_scans table (was missing)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS compliance_scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_timestamp TEXT NOT NULL,
                total_files INTEGER NOT NULL,
                compliant_files INTEGER NOT NULL,
                non_compliant_files INTEGER NOT NULL,
                total_violations INTEGER NOT NULL,
                compliance_score REAL NOT NULL,
                scan_duration REAL NOT NULL,
                phase TEXT NOT NULL DEFAULT 'PHASE_2',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create compliance_violations table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS compliance_violations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_id INTEGER NOT NULL,
                file_path TEXT NOT NULL,
                line_number INTEGER NOT NULL,
                column_number INTEGER NOT NULL,
                error_code TEXT NOT NULL,
                error_message TEXT NOT NULL,
                severity TEXT NOT NULL,
                category TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (scan_id) REFERENCES compliance_scans (id)
            )
        """)

        # Create PIS execution tracking table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS pis_execution_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                phase TEXT NOT NULL,
                status TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                duration REAL,
                files_processed INTEGER DEFAULT 0,
                files_compliant INTEGER DEFAULT 0,
                files_corrected INTEGER DEFAULT 0,
                violations_found INTEGER DEFAULT 0,
                violations_fixed INTEGER DEFAULT 0,
                compliance_score REAL DEFAULT 0.0,
                error_count INTEGER DEFAULT 0,
                success_rate REAL DEFAULT 0.0,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create PIS violations table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS pis_violations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                violation_id TEXT NOT NULL UNIQUE,
                file_path TEXT NOT NULL,
                line_number INTEGER NOT NULL,
                column_number INTEGER NOT NULL,
                error_code TEXT NOT NULL,
                error_message TEXT NOT NULL,
                severity TEXT NOT NULL,
                category TEXT NOT NULL,
                fix_applied BOOLEAN DEFAULT FALSE,
                fix_method TEXT,
                timestamp TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create PIS phase metrics table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS pis_phase_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                phase TEXT NOT NULL,
                status TEXT NOT NULL,
                start_time TEXT,
                end_time TEXT,
                duration REAL DEFAULT 0.0,
                files_processed INTEGER DEFAULT 0,
                compliance_score REAL DEFAULT 0.0,
                success_rate REAL DEFAULT 0.0,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()

        # Verify tables were created
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]

        required_tables = [
            'compliance_scans',
            'compliance_violations',
            'pis_execution_log',
            'pis_violations',
            'pis_phase_metrics'
        ]

        missing_tables = [table for table in required_tables if table not in tables]

        if missing_tables:
            print(f"❌ MISSING TABLES: {missing_tables}")
            return False
        else:
            print("✅ ALL REQUIRED TABLES EXIST")
            print(f"📊 Total tables: {len(tables)}")
            print(f"🔧 PIS tables: {len(required_tables)}")
            return True

    except Exception as e:
        print(f"❌ DATABASE SETUP FAILED: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()


def setup_production_database():
    """Setup/repair production database with all PIS tables."""
    try:
        print("🔧 SETTING UP PRODUCTION DATABASE...")

        prod_db_path = Path("production.db")
        conn = sqlite3.connect(str(prod_db_path))

        # Create all required tables for PIS framework
        tables = [
            ("""CREATE TABLE IF NOT EXISTS script_tracking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL UNIQUE,
                file_hash TEXT NOT NULL,
                last_modified TEXT NOT NULL,
                compliance_status TEXT DEFAULT 'UNKNOWN',
                last_scan TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )""", "script_tracking"),

            ("""CREATE TABLE IF NOT EXISTS compliance_scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_timestamp TEXT NOT NULL,
                total_files INTEGER NOT NULL,
                compliant_files INTEGER NOT NULL,
                non_compliant_files INTEGER NOT NULL,
                total_violations INTEGER NOT NULL,
                compliance_score REAL NOT NULL,
                scan_duration REAL NOT NULL,
                phase TEXT NOT NULL DEFAULT 'PHASE_2',
                session_id TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )""", "compliance_scans"),

            ("""CREATE TABLE IF NOT EXISTS violation_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                violation_code TEXT NOT NULL,
                violation_count INTEGER NOT NULL,
                file_path TEXT NOT NULL,
                line_number INTEGER,
                severity TEXT DEFAULT 'MEDIUM',
                scan_timestamp TEXT NOT NULL,
                phase TEXT NOT NULL DEFAULT 'PHASE_2',
                session_id TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )""", "violation_analytics"),

            ("""CREATE TABLE IF NOT EXISTS correction_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL,
                violation_code TEXT NOT NULL,
                original_line TEXT,
                corrected_line TEXT,
                correction_timestamp TEXT NOT NULL,
                phase TEXT NOT NULL DEFAULT 'PHASE_3',
                session_id TEXT,
                success BOOLEAN DEFAULT TRUE,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )""", "correction_history"),

            ("""CREATE TABLE IF NOT EXISTS pis_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL UNIQUE,
                phase_status TEXT NOT NULL DEFAULT 'INITIATED',
                start_timestamp TEXT NOT NULL,
                end_timestamp TEXT,
                total_files INTEGER DEFAULT 0,
                corrected_violations INTEGER DEFAULT 0,
                compliance_improvement REAL DEFAULT 0.0,
                session_metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )""", "pis_sessions")
        ]

        created_tables = 0
        for table_sql, table_name in tables:
            conn.execute(table_sql)
            # Verify table exists
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            if cursor.fetchone():
                created_tables += 1

        conn.commit()

        print(f"✅ ALL PIS TABLES CREATED/VERIFIED")
        print(f"📊 Total tables: {created_tables}")
        return True

    except Exception as e:
        print(f"❌ PRODUCTION DATABASE SETUP FAILED: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()


def main():
    """Main database setup execution."""
    print("🚀 PIS DATABASE SETUP & REPAIR UTILITY")
    print("=" * 60)
    
    success = True
    
    # Setup analytics database
    if not setup_analytics_database():
        success = False
        
    # Setup production database
    if not setup_production_database():
        success = False
        
    print("=" * 60)
    if success:
        print("✅ DATABASE SETUP COMPLETE")
        print("🎯 READY FOR PIS FRAMEWORK EXECUTION")
        return 0
    else:
        print("❌ DATABASE SETUP FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())
