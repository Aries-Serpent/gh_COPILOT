#!/usr/bin/env python3
"""
Production Database Analysis - Code Scripts and Environment Adaptation Capabilities
Comprehensive analysis of production.db for conversation logging, event tracking, and script generation
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime


def analyze_production_db():
    """Analyze production.db for logging, conversation, and script capabilities"""

    db_path = Path("databases/production.db")
    if not db_path.exists():
        print(f"[ERROR] Database not found: {db_path}")
        return

    print("=" * 100)
    print("[FILE_CABINET]  PRODUCTION.DB - COMPREHENSIVE ANALYSIS")
    print("=" * 100)
    print(f"[BAR_CHART] Database Size: {db_path.stat().st_size:,} bytes")
    print(f"[?] Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        print(f"[CLIPBOARD] TOTAL TABLES: {len(tables)}")
        print()

        # Analyze each table for specific capabilities
        conversation_tables = [
        event_logging_tables = [
        history_tracking_tables = [
        code_storage_tables = [
        environment_tables = [

        for table in tables:
            print(f"[SEARCH] ANALYZING TABLE: {table}")

            # Get table info
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()

            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            row_count = cursor.fetchone()[0]

            # Get column names for analysis
            column_names = [col[1].lower() for col in columns]

            print(f"   [BAR_CHART] Rows: {row_count:,}")
            print(f"   [CLIPBOARD] Columns: {len(columns)}")

            # Categorize tables by capability
            capabilities = [

            if any(keyword in ' '.join(column_names) for keyword in ['conversation', 'chat', 'dialog', 'message']):
                conversation_tables.append(table)
                capabilities.append("[?] CONVERSATIONS")

            if any(keyword in ' '.join(column_names) for keyword in ['event', 'log', 'tracking', 'activity']):
                event_logging_tables.append(table)
                capabilities.append("[NOTES] EVENT LOGGING")

            if any(keyword in ' '.join(column_names) for keyword in ['history', 'change', 'feedback', 'learning']):
                history_tracking_tables.append(table)
                capabilities.append("[BOOKS] HISTORY TRACKING")

            if any(keyword in ' '.join(column_names) for keyword in ['code', 'script', 'template', 'content']):
                code_storage_tables.append(table)
                capabilities.append("[LAPTOP] CODE STORAGE")

            if any(keyword in ' '.join(column_names) for keyword in ['environment', 'config', 'setting', 'parameter']):
                environment_tables.append(table)
                capabilities.append("[GEAR] ENVIRONMENT CONFIG")

            if capabilities:
                print(f"   [TARGET] CAPABILITIES: {' | '.join(capabilities)}")

            # Show detailed schema for interesting tables
            if row_count > 0 or any(keyword in table.lower() for keyword in ['copilot', 'learning', 'feedback', 'change']):
                print(f"   [NOTES] SCHEMA:")
                for col in columns:
                    col_name, col_type, not_null, default, pk = col[1], col[2], col[3], col[4], col[5]
                    indicators = [
                    if pk:
                        indicators.append("PK")
                    if not_null:
                        indicators.append("NOT NULL")
                    if default:
                        indicators.append(f"DEFAULT {default}")

                    indicator_str = f" [{', '.join(indicators)}]" if indicators else ""
                    print(f"      - {col_name}: {col_type}{indicator_str}")

                # Show sample data if available
                if row_count > 0:
                    print(f"   [?] SAMPLE DATA:")
                    try:
                        cursor.execute(f"SELECT * FROM {table} LIMIT 3")
                        rows = cursor.fetchall()
                        for i, row in enumerate(rows, 1):
                            print(
                                f"      Row {i}: {str(row)[:100]}{'...' if len(str(row)) > 100 else ''}")
                    except Exception as e:
                        print(f"      Error reading data: {e}")

            print()

        # Summary Analysis
        print("=" * 100)
        print("[TARGET] CAPABILITY SUMMARY")
        print("=" * 100)

        print(f"[?] CONVERSATION LOGGING TABLES ({len(conversation_tables)}):")
        for table in conversation_tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   - {table}: {count:,} records")

        print(f"\n[NOTES] EVENT LOGGING TABLES ({len(event_logging_tables)}):")
        for table in event_logging_tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   - {table}: {count:,} records")

        print(
            f"\n[BOOKS] HISTORY TRACKING TABLES ({len(history_tracking_tables)}):")
        for table in history_tracking_tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   - {table}: {count:,} records")

        print(f"\n[LAPTOP] CODE STORAGE TABLES ({len(code_storage_tables)}):")
        for table in code_storage_tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   - {table}: {count:,} records")

        print(
            f"\n[GEAR] ENVIRONMENT CONFIG TABLES ({len(environment_tables)}):")
        for table in environment_tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   - {table}: {count:,} records")

        # Check for script generation capabilities
        print("\n" + "=" * 100)
        print("[LAUNCH] SCRIPT GENERATION ANALYSIS")
        print("=" * 100)

        # Look for tables that might support script generation
        script_generation_evidence = [

        for table in tables:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            column_names = [col[1].lower() for col in columns]

            # Check for script generation indicators
            if any(keyword in ' '.join(column_names) for keyword in []):
                script_generation_evidence.append(]
                    ])]
                })

        if script_generation_evidence:
            print("[SUCCESS] SCRIPT GENERATION CAPABILITIES DETECTED:")
            for evidence in script_generation_evidence:
                print(f"   [CLIPBOARD] Table: {evidence['table']}")
                print(
                    f"      [WRENCH] Relevant Columns: {', '.join(evidence['relevant_columns'])}")
        else:
            print("[ERROR] NO EXPLICIT SCRIPT GENERATION CAPABILITIES DETECTED")

        # Environment adaptation analysis
        print("\n[NETWORK] ENVIRONMENT ADAPTATION ANALYSIS:")

        # Check for environment-related tables and columns
        env_adaptation_evidence = [

        for table in tables:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            column_names = [col[1].lower() for col in columns]

            if any(keyword in ' '.join(column_names) for keyword in []):
                env_adaptation_evidence.append(]
                    ])]
                })

        if env_adaptation_evidence:
            print("[SUCCESS] ENVIRONMENT ADAPTATION CAPABILITIES DETECTED:")
            for evidence in env_adaptation_evidence:
                print(f"   [CLIPBOARD] Table: {evidence['table']}")
                print(
                    f"      [GEAR] Relevant Columns: {', '.join(evidence['relevant_columns'])}")
        else:
            print("[ERROR] LIMITED ENVIRONMENT ADAPTATION CAPABILITIES")

        print("\n" + "=" * 100)
        print("[TARGET] FINAL ASSESSMENT")
        print("=" * 100)

        total_records = 0
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            total_records += cursor.fetchone()[0]

        print(
            f"[BAR_CHART] Total Records Across All Tables: {total_records:,}")
        print(
            f"[?][?] Tables with Logging Capabilities: {len(set(conversation_tables + event_logging_tables + history_tracking_tables))}")
        print(f"[LAPTOP] Tables with Code Storage: {len(code_storage_tables)}")
        print(
            f"[GEAR] Tables with Environment Config: {len(environment_tables)}")

        # Generate recommendations
        print("\n[NOTES] RECOMMENDATIONS:")
        if total_records == 0:
            print(
                "   [WARNING] Database appears to be empty - no conversation/event data logged yet")
            print(
                "   [LAUNCH] Framework is ready to start logging conversations and events")

        if len(code_storage_tables) > 0:
            print("   [SUCCESS] Code storage capabilities present")
        else:
            print(
                "   [ERROR] No explicit code storage detected - scripts likely stored in filesystem")

        if len(script_generation_evidence) > 0:
            print("   [SUCCESS] Script generation infrastructure detected")
        else:
            print(
                "   [WARNING] Script generation capabilities need to be implemented")


if __name__ == "__main__":
    analyze_production_db()
