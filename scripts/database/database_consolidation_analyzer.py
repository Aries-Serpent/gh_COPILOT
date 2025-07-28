#!/usr/bin/env python3
"""
🗄️ DATABASE CONSOLIDATION ANALYZER
================================================================
Comprehensive analysis tool for database consolidation strategy
- Identifies duplicates, backups, and optimization opportunities
- Analyzes schemas, content, and dependencies
- Generates detailed consolidation recommendations
================================================================
"""

import os
import sqlite3
import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from collections import defaultdict
import re


class DatabaseConsolidationAnalyzer:
    """🔍 Comprehensive Database Analysis Engine"""

    def __init__(self, databases_path: str = "databases"):
        self.databases_path = Path(databases_path)
        self.analysis_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.analysis_results = {
            "timestamp": self.analysis_timestamp,
            "total_databases": 0,
            "total_size_mb": 0,
            "duplicate_candidates": [],
            "backup_candidates": [],
            "consolidation_opportunities": [],
            "schema_analysis": {},
            "size_analysis": {},
            "dependency_matrix": {},
        }

    def get_database_info(self, db_path: Path) -> Dict:
        """📊 Extract comprehensive database information"""
        try:
            size_bytes = db_path.stat().st_size
            size_mb = size_bytes / (1024 * 1024)

            # Basic file info
            info = {
                "name": db_path.name,
                "path": str(db_path),
                "size_bytes": size_bytes,
                "size_mb": round(size_mb, 2),
                "last_modified": datetime.fromtimestamp(db_path.stat().st_mtime).isoformat(),
                "tables": [],
                "table_count": 0,
                "row_count": 0,
                "schema_hash": "",
                "content_hash": "",
                "is_backup": self._is_backup_database(db_path.name),
                "timestamp_pattern": self._extract_timestamp_pattern(db_path.name),
            }

            # Connect and analyze schema
            try:
                with sqlite3.connect(str(db_path)) as conn:
                    cursor = conn.cursor()

                    # Get table names
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    tables = [row[0] for row in cursor.fetchall()]
                    info["tables"] = tables
                    info["table_count"] = len(tables)

                    # Calculate total row count
                    total_rows = 0
                    for table in tables:
                        try:
                            cursor.execute(f"SELECT COUNT(*) FROM `{table}`")
                            total_rows += cursor.fetchone()[0]
                        except sqlite3.Error as e:
                            logging.warning("Failed counting rows for %s: %s", table, e)
                    info["row_count"] = total_rows

                    # Generate schema hash
                    schema_sql = ""
                    for table in tables:
                        try:
                            cursor.execute(f"SELECT sql FROM sqlite_master WHERE name='{table}'")
                            result = cursor.fetchone()
                            if result:
                                schema_sql += result[0] or ""
                        except sqlite3.Error as e:
                            logging.warning("Failed retrieving schema for %s: %s", table, e)

                    info["schema_hash"] = hashlib.md5(schema_sql.encode()).hexdigest()

                    # Simple content hash (first 1000 rows from each table)
                    content_data = ""
                    for table in tables:
                        try:
                            cursor.execute(f"SELECT * FROM `{table}` LIMIT 100")
                            content_data += str(cursor.fetchall())
                        except sqlite3.Error as e:
                            logging.warning("Failed hashing content for %s: %s", table, e)

                    info["content_hash"] = hashlib.md5(content_data.encode()).hexdigest()[:16]

            except sqlite3.Error as e:
                info["error"] = str(e)

        except (OSError, sqlite3.Error) as e:
            logging.error("Failed to gather info for %s: %s", db_path, e)
            info = {"name": db_path.name, "path": str(db_path), "error": str(e), "size_bytes": 0, "size_mb": 0}

        return info

    def _is_backup_database(self, name: str) -> bool:
        """🔍 Identify backup databases"""
        backup_patterns = [
            r"_backup_",
            r"backup\.db$",
            r"_\d{8}_\d{6}\.db$",  # timestamp pattern
            r"_\d{4}\d{2}\d{2}_\d{6}\.db$",
            r"\.backup\.db$",
            r"_old\.db$",
            r"_temp\.db$",
        ]

        for pattern in backup_patterns:
            if re.search(pattern, name, re.IGNORECASE):
                return True
        return False

    def _extract_timestamp_pattern(self, name: str) -> Optional[str]:
        """📅 Extract timestamp patterns from database names"""
        patterns = [r"_(\d{8}_\d{6})\.db$", r"_(\d{4}\d{2}\d{2}_\d{6})\.db$", r"_(\d{4}-\d{2}-\d{2})\.db$"]

        for pattern in patterns:
            match = re.search(pattern, name)
            if match:
                return match.group(1)
        return None

    def analyze_all_databases(self) -> Dict:
        """🔬 Perform comprehensive analysis of all databases"""
        print(f"🔍 Analyzing databases in {self.databases_path}")

        # Get all database files
        db_files = list(self.databases_path.glob("*.db"))
        self.analysis_results["total_databases"] = len(db_files)

        database_info = []
        total_size = 0

        print(f"📊 Processing {len(db_files)} databases...")

        for db_file in db_files:
            print(f"  📋 Analyzing {db_file.name}...")
            info = self.get_database_info(db_file)
            database_info.append(info)
            total_size += info.get("size_mb", 0)

        self.analysis_results["total_size_mb"] = round(total_size, 2)
        self.analysis_results["database_info"] = database_info

        # Perform analysis
        self._analyze_duplicates(database_info)
        self._analyze_backups(database_info)
        self._analyze_consolidation_opportunities(database_info)
        self._analyze_size_distribution(database_info)

        return self.analysis_results

    def _analyze_duplicates(self, database_info: List[Dict]):
        """🔍 Identify potential duplicate databases"""
        schema_groups = defaultdict(list)
        content_groups = defaultdict(list)
        name_groups = defaultdict(list)

        for db in database_info:
            if "error" not in db:
                # Group by schema hash
                schema_hash = db.get("schema_hash", "")
                if schema_hash:
                    schema_groups[schema_hash].append(db)

                # Group by content hash
                content_hash = db.get("content_hash", "")
                if content_hash:
                    content_groups[content_hash].append(db)

                # Group by base name (without timestamps)
                base_name = re.sub(r"_\d{8}_\d{6}", "", db["name"])
                base_name = re.sub(r"_\d{4}\d{2}\d{2}_\d{6}", "", base_name)
                name_groups[base_name].append(db)

        # Find duplicates
        duplicates = []

        # Schema duplicates
        for schema_hash, dbs in schema_groups.items():
            if len(dbs) > 1:
                duplicates.append(
                    {
                        "type": "schema_duplicate",
                        "databases": [db["name"] for db in dbs],
                        "count": len(dbs),
                        "total_size_mb": sum(db["size_mb"] for db in dbs),
                        "recommendation": "Consider merging or keeping only the most recent",
                    }
                )

        # Name pattern duplicates
        for base_name, dbs in name_groups.items():
            if len(dbs) > 1:
                duplicates.append(
                    {
                        "type": "name_pattern_duplicate",
                        "base_name": base_name,
                        "databases": [db["name"] for db in dbs],
                        "count": len(dbs),
                        "total_size_mb": sum(db["size_mb"] for db in dbs),
                        "recommendation": "Keep most recent, archive or merge older versions",
                    }
                )

        self.analysis_results["duplicate_candidates"] = duplicates

    def _analyze_backups(self, database_info: List[Dict]):
        """🗂️ Identify backup and timestamped databases"""
        backups = []

        for db in database_info:
            if db.get("is_backup", False):
                backups.append(
                    {
                        "name": db["name"],
                        "size_mb": db["size_mb"],
                        "timestamp_pattern": db.get("timestamp_pattern"),
                        "last_modified": db.get("last_modified"),
                        "recommendation": "Archive or remove if recent production version exists",
                    }
                )

        self.analysis_results["backup_candidates"] = backups

    def _analyze_consolidation_opportunities(self, database_info: List[Dict]):
        """🎯 Identify consolidation opportunities"""
        opportunities = []

        # Small databases that could be merged
        small_dbs = [db for db in database_info if db.get("size_mb", 0) < 1.0 and not db.get("error")]
        if len(small_dbs) > 5:
            opportunities.append(
                {
                    "type": "small_database_merge",
                    "databases": [db["name"] for db in small_dbs],
                    "count": len(small_dbs),
                    "total_size_mb": sum(db["size_mb"] for db in small_dbs),
                    "recommendation": "Consider merging into a single utilities database",
                }
            )

        # Similar purpose databases (by name patterns)
        purpose_groups = defaultdict(list)
        for db in database_info:
            if not db.get("error"):
                # Group by purpose keywords
                name_lower = db["name"].lower()
                if "log" in name_lower:
                    purpose_groups["logging"].append(db)
                elif "analytics" in name_lower:
                    purpose_groups["analytics"].append(db)
                elif "template" in name_lower:
                    purpose_groups["templates"].append(db)
                elif "quantum" in name_lower:
                    purpose_groups["quantum"].append(db)
                elif "enterprise" in name_lower:
                    purpose_groups["enterprise"].append(db)

        for purpose, dbs in purpose_groups.items():
            if len(dbs) > 2:
                opportunities.append(
                    {
                        "type": "purpose_consolidation",
                        "purpose": purpose,
                        "databases": [db["name"] for db in dbs],
                        "count": len(dbs),
                        "total_size_mb": sum(db["size_mb"] for db in dbs),
                        "recommendation": f"Consider consolidating {purpose} databases",
                    }
                )

        self.analysis_results["consolidation_opportunities"] = opportunities

    def _analyze_size_distribution(self, database_info: List[Dict]):
        """📏 Analyze size distribution and identify large databases"""
        sizes = [db.get("size_mb", 0) for db in database_info if not db.get("error")]

        size_analysis = {
            "total_size_mb": sum(sizes),
            "average_size_mb": round(sum(sizes) / len(sizes) if sizes else 0, 2),
            "largest_database": max(database_info, key=lambda x: x.get("size_mb", 0)),
            "smallest_database": min(database_info, key=lambda x: x.get("size_mb", 0)),
            "size_distribution": {
                "under_1mb": len([s for s in sizes if s < 1]),
                "1mb_to_10mb": len([s for s in sizes if 1 <= s < 10]),
                "10mb_to_50mb": len([s for s in sizes if 10 <= s < 50]),
                "over_50mb": len([s for s in sizes if s >= 50]),
            },
        }

        self.analysis_results["size_analysis"] = size_analysis

    def generate_consolidation_plan(self) -> Dict:
        """📋 Generate detailed consolidation action plan"""
        plan = {
            "timestamp": self.analysis_timestamp,
            "consolidation_actions": [],
            "estimated_reduction": {"databases_removed": 0, "size_saved_mb": 0, "percentage_reduction": 0},
            "risk_assessment": {},
            "implementation_steps": [],
        }

        # Process duplicates
        for duplicate in self.analysis_results["duplicate_candidates"]:
            if duplicate["type"] == "name_pattern_duplicate" and duplicate["count"] > 1:
                databases = duplicate["databases"]
                # Keep the one without timestamp (main) or most recent
                main_db = None
                candidates_for_removal = []

                for db_name in databases:
                    if not re.search(r"_\d{8}_\d{6}", db_name):
                        main_db = db_name
                    else:
                        candidates_for_removal.append(db_name)

                if main_db and candidates_for_removal:
                    for candidate in candidates_for_removal:
                        # Find the database info
                        db_info = next(
                            (db for db in self.analysis_results["database_info"] if db["name"] == candidate), None
                        )

                        if db_info:
                            plan["consolidation_actions"].append(
                                {
                                    "action": "MERGE_AND_REMOVE",
                                    "source": candidate,
                                    "target": main_db,
                                    "reason": f"Timestamped backup of {main_db}",
                                    "size_mb": db_info["size_mb"],
                                    "risk_level": "LOW",
                                    "validation_required": True,
                                }
                            )

                            plan["estimated_reduction"]["databases_removed"] += 1
                            plan["estimated_reduction"]["size_saved_mb"] += db_info["size_mb"]

        # Process backup candidates
        for backup in self.analysis_results["backup_candidates"]:
            # Check if production version exists
            base_name = re.sub(r"_\d{8}_\d{6}", "", backup["name"])
            base_name = re.sub(r"_backup.*", "", base_name)

            production_exists = any(
                db["name"] == base_name + ".db" or db["name"] == base_name
                for db in self.analysis_results["database_info"]
            )

            if production_exists:
                plan["consolidation_actions"].append(
                    {
                        "action": "ARCHIVE_AND_REMOVE",
                        "source": backup["name"],
                        "target": "archives/",
                        "reason": "Backup with production version available",
                        "size_mb": backup["size_mb"],
                        "risk_level": "LOW",
                        "validation_required": False,
                    }
                )

                plan["estimated_reduction"]["databases_removed"] += 1
                plan["estimated_reduction"]["size_saved_mb"] += backup["size_mb"]

        # Calculate reduction percentage
        total_databases = self.analysis_results["total_databases"]
        if total_databases > 0:
            reduction_percentage = (plan["estimated_reduction"]["databases_removed"] / total_databases) * 100
            plan["estimated_reduction"]["percentage_reduction"] = round(reduction_percentage, 1)

        return plan

    def save_analysis_report(self, output_file: Optional[str] = None):
        """💾 Save comprehensive analysis report"""
        if output_file is None:
            output_file = f"database_consolidation_analysis_{self.analysis_timestamp}.json"

        with open(output_file, "w") as f:
            json.dump(self.analysis_results, f, indent=2)

        print(f"📄 Analysis report saved to {output_file}")
        return output_file

    def print_summary(self):
        """📋 Print analysis summary"""
        print("\n" + "=" * 80)
        print("🗄️  DATABASE CONSOLIDATION ANALYSIS SUMMARY")
        print("=" * 80)

        print(f"📊 Total Databases: {self.analysis_results['total_databases']}")
        print(f"💾 Total Size: {self.analysis_results['total_size_mb']:.2f} MB")

        print(f"\n🔍 Duplicate Candidates: {len(self.analysis_results['duplicate_candidates'])}")
        for dup in self.analysis_results["duplicate_candidates"]:
            print(f"  • {dup['type']}: {dup['count']} databases ({dup['total_size_mb']:.2f} MB)")

        print(f"\n🗂️  Backup Candidates: {len(self.analysis_results['backup_candidates'])}")
        backup_size = sum(b["size_mb"] for b in self.analysis_results["backup_candidates"])
        print(f"  • Total backup size: {backup_size:.2f} MB")

        print(f"\n🎯 Consolidation Opportunities: {len(self.analysis_results['consolidation_opportunities'])}")
        for opp in self.analysis_results["consolidation_opportunities"]:
            print(f"  • {opp['type']}: {opp['count']} databases ({opp['total_size_mb']:.2f} MB)")

        size_dist = self.analysis_results["size_analysis"]["size_distribution"]
        print(f"\n📏 Size Distribution:")
        print(f"  • Under 1MB: {size_dist['under_1mb']} databases")
        print(f"  • 1-10MB: {size_dist['1mb_to_10mb']} databases")
        print(f"  • 10-50MB: {size_dist['10mb_to_50mb']} databases")
        print(f"  • Over 50MB: {size_dist['over_50mb']} databases")


def main():
    """🚀 Main execution function"""
    print("🗄️ DATABASE CONSOLIDATION ANALYZER")
    print("=" * 50)

    analyzer = DatabaseConsolidationAnalyzer()

    # Perform analysis
    results = analyzer.analyze_all_databases()

    # Generate consolidation plan
    plan = analyzer.generate_consolidation_plan()

    # Print summary
    analyzer.print_summary()

    # Print consolidation plan summary
    print(f"\n📋 CONSOLIDATION PLAN SUMMARY")
    print(f"  • Actions planned: {len(plan['consolidation_actions'])}")
    print(f"  • Databases to remove: {plan['estimated_reduction']['databases_removed']}")
    print(f"  • Size savings: {plan['estimated_reduction']['size_saved_mb']:.2f} MB")
    print(f"  • Reduction percentage: {plan['estimated_reduction']['percentage_reduction']:.1f}%")

    # Save reports
    analysis_file = analyzer.save_analysis_report()

    plan_file = f"database_consolidation_plan_{analyzer.analysis_timestamp}.json"
    with open(plan_file, "w") as f:
        json.dump(plan, f, indent=2)
    print(f"📄 Consolidation plan saved to {plan_file}")

    return analysis_file, plan_file


if __name__ == "__main__":
    main()
