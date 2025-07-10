#!/usr/bin/env python3
"""
🎯 AGGRESSIVE DOCUMENTATION DATABASE COMPRESSOR
===============================================
Targeted compression to achieve 99MB documentation.db size
Using advanced compression techniques and content optimization.

MANDATORY: Apply visual processing indicators
"""

import sqlite3

import sys
import json
import re


from datetime import datetime
from pathlib import Path

from tqdm import tqdm


class AggressiveDocumentationCompressor:
    """🗜️ Aggressive Database Compression Engine"""

    def __init__(self, workspace_path: str = "e:/gh_COPILOT"):
        # MANDATORY: Start time logging
        self.start_time = datetime.now()
        print(f"🚀 AGGRESSIVE COMPRESSOR STARTED: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)

        self.workspace_path = Path(workspace_path)
        self.db_path = self.workspace_path / "databases" / "documentation.db"
        self.target_size_mb = 99

    def analyze_current_state(self) -> Dict[str, Any]:
        """📊 Analyze current database state"""
        print("📊 ANALYZING CURRENT DATABASE STATE...")

        current_size = self.db_path.stat().st_size
        current_size_mb = current_size / (1024 * 1024)
        reduction_needed = current_size_mb - self.target_size_mb

        analysis = {
            "current_size_mb": current_size_mb,
            "target_size_mb": self.target_size_mb,
            "reduction_needed_mb": reduction_needed,
            "reduction_needed_percent": (reduction_needed / current_size_mb) * 100,
            "table_sizes": {}
        }

        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()

            # Analyze table sizes
            tables = ['enterprise_documentation', 'documentation_relationships',
                     'documentation_analytics', 'documentation_templates']

            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                row_count = cursor.fetchone()[0]

                if table == 'enterprise_documentation':
                    cursor.execute("SELECT SUM(LENGTH(content)) FROM enterprise_documentation")
                    content_size = cursor.fetchone()[0] or 0
                    analysis["table_sizes"][table] = {
                        "rows": row_count,
                        "content_size_bytes": content_size
                    }
                else:
                    analysis["table_sizes"][table] = {"rows": row_count}

        print(f"📦 Current size: {current_size_mb:.2f} MB")
        print(f"🎯 Target size: {self.target_size_mb} MB")
        print(f"📉 Reduction needed: {reduction_needed:.2f} MB ({analysis['reduction_needed_percent']:.1f}%)")

        return analysis

    def aggressive_content_compression(self) -> Dict[str, int]:
        """🗜️ Apply aggressive content compression"""
        print("\n🗜️ APPLYING AGGRESSIVE CONTENT COMPRESSION...")

        compression_stats = {
            "docs_processed": 0,
            "bytes_saved": 0,
            "compressed_content_count": 0,
            "whitespace_optimized": 0
        }

        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()

            # Get all documents with large content
            cursor.execute("""
                SELECT doc_id, content, LENGTH(content) as size
                FROM enterprise_documentation
                WHERE LENGTH(content) > 5000
                ORDER BY LENGTH(content) DESC
            """)
            documents = cursor.fetchall()

            with tqdm(
                      total=len(documents),
                      desc="🗜️ Compressing Content",
                      unit="docs") as pbar
            with tqdm(total=len(d)
                for doc_id, content, original_size in documents:
                    # Apply multiple compression techniques
                    compressed_content = self._ultra_compress_content(content)
                    new_size = len(compressed_content)

                    if new_size < original_size:
                        cursor.execute("""
                            UPDATE enterprise_documentation
                            SET content = ?
                            WHERE doc_id = ?
                        """, (compressed_content, doc_id))

                        compression_stats["bytes_saved"] += (original_size - new_size)
                        compression_stats["compressed_content_count"] += 1

                    compression_stats["docs_processed"] += 1
                    pbar.update(1)

            conn.commit()

        print("✅ CONTENT COMPRESSION COMPLETE:")
        print(f"   📄 Documents processed: {compression_stats['docs_processed']}")
        print(f"   🗜️ Content compressed: {compression_stats['compressed_content_count']}")
        print(f"   💾 Bytes saved: {compression_stats['bytes_saved']:,}")

        return compression_stats

    def _ultra_compress_content(self, content: str) -> str:
        """Apply ultra-aggressive content compression"""
        if not content:
            return content

        # 1. Remove excessive whitespace and empty lines
        lines = content.split('\n')
        optimized_lines = []

        prev_empty = False
        for line in lines:
            # Strip trailing whitespace
            line = line.rstrip()

            # Skip excessive empty lines
            if line.strip() == '':
                if not prev_empty:
                    optimized_lines.append('')
                prev_empty = True
                continue
            else:
                prev_empty = False

            # Compress multiple spaces (except in code blocks)
            if not line.strip().startswith('```') and not line.startswith('    '):
                # Replace multiple spaces with single space
                line = re.sub(r' +', ' ', line)
                # Remove spaces around certain punctuation
                line = re.sub(r' *([,.:;!?]) *', r'\1 ', line)
                line = re.sub(r' +', ' ', line)  # Clean up again

            optimized_lines.append(line)

        # 2. Remove trailing empty lines
        while optimized_lines and optimized_lines[-1].strip() == '':
            optimized_lines.pop()

        # 3. Compress markdown patterns
        result = '\n'.join(optimized_lines)

        # Compress repeated patterns
        result = re.sub(r'\n\n\n+', '\n\n', result)  # Max 2 consecutive newlines
        result = re.sub(
                        r'=+',
                        lambda m: '=' * min(len(m.group()),
                        50),
                        result)  # Limit header underlinin
        result = re.sub(r'=+', )
        result = re.sub(
                        r'-+',
                        lambda m: '-' * min(len(m.group()),
                        50),
                        result)  # Limit dashe
        result = re.sub(r'-+', )

        # 4. Compress JSON content if present
        if '{' in result and '}' in result:
            try:
                # Find and compress JSON blocks
                json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
                def compress_json_match(match):
                    try:
                        json_str = match.group(0)
                        parsed = json.loads(json_str)
                        return json.dumps(parsed, separators=(',', ':'))  # Compact JSON
                    except:
                        return match.group(0)

                result = re.sub(json_pattern, compress_json_match, result)
            except:
                pass

        return result

    def remove_redundant_data(self) -> Dict[str, int]:
        """🗑️ Remove redundant and unnecessary data"""
        print("\n🗑️ REMOVING REDUNDANT DATA...")

        removal_stats = {
            "duplicate_analytics_removed": 0,
            "orphaned_relationships_removed": 0,
            "empty_templates_removed": 0,
            "obsolete_records_removed": 0
        }

        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()

            with tqdm(total=100, desc="🗑️ Data Cleanup", unit="%") as pbar:
                # Remove duplicate analytics entries
                pbar.set_description("📊 Removing duplicate analytics")
                cursor.execute("""
                    DELETE FROM documentation_analytics
                    WHERE analytics_id NOT IN (
                        SELECT MIN(analytics_id)
                        FROM documentation_analytics
                        GROUP BY doc_id
                    )
                """)
                removal_stats["duplicate_analytics_removed"] = cursor.rowcount
                pbar.update(25)

                # Remove orphaned relationships
                pbar.set_description("🔗 Removing orphaned relationships")
                cursor.execute("""
                    DELETE FROM documentation_relationships
                    WHERE parent_doc_id NOT IN (SELECT doc_id FROM enterprise_documentation)
                    OR child_doc_id NOT IN (SELECT doc_id FROM enterprise_documentation)
                """)
                removal_stats["orphaned_relationships_removed"] = cursor.rowcount
                pbar.update(25)

                # Remove empty or minimal templates
                pbar.set_description("📝 Removing minimal templates")
                cursor.execute("""
                    DELETE FROM documentation_templates
                    WHERE LENGTH(template_content) < 100
                """)
                removal_stats["empty_templates_removed"] = cursor.rowcount
                pbar.update(25)

                # Remove obsolete analytics entries (zero access count and old)
                pbar.set_description("📈 Removing obsolete analytics")
                cursor.execute("""
                    DELETE FROM documentation_analytics
                    WHERE access_count = 0
                    AND (
                         last_accessed IS NULL OR last_accessed < datetime('now',
                         '-30 days')
                    AND (last_accessed IS NU)
                """)
                removal_stats["obsolete_records_removed"] = cursor.rowcount
                pbar.update(25)

            conn.commit()

        print("✅ REDUNDANT DATA REMOVAL COMPLETE:")
        print(f"   📊 Duplicate analytics removed: {removal_stats['duplicate_analytics_removed']}")
        print(f"   🔗 Orphaned relationships removed: {removal_stats['orphaned_relationships_removed']}")
        print(f"   📝 Empty templates removed: {removal_stats['empty_templates_removed']}")
        print(f"   📈 Obsolete records removed: {removal_stats['obsolete_records_removed']}")

        return removal_stats

    def optimize_database_structure(self) -> Dict[str, Any]:
        """🏗️ Optimize database structure for maximum compression"""
        print("\n🏗️ OPTIMIZING DATABASE STRUCTURE...")

        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()

            with tqdm(total=100, desc="🏗️ Structure Optimization", unit="%") as pbar:
                # Drop unnecessary indexes
                pbar.set_description("🗂️ Optimizing indexes")
                cursor.execute("DROP INDEX IF EXISTS idx_doc_title")
                pbar.update(20)

                # Analyze and optimize
                pbar.set_description("📊 Analyzing database")
                cursor.execute("ANALYZE")
                pbar.update(20)

                # Vacuum with aggressive settings
                pbar.set_description("🗜️ Aggressive vacuum")
                cursor.execute("PRAGMA auto_vacuum = FULL")
                cursor.execute("VACUUM")
                pbar.update(30)

                # Recreate only essential indexes
                pbar.set_description("🔧 Recreating essential indexes")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_doc_type ON enterprise_documentation(doc_type)")
                pbar.update(15)

                # Optimize database settings
                pbar.set_description("⚙️ Optimizing settings")
                cursor.execute("PRAGMA optimize")
                pbar.update(15)

            conn.commit()

        return {"structure_optimized": True}

    def final_compression_pass(self) -> Dict[str, Any]:
        """🎯 Final compression pass to reach target"""
        print("\n🎯 FINAL COMPRESSION PASS...")

        current_size = self.db_path.stat().st_size
        current_size_mb = current_size / (1024 * 1024)

        if current_size_mb <= self.target_size_mb:
            print(f"✅ TARGET ACHIEVED: {current_size_mb:.2f} MB")
            return {"target_achieved": True, "final_size_mb": current_size_mb}

        # If still over target, apply more aggressive measures
        reduction_needed = current_size_mb - self.target_size_mb
        print(f"🎯 Still need to reduce: {reduction_needed:.2f} MB")

        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()

            # Remove lower priority content if necessary
            if reduction_needed > 2:  # If we need to reduce more than 2MB
                print("🗑️ Removing lower priority content...")

                # Remove documents with very large content (>50KB) if low priority
                cursor.execute("""
                    DELETE FROM enterprise_documentation
                    WHERE LENGTH(content) > 50000
                    AND (priority IS NULL OR priority > 3)
                    AND doc_type IN ('LOG', 'BACKUP_LOG')
                """)
                removed_large = cursor.rowcount
                print(f"   📄 Removed {removed_large} large low-priority documents")

                # Clean up orphaned analytics and relationships
                cursor.execute("""
                    DELETE FROM documentation_analytics
                    WHERE doc_id NOT IN (SELECT doc_id FROM enterprise_documentation)
                """)
                cursor.execute("""
                    DELETE FROM documentation_relationships
                    WHERE parent_doc_id NOT IN (SELECT doc_id FROM enterprise_documentation)
                    OR child_doc_id NOT IN (SELECT doc_id FROM enterprise_documentation)
                """)

                conn.commit()
                cursor.execute("VACUUM")

        final_size = self.db_path.stat().st_size
        final_size_mb = final_size / (1024 * 1024)

        return {
            "target_achieved": final_size_mb <= self.target_size_mb,
            "final_size_mb": final_size_mb,
            "reduction_achieved_mb": current_size_mb - final_size_mb
        }

    def execute_aggressive_compression(self) -> Dict[str, Any]:
        """🚀 Execute complete aggressive compression"""
        print("\n" + "="*80)
        print("🎯 STARTING AGGRESSIVE DATABASE COMPRESSION")
        print("🛡️ Target: 99MB | Visual Processing: ACTIVE")
        print("="*80)

        results = {
            "timestamp": datetime.now().isoformat(),
            "original_size_mb": self.db_path.stat().st_size / (1024 * 1024),
            "target_size_mb": self.target_size_mb,
            "phases": {}
        }

        phases = [
            ("📊 Analysis", self.analyze_current_state),
            ("🗜️ Content Compression", self.aggressive_content_compression),
            ("🗑️ Redundant Data Removal", self.remove_redundant_data),
            ("🏗️ Structure Optimization", self.optimize_database_structure),
            ("🎯 Final Compression", self.final_compression_pass)
        ]

        for phase_name, phase_function in phases:
            print(f"\n🎯 EXECUTING: {phase_name}")
            try:
                result = phase_function()
                results["phases"][phase_name] = result
                print(f"✅ {phase_name} COMPLETED")
            except Exception as e:
                print(f"❌ {phase_name} ERROR: {e}")
                results["phases"][phase_name] = {"error": str(e)}

        # Final validation
        final_size = self.db_path.stat().st_size
        final_size_mb = final_size / (1024 * 1024)
        reduction_mb = results["original_size_mb"] - final_size_mb
        reduction_percent = (reduction_mb / results["original_size_mb"]) * 100

        results.update({
            "final_size_mb": final_size_mb,
            "reduction_mb": reduction_mb,
            "reduction_percent": reduction_percent,
            "target_achieved": final_size_mb <= self.target_size_mb
        })

        # Generate report
        report_path = self.workspace_path / f"aggressive_compression_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        # Summary
        duration = (datetime.now() - self.start_time).total_seconds()
        print("\n" + "="*80)
        print("✅ AGGRESSIVE COMPRESSION COMPLETE")
        print("="*80)
        print(f"📦 Original size: {results['original_size_mb']:.2f} MB")
        print(f"📦 Final size: {final_size_mb:.2f} MB")
        print(f"📉 Reduction: {reduction_mb:.2f} MB ({reduction_percent:.1f}%)")
        print(f"🎯 Target achieved: {'YES' if results['target_achieved'] else 'NO'}")
        print(f"⏱️ Duration: {duration:.1f} seconds")
        print(f"📄 Report: {report_path}")
        print("="*80)

        return results


def main():
    """Main execution with enterprise compliance"""
    print("🎯 AGGRESSIVE DOCUMENTATION DATABASE COMPRESSOR")
    print("🛡️ DUAL COPILOT [SUCCESS] | Target: 99MB")

    try:
        compressor = AggressiveDocumentationCompressor()
        results = compressor.execute_aggressive_compression()

        if results["target_achieved"]:
            print("\n🏆 COMPRESSION TARGET ACHIEVED!")
            print("📊 Documentation database successfully compressed to ~99MB")
        else:
            print(f"\n📊 COMPRESSION PROGRESS: {results['final_size_mb']:.2f} MB")
            print("🎯 Close to target - additional optimization may be needed")

    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
