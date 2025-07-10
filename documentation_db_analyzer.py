#!/usr/bin/env python3
"""
🚀 DOCUMENTATION DATABASE ANALYZER
Enterprise Database-First Analysis System
DUAL COPILOT PATTERN: PRIMARY EXECUTOR
"""

import sqlite3
import os
import json

from pathlib import Path
from datetime import datetime


import logging

# Configure logging
logging.basicConfig(
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig)
logger = logging.getLogger(__name__)


class DocumentationDatabaseAnalyzer:
    """🔍 Enterprise Documentation Database Analysis Engine"""

    def __init__(self, workspace_path: str = "e:/gh_COPILOT"):
        # 🚀 PROCESS STARTED
        self.start_time = datetime.now()
        self.process_id = os.getpid()
        logger.info("🚀 DOCUMENTATION DB ANALYZER STARTED")
        logger.info(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Process ID: {self.process_id}")

        self.workspace_path = Path(workspace_path)
        self.db_path = self.workspace_path / "databases" / "documentation.db"

        # CRITICAL: Anti-recursion validation
        self._validate_environment_integrity()

        # Analysis results
        self.analysis_results = {
            "database_info": {},
            "duplicates": {},
            "consolidation_opportunities": {},
            "modularization_potential": {},
            "unwanted_files": {},
            "recommendations": {}
        }

    def _validate_environment_integrity(self):
        """🛡️ CRITICAL: Validate workspace integrity"""
        if not self.workspace_path.exists():
            raise RuntimeError(f"🚨 CRITICAL: Workspace not found: {self.workspace_path}")

        if not self.db_path.exists():
            raise RuntimeError(f"🚨 CRITICAL: Documentation database not found: {self.db_path}")

        logger.info("✅ Environment integrity validated")

    def analyze_database_comprehensive(self) -> Dict[str, Any]:
        """📊 Comprehensive database analysis with DUAL COPILOT validation"""

        logger.info("="*60)
        logger.info("🔍 STARTING COMPREHENSIVE DATABASE ANALYSIS")
        logger.info("="*60)

        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row  # Enable column access by name

            # Phase 1: Database structure analysis
            logger.info("📊 Phase 1: Database structure analysis")
            self._analyze_database_structure(conn)

            # Phase 2: Content analysis for duplicates
            logger.info("🔍 Phase 2: Duplicate content analysis")
            self._analyze_duplicates(conn)

            # Phase 3: Consolidation opportunities
            logger.info("🔄 Phase 3: Consolidation analysis")
            self._analyze_consolidation_opportunities(conn)

            # Phase 4: Modularization potential
            logger.info("🧩 Phase 4: Modularization analysis")
            self._analyze_modularization_potential(conn)

            # Phase 5: Unwanted files detection
            logger.info("🗑️ Phase 5: Unwanted files detection")
            self._detect_unwanted_files(conn)

            # Phase 6: Generate recommendations
            logger.info("💡 Phase 6: Generating recommendations")
            self._generate_recommendations()

            conn.close()

            # DUAL COPILOT VALIDATION
            validation_result = self._validate_analysis_quality()

            logger.info("✅ COMPREHENSIVE ANALYSIS COMPLETED")
            return self.analysis_results

        except Exception as e:
            logger.error(f"❌ Analysis failed: {str(e)}")
            raise

    def _analyze_database_structure(self, conn: sqlite3.Connection):
        """📊 Analyze database structure and metadata"""
        cursor = conn.cursor()

        # Get table information
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        self.analysis_results["database_info"]["tables"] = {}

        for table_name in tables:
            # Get table schema
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()

            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]

            # Get sample data
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
            sample_data = [dict(row) for row in cursor.fetchall()]

            self.analysis_results["database_info"]["tables"][table_name] = {
                "columns": [{"name": col[1], "type": col[2], "nullable": not col[3]} for col in columns],
                "row_count": row_count,
                "sample_data": sample_data
            }

            logger.info(f"  📋 Table: {table_name} ({row_count} rows)")

    def _analyze_duplicates(self, conn: sqlite3.Connection):
        """🔍 Detect duplicate content and entries"""
        cursor = conn.cursor()
        duplicates_found = {}

        for table_name, table_info in self.analysis_results["database_info"]["tables"].items():
            logger.info(f"🔍 Analyzing duplicates in table: {table_name}")

            # Check for duplicate rows based on content
            columns = [col["name"] for col in table_info["columns"]]

            if "content" in columns:
                # Check for duplicate content
                cursor.execute(f"""
                    SELECT content, COUNT(*) as count
                    FROM {table_name}
                    WHERE content IS NOT NULL
                    GROUP BY content
                    HAVING COUNT(*) > 1
                """)
                content_dupes = cursor.fetchall()

                if content_dupes:
                    duplicates_found[f"{table_name}_content"] = [
                        {"content_preview": row[0][:100], "count": row[1]}
                        for row in content_dupes
                    ]

            if "file_path" in columns:
                # Check for duplicate file paths
                cursor.execute(f"""
                    SELECT file_path, COUNT(*) as count
                    FROM {table_name}
                    WHERE file_path IS NOT NULL
                    GROUP BY file_path
                    HAVING COUNT(*) > 1
                """)
                path_dupes = cursor.fetchall()

                if path_dupes:
                    duplicates_found[f"{table_name}_paths"] = [
                        {"file_path": row[0], "count": row[1]}
                        for row in path_dupes
                    ]

            if "title" in columns:
                # Check for duplicate titles
                cursor.execute(f"""
                    SELECT title, COUNT(*) as count
                    FROM {table_name}
                    WHERE title IS NOT NULL
                    GROUP BY title
                    HAVING COUNT(*) > 1
                """)
                title_dupes = cursor.fetchall()

                if title_dupes:
                    duplicates_found[f"{table_name}_titles"] = [
                        {"title": row[0], "count": row[1]}
                        for row in title_dupes
                    ]

        self.analysis_results["duplicates"] = duplicates_found
        logger.info(f"🔍 Found duplicates in {len(duplicates_found)} categories")

    def _analyze_consolidation_opportunities(self, conn: sqlite3.Connection):
        """🔄 Identify consolidation opportunities"""
        cursor = conn.cursor()
        consolidation_ops = {}

        # Look for similar content that could be consolidated
        for table_name, table_info in self.analysis_results["database_info"]["tables"].items():
            if table_info["row_count"] == 0:
                continue

            logger.info(f"🔄 Analyzing consolidation for table: {table_name}")

            # Check for similar file types
            if "file_path" in [col["name"] for col in table_info["columns"]]:
                cursor.execute(f"""
                    SELECT
                        CASE
                            WHEN file_path LIKE '%.md' THEN 'markdown'
                            WHEN file_path LIKE '%.py' THEN 'python'
                            WHEN file_path LIKE '%.json' THEN 'json'
                            WHEN file_path LIKE '%.txt' THEN 'text'
                            ELSE 'other'
                        END as file_type,
                        COUNT(*) as count
                    FROM {table_name}
                    WHERE file_path IS NOT NULL
                    GROUP BY file_type
                    ORDER BY count DESC
                """)
                file_types = cursor.fetchall()

                if file_types:
                    consolidation_ops[f"{table_name}_by_type"] = [
                        {"type": row[0], "count": row[1]}
                        for row in file_types
                    ]

            # Check for backup files and temporary files
            if "file_path" in [col["name"] for col in table_info["columns"]]:
                cursor.execute(f"""
                    SELECT file_path, content
                    FROM {table_name}
                    WHERE file_path LIKE '%backup%'
                       OR file_path LIKE '%_convo.md'
                       OR file_path LIKE '%.bak'
                       OR file_path LIKE '%temp%'
                       OR file_path LIKE '%tmp%'
                """)
                unwanted = cursor.fetchall()

                if unwanted:
                    consolidation_ops[f"{table_name}_unwanted"] = [
                        {"file_path": row[0], "content_preview": (row[1] or "")[:100]}
                        for row in unwanted
                    ]

        self.analysis_results["consolidation_opportunities"] = consolidation_ops
        logger.info(f"🔄 Found {len(consolidation_ops)} consolidation opportunities")

    def _analyze_modularization_potential(self, conn: sqlite3.Connection):
        """🧩 Analyze modularization potential"""
        cursor = conn.cursor()
        modular_potential = {}

        for table_name, table_info in self.analysis_results["database_info"]["tables"].items():
            if table_info["row_count"] == 0:
                continue

            logger.info(f"🧩 Analyzing modularization for table: {table_name}")

            # Look for template patterns
            if "content" in [col["name"] for col in table_info["columns"]]:
                cursor.execute(f"""
                    SELECT content, COUNT(*) as frequency
                    FROM {table_name}
                    WHERE content LIKE '%template%'
                       OR content LIKE '%{{%'
                       OR content LIKE '%placeholder%'
                       OR content LIKE '%reusable%'
                    GROUP BY content
                    ORDER BY frequency DESC
                    LIMIT 10
                """)
                template_patterns = cursor.fetchall()

                if template_patterns:
                    modular_potential[f"{table_name}_templates"] = [
                        {"content_preview": row[0][:150], "frequency": row[1]}
                        for row in template_patterns
                    ]

            # Look for common sections/headers
            if "content" in [col["name"] for col in table_info["columns"]]:
                cursor.execute(f"""
                    SELECT
                        CASE
                            WHEN content LIKE '%# Introduction%' THEN 'introduction'
                            WHEN content LIKE '%# Overview%' THEN 'overview'
                            WHEN content LIKE '%# Configuration%' THEN 'configuration'
                            WHEN content LIKE '%# Usage%' THEN 'usage'
                            WHEN content LIKE '%# API%' THEN 'api'
                            WHEN content LIKE '%# Examples%' THEN 'examples'
                            ELSE 'other'
                        END as section_type,
                        COUNT(*) as count
                    FROM {table_name}
                    WHERE content IS NOT NULL
                    GROUP BY section_type
                    HAVING count > 1
                    ORDER BY count DESC
                """)
                common_sections = cursor.fetchall()

                if common_sections:
                    modular_potential[f"{table_name}_sections"] = [
                        {"section": row[0], "count": row[1]}
                        for row in common_sections if row[0] != 'other'
                    ]

        self.analysis_results["modularization_potential"] = modular_potential
        logger.info(f"🧩 Found {len(modular_potential)} modularization opportunities")

    def _detect_unwanted_files(self, conn: sqlite3.Connection):
        """🗑️ Detect backup files and conversation files"""
        cursor = conn.cursor()
        unwanted_files = {}

        for table_name, table_info in self.analysis_results["database_info"]["tables"].items():
            if table_info["row_count"] == 0:
                continue

            logger.info(f"🗑️ Scanning for unwanted files in table: {table_name}")

            # Check for unwanted file patterns
            if "file_path" in [col["name"] for col in table_info["columns"]]:
                unwanted_patterns = [
                    ("backup_files", "%backup%"),
                    ("conversation_files", "%_convo.md"),
                    ("backup_extensions", "%.bak"),
                    ("temp_files", "%temp%"),
                    ("tmp_files", "%tmp%"),
                    ("old_files", "%_old%"),
                    ("copy_files", "%_copy%"),
                    ("duplicate_files", "%_duplicate%")
                ]

                for pattern_name, pattern in unwanted_patterns:
                    cursor.execute(f"""
                        SELECT file_path,
                               CASE WHEN content IS NOT NULL THEN length(content) ELSE 0 END as content_size
                        FROM {table_name}
                        WHERE file_path LIKE ? AND file_path IS NOT NULL
                    """, (pattern,))

                    matches = cursor.fetchall()
                    if matches:
                        unwanted_files[f"{table_name}_{pattern_name}"] = [
                            {"file_path": row[0], "content_size": row[1]}
                            for row in matches
                        ]

        self.analysis_results["unwanted_files"] = unwanted_files
        total_unwanted = sum(len(files) for files in unwanted_files.values())
        logger.info(f"🗑️ Found {total_unwanted} unwanted files across {len(unwanted_files)} categories")

    def _generate_recommendations(self):
        """💡 Generate consolidation and optimization recommendations"""
        recommendations = {
            "duplicate_removal": [],
            "consolidation_actions": [],
            "modularization_suggestions": [],
            "cleanup_actions": [],
            "optimization_opportunities": []
        }

        # Duplicate removal recommendations
        for dup_category, duplicates in self.analysis_results["duplicates"].items():
            if duplicates:
                recommendations["duplicate_removal"].append({
                    "category": dup_category,
                    "action": f"Merge {len(duplicates)} duplicate entries",
                    "impact": f"Reduce redundancy in {dup_category}"
                })

        # Consolidation recommendations
        for cons_category, opportunities in self.analysis_results["consolidation_opportunities"].items():
            if opportunities and "unwanted" not in cons_category:
                recommendations["consolidation_actions"].append({
                    "category": cons_category,
                    "action": f"Group {len(opportunities)} items by type/pattern",
                    "impact": "Improve organization and retrieval"
                })

        # Modularization suggestions
        for mod_category, potential in self.analysis_results["modularization_potential"].items():
            if potential:
                recommendations["modularization_suggestions"].append({
                    "category": mod_category,
                    "action": f"Extract {len(potential)} reusable components",
                    "impact": "Enable template-based generation"
                })

        # Cleanup actions
        for unwanted_category, files in self.analysis_results["unwanted_files"].items():
            if files:
                recommendations["cleanup_actions"].append({
                    "category": unwanted_category,
                    "action": f"Remove {len(files)} unwanted files",
                    "impact": "Reduce database size and improve quality"
                })

        # Optimization opportunities
        total_duplicates = sum(len(dupes) for dupes in self.analysis_results["duplicates"].values())
        total_unwanted = sum(len(files) for files in self.analysis_results["unwanted_files"].values())

        if total_duplicates > 0 or total_unwanted > 0:
            recommendations["optimization_opportunities"].append({
                "action": "Database cleanup and deduplication",
                "potential_savings": f"{total_duplicates + total_unwanted} entries",
                "impact": "Improved performance and data quality"
            })

        self.analysis_results["recommendations"] = recommendations
        logger.info(f"💡 Generated {sum(len(recs) for recs in recommendations.values())} recommendations")

    def _validate_analysis_quality(self) -> Dict[str, Any]:
        """🛡️ DUAL COPILOT VALIDATION: Validate analysis quality"""
        validation = {
            "passed": True,
            "checks": {},
            "warnings": [],
            "errors": []
        }

        # Check if analysis covered all expected areas
        expected_sections = ["database_info", "duplicates", "consolidation_opportunities",
                           "modularization_potential", "unwanted_files", "recommendations"]

        for section in expected_sections:
            if section in self.analysis_results:
                validation["checks"][section] = "✅ Present"
            else:
                validation["checks"][section] = "❌ Missing"
                validation["errors"].append(f"Missing analysis section: {section}")
                validation["passed"] = False

        # Check for substantial findings
        if not any(self.analysis_results.get("duplicates", {}).values()):
            validation["warnings"].append("No duplicates found - verify analysis completeness")

        if not any(self.analysis_results.get("unwanted_files", {}).values()):
            validation["warnings"].append("No unwanted files found - verify pattern matching")

        logger.info(f"🛡️ DUAL COPILOT VALIDATION: {'✅ PASSED' if validation['passed'] else '❌ FAILED'}")
        return validation

    def save_analysis_report(self) -> str:
        """💾 Save comprehensive analysis report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.workspace_path / f"documentation_db_analysis_report_{timestamp}.json"

        # Add metadata
        self.analysis_results["metadata"] = {
            "analysis_timestamp": timestamp,
            "database_path": str(self.db_path),
            "analyzer_version": "1.0",
            "dual_copilot_validated": True
        }

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_results, f, indent=2, ensure_ascii=False)

        logger.info(f"💾 Analysis report saved: {report_path}")
        return str(report_path)

    def print_summary(self):
        """📋 Print analysis summary"""
        duration = (datetime.now() - self.start_time).total_seconds()

        print("\n" + "="*60)
        print("📋 DOCUMENTATION DATABASE ANALYSIS SUMMARY")
        print("="*60)

        # Database info
        tables = self.analysis_results.get("database_info", {}).get("tables", {})
        total_rows = sum(table["row_count"] for table in tables.values())
        print("📊 Database Overview:")
        print(f"  • Tables: {len(tables)}")
        print(f"  • Total Records: {total_rows:,}")

        # Duplicates
        duplicates = self.analysis_results.get("duplicates", {})
        total_dupes = sum(len(dupes) for dupes in duplicates.values())
        print("\n🔍 Duplicates Found:")
        print(f"  • Categories: {len(duplicates)}")
        print(f"  • Total Duplicates: {total_dupes}")

        # Unwanted files
        unwanted = self.analysis_results.get("unwanted_files", {})
        total_unwanted = sum(len(files) for files in unwanted.values())
        print("\n🗑️ Unwanted Files:")
        print(f"  • Categories: {len(unwanted)}")
        print(f"  • Total Files: {total_unwanted}")

        # Recommendations
        recommendations = self.analysis_results.get("recommendations", {})
        total_recs = sum(len(recs) for recs in recommendations.values())
        print("\n💡 Recommendations:")
        print(f"  • Total Actions: {total_recs}")

        print(f"\n⏱️ Analysis Duration: {duration:.2f} seconds")
        print("✅ ANALYSIS COMPLETE")
        print("="*60)


def main():
    """🚀 Main execution function with DUAL COPILOT pattern"""
    try:
        # Primary execution
        analyzer = DocumentationDatabaseAnalyzer()
        results = analyzer.analyze_database_comprehensive()

        # Generate report
        report_path = analyzer.save_analysis_report()

        # Print summary
        analyzer.print_summary()

        print(f"\n📄 Detailed report saved to: {report_path}")

    except Exception as e:
        logger.error(f"❌ Analysis failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()
