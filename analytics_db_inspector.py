#!/usr/bin/env python3
"""
Analytics Database Inspector
Provides a comprehensive overview of the analytics.db database
"""

import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple


def inspect_database(db_path: str | Path = "databases/analytics.db") -> None:
    """Inspect the analytics database and provide a comprehensive report."""

    try:
        conn: sqlite3.Connection = sqlite3.connect(str(db_path))
        cursor: sqlite3.Cursor = conn.cursor()
        
        print("🔍 Analytics Database Inspection Report")
        print("=" * 50)
        
        # Get all tables
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        )
        tables: List[Tuple[str]] = cursor.fetchall()
        
        print(f"\n📊 Database Overview:")
        print(f"   • Total Tables: {len(tables)}")
        print(f"   • Database Size: {Path(db_path).stat().st_size:,} bytes")
        
        # Analyze each table
        table_stats: List[Dict[str, Any]] = []
        for table_name in [t[0] for t in tables]:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                
                # Get table schema
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns: Sequence[Tuple[Any, ...]] = cursor.fetchall()
                
                table_stats.append(
                    {
                        "name": table_name,
                        "records": count,
                        "columns": len(columns),
                        "schema": [{"name": col[1], "type": col[2]} for col in columns],
                    }
                )
            except Exception as e:  # pragma: no cover - diagnostic output
                print(f"   ⚠️  Error analyzing table {table_name}: {e}")
        
        # Sort by record count
        table_stats.sort(key=lambda x: x['records'], reverse=True)
        
        print(f"\n📋 Table Summary (Top 15 by record count):")
        print("   " + "-" * 60)
        print(f"   {'Table Name':<35} {'Records':<10} {'Columns':<8}")
        print("   " + "-" * 60)
        
        for table in table_stats[:15]:
            print(f"   {table['name']:<35} {table['records']:<10,} {table['columns']:<8}")
        
        # Analyze key tables in detail
        key_tables = ['templates', 'compliance_tracking', 'performance_metrics', 
                     'error_corrections', 'flake8_violations', 'code_quality_metrics']
        
        print(f"\n🔎 Key Tables Analysis:")
        for table_name in key_tables:
            table_info = next((t for t in table_stats if t["name"] == table_name), None)
            if table_info:
                print(f"\n   📁 {table_name.upper()}:")
                print(f"      Records: {table_info['records']:,}")
                print(
                    f"      Columns: {', '.join([col['name'] for col in table_info['schema'][:5]])}"
                )
                
                # Sample some data
                try:
                    cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                    sample_data = cursor.fetchall()
                    if sample_data:
                        print(f"      Sample: {len(sample_data)} rows")
                except Exception:
                    pass
        
        # Check for recent activity
        print(f"\n⏰ Recent Activity Analysis:")
        activity_tables = ['audit_trails', 'performance_metrics', 'compliance_tracking']
        
        for table_name in activity_tables:
            if any(t["name"] == table_name for t in table_stats):
                try:
                    # Look for timestamp columns
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    columns = cursor.fetchall()
                    timestamp_cols: List[str] = [
                        col[1]
                        for col in columns
                        if "time" in col[1].lower() or "date" in col[1].lower()
                    ]

                    if timestamp_cols:
                        timestamp_col = timestamp_cols[0]
                        cursor.execute(f"SELECT MAX({timestamp_col}) FROM {table_name}")
                        latest = cursor.fetchone()[0]
                        if latest:
                            print(f"   • {table_name}: Latest entry at {latest}")
                except Exception:
                    pass
        
        # Enterprise features
        print(f"\n🏢 Enterprise Features Detected:")
        enterprise_tables: List[Dict[str, Any]] = [
            t for t in table_stats if "enterprise" in t["name"]
        ]
        if enterprise_tables:
            for table in enterprise_tables:
                print(f"   • {table['name']}: {table['records']:,} records")
        else:
            print("   • No enterprise-specific tables found")
        
        # Compliance and security
        compliance_tables: List[Dict[str, Any]] = [
            t
            for t in table_stats
            if any(
                keyword in t["name"]
                for keyword in ["compliance", "security", "audit", "violation"]
            )
        ]
        
        print(f"\n🔒 Compliance & Security Tables:")
        for table in compliance_tables:
            print(f"   • {table['name']}: {table['records']:,} records")
        
        conn.close()
        print(f"\n✅ Database inspection completed successfully!")

    except Exception as e:  # pragma: no cover - diagnostic output
        print(f"❌ Error inspecting database: {e}")

if __name__ == "__main__":
    inspect_database()
