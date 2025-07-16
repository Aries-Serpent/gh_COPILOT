#!/usr/bin/env python3
"""
🔍 DATABASE SCHEMA ANALYZER
Analyze and fix schema mismatches between databases
"""

import os
import sqlite3
from pathlib import Path
from datetime import datetime
import json

class DatabaseSchemaAnalyzer:
    """🔍 Analyze database schemas for intelligent merging"""
    
    def __init__(self):
        self.workspace_root = Path(os.getcwd())
        self.source_db = self.workspace_root / "logs.db"
        self.target_db = self.workspace_root / "databases" / "logs.db"
        
        print(f"🚀 DATABASE SCHEMA ANALYZER STARTED")
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
    
    def get_table_schema(self, db_path: Path, table_name: str):
        """📊 Get detailed table schema information"""
        schema_info = {
            "columns": [],
            "column_count": 0,
            "create_sql": "",
            "sample_data": []
        }
        
        try:
            with sqlite3.connect(str(db_path)) as conn:
                cursor = conn.cursor()
                
                # Get table creation SQL
                cursor.execute(f"SELECT sql FROM sqlite_master WHERE name='{table_name}'")
                create_sql = cursor.fetchone()
                if create_sql:
                    schema_info["create_sql"] = create_sql[0]
                
                # Get column information
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                
                for col in columns:
                    schema_info["columns"].append({
                        "index": col[0],
                        "name": col[1],
                        "type": col[2],
                        "not_null": col[3],
                        "default": col[4],
                        "primary_key": col[5]
                    })
                
                schema_info["column_count"] = len(columns)
                
                # Get sample data (first 3 rows)
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                sample_rows = cursor.fetchall()
                schema_info["sample_data"] = [list(row) for row in sample_rows]
                
        except Exception as e:
            schema_info["error"] = str(e)
        
        return schema_info
    
    def analyze_schema_differences(self):
        """🔍 Analyze schema differences between databases"""
        
        print("🔍 ANALYZING ENTERPRISE_LOGS SCHEMA DIFFERENCES")
        print("="*60)
        
        # Get schemas
        source_schema = self.get_table_schema(self.source_db, "enterprise_logs")
        target_schema = self.get_table_schema(self.target_db, "enterprise_logs")
        
        print(f"📊 SOURCE TABLE (logs.db):")
        print(f"   Columns: {source_schema['column_count']}")
        for col in source_schema['columns']:
            print(f"   - {col['name']} ({col['type']})")
        
        print(f"\n🎯 TARGET TABLE (databases/logs.db):")
        print(f"   Columns: {target_schema['column_count']}")
        for col in target_schema['columns']:
            print(f"   - {col['name']} ({col['type']})")
        
        # Compare schemas
        source_cols = {col['name']: col for col in source_schema['columns']}
        target_cols = {col['name']: col for col in target_schema['columns']}
        
        common_cols = set(source_cols.keys()) & set(target_cols.keys())
        source_only = set(source_cols.keys()) - set(target_cols.keys())
        target_only = set(target_cols.keys()) - set(source_cols.keys())
        
        print(f"\n🔄 SCHEMA COMPARISON:")
        print(f"   Common Columns: {len(common_cols)} - {list(common_cols)}")
        print(f"   Source Only: {len(source_only)} - {list(source_only)}")
        print(f"   Target Only: {len(target_only)} - {list(target_only)}")
        
        # Show sample data
        print(f"\n📋 SOURCE SAMPLE DATA:")
        for i, row in enumerate(source_schema['sample_data'][:2]):
            print(f"   Row {i+1}: {row}")
        
        print(f"\n📋 TARGET SAMPLE DATA:")
        for i, row in enumerate(target_schema['sample_data'][:2]):
            print(f"   Row {i+1}: {row}")
        
        # Generate migration strategy
        migration_strategy = self.generate_migration_strategy(source_schema, target_schema)
        
        # Save analysis report
        analysis_report = {
            "timestamp": datetime.now().isoformat(),
            "source_schema": source_schema,
            "target_schema": target_schema,
            "comparison": {
                "common_columns": list(common_cols),
                "source_only": list(source_only),
                "target_only": list(target_only)
            },
            "migration_strategy": migration_strategy
        }
        
        report_path = self.workspace_root / f"schema_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(analysis_report, f, indent=2)
        
        print(f"\n📋 Analysis report saved: {report_path}")
        return migration_strategy
    
    def generate_migration_strategy(self, source_schema, target_schema):
        """🧠 Generate intelligent migration strategy"""
        
        strategy = {
            "approach": "SCHEMA_AWARE_MERGE",
            "steps": [],
            "sql_mapping": {},
            "feasible": True
        }
        
        source_cols = {col['name']: col for col in source_schema['columns']}
        target_cols = {col['name']: col for col in target_schema['columns']}
        
        # Find common columns for mapping
        common_cols = []
        for col_name in source_cols:
            if col_name in target_cols:
                common_cols.append(col_name)
        
        if len(common_cols) >= 3:  # Need at least some common columns
            strategy["steps"] = [
                "1. Map source columns to target columns using common fields",
                "2. Insert only mappable columns from source to target",
                "3. Set default values for target-only columns",
                "4. Skip source-only columns",
                "5. Verify data integrity after merge"
            ]
            
            # Create SQL mapping
            source_select = ", ".join(common_cols)
            target_insert = ", ".join(common_cols)
            placeholders = ", ".join(["?" for _ in common_cols])
            
            strategy["sql_mapping"] = {
                "source_select": f"SELECT {source_select} FROM enterprise_logs",
                "target_insert": f"INSERT OR IGNORE INTO enterprise_logs ({target_insert}) VALUES ({placeholders})",
                "common_columns": common_cols
            }
        else:
            strategy["feasible"] = False
            strategy["reason"] = "Insufficient common columns for safe migration"
        
        print(f"\n🧠 MIGRATION STRATEGY:")
        print(f"   Approach: {strategy['approach']}")
        print(f"   Feasible: {strategy['feasible']}")
        if strategy['feasible']:
            print(f"   Common Columns: {len(common_cols)} - {common_cols}")
            for step in strategy['steps']:
                print(f"   {step}")
        else:
            print(f"   Issue: {strategy['reason']}")
        
        return strategy

def main():
    analyzer = DatabaseSchemaAnalyzer()
    migration_strategy = analyzer.analyze_schema_differences()

if __name__ == "__main__":
    main()
