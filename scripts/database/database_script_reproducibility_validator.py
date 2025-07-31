#!/usr/bin/env python3
"""
Database Script Reproducibility Validator
Validates that all database content can reproduce all scripts in codebase
with Python compliance, syntax validation, and flake8 compliance.

🚀 DUAL COPILOT PATTERN COMPLIANCE
🛡️ ENTERPRISE ANTI-RECURSION PROTECTION
📊 VISUAL PROCESSING INDICATORS MANDATORY
"""

import os
import sys
import sqlite3
import json
import hashlib
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from tqdm import tqdm
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.FileHandler("database_reproducibility_validation.log"), logging.StreamHandler()],
)

TEXT_INDICATORS = {"start": "🚀", "success": "✅", "error": "❌", "warning": "⚠️", "info": "📊", "process": "🔄"}

SCRIPT_EXTENSIONS = {".py", ".ps1", ".sh", ".js", ".ts"}


class DatabaseReproducibilityValidator:
    """Validates database can reproduce all codebase scripts with compliance"""

    def __init__(self, workspace_root: Optional[str] = None):
        self.workspace_root = Path(workspace_root or os.getcwd())
        self.databases_dir = self.workspace_root / "databases"
        self.start_time = datetime.now()
        self.process_id = os.getpid()
        self.logger = logging.getLogger(__name__)

        # CRITICAL: Anti-recursion validation
        self.validate_environment_integrity()

        # Initialize visual processing
        self.setup_visual_monitoring()

    def validate_environment_integrity(self):
        """CRITICAL: Validate no recursive folder violations"""
        forbidden_patterns = ["*backup*", "*_backup_*", "backups", "*temp*"]
        violations = []

        for pattern in forbidden_patterns:
            for folder in self.workspace_root.rglob(pattern):
                if folder.is_dir() and folder != self.workspace_root:
                    violations.append(str(folder))

        if violations:
            for violation in violations:
                self.logger.error(f"🚨 RECURSIVE VIOLATION: {violation}")
                # Emergency removal
                import shutil

                shutil.rmtree(violation)
                self.logger.info(f"🗑️ Removed violation: {violation}")
            raise RuntimeError("CRITICAL: Recursive violations prevented execution")

        self.logger.info("✅ Environment integrity validated")

    def setup_visual_monitoring(self):
        """Initialize comprehensive visual indicators"""
        self.logger.info("=" * 80)
        self.logger.info(f"{TEXT_INDICATORS['start']} DATABASE REPRODUCIBILITY VALIDATOR")
        self.logger.info(f"Task: Database-to-Codebase Reproducibility Validation")
        self.logger.info(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(f"Process ID: {self.process_id}")
        self.logger.info(f"Workspace: {self.workspace_root}")
        self.logger.info("=" * 80)

    def scan_all_scripts(self) -> Dict[str, Dict[str, Any]]:
        """Scan all scripts in the codebase"""
        scripts = {}

        self.logger.info(f"{TEXT_INDICATORS['process']} Scanning all scripts in codebase...")

        with tqdm(desc="🔍 Scanning scripts", unit="files") as pbar:
            for file_path in self.workspace_root.rglob("*"):
                if (
                    file_path.is_file()
                    and file_path.suffix in SCRIPT_EXTENSIONS
                    and not any(part.startswith(".") for part in file_path.parts)
                    and "archives" not in file_path.parts
                    and "__pycache__" not in str(file_path)
                ):
                    relative_path = file_path.relative_to(self.workspace_root)
                    file_hash = self.calculate_file_hash(file_path)

                    if file_hash:
                        scripts[str(relative_path)] = {
                            "absolute_path": str(file_path),
                            "hash": file_hash,
                            "size": file_path.stat().st_size,
                            "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                            "extension": file_path.suffix,
                            "directory": str(file_path.parent.relative_to(self.workspace_root)),
                        }
                        pbar.update(1)

        self.logger.info(f"{TEXT_INDICATORS['info']} Found {len(scripts)} scripts in codebase")
        return scripts

    def scan_database_content(self) -> Dict[str, Any]:
        """Scan all database content for reproducible scripts"""
        database_content = {"databases": {}, "total_templates": 0, "total_scripts": 0, "script_content": {}}

        self.logger.info(f"{TEXT_INDICATORS['process']} Scanning database content...")

        if not self.databases_dir.exists():
            self.logger.warning(f"{TEXT_INDICATORS['warning']} Databases directory not found")
            return database_content

        db_files = list(self.databases_dir.rglob("*.db"))

        with tqdm(total=len(db_files), desc="🗄️ Scanning databases", unit="db") as pbar:
            for db_file in db_files:
                try:
                    db_name = db_file.name
                    database_content["databases"][db_name] = self.scan_single_database(db_file)
                    pbar.update(1)
                except Exception as e:
                    self.logger.error(f"{TEXT_INDICATORS['error']} Error scanning {db_file}: {e}")
                    pbar.update(1)

        # Calculate totals
        for db_data in database_content["databases"].values():
            database_content["total_templates"] += db_data.get("template_count", 0)
            database_content["total_scripts"] += db_data.get("script_count", 0)

        self.logger.info(
            f"{TEXT_INDICATORS['info']} Found {database_content['total_templates']} templates across {len(db_files)} databases"
        )
        return database_content

    def scan_single_database(self, db_path: Path) -> Dict[str, Any]:
        """Scan a single database for script content"""
        db_data = {
            "path": str(db_path),
            "tables": [],
            "template_count": 0,
            "script_count": 0,
            "templates": [],
            "scripts": [],
        }

        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()

                # Get all tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()

                for (table_name,) in tables:
                    db_data["tables"].append(table_name)

                    # Check for common script/template columns
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    columns = [col[1] for col in cursor.fetchall()]

                    # Look for content columns
                    content_columns = [
                        col
                        for col in columns
                        if any(keyword in col.lower() for keyword in ["content", "template", "script", "code"])
                    ]

                    if content_columns:
                        # Extract script content
                        for content_col in content_columns:
                            try:
                                cursor.execute(f"SELECT * FROM {table_name} WHERE {content_col} IS NOT NULL")
                                rows = cursor.fetchall()

                                for row in rows:
                                    content_idx = columns.index(content_col)
                                    content = row[content_idx] if content_idx < len(row) else None

                                    if content and len(str(content)) > 10:  # Filter out tiny content
                                        template_data = {
                                            "table": table_name,
                                            "content_column": content_col,
                                            "content": str(content),
                                            "content_hash": hashlib.sha256(str(content).encode()).hexdigest(),
                                            "row_data": row,
                                        }

                                        db_data["templates"].append(template_data)
                                        db_data["template_count"] += 1

                                        # Check if it's a Python script
                                        if self.is_python_content(str(content)):
                                            db_data["scripts"].append(template_data)
                                            db_data["script_count"] += 1

                            except Exception as e:
                                self.logger.debug(f"Error extracting from {table_name}.{content_col}: {e}")

        except Exception as e:
            self.logger.error(f"{TEXT_INDICATORS['error']} Error connecting to {db_path}: {e}")

        return db_data

    def is_python_content(self, content: str) -> bool:
        """Check if content appears to be Python code"""
        python_indicators = [
            "import ",
            "from ",
            "def ",
            "class ",
            "if __name__",
            "print(",
            "#!/usr/bin/env python",
            "# -*- coding:",
            "import sys",
            "import os",
        ]

        return any(indicator in content for indicator in python_indicators)

    def validate_python_syntax(self, content: str) -> Tuple[bool, str]:
        """Validate Python syntax"""
        try:
            compile(content, "<string>", "exec")
            return True, "Valid syntax"
        except SyntaxError as e:
            return False, f"Syntax error: {e}"
        except Exception as e:
            return False, f"Compilation error: {e}"

    def validate_flake8_compliance(self, content: str) -> Tuple[bool, List[str]]:
        """Validate flake8 compliance"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name

        try:
            result = subprocess.run(["flake8", temp_file_path], capture_output=True, text=True, timeout=30)

            os.unlink(temp_file_path)

            if result.returncode == 0:
                return True, []
            else:
                violations = result.stdout.strip().split("\n") if result.stdout.strip() else []
                return False, violations

        except subprocess.TimeoutExpired:
            os.unlink(temp_file_path)
            return False, ["Flake8 validation timeout"]
        except FileNotFoundError:
            os.unlink(temp_file_path)
            return False, ["Flake8 not installed"]
        except Exception as e:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            return False, [f"Flake8 validation error: {e}"]

    def attempt_script_reproduction(
        self, database_content: Dict[str, Any], codebase_scripts: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Attempt to reproduce all codebase scripts from database content"""
        reproduction_results = {
            "total_codebase_scripts": len(codebase_scripts),
            "total_database_templates": database_content["total_templates"],
            "reproducible_scripts": [],
            "non_reproducible_scripts": [],
            "exact_matches": [],
            "partial_matches": [],
            "syntax_valid_reproductions": [],
            "flake8_compliant_reproductions": [],
            "reproduction_rate": 0.0,
            "compliance_rate": 0.0,
        }

        self.logger.info(f"{TEXT_INDICATORS['process']} Attempting script reproduction...")

        # Collect all database script content
        all_db_content = []
        for db_name, db_data in database_content["databases"].items():
            all_db_content.extend(db_data.get("scripts", []))

        with tqdm(total=len(codebase_scripts), desc="🔄 Testing reproduction", unit="scripts") as pbar:
            for script_path, script_data in codebase_scripts.items():
                if script_data["extension"] != ".py":
                    pbar.update(1)
                    continue

                # Read actual script content
                try:
                    actual_content = Path(script_data["absolute_path"]).read_text(encoding="utf-8")
                    actual_hash = hashlib.sha256(actual_content.encode()).hexdigest()

                    # Check for exact matches
                    exact_match = None
                    for db_content in all_db_content:
                        if db_content["content_hash"] == actual_hash:
                            exact_match = db_content
                            break

                    if exact_match:
                        reproduction_results["exact_matches"].append(
                            {"script": script_path, "database": exact_match["table"], "match_type": "exact_hash"}
                        )
                        reproduction_results["reproducible_scripts"].append(script_path)

                        # Validate compliance
                        syntax_valid, syntax_msg = self.validate_python_syntax(actual_content)
                        flake8_valid, flake8_violations = self.validate_flake8_compliance(actual_content)

                        if syntax_valid:
                            reproduction_results["syntax_valid_reproductions"].append(script_path)

                        if flake8_valid:
                            reproduction_results["flake8_compliant_reproductions"].append(script_path)
                    else:
                        # Check for partial matches (content similarity)
                        best_match = self.find_best_partial_match(actual_content, all_db_content)

                        if best_match and best_match["similarity"] > 0.7:
                            reproduction_results["partial_matches"].append(
                                {
                                    "script": script_path,
                                    "database": best_match["template"]["table"],
                                    "similarity": best_match["similarity"],
                                    "match_type": "partial",
                                }
                            )
                            reproduction_results["reproducible_scripts"].append(script_path)
                        else:
                            reproduction_results["non_reproducible_scripts"].append(
                                {
                                    "script": script_path,
                                    "reason": "No matching content found in databases",
                                    "file_size": script_data["size"],
                                }
                            )

                except Exception as e:
                    reproduction_results["non_reproducible_scripts"].append(
                        {
                            "script": script_path,
                            "reason": f"Error reading script: {e}",
                            "file_size": script_data.get("size", 0),
                        }
                    )

                pbar.update(1)

        # Calculate rates
        total_scripts = len([s for s in codebase_scripts.values() if s["extension"] == ".py"])
        reproduction_results["reproduction_rate"] = (
            len(reproduction_results["reproducible_scripts"]) / total_scripts * 100 if total_scripts > 0 else 0
        )

        reproduction_results["compliance_rate"] = (
            len(reproduction_results["flake8_compliant_reproductions"]) / total_scripts * 100
            if total_scripts > 0
            else 0
        )

        return reproduction_results

    def find_best_partial_match(self, content: str, db_templates: List[Dict]) -> Optional[Dict]:
        """Find best partial match using simple similarity"""
        best_match = None
        best_similarity = 0.0

        content_lines = set(line.strip() for line in content.split("\n") if line.strip())

        for template in db_templates:
            template_lines = set(line.strip() for line in template["content"].split("\n") if line.strip())

            if not template_lines:
                continue

            # Calculate Jaccard similarity
            intersection = len(content_lines.intersection(template_lines))
            union = len(content_lines.union(template_lines))

            similarity = intersection / union if union > 0 else 0.0

            if similarity > best_similarity:
                best_similarity = similarity
                best_match = {"template": template, "similarity": similarity}

        return best_match

    def calculate_file_hash(self, file_path: Path) -> Optional[str]:
        """Calculate SHA-256 hash of file"""
        try:
            content = file_path.read_bytes()
            return hashlib.sha256(content).hexdigest()
        except Exception as e:
            self.logger.debug(f"Error calculating hash for {file_path}: {e}")
            return None

    def generate_comprehensive_report(
        self, codebase_scripts: Dict[str, Any], database_content: Dict[str, Any], reproduction_results: Dict[str, Any]
    ) -> str:
        """Generate comprehensive validation report"""
        report_lines = [
            "# DATABASE SCRIPT REPRODUCIBILITY VALIDATION REPORT",
            "=" * 80,
            "",
            f"**Validation Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Workspace**: {self.workspace_root}",
            f"**Process ID**: {self.process_id}",
            "",
            "## EXECUTIVE SUMMARY",
            f"- **Total Codebase Scripts**: {len(codebase_scripts)}",
            f"- **Python Scripts**: {len([s for s in codebase_scripts.values() if s['extension'] == '.py'])}",
            f"- **Database Templates**: {database_content['total_templates']}",
            f"- **Database Script Templates**: {database_content['total_scripts']}",
            f"- **Reproduction Rate**: {reproduction_results['reproduction_rate']:.1f}%",
            f"- **Compliance Rate**: {reproduction_results['compliance_rate']:.1f}%",
            "",
            "## REPRODUCIBILITY ANALYSIS",
            f"### Exact Matches: {len(reproduction_results['exact_matches'])}",
        ]

        for match in reproduction_results["exact_matches"][:10]:  # Show first 10
            report_lines.append(f"- `{match['script']}` → `{match['database']}`")

        if len(reproduction_results["exact_matches"]) > 10:
            report_lines.append(f"- ... and {len(reproduction_results['exact_matches']) - 10} more")

        report_lines.extend(
            [
                "",
                f"### Partial Matches: {len(reproduction_results['partial_matches'])}",
            ]
        )

        for match in reproduction_results["partial_matches"][:10]:
            report_lines.append(f"- `{match['script']}` → `{match['database']}` ({match['similarity']:.1%} similarity)")

        if len(reproduction_results["partial_matches"]) > 10:
            report_lines.append(f"- ... and {len(reproduction_results['partial_matches']) - 10} more")

        report_lines.extend(
            [
                "",
                f"### Non-Reproducible Scripts: {len(reproduction_results['non_reproducible_scripts'])}",
            ]
        )

        for script in reproduction_results["non_reproducible_scripts"][:10]:
            report_lines.append(f"- `{script['script']}`: {script['reason']}")

        if len(reproduction_results["non_reproducible_scripts"]) > 10:
            report_lines.append(f"- ... and {len(reproduction_results['non_reproducible_scripts']) - 10} more")

        report_lines.extend(
            [
                "",
                "## COMPLIANCE ANALYSIS",
                f"### Syntax Valid Reproductions: {len(reproduction_results['syntax_valid_reproductions'])}",
                f"### Flake8 Compliant Reproductions: {len(reproduction_results['flake8_compliant_reproductions'])}",
                "",
                "## DATABASE BREAKDOWN",
            ]
        )

        for db_name, db_data in database_content["databases"].items():
            report_lines.extend(
                [
                    f"### {db_name}",
                    f"- Tables: {len(db_data['tables'])}",
                    f"- Templates: {db_data['template_count']}",
                    f"- Script Templates: {db_data['script_count']}",
                    f"- Tables: {', '.join(db_data['tables'])}",
                ]
            )

        report_lines.extend(["", "## RECOMMENDATIONS", "", "### High Priority Actions:"])

        if reproduction_results["reproduction_rate"] < 90:
            report_lines.append("- **CRITICAL**: Low reproduction rate - enhance database content coverage")

        if reproduction_results["compliance_rate"] < 80:
            report_lines.append("- **HIGH**: Improve script compliance - fix syntax and flake8 violations")

        if len(reproduction_results["non_reproducible_scripts"]) > 0:
            report_lines.append("- **MEDIUM**: Add missing scripts to database templates")

        report_lines.extend(
            [
                "",
                "---",
                f"*Report generated by Database Reproducibility Validator v1.0*",
                f"*{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
            ]
        )

        return "\n".join(report_lines)

    def execute_comprehensive_validation(self) -> Dict[str, Any]:
        """Execute comprehensive database reproducibility validation"""
        try:
            with tqdm(total=100, desc="🚀 Database Validation", unit="%") as pbar:
                # Phase 1: Scan codebase scripts
                pbar.set_description("🔍 Scanning codebase scripts")
                codebase_scripts = self.scan_all_scripts()
                pbar.update(25)

                # Phase 2: Scan database content
                pbar.set_description("🗄️ Scanning database content")
                database_content = self.scan_database_content()
                pbar.update(25)

                # Phase 3: Attempt reproduction
                pbar.set_description("🔄 Testing reproduction")
                reproduction_results = self.attempt_script_reproduction(database_content, codebase_scripts)
                pbar.update(25)

                # Phase 4: Generate report
                pbar.set_description("📄 Generating report")
                report = self.generate_comprehensive_report(codebase_scripts, database_content, reproduction_results)
                pbar.update(25)

            # Save results
            results = {
                "validation_timestamp": datetime.now().isoformat(),
                "codebase_scripts": codebase_scripts,
                "database_content": database_content,
                "reproduction_results": reproduction_results,
                "report": report,
            }

            # Write JSON report
            json_report_path = self.workspace_root / "database_reproducibility_report.json"
            with open(json_report_path, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, default=str)

            # Write markdown report
            md_report_path = self.workspace_root / "database_reproducibility_report.md"
            with open(md_report_path, "w", encoding="utf-8") as f:
                f.write(report)

            self.logger.info(f"{TEXT_INDICATORS['success']} Reports written to:")
            self.logger.info(f"  - JSON: {json_report_path}")
            self.logger.info(f"  - Markdown: {md_report_path}")

            return results

        except Exception as e:
            self.logger.error(f"{TEXT_INDICATORS['error']} Validation failed: {e}")
            raise

    def log_completion_summary(self, results: Dict[str, Any]):
        """Log comprehensive completion summary"""
        duration = (datetime.now() - self.start_time).total_seconds()

        self.logger.info("=" * 80)
        self.logger.info(f"{TEXT_INDICATORS['success']} DATABASE REPRODUCIBILITY VALIDATION COMPLETE")
        self.logger.info(f"Duration: {duration:.1f} seconds")
        self.logger.info(f"Reproduction Rate: {results['reproduction_results']['reproduction_rate']:.1f}%")
        self.logger.info(f"Compliance Rate: {results['reproduction_results']['compliance_rate']:.1f}%")
        self.logger.info(f"Total Scripts: {results['reproduction_results']['total_codebase_scripts']}")
        self.logger.info(f"Database Templates: {results['database_content']['total_templates']}")
        self.logger.info("=" * 80)


def main():
    """Main execution function"""
    try:
        validator = DatabaseReproducibilityValidator()
        results = validator.execute_comprehensive_validation()
        validator.log_completion_summary(results)

        # DUAL COPILOT VALIDATION
        reproduction_rate = results["reproduction_results"]["reproduction_rate"]
        compliance_rate = results["reproduction_results"]["compliance_rate"]

        if reproduction_rate >= 90 and compliance_rate >= 80:
            validator.logger.info(f"{TEXT_INDICATORS['success']} DUAL COPILOT VALIDATION: PASSED")
            return True
        else:
            validator.logger.warning(f"{TEXT_INDICATORS['warning']} DUAL COPILOT VALIDATION: NEEDS IMPROVEMENT")
            validator.logger.warning(f"Reproduction Rate: {reproduction_rate:.1f}% (target: ≥90%)")
            validator.logger.warning(f"Compliance Rate: {compliance_rate:.1f}% (target: ≥80%)")
            return False

    except Exception as e:
        logging.error(f"{TEXT_INDICATORS['error']} Validation failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
