#!/usr/bin/env python3
"""
Quick Database Script Reproduction Analysis
==========================================
Immediate validation of database script reproduction capabilities.
"""

import sys
import sqlite3
import json
import ast
from pathlib import Path
from datetime import datetime

# Text indicators
TEXT = {"start": "[START]", "success": "[SUCCESS]", "error": "[ERROR]", "info": "[INFO]"}


def main():
    print(f"{TEXT['start']} Quick Database Script Reproduction Analysis")

    workspace = Path("e:/gh_COPILOT")
    databases_path = workspace / "databases"

    # 1. Count Python scripts in workspace
    all_scripts = list(workspace.rglob("*.py"))
    print(f"{TEXT['info']} Found {len(all_scripts)} Python scripts in workspace")

    # 2. Count database files
    db_files = list(databases_path.glob("*.db"))
    print(f"{TEXT['info']} Found {len(db_files)} database files in databases/ directory")

    # 3. Quick sample of database content analysis
    scripts_in_databases = 0
    sample_db_scripts = {}

    for db_file in db_files[:5]:  # Sample first 5 databases
        try:
            with sqlite3.connect(str(db_file)) as conn:
                cursor = conn.cursor()

                # Get table names
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]

                for table in tables:
                    try:
                        # Try to find content columns
                        cursor.execute(f"PRAGMA table_info({table})")
                        columns = [row[1] for row in cursor.fetchall()]

                        content_cols = [col for col in columns if "content" in col.lower() or "script" in col.lower()]
                        if content_cols:
                            cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {content_cols[0]} IS NOT NULL")
                            count = cursor.fetchone()[0]
                            if count > 0:
                                scripts_in_databases += count
                                sample_db_scripts[f"{db_file.name}.{table}"] = count
                    except (sqlite3.Error, OSError) as exc:
                        print(f"{TEXT['error']} Query failed for {table}: {exc}")
                        continue
        except (sqlite3.Error, OSError) as e:
            print(f"{TEXT['error']} Failed to analyze {db_file.name}: {e}")

    print(f"{TEXT['info']} Found approximately {scripts_in_databases} script entries in sampled databases")
    print(f"{TEXT['info']} Sample database script counts: {sample_db_scripts}")

    # 4. Quick syntax validation of random scripts
    import random

    sample_scripts = random.sample(all_scripts, min(10, len(all_scripts)))

    syntax_valid = 0
    syntax_errors = []

    for script in sample_scripts:
        try:
            with open(script, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            ast.parse(content)
            syntax_valid += 1
        except SyntaxError as e:
            syntax_errors.append(f"{script.name}: {e}")
        except OSError as e:
            syntax_errors.append(f"{script.name}: {e}")

    print(f"{TEXT['info']} Sample syntax validation: {syntax_valid}/{len(sample_scripts)} scripts valid")
    if syntax_errors:
        print(f"{TEXT['error']} Sample syntax errors found:")
        for error in syntax_errors[:3]:  # Show first 3 errors
            print(f"  - {error}")

    # 5. Generate quick report
    report = {
        "timestamp": datetime.now().isoformat(),
        "workspace_scripts": len(all_scripts),
        "database_files": len(db_files),
        "estimated_database_scripts": scripts_in_databases,
        "sample_syntax_validation": {
            "total_tested": len(sample_scripts),
            "valid": syntax_valid,
            "error_rate": (len(sample_scripts) - syntax_valid) / len(sample_scripts) * 100,
        },
        "database_sample_analysis": sample_db_scripts,
    }

    # Save quick report
    report_file = workspace / "config/quick_database_analysis_report.json"
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n{TEXT['success']} Quick analysis complete!")
    print(f"📊 Report saved: {report_file}")
    print(f"\n📈 QUICK SUMMARY:")
    print(f"   Total Python Scripts: {len(all_scripts)}")
    print(f"   Database Files: {len(db_files)}")
    print(f"   Estimated Database Scripts: {scripts_in_databases}")
    print(
        f"   Sample Syntax Valid Rate: {syntax_valid}/{len(sample_scripts)} ({syntax_valid / len(sample_scripts) * 100:.1f}%)"
    )

    # Recommendation
    if scripts_in_databases > 0:
        print(f"\n{TEXT['success']} DATABASES CONTAIN SCRIPT DATA - Reproduction capability likely available")
    else:
        print(f"\n{TEXT['info']} Limited script data found in databases - Further investigation needed")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
