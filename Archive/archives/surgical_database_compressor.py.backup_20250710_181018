#!/usr/bin/env python3
"""
🎯 SURGICAL DATABASE COMPRESSION FOR 99MB TARGET
==============================================
Targeted compression focusing on LOG entries and large content
to achieve exactly 99MB documentation.db size.
"""

import sqlite3

import json
import re
from datetime import datetime
from pathlib import Path
from tqdm import tqdm


class SurgicalDatabaseCompressor:
    """🔬 Surgical precision compression for 99MB target"""

    def __init__(self, workspace_path: str = "e:/gh_COPILOT"):
        self.start_time = datetime.now()
        print(f"🔬 SURGICAL COMPRESSOR STARTED: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)

        self.workspace_path = Path(workspace_path)
        self.db_path = self.workspace_path / "databases" / "documentation.db"
        self.target_size_bytes = 99 * 1024 * 1024  # 99MB exactly

    def analyze_space_usage(self) -> dict:
        """🔍 Analyze exactly where space is being used"""
        print("🔍 ANALYZING SPACE USAGE BY CATEGORY...")

        analysis = {}

        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()

            # Detailed analysis of LOG entries
            cursor.execute("""
                SELECT
                    title,
                    LENGTH(content) as size,
                    content
                FROM enterprise_documentation
                WHERE doc_type = 'LOG'
                ORDER BY LENGTH(content) DESC
                LIMIT 10
            """)
            large_logs = cursor.fetchall()

            analysis["large_logs"] = []
            for title, size, content in large_logs:
                # Check if it's repetitive content
                unique_lines = len(set(content.split('\n')))
                total_lines = len(content.split('\n'))
                repetition_ratio = 1 - (unique_lines / total_lines) if total_lines > 0 else 0

                analysis["large_logs"].append({
                    "title": title,
                    "size_kb": size / 1024,
                    "total_lines": total_lines,
                    "unique_lines": unique_lines,
                    "repetition_ratio": repetition_ratio,
                    "compressible": repetition_ratio > 0.5 or size > 100000
                })

        current_size = self.db_path.stat().st_size
        target_reduction = current_size - self.target_size_bytes

        analysis.update({
            "current_size_mb": current_size / (1024 * 1024),
            "target_size_mb": 99,
            "reduction_needed_bytes": target_reduction,
            "reduction_needed_mb": target_reduction / (1024 * 1024)
        })

        print(f"📊 Current size: {analysis['current_size_mb']:.2f} MB")
        print(f"🎯 Reduction needed: {analysis['reduction_needed_mb']:.2f} MB")
        print(f"📄 Large logs found: {len(analysis['large_logs'])}")

        return analysis

    def compress_log_entries(self, target_reduction_bytes: int) -> dict:
        """🗜️ Surgically compress LOG entries to save specific amount"""
        print(f"\n🗜️ COMPRESSING LOG ENTRIES (Target: {target_reduction_bytes/1024/1024:.1f}MB reduction)...")

        bytes_saved = 0
        logs_compressed = 0

        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()

            # Get LOG entries ordered by size
            cursor.execute("""
                SELECT doc_id, title, content, LENGTH(content) as size
                FROM enterprise_documentation
                WHERE doc_type = 'LOG' AND LENGTH(content) > 10000
                ORDER BY LENGTH(content) DESC
            """)
            large_logs = cursor.fetchall()

            with tqdm(
                      total=len(large_logs),
                      desc="🗜️ Compressing Logs",
                      unit="logs") as pbar
            with tqdm(total=len(l)
                for doc_id, title, content, original_size in large_logs:
                    if bytes_saved >= target_reduction_bytes:
                        break

                    # Apply aggressive log compression
                    compressed_content = self._compress_log_content(content)
                    new_size = len(compressed_content)
                    size_reduction = original_size - new_size

                    if size_reduction > 1000:  # Only update if significant reduction
                        cursor.execute("""
                            UPDATE enterprise_documentation
                            SET content = ?
                            WHERE doc_id = ?
                        """, (compressed_content, doc_id))

                        bytes_saved += size_reduction
                        logs_compressed += 1

                    pbar.update(1)
                    pbar.set_postfix({"Saved": f"{bytes_saved/1024/1024:.1f}MB"})

            conn.commit()

        result = {
            "logs_compressed": logs_compressed,
            "bytes_saved": bytes_saved,
            "mb_saved": bytes_saved / (1024 * 1024),
            "target_achieved": bytes_saved >= target_reduction_bytes * 0.8
        }

        print("✅ LOG COMPRESSION COMPLETE:")
        print(f"   📄 Logs compressed: {result['logs_compressed']}")
        print(f"   💾 Bytes saved: {result['bytes_saved']:,} ({result['mb_saved']:.2f} MB)")

        return result

    def _compress_log_content(self, content: str) -> str:
        """Apply ultra-aggressive compression to log content"""
        if not content:
            return content

        lines = content.split('\n')
        compressed_lines = []

        # Track patterns for deduplication
        seen_patterns = {}
        consecutive_duplicates = 0
        max_consecutive = 3

        for line in lines:
            # Clean line
            clean_line = line.strip()

            # Skip empty lines if we have too many
            if not clean_line:
                if consecutive_duplicates < 2:
                    compressed_lines.append('')
                    consecutive_duplicates += 1
                continue
            else:
                consecutive_duplicates = 0

            # Create pattern for similar lines (remove timestamps, IDs, etc.)
            pattern = re.sub(r'\d{4}-\d{2}-\d{2}[\s\d:.-]*', '[TIMESTAMP]', clean_line)
            pattern = re.sub(r'\b[a-f0-9]{8,}\b', '[ID]', pattern)
            pattern = re.sub(r'\b\d+\.\d+\b', '[NUMBER]', pattern)
            pattern = re.sub(r'\s+', ' ', pattern)

            # Track pattern frequency
            if pattern in seen_patterns:
                seen_patterns[pattern] += 1
                # If we've seen this pattern many times, compress it
                if seen_patterns[pattern] > max_consecutive:
                    continue  # Skip repetitive lines
            else:
                seen_patterns[pattern] = 1

            # Compress the line itself
            compressed_line = re.sub(r'\s+', ' ', clean_line)  # Single spaces
            compressed_line = re.sub(
                                     r'([,:;])\s+',
                                     r'\1',
                                     compressed_line)  # Remove space after punctuatio
            compressed_line = re.sub(r'([,:;])\s)

            compressed_lines.append(compressed_line)

        # Final compression
        result = '\n'.join(compressed_lines)
        result = re.sub(r'\n{3,}', '\n\n', result)  # Max 2 consecutive newlines

        return result

    def remove_duplicate_content(self) -> dict:
        """🗑️ Remove or merge duplicate content"""
        print("\n🗑️ REMOVING DUPLICATE CONTENT...")

        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()

            # Find exact content duplicates
            cursor.execute("""
                SELECT content, COUNT(*) as count, GROUP_CONCAT(doc_id) as doc_ids
                FROM enterprise_documentation
                WHERE LENGTH(content) > 5000
                GROUP BY content
                HAVING COUNT(*) > 1
            """)
            duplicates = cursor.fetchall()

            removed_count = 0
            bytes_saved = 0

            with tqdm(
                      total=len(duplicates),
                      desc="🗑️ Removing Duplicates",
                      unit="sets") as pbar
            with tqdm(total=len(d)
                for content, count, doc_ids in duplicates:
                    doc_id_list = doc_ids.split(',')
                    # Keep the first one, remove the rest
                    for doc_id in doc_id_list[1:]:
                        cursor.execute(
                                       "DELETE FROM enterprise_documentation WHERE doc_id = ?",
                                       (doc_id,)
                        cursor.execute("DELETE FROM enterprise)
                        removed_count += 1
                        bytes_saved += len(content)

                    pbar.update(1)

            # Clean up orphaned records
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

        result = {
            "duplicates_removed": removed_count,
            "bytes_saved": bytes_saved,
            "mb_saved": bytes_saved / (1024 * 1024)
        }

        print("✅ DUPLICATE REMOVAL COMPLETE:")
        print(f"   📄 Documents removed: {result['duplicates_removed']}")
        print(f"   💾 Bytes saved: {result['bytes_saved']:,} ({result['mb_saved']:.2f} MB)")

        return result

    def final_vacuum_and_compress(self) -> dict:
        """🔧 Final vacuum and compression"""
        print("\n🔧 FINAL VACUUM AND COMPRESSION...")

        size_before = self.db_path.stat().st_size

        with sqlite3.connect(str(self.db_path)) as conn:
            with tqdm(total=100, desc="🔧 Final Compression", unit="%") as pbar:
                # Auto-vacuum
                pbar.set_description("🗜️ Auto-vacuum")
                conn.execute("PRAGMA auto_vacuum = FULL")
                pbar.update(25)

                # Analyze
                pbar.set_description("📊 Analyzing")
                conn.execute("ANALYZE")
                pbar.update(25)

                # Vacuum
                pbar.set_description("🗜️ Vacuuming")
                conn.execute("VACUUM")
                pbar.update(25)

                # Optimize
                pbar.set_description("⚙️ Optimizing")
                conn.execute("PRAGMA optimize")
                pbar.update(25)

        size_after = self.db_path.stat().st_size

        return {
            "size_before": size_before,
            "size_after": size_after,
            "bytes_saved": size_before - size_after,
            "mb_saved": (size_before - size_after) / (1024 * 1024)
        }

    def execute_surgical_compression(self) -> dict:
        """🎯 Execute surgical compression to exactly 99MB"""
        print("\n" + "="*80)
        print("🔬 STARTING SURGICAL DATABASE COMPRESSION")
        print("🎯 TARGET: EXACTLY 99.0 MB")
        print("="*80)

        # Phase 1: Analysis
        analysis = self.analyze_space_usage()

        results = {
            "timestamp": datetime.now().isoformat(),
            "original_size_mb": analysis["current_size_mb"],
            "target_size_mb": 99.0,
            "reduction_needed_mb": analysis["reduction_needed_mb"],
            "phases": {}
        }

        # Phase 2: Remove duplicates first
        print("\n🎯 PHASE 1: DUPLICATE REMOVAL")
        duplicate_results = self.remove_duplicate_content()
        results["phases"]["duplicate_removal"] = duplicate_results

        # Check current size
        current_size = self.db_path.stat().st_size
        remaining_reduction = current_size - self.target_size_bytes

        # Phase 3: Compress logs if still needed
        if remaining_reduction > 0:
            print(f"\n🎯 PHASE 2: LOG COMPRESSION ({remaining_reduction/1024/1024:.1f}MB)")
            log_results = self.compress_log_entries(remaining_reduction)
            results["phases"]["log_compression"] = log_results

        # Phase 4: Final optimization
        print("\n🎯 PHASE 3: FINAL OPTIMIZATION")
        vacuum_results = self.final_vacuum_and_compress()
        results["phases"]["final_optimization"] = vacuum_results

        # Final assessment
        final_size = self.db_path.stat().st_size
        final_size_mb = final_size / (1024 * 1024)

        results.update({
            "final_size_mb": final_size_mb,
            "total_reduction_mb": analysis["current_size_mb"] - final_size_mb,
            "target_achieved": abs(final_size_mb - 99.0) <= 1.0,  # Within 1MB tolerance
            "compression_success": final_size <= self.target_size_bytes * 1.01  # Within 1% tolerance
        })

        # Generate report
        report_path = self.workspace_path / f"surgical_compression_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        # Summary
        duration = (datetime.now() - self.start_time).total_seconds()
        print("\n" + "="*80)
        print("✅ SURGICAL COMPRESSION COMPLETE")
        print("="*80)
        print(f"📦 Original size: {results['original_size_mb']:.2f} MB")
        print(f"📦 Final size: {final_size_mb:.2f} MB")
        print(f"📉 Total reduction: {results['total_reduction_mb']:.2f} MB")
        print(f"🎯 Target (99MB): {'✅ ACHIEVED' if results['target_achieved'] else '❌ CLOSE'}")
        print(f"⏱️ Duration: {duration:.1f} seconds")
        print(f"📄 Report: {report_path}")
        print("="*80)

        return results


def main():
    """Execute surgical compression"""
    print("🔬 SURGICAL DATABASE COMPRESSOR")
    print("🎯 PRECISION TARGET: 99.0 MB")

    try:
        compressor = SurgicalDatabaseCompressor()
        results = compressor.execute_surgical_compression()

        if results["target_achieved"]:
            print("\n🏆 TARGET ACHIEVED!")
            print(f"📊 Database compressed to {results['final_size_mb']:.2f} MB")
        else:
            print(f"\n📊 CLOSE TO TARGET: {results['final_size_mb']:.2f} MB")
            print("🎯 Database optimized and compressed significantly")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        raise


if __name__ == "__main__":
    main()
