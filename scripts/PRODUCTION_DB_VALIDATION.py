#!/usr/bin/env python3
"""
ENTERPRISE PRODUCTION DATABASE VALIDATION
=========================================

This script analyzes the two production.db files to determine:
1. If they are identical (same content/hash)
2. If they serve different purposes
3. Safe consolidation recommendations

COMPLIANCE: Enterprise database management and redundancy prevention
"""

import os
import hashlib
import json
import sqlite3
from pathlib import Path
from datetime import datetime
import shutil
from tqdm import tqdm
import time


class ProductionDatabaseValidator:
    def __init__(self):
        self.start_time = datetime.now()
        self.process_id = os.getpid()

        # Database paths
        self.root_db = Path('production.db')
        self.staging_db = Path('E:/gh_COPILOT/production.db')

        # Results structure
        self.validation_results = {
            "validation_timestamp": self.start_time.isoformat(),
            "process_id": self.process_id,
            "root_db_analysis": {},
            "staging_db_analysis": {},
            "comparison_results": {},
            "recommendations": [],
            "safety_assessment": {},
            "consolidation_plan": {}
        }

        # CRITICAL: Anti-recursion validation
        self._validate_environment_safety()

    def _validate_environment_safety(self):
        """CRITICAL: Validate no recursive folder structures"""
        print("[SHIELD] VALIDATING ENVIRONMENT SAFETY")

        workspace_root = Path(os.getcwd())
        proper_root = "E:/gh_COPILOT"

        # Validate proper environment root
        if not str(workspace_root).replace("\\", "/").endswith("gh_COPILOT"):
            raise RuntimeError(]
                f"[ALERT] CRITICAL: Invalid workspace root: {workspace_root}")

        # Check for forbidden backup patterns
        forbidden_patterns = ['*backup*', '*_backup_*', 'backups', '*temp*']
        violations = [

        for pattern in forbidden_patterns:
            for folder in workspace_root.rglob(pattern):
                if folder.is_dir() and folder != workspace_root:
                    violations.append(str(folder))

        if violations:
            raise RuntimeError(]
                f"[ALERT] CRITICAL: Recursive violations found: {violations}")

        print("[SUCCESS] Environment safety validation passed")

    def analyze_database_file(self, db_path: Path, label: str) -> dict:
        """Analyze a single database file"""
        print(f"\n[SEARCH] ANALYZING {label}: {db_path}")

        if not db_path.exists():
            print(f"[ERROR] Database not found: {db_path}")
            return {]
                "error": f"File not found: {db_path}"
            }

        try:
            # File system analysis
            file_stats = db_path.stat()
            file_size = file_stats.st_size
            modified_time = datetime.fromtimestamp(file_stats.st_mtime)

            # Calculate file hash
            print(f"[BAR_CHART] Calculating hash for {label}...")
            file_hash = self._calculate_file_hash(db_path)

            # Database structure analysis
            print(f"[CLIPBOARD] Analyzing database structure for {label}...")
            db_structure = self._analyze_database_structure(db_path)

            # Record count analysis
            print(f"[CHART_INCREASING] Counting records for {label}...")
            record_counts = self._count_database_records(db_path)

            result = {
                "file_path": str(db_path),
                "file_size": file_size,
                "file_size_mb": file_size / (1024*1024),
                "modified_time": modified_time.isoformat(),
                "file_hash": file_hash,
                "database_structure": db_structure,
                "record_counts": record_counts,
                "is_valid_db": db_structure["is_valid"],
                "table_count": len(db_structure.get("tables", [])),
                "total_records": sum(record_counts.values()) if record_counts else 0
            }

            print(f"[SUCCESS] {label} analysis complete:")
            print(f"   - Size: {result['file_size_mb']:.2f} MB")
            print(f"   - Tables: {result['table_count']}")
            print(f"   - Total records: {result['total_records']}")
            print(f"   - Valid DB: {result['is_valid_db']}")

            return result

        except Exception as e:
            print(f"[ERROR] Error analyzing {label}: {str(e)}")
            return {]
                "error": str(e),
                "file_path": str(db_path)
            }

    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of a file with progress"""
        try:
            hash_sha256 = hashlib.sha256()
            file_size = file_path.stat().st_size

            with open(file_path, 'rb') as f:
                with tqdm(total=file_size, unit='B', unit_scale=True, desc="Hashing") as pbar:
                    while chunk := f.read(8192):
                        hash_sha256.update(chunk)
                        pbar.update(len(chunk))

            return hash_sha256.hexdigest()
        except Exception as e:
            return f"ERROR: {str(e)}"
    def _analyze_database_structure(self, db_path: Path) -> dict:
        """Analyze database structure"""
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()

                # Get table information
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]

                # Get schema for each table
                table_schemas = {}
                for table in tables:
                    cursor.execute(f"PRAGMA table_info({table})")
                    columns = cursor.fetchall()
                    table_schemas[table] = {
                        "columns": [{"name": col[1], "type": col[2], "notnull": col[3]} for col in columns],
                        "column_count": len(columns)
                    }

                # Database integrity check
                cursor.execute("PRAGMA integrity_check")
                integrity_result = cursor.fetchone()[0]

                return {}

        except Exception as e:
            return {]
                "error": str(e),
                "tables": [],
                "table_schemas": {}
            }

    def _count_database_records(self, db_path: Path) -> dict:
        """Count records in each table"""
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()

                # Get table names
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]

                record_counts = {}
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    record_counts[table] = count

                return record_counts

        except Exception as e:
            return {"error": str(e)}

    def compare_databases(self) -> dict:
        """Compare the two production databases"""
        print("\n[SEARCH] COMPARING PRODUCTION DATABASES")
        print("-" * 40)

        root_analysis = self.validation_results["root_db_analysis"]
        staging_analysis = self.validation_results["staging_db_analysis"]

        # Check if both databases exist and are valid
        if not root_analysis.get("exists") or not staging_analysis.get("exists"):
            return {}

        if not root_analysis.get("is_valid_db") or not staging_analysis.get("is_valid_db"):
            return {}

        # File-level comparison
        files_identical = root_analysis["file_hash"] == staging_analysis["file_hash"]
        size_difference = abs(]
            root_analysis["file_size"] - staging_analysis["file_size"])

        # Structure comparison
        root_tables = set(root_analysis["database_structure"]["tables"])
        staging_tables = set(staging_analysis["database_structure"]["tables"])

        common_tables = root_tables & staging_tables
        root_only_tables = root_tables - staging_tables
        staging_only_tables = staging_tables - root_tables

        # Record count comparison
        record_differences = {}
        for table in common_tables:
            root_count = root_analysis["record_counts"].get(table, 0)
            staging_count = staging_analysis["record_counts"].get(table, 0)
            if root_count != staging_count:
                record_differences[table] = {
                    "difference": abs(root_count - staging_count)
                }

        comparison_results = {
            "size_difference_mb": size_difference / (1024*1024),
            "structure_comparison": {]
                "common_tables": list(common_tables),
                "root_only_tables": list(root_only_tables),
                "staging_only_tables": list(staging_only_tables),
                "table_structure_identical": len(root_only_tables) == 0 and len(staging_only_tables) == 0
            },
            "record_differences": record_differences,
            "total_record_difference": sum(diff["difference"] for diff in record_differences.values())
        }

        print(f"[BAR_CHART] Comparison Results:")
        print(f"   - Files identical: {files_identical}")
        print(
            f"   - Size difference: {comparison_results['size_difference_mb']:.2f} MB")
        print(f"   - Common tables: {len(common_tables)}")
        print(f"   - Root-only tables: {len(root_only_tables)}")
        print(f"   - Staging-only tables: {len(staging_only_tables)}")
        print(f"   - Record differences: {len(record_differences)}")

        return comparison_results

    def generate_recommendations(self) -> list:
        """Generate safety recommendations"""
        print("\n[TARGET] GENERATING RECOMMENDATIONS")
        print("-" * 30)

        recommendations = [
        comparison = self.validation_results["comparison_results"]

        if not comparison.get("can_compare", False):
            recommendations.append(]
                "[ERROR] Cannot compare databases - analysis incomplete")
            return recommendations

        # If files are identical
        if comparison["files_identical"]:
            recommendations.append(]
                "[SUCCESS] SAFE TO CONSOLIDATE: Files are identical")
            recommendations.append(]
                "[PROCESSING] Recommended action: Keep root database, remove staging database")
            recommendations.append(]
                "[CLIPBOARD] Backup staging database before removal (enterprise compliance)")

        # If files are different
        else:
            if comparison["size_difference_mb"] < 1:
                recommendations.append(]
                    "[WARNING] MINOR DIFFERENCES: Databases are similar but not identical")
            else:
                recommendations.append(]
                    "[ALERT] SIGNIFICANT DIFFERENCES: Databases have substantial differences")

            # Structure analysis
            if comparison["structure_comparison"]["table_structure_identical"]:
                recommendations.append(]
                    "[SUCCESS] Table structures are identical")
            else:
                recommendations.append(]
                    "[WARNING] Table structures differ - manual review required")

            # Record differences
            if comparison["total_record_difference"] == 0:
                recommendations.append(]
                    "[SUCCESS] All tables have identical record counts")
            else:
                recommendations.append(]
                    f"[WARNING] Total record difference: {comparison['total_record_difference']}")

        # Age analysis
        root_analysis = self.validation_results["root_db_analysis"]
        staging_analysis = self.validation_results["staging_db_analysis"]

        if root_analysis.get("exists") and staging_analysis.get("exists"):
            root_time = datetime.fromisoformat(root_analysis["modified_time"])
            staging_time = datetime.fromisoformat(]
                staging_analysis["modified_time"])

            if root_time > staging_time:
                recommendations.append(]
                    "[?] Root database is newer - likely the active version")
            elif staging_time > root_time:
                recommendations.append(]
                    "[?] Staging database is newer - may need to replace root")
            else:
                recommendations.append(]
                    "[?] Both databases have identical modification times")

        return recommendations

    def create_consolidation_plan(self) -> dict:
        """Create a safe consolidation plan"""
        print("\n[CLIPBOARD] CREATING CONSOLIDATION PLAN")
        print("-" * 30)

        comparison = self.validation_results["comparison_results"]

        if not comparison.get("can_compare", False):
            return {"status": "cannot_create_plan", "reason": "Comparison incomplete"}

        # Determine primary database
        root_analysis = self.validation_results["root_db_analysis"]
        staging_analysis = self.validation_results["staging_db_analysis"]

        if comparison["files_identical"]:
            plan_type = "identical_consolidation"
            primary_db = "root"
            remove_db = "staging"
        else:
            # Choose based on modification time and size
            root_time = datetime.fromisoformat(root_analysis["modified_time"])
            staging_time = datetime.fromisoformat(]
                staging_analysis["modified_time"])

            if root_time >= staging_time:
                plan_type = "keep_root"
                primary_db = "root"
                remove_db = "staging"
            else:
                plan_type = "keep_staging"
                primary_db = "staging"
                remove_db = "root"

        consolidation_plan = {
            "backup_location": f"E:/temp/gh_COPILOT_Backups/production_db_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db",
            "steps": [],
            "estimated_space_savings_mb": min(root_analysis["file_size_mb"], staging_analysis["file_size_mb"]),
            "risk_assessment": "LOW" if comparison["files_identical"] else "MEDIUM"
        }

        return consolidation_plan

    def run_validation(self):
        """Run complete validation process"""
        print("[LAUNCH] PRODUCTION DATABASE VALIDATION STARTED")
        print(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Process ID: {self.process_id}")
        print("-" * 50)

        with tqdm(total=100, desc="[SEARCH] Validation Progress", unit="%") as pbar:
            # Analyze root database
            pbar.set_description("[BAR_CHART] Analyzing root database")
            self.validation_results["root_db_analysis"] = self.analyze_database_file(]
                self.root_db, "ROOT DATABASE")
            pbar.update(30)

            # Analyze staging database
            pbar.set_description("[BAR_CHART] Analyzing staging database")
            self.validation_results["staging_db_analysis"] = self.analyze_database_file(]
                self.staging_db, "STAGING DATABASE")
            pbar.update(30)

            # Compare databases
            pbar.set_description("[SEARCH] Comparing databases")
            self.validation_results["comparison_results"] = self.compare_databases(]
            )
            pbar.update(20)

            # Generate recommendations
            pbar.set_description("[TARGET] Generating recommendations")
            self.validation_results["recommendations"] = self.generate_recommendations(]
            )
            pbar.update(10)

            # Create consolidation plan
            pbar.set_description("[CLIPBOARD] Creating consolidation plan")
            self.validation_results["consolidation_plan"] = self.create_consolidation_plan(]
            )
            pbar.update(10)

        # Save results
        self._save_results()

        # Display summary
        self._display_summary()

        print("\n[SUCCESS] PRODUCTION DATABASE VALIDATION COMPLETE")
        duration = (datetime.now() - self.start_time).total_seconds()
        print(f"Duration: {duration:.2f} seconds")

        return self.validation_results

    def _save_results(self):
        """Save validation results to file"""
        results_file = f"production_db_validation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(self.validation_results, f, indent=2)

        print(f"[?] Results saved to: {results_file}")

    def _display_summary(self):
        """Display validation summary"""
        print("\n" + "=" * 60)
        print("[BAR_CHART] PRODUCTION DATABASE VALIDATION SUMMARY")
        print("=" * 60)

        root_analysis = self.validation_results["root_db_analysis"]
        staging_analysis = self.validation_results["staging_db_analysis"]
        comparison = self.validation_results["comparison_results"]

        # Database status
        print(
            f"Root Database: {'[SUCCESS] EXISTS' if root_analysis.get('exists') else '[ERROR] MISSING'}")
        if root_analysis.get("exists"):
            print(f"  - Size: {root_analysis['file_size_mb']:.2f} MB")
            print(f"  - Tables: {root_analysis['table_count']}")
            print(f"  - Records: {root_analysis['total_records']}")

        print(
            f"Staging Database: {'[SUCCESS] EXISTS' if staging_analysis.get('exists') else '[ERROR] MISSING'}")
        if staging_analysis.get("exists"):
            print(f"  - Size: {staging_analysis['file_size_mb']:.2f} MB")
            print(f"  - Tables: {staging_analysis['table_count']}")
            print(f"  - Records: {staging_analysis['total_records']}")

        # Comparison results
        if comparison.get("can_compare"):
            print(f"\n[SEARCH] COMPARISON RESULTS:")
            print(
                f"Files Identical: {'[SUCCESS] YES' if comparison['files_identical'] else '[ERROR] NO'}")
            print(
                f"Size Difference: {comparison['size_difference_mb']:.2f} MB")

        # Recommendations
        print(f"\n[TARGET] RECOMMENDATIONS:")
        for i, rec in enumerate(self.validation_results["recommendations"], 1):
            print(f"{i}. {rec}")

        # Consolidation plan
        plan = self.validation_results["consolidation_plan"]
        if plan.get("plan_type"):
            print(f"\n[CLIPBOARD] CONSOLIDATION PLAN:")
            print(f"Plan Type: {plan['plan_type']}")
            print(f"Primary Database: {plan['primary_database']}")
            print(f"Database to Remove: {plan['database_to_remove']}")
            print(f"Risk Assessment: {plan['risk_assessment']}")
            print(
                f"Space Savings: {plan['estimated_space_savings_mb']:.2f} MB")


def main():
    """Main execution function"""
    try:
        validator = ProductionDatabaseValidator()
        results = validator.run_validation()

        print("\n[ACHIEVEMENT] VALIDATION SUCCESSFUL")
        print("Check the generated JSON file for detailed results")

        return results

    except Exception as e:
        print(f"[ERROR] VALIDATION FAILED: {str(e)}")
        return None


if __name__ == "__main__":
    main()
