#!/usr/bin/env python3
"""
PRODUCTION DATABASE ANALYSIS SCRIPT
==================================
Enterprise-grade analysis of duplicate production.db files
Determines correct handling approach for database consolidation
"""

import sqlite3
import os
import json
import hashlib
from datetime import datetime
from pathlib import Path


def get_file_hash(filepath):
    """Calculate SHA256 hash of file"""
    hash_sha256 = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    except Exception as e:
        return f"ERROR: {str(e)}"


def analyze_database_structure(db_path):
    """Analyze database structure and contents"""
    analysis = {
        "file_path": str(db_path),
        "file_size": 0,
        "last_modified": None,
        "tables": [],
        "record_counts": {},
        "schema_info": {},
        "connection_status": "UNKNOWN",
        "hash": None
    }

    try:
        # File stats
        stat = os.stat(db_path)
        analysis["file_size"] = stat.st_size
        analysis["last_modified"] = datetime.fromtimestamp(]
            stat.st_mtime).isoformat()
        analysis["hash"] = get_file_hash(db_path)

        # Database analysis
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        analysis["tables"] = [table[0] for table in tables]

        # Get record counts for each table
        for table in analysis["tables"]:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                analysis["record_counts"][table] = count
            except Exception as e:
                analysis["record_counts"][table] = f"ERROR: {str(e)}"
        # Get schema info
        for table in analysis["tables"]:
            try:
                cursor.execute(f"PRAGMA table_info({table})")
                columns = cursor.fetchall()
                analysis["schema_info"][table] = [
                        "column_name": col[1],
                        "data_type": col[2],
                        "not_null": bool(col[3]),
                        "primary_key": bool(col[5])
                    }
                    for col in columns
                ]
            except Exception as e:
                analysis["schema_info"][table] = f"ERROR: {str(e)}"
        analysis["connection_status"] = "SUCCESS"
        conn.close()

    except Exception as e:
        analysis["connection_status"] = f"ERROR: {str(e)}"
    return analysis


def compare_databases(db1_analysis, db2_analysis):
    """Compare two database analyses"""
    comparison = {
        "timestamp": datetime.now().isoformat(),
        "file_comparison": {]
                "path": db1_analysis["file_path"],
                "size": db1_analysis["file_size"],
                "modified": db1_analysis["last_modified"],
                "hash": db1_analysis["hash"]
            },
            "db2": {]
                "path": db2_analysis["file_path"],
                "size": db2_analysis["file_size"],
                "modified": db2_analysis["last_modified"],
                "hash": db2_analysis["hash"]
            }
        },
        "identical_files": False,
        "size_difference": abs(db1_analysis["file_size"] - db2_analysis["file_size"]),
        "table_comparison": {]
            "db1_tables": db1_analysis["tables"],
            "db2_tables": db2_analysis["tables"],
            "common_tables": [],
            "db1_only": [],
            "db2_only": []
        },
        "record_comparison": {},
        "recommendations": []
    }

    # Check if files are identical
    if db1_analysis["hash"] == db2_analysis["hash"]:
        comparison["identical_files"] = True

    # Compare tables
    db1_tables = set(db1_analysis["tables"])
    db2_tables = set(db2_analysis["tables"])

    comparison["table_comparison"]["common_tables"] = list(]
        db1_tables & db2_tables)
    comparison["table_comparison"]["db1_only"] = list(db1_tables - db2_tables)
    comparison["table_comparison"]["db2_only"] = list(db2_tables - db1_tables)

    # Compare record counts for common tables
    for table in comparison["table_comparison"]["common_tables"]:
        if table in db1_analysis["record_counts"] and table in db2_analysis["record_counts"]:
            comparison["record_comparison"][table] = {
                "db1_count": db1_analysis["record_counts"][table],
                "db2_count": db2_analysis["record_counts"][table],
                "difference": abs(]
                    int(db1_analysis["record_counts"][table]) -
                    int(db2_analysis["record_counts"][table])
                ) if isinstance(db1_analysis["record_counts"][table], int) and isinstance(db2_analysis["record_counts"][table], int) else "N/A"
            }

    # Generate recommendations
    if comparison["identical_files"]:
        comparison["recommendations"].append(]
            "recommended_action": "Keep database in /databases/ folder (proper enterprise location)"
        })
    else:
        if db1_analysis["file_size"] > db2_analysis["file_size"]:
            comparison["recommendations"].append(]
                "description": f"Root database is {comparison['size_difference']} bytes larger",
                "recommended_action": "Root database appears to have more data"
            })
        elif db2_analysis["file_size"] > db1_analysis["file_size"]:
            comparison["recommendations"].append(]
                "description": f"Databases database is {comparison['size_difference']} bytes larger",
                "recommended_action": "Databases database appears to have more data"
            })

        # Check modification times
        db1_time = datetime.fromisoformat(db1_analysis["last_modified"])
        db2_time = datetime.fromisoformat(db2_analysis["last_modified"])

        if db1_time > db2_time:
            comparison["recommendations"].append(]
            })
        else:
            comparison["recommendations"].append(]
            })

    return comparison


