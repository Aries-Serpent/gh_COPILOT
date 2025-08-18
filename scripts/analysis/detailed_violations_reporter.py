#!/usr/bin/env python3
"""
# # 🎯 DETAILED VIOLATIONS REPORTER
Enterprise-grade detailed reporting system for, 6,422+ Flake8 violations
"""

import sqlite3
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
from tqdm import tqdm
import matplotlib.pyplot as plt
import seaborn as sns

# MANDATORY: Anti-recursion validation


def validate_workspace_integrity() -> bool:
    """🛡️ CRITICAL: Validate workspace integrity before operations"""
    workspace_root = Path(os.getcwd())

    # Check for recursive patterns
    forbidden_patterns = ["*backup*", "*_backup_*", "backups", "*temp*"]
    violations = []

    for pattern in forbidden_patterns:
        for folder in workspace_root.rglob(pattern):
            if folder.is_dir() and folder != workspace_root:
                violations.append(str(folder))

    if violations:
        for violation in violations:
            print(f"# # 🚨 RECURSIVE VIOLATION: {violation}")
        raise RuntimeError("CRITICAL: Recursive violations prevent execution")

    return True


@dataclass
class ViolationReport:
    """# # # 📊 Comprehensive violation report structure"""

    session_id: str
    total_violations: int
    violations_by_type: Dict[str, int]
    violations_by_file: Dict[str, int]
    top_violating_files: List[Dict[str, Any]]
    violation_severity: Dict[str, int]
    detailed_breakdown: Dict[str, Any]
    timestamp: str


