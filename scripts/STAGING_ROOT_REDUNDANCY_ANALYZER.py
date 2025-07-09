#!/usr/bin/env python3
"""
STAGING ROOT DIRECTORY REDUNDANCY ANALYZER
==========================================
Enterprise-grade analysis of staging root directory files to identify
redundant variations and recommend cleanup actions

COMPLIANCE: Enterprise GitHub Copilot integration standards
PATTERN: DUAL COPILOT with visual processing indicators
OBJECTIVE: Optimize staging root directory organization
"""

import difflib
import hashlib
import json
import os
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from tqdm import tqdm

from copilot.common.workspace_utils import get_workspace_path


class StagingRootRedundancyAnalyzer:
    def __init__(self):
        self.start_time = datetime.now()
        self.process_id = os.getpid()
        self.session_id = f"STAGING_REDUNDANCY_ANALYSIS_{int(time.time())}"

        # Initialize paths
        self.staging_root = get_workspace_path()
        self.sandbox_root = get_workspace_path()
        self.database_path = self.staging_root / "databases" / "production.db"

        # Analysis results
        self.analysis_results = {
            "session_id": self.session_id,
            "timestamp": self.start_time.isoformat(),
            "process_id": self.process_id,
            "total_files": 0,
            "file_groups": {},
            "duplicates": [],
            "variations": [],
            "recommendations": [],
            "cleanup_actions": []
        }

        print(f"[SEARCH] STAGING ROOT REDUNDANCY ANALYZER INITIATED")
        print(f"Session ID: {self.session_id}")
        print(f"Start Time: {self.start_time}")
        print(f"Process ID: {self.process_id}")
        print("=" * 60)

    def analyze_file_content(self, file_path: Path) -> Dict:
        """Analyze file content for comparison"""
        try:
            content = file_path.read_text(encoding='utf-8')

            # Calculate hash
            content_hash = hashlib.sha256(content.encode()).hexdigest()

            # Extract key characteristics
            lines = content.split('\n')

            analysis = {
                "file_path": str(file_path),
                "file_name": file_path.name,
                "file_size": file_path.stat().st_size,
                "content_hash": content_hash,
                "line_count": len(lines),
                "char_count": len(content),
                "modification_time": file_path.stat().st_mtime,
                "functions": [],
                "classes": [],
                "imports": [],
                "key_patterns": []
            }

            # Analyze Python files
            if file_path.suffix == '.py':
                for line in lines:
                    line = line.strip()
                    if line.startswith('def '):
                        analysis["functions"].append(line)
                    elif line.startswith('class '):
                        analysis["classes"].append(line)
                    elif line.startswith('import ') or line.startswith('from '):
                        analysis["imports"].append(line)
                    elif any(pattern in line for pattern in ['DUAL COPILOT', 'AUTONOMOUS', 'ENTERPRISE']):
                        analysis["key_patterns"].append(line)

            return analysis

        except Exception as e:
            return {
                "file_path": str(file_path),
                "file_name": file_path.name,
                "error": str(e),
                "analysis_failed": True
            }

    def group_similar_files(self, file_analyses: List[Dict]) -> Dict:
        """Group files by similarity"""
        print("\n[SEARCH] GROUPING SIMILAR FILES")
        print("-" * 30)

        groups = {}

        with tqdm(total=len(file_analyses), desc="Grouping files", unit="file") as pbar:
            for analysis in file_analyses:
                if analysis.get("analysis_failed"):
                    pbar.update(1)
                    continue

                file_name = analysis["file_name"]
                base_name = self.extract_base_name(file_name)

                if base_name not in groups:
                    groups[base_name] = []

                groups[base_name].append(analysis)
                pbar.update(1)

        return groups

    def extract_base_name(self, filename: str) -> str:
        """Extract base name from filename variations"""
        # Remove common suffixes
        base = filename.replace('.py', '')

        # Remove version indicators
        for suffix in [
            '_clean',
            '_enhanced',
            '_complete',
            '_final',
            '_v2',
            '_v3',
                '_advanced']:
            if base.endswith(suffix):
                base = base[:-len(suffix)]
                break

        # Remove step numbers
        if base.startswith('step') and len(base) > 4 and base[4].isdigit():
            return 'step_framework'

        return base

    def analyze_file_similarity(self, file1: Dict, file2: Dict) -> float:
        """Calculate similarity between two files"""
        try:
            # Size similarity
            size1, size2 = file1["file_size"], file2["file_size"]
            size_ratio = min(size1, size2) / max(size1,
                                                 size2) if max(size1, size2) > 0 else 0

            # Function similarity
            func1 = set(file1.get("functions", []))
            func2 = set(file2.get("functions", []))
            func_similarity = len(
                func1 & func2) / len(func1 | func2) if len(func1 | func2) > 0 else 0

            # Class similarity
            class1 = set(file1.get("classes", []))
            class2 = set(file2.get("classes", []))
            class_similarity = len(
                class1 & class2) / len(class1 | class2) if len(class1 | class2) > 0 else 0

            # Import similarity
            import1 = set(file1.get("imports", []))
            import2 = set(file2.get("imports", []))
            import_similarity = len(
                import1 & import2) / len(import1 | import2) if len(import1 | import2) > 0 else 0

            # Overall similarity
            similarity = (
                size_ratio *
                0.2 +
                func_similarity *
                0.4 +
                class_similarity *
                0.2 +
                import_similarity *
                0.2)

            return similarity

        except Exception as e:
            return 0.0

    def identify_redundant_files(self, groups: Dict) -> List[Dict]:
        """Identify files that are redundant or variations"""
        print("\n[SEARCH] IDENTIFYING REDUNDANT FILES")
        print("-" * 35)

        redundant_files = []

        for group_name, files in groups.items():
            if len(files) <= 1:
                continue

            print(
                f"\n[BAR_CHART] Analyzing group: {group_name} ({
                    len(files)} files)")

            # Sort by modification time (newest first)
            files.sort(
                key=lambda x: x.get(
                    "modification_time",
                    0),
                reverse=True)

            # Compare files in the group
            for i, file1 in enumerate(files):
                for j, file2 in enumerate(files[i + 1:], i + 1):
                    similarity = self.analyze_file_similarity(file1, file2)

                    if similarity > 0.8:  # High similarity threshold
                        redundant_files.append({
                            "group": group_name,
                            "primary_file": file1["file_path"],
                            "redundant_file": file2["file_path"],
                            "similarity": similarity,
                            "recommendation": "REMOVE_REDUNDANT",
                            "reason": f"High similarity ({similarity:.1%}) with newer file"
                        })
                        print(
                            f"  [?] REDUNDANT: {
                                file2['file_name']} (similarity: {
                                similarity:.1%})")
                    elif similarity > 0.6:  # Moderate similarity
                        redundant_files.append({
                            "group": group_name,
                            "primary_file": file1["file_path"],
                            "variation_file": file2["file_path"],
                            "similarity": similarity,
                            "recommendation": "REVIEW_VARIATION",
                            "reason": f"Moderate similarity ({similarity:.1%}) - may be variation"
                        })
                        print(
                            f"  [?] VARIATION: {
                                file2['file_name']} (similarity: {
                                similarity:.1%})")

        return redundant_files

    def check_file_in_database(self, file_path: str) -> bool:
        """Check if file content is already captured in database"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()

            # Check if file exists in deployment history
            cursor.execute("""
                SELECT COUNT(*) FROM deployment_gaps
                WHERE gap_description LIKE ? OR resolution_actions LIKE ?
            """, (f"%{Path(file_path).name}%", f"%{Path(file_path).name}%"))

            count = cursor.fetchone()[0]
            conn.close()

            return count > 0

        except Exception as e:
            return False

    def generate_recommendations(
            self, redundant_files: List[Dict]) -> List[Dict]:
        """Generate cleanup recommendations"""
        print("\n[CLIPBOARD] GENERATING RECOMMENDATIONS")
        print("-" * 35)

        recommendations = []

        # Group by recommendation type
        remove_files = [
            f for f in redundant_files if f["recommendation"] == "REMOVE_REDUNDANT"]
        review_files = [
            f for f in redundant_files if f["recommendation"] == "REVIEW_VARIATION"]

        print(f"[BAR_CHART] Analysis Summary:")
        print(f"  [?] Files to remove: {len(remove_files)}")
        print(f"  [?] Files to review: {len(review_files)}")

        # Generate removal recommendations
        for file_info in remove_files:
            file_path = file_info["redundant_file"]
            in_database = self.check_file_in_database(file_path)

            recommendations.append({
                "action": "REMOVE",
                "file_path": file_path,
                "reason": file_info["reason"],
                "similarity": file_info["similarity"],
                "database_captured": in_database,
                "priority": "HIGH" if in_database else "MEDIUM",
                "safe_to_remove": in_database
            })

        # Generate review recommendations
        for file_info in review_files:
            file_path = file_info["variation_file"]
            in_database = self.check_file_in_database(file_path)

            recommendations.append({
                "action": "REVIEW",
                "file_path": file_path,
                "reason": file_info["reason"],
                "similarity": file_info["similarity"],
                "database_captured": in_database,
                "priority": "MEDIUM",
                "safe_to_remove": False
            })

        return recommendations

    def execute_cleanup_analysis(self):
        """Execute the complete cleanup analysis"""
        print("\n[LAUNCH] EXECUTING STAGING ROOT CLEANUP ANALYSIS")
        print("=" * 50)

        try:
            # Step 1: Discover Python files in staging root
            print("\n[CLIPBOARD] STEP 1: DISCOVERING FILES")
            python_files = list(self.staging_root.glob("*.py"))
            self.analysis_results["total_files"] = len(python_files)

            print(
                f"[BAR_CHART] Found {
                    len(python_files)} Python files in staging root")

            # Step 2: Analyze file content
            print("\n[CLIPBOARD] STEP 2: ANALYZING FILE CONTENT")
            file_analyses = []

            with tqdm(total=len(python_files), desc="Analyzing content", unit="file") as pbar:
                for py_file in python_files:
                    analysis = self.analyze_file_content(py_file)
                    file_analyses.append(analysis)
                    pbar.update(1)

            # Step 3: Group similar files
            print("\n[CLIPBOARD] STEP 3: GROUPING SIMILAR FILES")
            groups = self.group_similar_files(file_analyses)
            self.analysis_results["file_groups"] = {
                name: len(files) for name, files in groups.items()
            }

            # Step 4: Identify redundant files
            print("\n[CLIPBOARD] STEP 4: IDENTIFYING REDUNDANCIES")
            redundant_files = self.identify_redundant_files(groups)

            # Step 5: Generate recommendations
            print("\n[CLIPBOARD] STEP 5: GENERATING RECOMMENDATIONS")
            recommendations = self.generate_recommendations(redundant_files)
            self.analysis_results["recommendations"] = recommendations

            # Step 6: Save analysis results
            print("\n[CLIPBOARD] STEP 6: SAVING ANALYSIS RESULTS")
            self.save_analysis_results()

            # Step 7: Generate summary report
            print("\n[CLIPBOARD] STEP 7: GENERATING SUMMARY REPORT")
            self.generate_summary_report()

            print("\n" + "=" * 60)
            print("[TARGET] STAGING ROOT CLEANUP ANALYSIS COMPLETE")
            print("=" * 60)

        except Exception as e:
            print(f"[ERROR] Analysis failed: {str(e)}")
            raise

    def save_analysis_results(self):
        """Save analysis results to JSON file"""
        try:
            results_file = self.sandbox_root / \
                f"STAGING_ROOT_REDUNDANCY_ANALYSIS_{self.session_id}.json"

            with open(results_file, 'w') as f:
                json.dump(self.analysis_results, f, indent=2)

            print(f"[SUCCESS] Analysis results saved: {results_file}")

        except Exception as e:
            print(f"[ERROR] Failed to save analysis results: {str(e)}")

    def generate_summary_report(self):
        """Generate comprehensive summary report"""
        print("\n[BAR_CHART] STAGING ROOT CLEANUP ANALYSIS SUMMARY")
        print("=" * 50)

        recommendations = self.analysis_results.get("recommendations", [])

        # Summary statistics
        remove_count = len(
            [r for r in recommendations if r["action"] == "REMOVE"])
        review_count = len(
            [r for r in recommendations if r["action"] == "REVIEW"])
        safe_remove_count = len(
            [r for r in recommendations if r.get("safe_to_remove", False)])

        print(f"[BAR_CHART] Analysis Summary:")
        print(
            f"  [?] Total files analyzed: {
                self.analysis_results['total_files']}")
        print(
            f"  [?] File groups identified: {len(self.analysis_results['file_groups'])}")
        print(f"  [?] Redundant files found: {remove_count}")
        print(f"  [?] Files for review: {review_count}")
        print(f"  [?] Safe to remove (in database): {safe_remove_count}")

        # Detailed recommendations
        print(f"\n[?] CLEANUP RECOMMENDATIONS:")

        high_priority = [
            r for r in recommendations if r.get("priority") == "HIGH"]
        medium_priority = [
            r for r in recommendations if r.get("priority") == "MEDIUM"]

        if high_priority:
            print(
                f"\n[?] HIGH PRIORITY REMOVALS ({
                    len(high_priority)} files):")
            for rec in high_priority:
                filename = Path(rec["file_path"]).name
                print(f"  [?] {filename} - {rec['reason']}")

        if medium_priority:
            print(
                f"\n[?] MEDIUM PRIORITY REVIEWS ({
                    len(medium_priority)} files):")
            for rec in medium_priority:
                filename = Path(rec["file_path"]).name
                print(f"  [?] {filename} - {rec['reason']}")

        # File group analysis
        print(f"\n[BAR_CHART] FILE GROUP ANALYSIS:")
        for group_name, count in self.analysis_results["file_groups"].items():
            if count > 1:
                print(f"  [?] {group_name}: {count} files")

        # Calculate potential space savings
        total_size = sum(Path(r["file_path"]).stat(
        ).st_size for r in recommendations if r["action"] == "REMOVE")
        print(
            f"\n[STORAGE] POTENTIAL SPACE SAVINGS: {
                total_size /
                1024:.1f} KB")

        print(
            f"\n[TARGET] RECOMMENDATION: Remove {safe_remove_count} files safely captured in database")
        print(
            f"[CLIPBOARD] NEXT STEPS: Review {review_count} variation files for consolidation")


def main():
    """Main execution function"""
    try:
        # Initialize the analyzer
        analyzer = StagingRootRedundancyAnalyzer()

        # Execute the analysis
        analyzer.execute_cleanup_analysis()

        print("\n[COMPLETE] STAGING ROOT REDUNDANCY ANALYSIS COMPLETE")

    except Exception as e:
        print(f"[ERROR] CRITICAL ERROR: {str(e)}")
        return 1


if __name__ == "__main__":
    main()