def generate_enterprise_recommendation(comparison):
    """Generate enterprise-compliant recommendation"""
    recommendation = {
        "timestamp": datetime.now().isoformat(),
        "analysis_summary": {]
            "identical_files": comparison["identical_files"],
            "size_difference": comparison["size_difference"],
            "both_accessible": True
        },
        "enterprise_compliance": {},
        "recommended_actions": [],
        "risk_assessment": "LOW",
        "implementation_steps": []
    }

    if comparison["identical_files"]:
        recommendation["recommended_actions"] = [
                "command": "cp 'E:/gh_COPILOT/production.db' 'E:/gh_COPILOT/databases/production_backup_$(date +%Y%m%d_%H%M%S).db'"
            },
            {},
            {}
        ]
        recommendation["risk_assessment"] = "MINIMAL"
    else:
        # Files are different - need more careful analysis
        root_size = comparison["file_comparison"]["db1"]["size"]
        db_size = comparison["file_comparison"]["db2"]["size"]

        if root_size > db_size:
            recommendation["recommended_actions"] = [
                },
                {},
                {}
            ]
            recommendation["risk_assessment"] = "MEDIUM"
        else:
            recommendation["recommended_actions"] = [
                },
                {},
                {}
            ]
            recommendation["risk_assessment"] = "LOW"

    return recommendation


def main():
    """Main analysis function"""
    print("[SEARCH] PRODUCTION DATABASE ANALYSIS INITIATED")
    print("=" * 60)

    # Define database paths
    root_db = Path("E:/gh_COPILOT/production.db")
    databases_db = Path("E:/gh_COPILOT/databases/production.db")

    # Check if both files exist
    if not root_db.exists():
        print(f"[ERROR] Root database not found: {root_db}")
        return

    if not databases_db.exists():
        print(f"[ERROR] Databases database not found: {databases_db}")
        return

    print(f"[SUCCESS] Both database files found")
    print(f"[FOLDER] Root: {root_db}")
    print(f"[FOLDER] Databases: {databases_db}")
    print()

    # Analyze both databases
    print("[SEARCH] Analyzing root database...")
    root_analysis = analyze_database_structure(root_db)

    print("[SEARCH] Analyzing databases database...")
    databases_analysis = analyze_database_structure(databases_db)

    # Compare databases
    print("[SEARCH] Comparing databases...")
    comparison = compare_databases(root_analysis, databases_analysis)

    # Generate recommendation
    print("[SEARCH] Generating enterprise recommendation...")
    recommendation = generate_enterprise_recommendation(comparison)

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save detailed analysis
    analysis_file = f"E:/gh_COPILOT/production_db_analysis_{timestamp}.json"
    with open(analysis_file, 'w') as f:
        json.dump(]
        }, f, indent=2)

    # Print summary
    print("\n" + "=" * 60)
    print("[BAR_CHART] ANALYSIS SUMMARY")
    print("=" * 60)
    print(f"Root Database Size: {root_analysis['file_size']:,} bytes")
    print(
        f"Databases Database Size: {databases_analysis['file_size']:,} bytes")
    print(f"Size Difference: {comparison['size_difference']:,} bytes")
    print(f"Files Identical: {comparison['identical_files']}")
    print(f"Risk Assessment: {recommendation['risk_assessment']}")
    print()

    print("[CLIPBOARD] RECOMMENDED ACTIONS:")
    for action in recommendation["recommended_actions"]:
        print(
            f"  {action['priority']}. {action['action']}: {action['description']}")

    print(f"\n[STORAGE] Detailed analysis saved to: {analysis_file}")
    print("[SUCCESS] PRODUCTION DATABASE ANALYSIS COMPLETE")


if __name__ == "__main__":
    main()
