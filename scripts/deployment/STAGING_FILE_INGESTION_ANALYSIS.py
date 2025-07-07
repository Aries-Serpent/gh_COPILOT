#!/usr/bin/env python3
"""
[BAR_CHART] STAGING FILE INGESTION ANALYSIS
==================================
Analyze staging deployment files and database ingestion status
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

def analyze_staging_file_ingestion():
    """Comprehensive analysis of staging file deployment and database ingestion"""
    
    print("[BAR_CHART] STAGING FILE INGESTION ANALYSIS")
    print("=" * 60)
    
    # Staging environment analysis
    staging_path = Path("e:/gh_COPILOT")
    workspace_path = Path("e:/gh_COPILOT")
    
    if not staging_path.exists():
        print("[ERROR] Staging environment not found")
        return
    
    # Count deployed files
    all_files = list(staging_path.rglob("*"))
    file_types = {
        'python_scripts': len(list(staging_path.rglob("*.py"))),
        'databases': len(list(staging_path.rglob("*.db"))),
        'json_files': len(list(staging_path.rglob("*.json"))),
        'markdown_docs': len(list(staging_path.rglob("*.md"))),
        'config_files': len(list(staging_path.rglob("*.json"))) + len(list(staging_path.rglob("*.yaml"))),
        'total_files': len([f for f in all_files if f.is_file()]),
        'directories': len([f for f in all_files if f.is_dir()])
    }
    
    print(f"[PACKAGE] DEPLOYED FILES BREAKDOWN:")
    print(f"  Total Files: {file_types['total_files']}")
    print(f"  Python Scripts: {file_types['python_scripts']}")
    print(f"  Database Files: {file_types['databases']}")
    print(f"  JSON Files: {file_types['json_files']}")
    print(f"  Documentation: {file_types['markdown_docs']}")
    print(f"  Directories: {file_types['directories']}")
    
    # Analyze database content vs file content
    print(f"\n[FILE_CABINET]  DATABASE VS FILE ANALYSIS:")
    
    # Check if production.db contains file references
    production_db = staging_path / "production.db"
    if production_db.exists():
        try:
            conn = sqlite3.connect(production_db)
            cursor = conn.cursor()
            
            # Get table list
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            print(f"  Production DB Tables: {len(tables)}")
            
            # Check for file tracking tables
            file_tracking_tables = [t for t in tables if any(keyword in t.lower() 
                                  for keyword in ['file', 'script', 'template', 'code'])]
            
            if file_tracking_tables:
                print(f"  File-related tables: {len(file_tracking_tables)}")
                for table in file_tracking_tables[:5]:  # Show first 5
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    print(f"    {table}: {count} records")
            
            # Check if files are ingested as data
            scripts_in_db = 0
            for table in file_tracking_tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE file_path IS NOT NULL OR script_content IS NOT NULL")
                    scripts_in_db += cursor.fetchone()[0]
                except:
                    pass
            
            print(f"  Files ingested as data: {scripts_in_db}")
            
            conn.close()
            
        except Exception as e:
            print(f"  [ERROR] Database analysis error: {e}")
    
    # Functional dependency analysis
    print(f"\n[WRENCH] FUNCTIONAL DEPENDENCY ANALYSIS:")
    
    critical_files = {
        'executable_scripts': list(staging_path.rglob("*.py")),
        'configuration': list(staging_path.rglob("*.json")) + list(staging_path.rglob("*.yaml")),
        'documentation': list(staging_path.rglob("*.md")),
        'databases': list(staging_path.rglob("*.db"))
    }
    
    # Analyze if system can function database-only
    database_only_capable = True
    missing_critical_functions = []
    
    # Check for runtime dependencies
    python_scripts = critical_files['executable_scripts']
    runtime_scripts = []
    
    for script in python_scripts[:10]:  # Check first 10 scripts
        try:
            with open(script, 'r', encoding='utf-8') as f:
                content = f.read()
                if any(keyword in content for keyword in ['if __name__ == "__main__"', 'main()', 'execute', 'run']):
                    runtime_scripts.append(script.name)
        except:
            pass
    
    if len(runtime_scripts) > 5:  # If many runtime scripts exist
        database_only_capable = False
        missing_critical_functions.append("Runtime execution scripts needed")
    
    # Check for configuration dependencies
    config_files = critical_files['configuration']
    if len(config_files) > 3:
        database_only_capable = False
        missing_critical_functions.append("Configuration files needed for runtime")
    
    print(f"  Database-only operation: {'[SUCCESS] POSSIBLE' if database_only_capable else '[ERROR] NOT RECOMMENDED'}")
    if missing_critical_functions:
        print(f"  Missing functions without files:")
        for func in missing_critical_functions:
            print(f"    - {func}")
    
    # Ingestion status assessment
    print(f"\n[CHART_INCREASING] INGESTION STATUS ASSESSMENT:")
    
    ingestion_status = {
        'files_as_data': scripts_in_db if 'scripts_in_db' in locals() else 0,
        'files_as_filesystem': file_types['total_files'],
        'ingestion_percentage': (scripts_in_db / file_types['total_files'] * 100) if 'scripts_in_db' in locals() and file_types['total_files'] > 0 else 0
    }
    
    print(f"  Files stored as data: {ingestion_status['files_as_data']}")
    print(f"  Files on filesystem: {ingestion_status['files_as_filesystem']}")
    print(f"  Ingestion rate: {ingestion_status['ingestion_percentage']:.1f}%")
    
    # Recommendations
    print(f"\n[TARGET] RECOMMENDATIONS:")
    
    if ingestion_status['ingestion_percentage'] < 50:
        print("  [INPUT] INCREASE INGESTION: Consider ingesting more files as database content")
        print("     - Convert static scripts to stored procedures")
        print("     - Store configuration as database parameters")
        print("     - Archive documentation in database tables")
    
    if not database_only_capable:
        print("  [WRENCH] HYBRID APPROACH: Maintain both database and file-based operation")
        print("     - Keep runtime scripts as files for execution")
        print("     - Store data and templates in databases")
        print("     - Use database for configuration management")
    else:
        print("  [SUCCESS] DATABASE-FIRST SUCCESS: System can operate database-only")
        print("     - All critical functions available in database")
        print("     - Files serve as backup/reference only")
    
    return {
        'file_types': file_types,
        'ingestion_status': ingestion_status,
        'database_only_capable': database_only_capable,
        'recommendations': missing_critical_functions
    }

if __name__ == "__main__":
    analyze_staging_file_ingestion()