class DetailedViolationsReporter:
    """# # 🎯 Enterprise-grade detailed violations reporting system"""

    def __init__(self, workspace_path: str = "e:/gh_COPILOT"):
        # CRITICAL: Validate workspace integrity
        validate_workspace_integrity()

        self.workspace_path = Path(workspace_path)
        self.database_path = self.workspace_path / "databases" / "flake8_violations.db"
        self.reports_dir = self.workspace_path / "reports" / "violations"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        # Initialize logging
        self.setup_logging()

        # Initialize visualization
        plt.style.use("seaborn-v0_8")
        sns.set_palette("husl")

        self.logger.info("# # 🎯 DETAILED VIOLATIONS REPORTER INITIALIZED")
        self.logger.info(f"Database: {self.database_path}")
        self.logger.info(f"Reports: {self.reports_dir}")

    def setup_logging(self):
        """📋 Setup enterprise logging"""
        log_dir = self.workspace_path / "logs"
        log_dir.mkdir(exist_ok=True)

        # Create formatter for file logging only
        file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

        # File handler with UTF-8 encoding
        file_handler = logging.FileHandler(log_dir / "detailed_violations_reporter.log", encoding="utf-8")
        file_handler.setFormatter(file_formatter)

        # Console handler with safe ASCII output
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter("%(message)s")
        console_handler.setFormatter(console_formatter)

        # Setup logger
        self.logger = logging.getLogger("detailed_violations_reporter")
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def generate_comprehensive_report(self) -> ViolationReport:
        """# # # 📊 Generate comprehensive violation breakdown report"""
        start_time = datetime.now()
        self.logger.info("# # # 🚀 GENERATING COMPREHENSIVE VIOLATION REPORT")

        # Connect to database
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()

            # Get total violations with progress
            with tqdm(total=100, desc="# # # 📊 Analyzing Violations", unit="%") as pbar:
                # Phase 1: Basic counts (20%)
                pbar.set_description("# # # 📊 Counting total violations")
                cursor.execute("SELECT COUNT(*) FROM violations")
                total_violations = cursor.fetchone()[0]
                pbar.update(20)

                # Phase 2: Violations by type (25%)
                pbar.set_description("# # # 🔍 Analyzing by violation type")
                cursor.execute("""
                    SELECT, error_code, COUNT(*) as count
                    FROM violations
                    GROUP BY error_code
                    ORDER BY count DESC
                """)
                violations_by_type = dict(cursor.fetchall())
                pbar.update(25)

                # Phase 3: Violations by file (25%)
                pbar.set_description("📁 Analyzing by file")
                cursor.execute("""
                    SELECT, file_path, COUNT(*) as count
                    FROM violations
                    GROUP BY file_path
                    ORDER BY count DESC
                    LIMIT 50
                """)
                violations_by_file = dict(cursor.fetchall())
                pbar.update(25)

                # Phase 4: Top violating files (30%)
                pbar.set_description("# # 🎯 Finding top violating files")
                cursor.execute("""
                    SELECT, file_path,
                        COUNT(*) as, violation_count,
                        COUNT(DISTINCT, error_code) as unique_types
                    FROM violations
                    GROUP BY file_path
                    ORDER BY violation_count DESC
                    LIMIT 20
                """)
                top_files_data = cursor.fetchall()
                top_violating_files = [
                    {"file": file_path, "violations": count, "unique_types": types}
                    for file_path, count, types in top_files_data
                ]
                pbar.update(30)

        # Generate severity analysis
        violation_severity = self._analyze_violation_severity(violations_by_type)

        # Create detailed breakdown
        detailed_breakdown = self._create_detailed_breakdown(
            violations_by_type, violations_by_file, top_violating_files
        )

        # Create report
        report = ViolationReport(
            session_id=f"DETAILED_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            total_violations=total_violations,
            violations_by_type=violations_by_type,
            violations_by_file=violations_by_file,
            top_violating_files=top_violating_files,
            violation_severity=violation_severity,
            detailed_breakdown=detailed_breakdown,
            timestamp=datetime.now().isoformat(),
        )

        duration = (datetime.now() - start_time).total_seconds()
        self.logger.info(f"# # # ✅ COMPREHENSIVE REPORT GENERATED: {duration:.2f}s")

        return report

    def _analyze_violation_severity(self, violations_by_type: Dict[str, int]) -> Dict[str, int]:
        """# # # ⚠️ Analyze violation severity levels"""
        severity_mapping = {
            # Critical (E9xx, F8xx)
            "critical": ["E901", "E902", "F821", "F822", "F823", "F831"],
            # Error (E, F)
            "error": [code for code in violations_by_type.keys() if code.startswith(("E", "F"))],
            # Warning (W)
            "warning": [code for code in violations_by_type.keys() if code.startswith("W")],
            # Style (other)
            "style": [code for code in violations_by_type.keys() if not code.startswith(("EFW"))],
        }

        severity_counts = {}
        for severity, codes in severity_mapping.items():
            severity_counts[severity] = sum(violations_by_type.get(code, 0) for code in codes)

        return severity_counts

    def _create_detailed_breakdown(
        self, violations_by_type: Dict[str, int], violations_by_file: Dict[str, int], top_files: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """📋 Create detailed violation breakdown"""
        return {
            "top_violation_types": list(violations_by_type.items())[:10],
            "file_statistics": {
                "total_files_with_violations": len(violations_by_file),
                "average_violations_per_file": sum(violations_by_file.values()) / len(violations_by_file)
                if violations_by_file
                else 0,
                "max_violations_in_single_file": max(violations_by_file.values()) if violations_by_file else 0,
            },
            "type_categories": {
                "import_errors": sum(count for code, count in violations_by_type.items() if code.startswith("F4")),
                "undefined_names": sum(count for code, count in violations_by_type.items() if code == "F821"),
                "syntax_errors": sum(count for code, count in violations_by_type.items() if code.startswith("E9")),
                "indentation_errors": sum(count for code, count in violations_by_type.items() if code.startswith("E1")),
                "whitespace_issues": sum(count for code, count in violations_by_type.items() if code.startswith("E2")),
                "line_length": sum(count for code, count in violations_by_type.items() if code == "E501"),
            },
        }

    def save_report_json(self, report: ViolationReport) -> str:
        """# # 💾 Save detailed report as JSON"""
        report_file = self.reports_dir / f"detailed_violations_report_{report.session_id}.json"

        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(asdict(report), f, indent=2, ensure_ascii=False)

        self.logger.info(f"# # 💾 JSON REPORT SAVED: {report_file}")
        return str(report_file)

    def generate_visualizations(self, report: ViolationReport) -> List[str]:
        """# # # 📊 Generate comprehensive violation visualizations"""
        visualization_files = []

        # 1. Violations by Type (Top, 15)
        fig, ax = plt.subplots(figsize=(12, 8))
        top_types = list(report.violations_by_type.items())[:15]
        types, counts = zip(*top_types)

        bars = ax.bar(types, counts, color="lightcoral")
        ax.set_title("Top 15 Violation Types", fontsize=16, fontweight="bold")
        ax.set_xlabel("Violation Type")
        ax.set_ylabel("Count")
        ax.tick_params(axis="x", rotation=45)

        # Add value labels on bars
        for bar, count in zip(bars, counts):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1, str(count), ha="center", va="bottom")

        plt.tight_layout()
        viz_file = self.reports_dir / f"violations_by_type_{report.session_id}.png"
        plt.savefig(viz_file, dpi=300, bbox_inches="tight")
        plt.close()
        visualization_files.append(str(viz_file))

        # 2. Severity Distribution
        fig, ax = plt.subplots(figsize=(10, 6))
        severities = list(report.violation_severity.keys())
        counts = list(report.violation_severity.values())

        colors = ["red", "orange", "yellow", "lightblue"]
        ax.pie(counts, labels=severities, colors=colors, autopct="%1.1f%%", startangle=90)
        ax.set_title("Violation Severity Distribution", fontsize=16, fontweight="bold")

        viz_file = self.reports_dir / f"severity_distribution_{report.session_id}.png"
        plt.savefig(viz_file, dpi=300, bbox_inches="tight")
        plt.close()
        visualization_files.append(str(viz_file))

        # 3. Top Files with Violations
        fig, ax = plt.subplots(figsize=(14, 8))
        top_files = report.top_violating_files[:10]
        file_names = [Path(f["file"]).name for f in top_files]
        violation_counts = [f["violations"] for f in top_files]

        bars = ax.barh(file_names, violation_counts, color="skyblue")
        ax.set_title("Top 10 Files with Most Violations", fontsize=16, fontweight="bold")
        ax.set_xlabel("Number of Violations")
        ax.set_ylabel("File")

        # Add value labels
        for bar, count in zip(bars, violation_counts):
            ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height() / 2, str(count), ha="left", va="center")

        plt.tight_layout()
        viz_file = self.reports_dir / f"top_files_violations_{report.session_id}.png"
        plt.savefig(viz_file, dpi=300, bbox_inches="tight")
        plt.close()
        visualization_files.append(str(viz_file))

        self.logger.info(f"# # # 📊 VISUALIZATIONS GENERATED: {len(visualization_files)} files")
        return visualization_files

    def generate_html_report(self, report: ViolationReport, visualization_files: List[str]) -> str:
        """🌐 Generate comprehensive HTML report"""
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Detailed Violations Report - {report.session_id}</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; background-color:
    #f5f5f5; }}        .header {{ background: linear-gradient(135deg,
    #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; }}        .summary {{ background: white; padding: 20px; margin: 20px 0; border-radius: 10px; box-shadow: 0 2px 5px rgba(
    


            0,
            0,
            0,
            0.1); }}
        .metric {{ display: inline-block; margin: 10px; padding: 15px; background:
    #e8f4f8; border-radius: 8px; text-align: center; }}        .metric h3 {{ margin: 0; color: #2c3e50; }}
        .metric p {{ margin: 5px 0 0 0; font-size: 24px; font-weight: bold; color: #3498db; }}
        .section {{ background: white; padding: 20px; margin: 20px 0; border-radius: 10px; box-shadow: 0 2px 5px rgba(
                                                                                                                      0
                                                                                                                      0
                                                                                                                      0
                                                                                                                      0.1
                                                                                                                 ); }}
        .table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
        .table, th, .table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        .table th {{ background-color: #3498db; color: white; }}
        .table tr:nth-child(even) {{ background-color: #f2f2f2; }}
        .visualization {{ text-align: center; margin: 20px 0; }}
        .visualization img {{ max-width: 100%; height: auto; border-radius: 10px; box-shadow: 0 4px 8px rgba(
                                                                                                             0
                                                                                                             0
                                                                                                             0
                                                                                                             0.1
                                                                                                        ); }}
        .footer {{ text-align: center; color: #7f8c8d; margin-top: 40px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1># # 🎯 Detailed Violations Report</h1>
        <p>Session: {report.session_id}</p>
        <p>Generated: {report.timestamp}</p>
    </div>

    <div class="summary">
        <h2># # # 📊 Executive Summary</h2>
        <div class="metric">
            <h3>Total Violations</h3>
            <p>{report.total_violations:,}</p>
        </div>
        <div class="metric">
            <h3>Files Affected</h3>
            <p>{len(report.violations_by_file):,}</p>
        </div>
        <div class="metric">
            <h3>Violation Types</h3>
            <p>{len(report.violations_by_type):,}</p>
        </div>
        <div class="metric">
            <h3>Avg per File</h3>
            <p>{report.detailed_breakdown["file_statistics"]["average_violations_per_file"]:.1f}</p>
        </div>
    </div>

    <div class="section">
        <h2># # # 🔍 Top Violation Types</h2>
        <table class="table">
            <thead>
                <tr><th>Violation Type</th><th>Count</th><th>Percentage</th></tr>
            </thead>
            <tbody>
        """

        for violation_type, count in list(report.violations_by_type.items())[:10]:
            percentage = (count / report.total_violations) * 100
            html_content += f"""
                <tr>
                    <td><code>{violation_type}</code></td>
                    <td>{count:,}</td>
                    <td>{percentage:.1f}%</td>
                </tr>
            """

        html_content += """
            </tbody>
        </table>
    </div>

    <div class="section">
        <h2>📁 Top Files with Violations</h2>
        <table class="table">
            <thead>
                <tr><th>File</th><th>Violations</th><th>Unique Types</th></tr>
            </thead>
            <tbody>
        """

        for file_info in report.top_violating_files[:10]:
            file_name = Path(file_info["file"]).name
            html_content += f"""
                <tr>
                    <td><code>{file_name}</code></td>
                    <td>{file_info["violations"]:,}</td>
                    <td>{file_info["unique_types"]}</td>
                </tr>
            """

        html_content += """
            </tbody>
        </table>
    </div>

    <div class="section">
        <h2># # # ⚠️ Severity Analysis</h2>
        <table class="table">
            <thead>
                <tr><th>Severity</th><th>Count</th><th>Percentage</th></tr>
            </thead>
            <tbody>
        """

        for severity, count in report.violation_severity.items():
            percentage = (count / report.total_violations) * 100 if report.total_violations > 0 else 0
            html_content += f"""
                <tr>
                    <td><strong>{severity.title()}</strong></td>
                    <td>{count:,}</td>
                    <td>{percentage:.1f}%</td>
                </tr>
            """

        html_content += """
            </tbody>
        </table>
    </div>
        """

        # Add visualizations
        for viz_file in visualization_files:
            viz_name = Path(viz_file).name
            html_content += f"""
    <div class="section">
        <div class="visualization">
            <img src="{viz_name}" alt="Visualization: {viz_name}">
        </div>
    </div>
            """

        html_content += """
    <div class="footer">
        <p>Generated by Enterprise Flake8 Violations Processor</p>
        <p>gh_COPILOT Toolkit v4.0 - Comprehensive Session Integrity Framework</p>
    </div>
</body>
</html>
        """

        html_file = self.reports_dir / f"detailed_violations_report_{report.session_id}.html"
        try:
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(html_content)
            self.logger.info(f"🌐 HTML REPORT GENERATED: {html_file}")
            return str(html_file)
        except Exception as e:
            logging.exception("analysis script error")
            self.logger.error(f"❌ Failed to generate HTML report: {e}")
            return ""


def main():
    """🎯 Main execution function for detailed violations reporting"""
    try:
        print("🎯 DETAILED VIOLATIONS REPORTER")
        print("=" * 50)

        DetailedViolationsReporter()
        print("✅ Detailed violations reporter initialized successfully")

    except Exception as e:
        logging.exception("analysis script error")
        print(f"❌ Error in detailed violations reporter: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
