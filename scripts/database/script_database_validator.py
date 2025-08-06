#!/usr/bin/env python3
"""
Script Database Validator - Enterprise Database-First Validation System
Validates that all scripts within databases are up-to-date with current repository scripts

Enterprise Standards Compliance:
- Flake8/PEP 8 Compliant
- Emoji-free code (text-based indicators only)
- Database-first architecture
- Hash validation for integrity
- Timestamp tracking for sync operations
"""

import hashlib
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Text-based indicators (NO Unicode emojis)
TEXT_INDICATORS = {
    "start": "[START]",
    "success": "[SUCCESS]",
    "error": "[ERROR]",
    "warning": "[WARNING]",
    "database": "[DATABASE]",
    "sync": "[SYNC]",
    "hash": "[HASH]",
    "info": "[INFO]",
}

# Supported script extensions
SCRIPT_EXTENSIONS = {".py", ".ps1", ".sh", ".bat"}


class ScriptDatabaseValidator:
    """Enterprise script database validation system"""

    def __init__(self, workspace_root: Optional[str] = None):
        """Initialize the validator"""
        self.workspace_root = Path(workspace_root or ".")
        self.databases_dir = self.workspace_root / "databases"
        self.script_db_path = self.databases_dir / "script_generation.db"

        # Setup logging
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
        self.logger = logging.getLogger(__name__)

    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of a file"""
        try:
            with open(file_path, "rb") as f:
                content = f.read()
                return hashlib.sha256(content).hexdigest()
        except Exception as e:
            self.logger.error(f"{TEXT_INDICATORS['error']} Failed to hash {file_path}: {e}")
            return ""

    def get_repository_scripts(self) -> Dict[str, Dict[str, str]]:
        """Scan repository for all script files and their metadata"""
        scripts = {}

        self.logger.info(f"{TEXT_INDICATORS['start']} Scanning repository scripts...")

        for file_path in self.workspace_root.rglob("*"):
            if (
                file_path.is_file()
                and file_path.suffix in SCRIPT_EXTENSIONS
                and not any(part.startswith(".") for part in file_path.parts)
                and "archives" not in file_path.parts
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
                    }

        self.logger.info(f"{TEXT_INDICATORS['info']} Found {len(scripts)} scripts in repository")
        return scripts

    def get_database_scripts(self) -> Dict[str, Dict[str, str]]:
        """Get all scripts stored in databases"""
        db_scripts = {}

        if not self.script_db_path.exists():
            self.logger.warning(f"{TEXT_INDICATORS['warning']} Script database not found: {self.script_db_path}")
            return db_scripts

        try:
            with sqlite3.connect(self.script_db_path) as conn:
                cursor = conn.cursor()

                # Get all script templates
                cursor.execute("""
                    SELECT template_id, name, quantum_hash, created_at, updated_at, 
                           content, category, description
                    FROM script_templates
                """)

                for row in cursor.fetchall():
                    template_id, name, quantum_hash, created_at, updated_at, content, category, description = row

                    # Calculate hash of current content
                    content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest() if content else ""

                    db_scripts[name] = {
                        "template_id": template_id,
                        "database_hash": quantum_hash or "",
                        "content_hash": content_hash,
                        "created_at": created_at,
                        "updated_at": updated_at,
                        "category": category,
                        "description": description,
                        "content_size": len(content.encode("utf-8")) if content else 0,
                    }

        except Exception as e:
            self.logger.error(f"{TEXT_INDICATORS['error']} Failed to read database: {e}")

        self.logger.info(f"{TEXT_INDICATORS['database']} Found {len(db_scripts)} scripts in database")
        return db_scripts

    def validate_script_sync(self) -> Dict[str, any]:
        """Validate synchronization between repository and database scripts"""
        self.logger.info(f"{TEXT_INDICATORS['start']} Starting script database validation...")

        repo_scripts = self.get_repository_scripts()
        db_scripts = self.get_database_scripts()

        # Analysis results
        validation_results = {
            "timestamp": datetime.now().isoformat(),
            "total_repo_scripts": len(repo_scripts),
            "total_db_scripts": len(db_scripts),
            "in_sync": [],
            "out_of_sync": [],
            "missing_from_db": [],
            "missing_from_repo": [],
            "hash_mismatches": [],
            "sync_percentage": 0.0,
        }

        # Check each repository script
        for script_path, repo_data in repo_scripts.items():
            script_name = Path(script_path).name

            if script_name in db_scripts:
                db_data = db_scripts[script_name]

                # Compare hashes (use content hash for accuracy)
                if repo_data["hash"] == db_data["content_hash"]:
                    validation_results["in_sync"].append(
                        {"script": script_path, "hash": repo_data["hash"], "last_updated": db_data["updated_at"]}
                    )
                else:
                    validation_results["hash_mismatches"].append(
                        {
                            "script": script_path,
                            "repo_hash": repo_data["hash"],
                            "db_hash": db_data["content_hash"],
                            "repo_modified": repo_data["modified"],
                            "db_updated": db_data["updated_at"],
                        }
                    )
                    validation_results["out_of_sync"].append(script_path)
            else:
                validation_results["missing_from_db"].append(
                    {
                        "script": script_path,
                        "hash": repo_data["hash"],
                        "size": repo_data["size"],
                        "modified": repo_data["modified"],
                    }
                )

        # Check for scripts in DB but not in repo
        repo_script_names = {Path(path).name for path in repo_scripts.keys()}
        for db_script_name in db_scripts.keys():
            if db_script_name not in repo_script_names:
                validation_results["missing_from_repo"].append(db_script_name)

        # Calculate sync percentage
        total_scripts = len(repo_scripts)
        if total_scripts > 0:
            in_sync_count = len(validation_results["in_sync"])
            validation_results["sync_percentage"] = (in_sync_count / total_scripts) * 100

        self._log_validation_summary(validation_results)
        return validation_results

    def _log_validation_summary(self, results: Dict[str, any]) -> None:
        """Log validation summary"""
        self.logger.info(f"{TEXT_INDICATORS['info']} === VALIDATION SUMMARY ===")
        self.logger.info(f"{TEXT_INDICATORS['info']} Repository Scripts: {results['total_repo_scripts']}")
        self.logger.info(f"{TEXT_INDICATORS['info']} Database Scripts: {results['total_db_scripts']}")
        self.logger.info(f"{TEXT_INDICATORS['info']} In Sync: {len(results['in_sync'])}")
        self.logger.info(f"{TEXT_INDICATORS['warning']} Out of Sync: {len(results['out_of_sync'])}")
        self.logger.info(f"{TEXT_INDICATORS['warning']} Missing from DB: {len(results['missing_from_db'])}")
        self.logger.info(f"{TEXT_INDICATORS['warning']} Missing from Repo: {len(results['missing_from_repo'])}")
        self.logger.info(f"{TEXT_INDICATORS['hash']} Hash Mismatches: {len(results['hash_mismatches'])}")
        self.logger.info(f"{TEXT_INDICATORS['sync']} Sync Percentage: {results['sync_percentage']:.2f}%")

    def update_database_scripts(self, scripts_to_update: List[str]) -> bool:
        """Update database with current script content"""
        if not self.script_db_path.exists():
            self.logger.error(f"{TEXT_INDICATORS['error']} Script database not found")
            return False

        repo_scripts = self.get_repository_scripts()
        updated_count = 0

        try:
            with sqlite3.connect(self.script_db_path) as conn:
                cursor = conn.cursor()

                for script_path in scripts_to_update:
                    if script_path not in repo_scripts:
                        continue

                    script_name = Path(script_path).name
                    script_data = repo_scripts[script_path]

                    # Read script content
                    with open(script_data["absolute_path"], "r", encoding="utf-8") as f:
                        content = f.read()

                    # Check if script exists in database
                    cursor.execute("SELECT template_id FROM script_templates WHERE name = ?", (script_name,))
                    existing = cursor.fetchone()

                    current_time = datetime.now().isoformat()

                    if existing:
                        # Update existing script
                        cursor.execute(
                            """
                            UPDATE script_templates 
                            SET content = ?, quantum_hash = ?, updated_at = ?
                            WHERE name = ?
                        """,
                            (content, script_data["hash"], current_time, script_name),
                        )
                    else:
                        # Insert new script with unique template_id
                        base_template_id = f"script_{script_data['hash'][:8]}"
                        template_id = base_template_id
                        counter = 1

                        # Ensure unique template_id
                        while True:
                            cursor.execute(
                                "SELECT template_id FROM script_templates WHERE template_id = ?", (template_id,)
                            )
                            if not cursor.fetchone():
                                break
                            template_id = f"{base_template_id}_{counter}"
                            counter += 1

                        cursor.execute(
                            """
                            INSERT INTO script_templates 
                            (template_id, name, category, description, content, quantum_hash, created_at, updated_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                            (
                                template_id,
                                script_name,
                                "repository_script",
                                f"Auto-synced from {script_path}",
                                content,
                                script_data["hash"],
                                current_time,
                                current_time,
                            ),
                        )

                    updated_count += 1

                conn.commit()
                self.logger.info(f"{TEXT_INDICATORS['success']} Updated {updated_count} scripts in database")
                return True

        except Exception as e:
            self.logger.error(f"{TEXT_INDICATORS['error']} Failed to update database: {e}")
            return False

    def generate_validation_report(self, output_file: Optional[str] = None) -> str:
        """Generate comprehensive validation report"""
        results = self.validate_script_sync()

        report_lines = [
            "# Script Database Validation Report",
            f"Generated: {results['timestamp']}",
            "",
            "## Summary",
            f"- Total Repository Scripts: {results['total_repo_scripts']}",
            f"- Total Database Scripts: {results['total_db_scripts']}",
            f"- Synchronization Percentage: {results['sync_percentage']:.2f}%",
            "",
            "## Synchronization Status",
            f"- Scripts In Sync: {len(results['in_sync'])}",
            f"- Scripts Out of Sync: {len(results['out_of_sync'])}",
            f"- Missing from Database: {len(results['missing_from_db'])}",
            f"- Missing from Repository: {len(results['missing_from_repo'])}",
            f"- Hash Mismatches: {len(results['hash_mismatches'])}",
            "",
        ]

        # Add detailed sections
        if results["missing_from_db"]:
            report_lines.extend(
                [
                    "## Scripts Missing from Database",
                    "| Script | Hash | Size | Modified |",
                    "|--------|------|------|----------|",
                ]
            )
            for item in results["missing_from_db"][:10]:  # Limit for readability
                report_lines.append(
                    f"| {item['script']} | {item['hash'][:16]}... | {item['size']} | {item['modified']} |"
                )
            if len(results["missing_from_db"]) > 10:
                report_lines.append(f"... and {len(results['missing_from_db']) - 10} more")
            report_lines.append("")

        if results["hash_mismatches"]:
            report_lines.extend(
                [
                    "## Hash Mismatches (Out of Sync)",
                    "| Script | Repository Modified | Database Updated |",
                    "|--------|-------------------|------------------|",
                ]
            )
            for item in results["hash_mismatches"][:10]:
                report_lines.append(f"| {item['script']} | {item['repo_modified']} | {item['db_updated']} |")
            if len(results["hash_mismatches"]) > 10:
                report_lines.append(f"... and {len(results['hash_mismatches']) - 10} more")
            report_lines.append("")

        report_content = "\n".join(report_lines)

        if output_file:
            with open(output_file, "w") as f:
                f.write(report_content)
            self.logger.info(f"{TEXT_INDICATORS['success']} Report saved to {output_file}")

        return report_content


def main():
    """Main execution function"""
    import argparse

    parser = argparse.ArgumentParser(description="Validate script database synchronization")
    parser.add_argument("--workspace", "-w", help="Workspace root directory")
    parser.add_argument("--report", "-r", help="Generate report to file")
    parser.add_argument("--update", "-u", action="store_true", help="Update database with out-of-sync scripts")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    validator = ScriptDatabaseValidator(args.workspace)

    if args.report:
        report = validator.generate_validation_report(args.report)
        print(report)
    else:
        results = validator.validate_script_sync()

        if args.update and results["missing_from_db"]:
            scripts_to_update = [item["script"] for item in results["missing_from_db"]]
            validator.update_database_scripts(scripts_to_update)


if __name__ == "__main__":
    main()
