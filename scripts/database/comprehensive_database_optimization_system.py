#!/usr/bin/env python3
"""
🗄️ COMPREHENSIVE DATABASE OPTIMIZATION SYSTEM
================================================================
ENTERPRISE MANDATE: Free up deployment_logs.db, consolidate ALL databases
to databases/ folder, reduce ALL sizes below 99.9MB, eliminate duplicates
while maintaining FULL functionality
================================================================
"""

import os
import sqlite3
import shutil
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from tqdm import tqdm
import time
import logging


# 🚨 CRITICAL: Anti-recursion validation
def validate_no_recursive_folders():
    """CRITICAL: Validate no recursive folder structures"""
    workspace_root = Path("e:/gh_COPILOT")
    forbidden_patterns = ["*backup*", "*_backup_*", "backups", "*temp*"]
    violations = []

    for pattern in forbidden_patterns:
        for folder in workspace_root.rglob(pattern):
            if folder.is_dir() and folder != workspace_root:
                violations.append(str(folder))

    if violations:
        for violation in violations:
            print(f"🚨 RECURSIVE VIOLATION: {violation}")
        return False
    return True


class ComprehensiveDatabaseOptimizer:
    """🏗️ Enterprise Database Optimization Engine"""

    def __init__(self):
        self.start_time = datetime.now()
        self.process_id = os.getpid()
        self.workspace_path = Path("e:/gh_COPILOT")
        self.databases_folder = self.workspace_path / "databases"
        self.max_size_mb = 99.9
        self.max_size_bytes = int(self.max_size_mb * 1024 * 1024)

        # Ensure databases folder exists
        self.databases_folder.mkdir(exist_ok=True)

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler("database_optimization.log"), logging.StreamHandler()],
        )
        self.logger = logging.getLogger(__name__)

        print("=" * 80)
        print("🗄️ COMPREHENSIVE DATABASE OPTIMIZATION SYSTEM INITIALIZED")
        print(f"🚀 Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔧 Process ID: {self.process_id}")
        print(f"📁 Target Folder: {self.databases_folder}")
        print(f"📏 Size Limit: {self.max_size_mb} MB ({self.max_size_bytes:,} bytes)")
        print("=" * 80)

    def discover_all_databases(self) -> List[Dict]:
        """🔍 Discover ALL database files in workspace"""
        databases = []

        # Find all .db files
        for db_file in self.workspace_path.rglob("*.db"):
            if db_file.is_file():
                size = db_file.stat().st_size
                databases.append(
                    {
                        "path": db_file,
                        "name": db_file.name,
                        "size": size,
                        "size_mb": size / (1024 * 1024),
                        "location": "databases_folder" if "databases" in str(db_file.parent) else "root",
                        "exceeds_limit": size > self.max_size_bytes,
                    }
                )

        # Sort by size (largest first)
        databases.sort(key=lambda x: x["size"], reverse=True)

        self.logger.info(f"📊 DISCOVERED {len(databases)} DATABASE FILES")
        return databases

    def analyze_duplicates(self, databases: List[Dict]) -> Dict:
        """🔍 Analyze potential duplicate databases"""
        duplicates = {}
        name_groups = {}

        # Group by name
        for db in databases:
            name = db["name"]
            if name not in name_groups:
                name_groups[name] = []
            name_groups[name].append(db)

        # Find duplicates
        for name, group in name_groups.items():
            if len(group) > 1:
                duplicates[name] = group

        return duplicates

    def calculate_database_hash(self, db_path: Path) -> str:
        """🔐 Calculate database content hash for duplicate detection"""
        try:
            hasher = hashlib.md5()
            with open(db_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            self.logger.error(f"❌ Hash calculation failed for {db_path}: {e}")
            return ""

    def optimize_database(self, db_path: Path) -> Dict:
        """⚡ Optimize single database with VACUUM and compression"""
        optimization_result = {
            "original_size": 0,
            "optimized_size": 0,
            "reduction_bytes": 0,
            "reduction_percent": 0,
            "success": False,
            "error": None,
        }

        try:
            # Get original size
            optimization_result["original_size"] = db_path.stat().st_size

            # Connect and optimize
            with sqlite3.connect(str(db_path)) as conn:
                # Enable WAL mode for better performance
                conn.execute("PRAGMA journal_mode=WAL")

                # Optimize database
                conn.execute("VACUUM")
                conn.execute("PRAGMA optimize")
                conn.execute("PRAGMA shrink_memory")

                # Analyze tables for better query plans
                conn.execute("ANALYZE")

                conn.commit()

            # Get optimized size
            optimization_result["optimized_size"] = db_path.stat().st_size
            optimization_result["reduction_bytes"] = (
                optimization_result["original_size"] - optimization_result["optimized_size"]
            )

            if optimization_result["original_size"] > 0:
                optimization_result["reduction_percent"] = (
                    optimization_result["reduction_bytes"] / optimization_result["original_size"]
                ) * 100

            optimization_result["success"] = True

        except Exception as e:
            optimization_result["error"] = str(e)
            self.logger.error(f"❌ Optimization failed for {db_path}: {e}")

        return optimization_result

    def migrate_database(self, source_path: Path, target_folder: Path) -> bool:
        """📦 Migrate database to target folder"""
        try:
            target_path = target_folder / source_path.name

            # If target exists and is identical, remove source
            if target_path.exists():
                source_hash = self.calculate_database_hash(source_path)
                target_hash = self.calculate_database_hash(target_path)

                if source_hash == target_hash:
                    self.logger.info(f"🔄 Identical database found, removing duplicate: {source_path.name}")
                    source_path.unlink()
                    return True
                else:
                    # Rename to avoid conflict
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    target_path = target_folder / f"{source_path.stem}_{timestamp}.db"

            # Move file
            shutil.move(str(source_path), str(target_path))
            self.logger.info(f"📦 Migrated: {source_path} → {target_path}")
            return True

        except Exception as e:
            self.logger.error(f"❌ Migration failed for {source_path}: {e}")
            return False

    def compress_large_database(self, db_path: Path) -> Dict:
        """🗜️ Compress large database if needed"""
        compression_result = {
            "compressed": False,
            "original_size": 0,
            "final_size": 0,
            "method": "none",
            "success": False,
        }

        try:
            compression_result["original_size"] = db_path.stat().st_size

            if compression_result["original_size"] > self.max_size_bytes:
                # Try aggressive optimization first
                opt_result = self.optimize_database(db_path)

                current_size = db_path.stat().st_size
                compression_result["final_size"] = current_size
                compression_result["method"] = "vacuum_optimize"
                compression_result["compressed"] = True
                compression_result["success"] = True

                if current_size <= self.max_size_bytes:
                    self.logger.info(f"✅ Successfully compressed {db_path.name} to {current_size / 1024 / 1024:.1f}MB")
                else:
                    self.logger.warning(f"⚠️ {db_path.name} still {current_size / 1024 / 1024:.1f}MB after optimization")
            else:
                compression_result["final_size"] = compression_result["original_size"]
                compression_result["success"] = True

        except Exception as e:
            compression_result["error"] = str(e)
            self.logger.error(f"❌ Compression failed for {db_path}: {e}")

        return compression_result

    def execute_comprehensive_optimization(self):
        """🚀 Execute complete database optimization process"""

        # CRITICAL: Anti-recursion validation
        if not validate_no_recursive_folders():
            raise RuntimeError("CRITICAL: Recursive violations prevent execution")

        start_time = time.time()

        with tqdm(total=100, desc="🗄️ Database Optimization", unit="%") as pbar:
            # Phase 1: Discovery (20%)
            pbar.set_description("🔍 Discovering databases")
            databases = self.discover_all_databases()
            pbar.update(20)

            # Phase 2: Analysis (20%)
            pbar.set_description("📊 Analyzing duplicates")
            duplicates = self.analyze_duplicates(databases)
            pbar.update(20)

            # Phase 3: Migration (30%)
            pbar.set_description("📦 Migrating databases")
            migration_results = []
            root_databases = [db for db in databases if db["location"] == "root"]

            for i, db in enumerate(root_databases):
                success = self.migrate_database(db["path"], self.databases_folder)
                migration_results.append({"database": db["name"], "success": success})
                pbar.update(30 / len(root_databases) if root_databases else 30)

            # Phase 4: Optimization (30%)
            pbar.set_description("⚡ Optimizing databases")
            optimization_results = []

            # Re-scan after migration
            current_databases = self.discover_all_databases()
            large_databases = [db for db in current_databases if db["exceeds_limit"]]

            for i, db in enumerate(large_databases):
                result = self.compress_large_database(db["path"])
                optimization_results.append({"database": db["name"], "result": result})
                pbar.update(30 / len(large_databases) if large_databases else 30)

        # Generate comprehensive report
        self.generate_optimization_report(databases, duplicates, migration_results, optimization_results)

        duration = time.time() - start_time
        print("=" * 80)
        print("✅ COMPREHENSIVE DATABASE OPTIMIZATION COMPLETED")
        print(f"⏱️ Duration: {duration:.2f} seconds")
        print(f"📊 Total Databases Processed: {len(databases)}")
        print("=" * 80)

    def generate_optimization_report(self, databases, duplicates, migrations, optimizations):
        """📊 Generate comprehensive optimization report"""

        report = {
            "timestamp": datetime.now().isoformat(),
            "total_databases": len(databases),
            "databases_moved": len([m for m in migrations if m["success"]]),
            "duplicates_found": len(duplicates),
            "optimizations_performed": len(optimizations),
            "size_summary": {
                "before": sum(db["size"] for db in databases),
                "after": 0,  # Will be calculated
            },
            "compliance_status": {"under_limit": 0, "over_limit": 0, "percentage_compliant": 0},
        }

        # Re-scan for final status
        final_databases = self.discover_all_databases()
        report["size_summary"]["after"] = sum(db["size"] for db in final_databases)
        report["compliance_status"]["under_limit"] = len([db for db in final_databases if not db["exceeds_limit"]])
        report["compliance_status"]["over_limit"] = len([db for db in final_databases if db["exceeds_limit"]])
        report["compliance_status"]["percentage_compliant"] = (
            report["compliance_status"]["under_limit"] / len(final_databases)
        ) * 100

        # Save report
        report_path = (
            self.workspace_path / f"database_optimization_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        # Display summary
        print("📊 OPTIMIZATION REPORT SUMMARY:")
        print(f"   Total Databases: {report['total_databases']}")
        print(f"   Databases Moved: {report['databases_moved']}")
        print(f"   Duplicates Found: {report['duplicates_found']}")
        print(
            f"   Size Reduction: {(report['size_summary']['before'] - report['size_summary']['after']) / 1024 / 1024:.1f} MB"
        )
        print(f"   Compliance: {report['compliance_status']['percentage_compliant']:.1f}% under 99.9MB limit")

        if report["compliance_status"]["over_limit"] > 0:
            print(f"⚠️ WARNING: {report['compliance_status']['over_limit']} databases still exceed size limit")
            for db in final_databases:
                if db["exceeds_limit"]:
                    print(f"   - {db['name']}: {db['size_mb']:.1f} MB")


if __name__ == "__main__":
    # MANDATORY: Visual processing indicators
    print("🚀 STARTING COMPREHENSIVE DATABASE OPTIMIZATION")
    print(f"⏰ Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    optimizer = ComprehensiveDatabaseOptimizer()
    optimizer.execute_comprehensive_optimization()

    print("✅ DATABASE OPTIMIZATION SYSTEM COMPLETE")
