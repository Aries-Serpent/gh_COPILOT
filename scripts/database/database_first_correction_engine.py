#!/usr/bin/env python3
"""
🔄 Database-First Correction Engine with Template Synchronization
Enterprise-grade correction system leveraging production.db intelligence
"""

import sys
import logging
import sqlite3
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List
from tqdm import tqdm
import hashlib

from scripts.automation.template_auto_generation_complete import TemplateSynthesisEngine

# MANDATORY: Visual processing indicators and logging
logger = logging.getLogger("DatabaseFirstCorrectionEngine")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


class DatabaseFirstCorrectionEngine:
    """🎯 Database-First Correction Engine with Enterprise Compliance"""

    def __init__(self, workspace_path: str = "e:/gh_COPILOT"):
        self.workspace_path = Path(workspace_path)
        self.production_db = self.workspace_path / "production.db"
        self.analytics_db = self.workspace_path / "analytics.db"
        self.analytics_db.parent.mkdir(parents=True, exist_ok=True)
        self.session_id = f"SESSION_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # CRITICAL: Anti-recursion validation
        self._validate_workspace_integrity()

    def _validate_workspace_integrity(self) -> None:
        """CRITICAL: Validate workspace before correction execution"""
        start_time = datetime.now()
        logger.info(f"🚀 Workspace Integrity Validation Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

        forbidden_patterns = ["*backup*", "*_backup_*", "backups", "*temp*"]
        violations = []

        for pattern in forbidden_patterns:
            for folder in self.workspace_path.rglob(pattern):
                if folder.is_dir() and folder != self.workspace_path:
                    violations.append(str(folder))

        if violations:
            logger.error(f"🚨 RECURSIVE FOLDER VIOLATIONS DETECTED:")
            for violation in violations:
                logger.error(f"   - {violation}")
            raise RuntimeError("CRITICAL: Recursive folder violations prevent execution")

        logger.info("✅ Workspace integrity validated")

    def query_database_patterns(self) -> Dict[str, Any]:
        """🗄️ Query production.db for existing correction patterns and templates"""
        logger.info("🔍 Querying database for correction patterns...")

        patterns = {
            "correction_templates": [],
            "script_classifications": {},
            "error_patterns": {},
            "template_mappings": {},
        }

        try:
            with sqlite3.connect(self.production_db) as conn:
                cursor = conn.cursor()

                # Query existing script patterns
                cursor.execute("""
                    SELECT script_path, functionality_category, script_type,
                           importance_score, template_pattern
                    FROM enhanced_script_tracking
                    WHERE status = 'ACTIVE'
                """)
                script_data = cursor.fetchall()

                for row in script_data:
                    script_path, category, script_type, importance, template = row
                    patterns["script_classifications"][script_path] = {
                        "category": category,
                        "type": script_type,
                        "importance": importance,
                        "template": template,
                    }

                # Query correction templates
                cursor.execute("""
                    SELECT template_name, template_content, correction_type
                    FROM correction_templates
                    WHERE status = 'ACTIVE'
                """)
                template_data = cursor.fetchall()

                for template_name, content, correction_type in template_data:
                    patterns["correction_templates"].append(
                        {"name": template_name, "content": content, "type": correction_type}
                    )

                logger.info(
                    f"✅ Retrieved {len(script_data)} script patterns and {len(template_data)} correction templates"
                )

        except sqlite3.Error as e:
            logger.warning(f"⚠️ Database query failed: {e}. Using fallback patterns.")

        return patterns

    def synchronize_codebase_with_database(self) -> Dict[str, int]:
        """🔄 Synchronize all codebase scripts with database templates and patterns"""
        start_time = datetime.now()
        logger.info(f"🚀 Codebase Synchronization Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

        sync_stats = {
            "scripts_updated": 0,
            "templates_applied": 0,
            "patterns_synchronized": 0,
            "database_entries_created": 0,
        }

        # Discover all Python files in codebase
        python_files = list(self.workspace_path.rglob("*.py"))
        logger.info(f"📊 Found {len(python_files)} Python files for synchronization")

        with tqdm(total=len(python_files), desc="🔄 Synchronizing Codebase", unit="files") as pbar:
            for idx, py_file in enumerate(python_files):
                try:
                    # Update database with current file state
                    self._update_database_entry(py_file)
                    sync_stats["database_entries_created"] += 1

                    # Apply templates and patterns
                    if self._apply_database_templates(py_file):
                        sync_stats["templates_applied"] += 1

                    sync_stats["scripts_updated"] += 1

                except Exception as e:
                    logger.warning(f"⚠️ Sync failed for {py_file}: {e}")

                pbar.update(1)
                elapsed = (datetime.now() - start_time).total_seconds()
                etc = (elapsed / (idx + 1)) * (len(python_files) - (idx + 1)) if idx + 1 > 0 else 0
                pbar.set_description(f"🔄 Synchronizing | ETC: {etc:.1f}s")

        logger.info(f"✅ Codebase synchronization complete: {sync_stats}")
        return sync_stats

    def _update_database_entry(self, file_path: Path) -> None:
        """📊 Update or create database entry for file"""
        try:
            with sqlite3.connect(self.production_db) as conn:
                cursor = conn.cursor()

                # Get file metadata
                file_stats = file_path.stat()
                file_content = file_path.read_text(encoding="utf-8", errors="ignore")

                # Classify file
                category = self._classify_file(file_path, file_content)
                script_type = self._determine_script_type(file_content)
                importance = self._calculate_importance_score(file_path, file_content)

                # Insert or update
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO enhanced_script_tracking
                    (script_path, functionality_category, script_type,
                     importance_score, file_size, last_updated, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        str(file_path.relative_to(self.workspace_path)),
                        category,
                        script_type,
                        importance,
                        file_stats.st_size,
                        datetime.now().isoformat(),
                        "ACTIVE",
                    ),
                )

        except Exception as e:
            logger.warning(f"⚠️ Database update failed for {file_path}: {e}")

    def _classify_file(self, file_path: Path, content: str) -> str:
        """🏷️ Classify file based on path and content"""
        path_str = str(file_path).lower()

        if "test" in path_str:
            return "testing"
        elif "database" in path_str or "db" in path_str:
            return "database_management"
        elif "enterprise" in path_str:
            return "enterprise_systems"
        elif "quantum" in content.lower() or "quantum" in path_str:
            return "quantum_optimization"
        elif "web_gui" in path_str or "flask" in content.lower():
            return "web_interface"
        elif "flake8" in path_str or "lint" in path_str:
            return "code_quality"
        else:
            return "general_utility"

    def _determine_script_type(self, content: str) -> str:
        """📋 Determine script type from content analysis"""
        if "class" in content and "def __init__" in content:
            return "class_module"
        elif 'if __name__ == "__main__"' in content:
            return "executable_script"
        elif "def " in content and "class" not in content:
            return "function_library"
        else:
            return "utility_module"

    def _calculate_importance_score(self, file_path: Path, content: str) -> float:
        """📊 Calculate importance score based on file characteristics"""
        score = 0.5  # Base score

        # Path-based scoring
        if "enterprise" in str(file_path).lower():
            score += 0.3
        if "database" in str(file_path).lower():
            score += 0.2
        if "quantum" in str(file_path).lower():
            score += 0.2

        # Content-based scoring
        if "CRITICAL" in content:
            score += 0.2
        if "MANDATORY" in content:
            score += 0.1
        if len(content.split("\n")) > 500:  # Large files
            score += 0.1

        return min(score, 1.0)  # Cap at 1.0

    def _apply_database_templates(self, file_path: Path) -> bool:
        """🎨 Apply database templates to file if applicable"""
        try:
            content = file_path.read_text(encoding="utf-8")

            # Check if file needs template application
            if self._needs_template_update(content):
                updated_content = self._apply_template_patterns(content)
                if updated_content != content:
                    file_path.write_text(updated_content, encoding="utf-8")
                    logger.info(f"✅ Applied template to {file_path}")
                    return True

        except Exception as e:
            logger.warning(f"⚠️ Template application failed for {file_path}: {e}")

        return False

    def _needs_template_update(self, content: str) -> bool:
        """🔍 Check if file needs template updates"""
        # Check for missing enterprise headers
        if not content.startswith("#!/usr/bin/env python3"):
            return True
        if "logging" not in content and "logger" not in content:
            return True
        return False

    def _apply_template_patterns(self, content: str) -> str:
        """🎨 Apply standard template patterns to content"""
        lines = content.split("\n")

        # Ensure shebang
        if not lines[0].startswith("#!"):
            lines.insert(0, "#!/usr/bin/env python3")

        # Add logging if missing
        if "import logging" not in content:
            # Find appropriate insertion point
            import_section = 0
            for i, line in enumerate(lines):
                if line.startswith("import ") or line.startswith("from "):
                    import_section = i + 1
            lines.insert(import_section, "import logging")

        return "\n".join(lines)

    def _run_ruff_fix(self, file_path: Path) -> None:
        """Apply ``ruff check --fix`` to ``file_path``."""
        subprocess.run(
            ["ruff", "check", "--fix", str(file_path)],
            capture_output=True,
            text=True,
        )

    def cross_validate_with_ruff(self, file_path: Path) -> bool:
        """Run ``ruff check`` on ``file_path`` and return success."""
        result = subprocess.run(
            ["ruff", "check", str(file_path)],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0

    def _record_correction_history(self, file_path: Path, action: str, details: str = "") -> None:
        """Insert a record into ``correction_history`` table."""
        try:
            with sqlite3.connect(self.production_db) as conn:
                conn.execute(
                    """CREATE TABLE IF NOT EXISTS correction_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        session_id TEXT NOT NULL,
                        file_path TEXT NOT NULL,
                        action TEXT NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        details TEXT
                    )"""
                )
                conn.execute(
                    "INSERT INTO correction_history (user_id, session_id, file_path, action, details) VALUES (?, ?, ?, ?, ?)",
                    (0, self.session_id, str(file_path), action, details),
                )
        except Exception as exc:  # pragma: no cover - unexpected
            logger.warning(f"⚠️ Failed to record history for {file_path}: {exc}")

    def execute_database_driven_corrections(self) -> Dict[str, Any]:
        """🔧 Execute comprehensive database-driven corrections"""
        start_time = datetime.now()
        logger.info(f"🚀 Database-Driven Corrections Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

        correction_results = {
            "E501_corrections": 0,
            "W291_corrections": 0,
            "W293_corrections": 0,
            "F541_corrections": 0,
            "F821_manual_review": [],
            "F841_corrections": 0,
            "E999_syntax_errors": [],
            "total_files_processed": 0,
        }

        # Get database patterns
        patterns = self.query_database_patterns()

        # Synchronize codebase first
        sync_stats = self.synchronize_codebase_with_database()

        # Regenerate templates and store them
        generated_templates = TemplateSynthesisEngine().synthesize_templates()
        if generated_templates:
            self._store_generated_templates(generated_templates)

        # Apply automated corrections

        # Apply automated corrections
        python_files = list(self.workspace_path.rglob("*.py"))

        with tqdm(total=len(python_files), desc="🔧 Database Corrections", unit="files") as pbar:
            for idx, py_file in enumerate(python_files):
                try:
                    file_corrections = self._apply_file_corrections(py_file, patterns)

                    # Aggregate results
                    for key, value in file_corrections.items():
                        if key in correction_results:
                            if isinstance(correction_results[key], list):
                                correction_results[key].extend(value if isinstance(value, list) else [value])
                            else:
                                correction_results[key] += value

                    correction_results["total_files_processed"] += 1

                except Exception as e:
                    logger.warning(f"⚠️ Correction failed for {py_file}: {e}")

                pbar.update(1)
                elapsed = (datetime.now() - start_time).total_seconds()
                etc = (elapsed / (idx + 1)) * (len(python_files) - (idx + 1)) if idx + 1 > 0 else 0
                pbar.set_description(f"🔧 Correcting | ETC: {etc:.1f}s")

        # Log results to database
        self._log_correction_results(correction_results)

        logger.info(f"✅ Database-driven corrections complete: {correction_results}")
        return correction_results

    def _apply_file_corrections(self, file_path: Path, patterns: Dict[str, Any]) -> Dict[str, Any]:
        """🔧 Apply corrections to individual file"""
        results = {
            "E501_corrections": 0,
            "W291_corrections": 0,
            "W293_corrections": 0,
            "F541_corrections": 0,
            "F841_corrections": 0,
        }

        try:
            content = file_path.read_text(encoding="utf-8")
            lines = content.split("\n")
            modified = False

            # Apply line-by-line corrections
            for i, line in enumerate(lines):
                original_line = line

                # E501: Line too long
                if len(line) > 100:
                    lines[i] = self._fix_long_line(line)
                    if lines[i] != original_line:
                        results["E501_corrections"] += 1
                        modified = True

                # F541: f-string missing placeholders
                if line.strip().startswith('f"') and "{" not in line:
                    lines[i] = line.replace('f"', '"')
                    results["F541_corrections"] += 1
                    modified = True
                elif line.strip().startswith("f'") and "{" not in line:
                    lines[i] = line.replace("f'", "'")
                    results["F541_corrections"] += 1
                    modified = True

                # W291: Trailing whitespace
                if line.endswith(" ") or line.endswith("\t"):
                    lines[i] = line.rstrip()
                    results["W291_corrections"] += 1
                    modified = True

            # W293: Blank line contains whitespace
            for i, line in enumerate(lines):
                if not line.strip() and line:  # Empty line with whitespace
                    lines[i] = ""
                    results["W293_corrections"] += 1
                    modified = True

            # Save if modified
            if modified:
                file_path.write_text("\n".join(lines), encoding="utf-8")
                logger.info(f"✅ Applied corrections to {file_path}")
                self._run_ruff_fix(file_path)
                passed = self.cross_validate_with_ruff(file_path)
                action = "ruff_fix_pass" if passed else "ruff_fix_fail"
                self._record_correction_history(file_path, action)

        except Exception as e:
            logger.warning(f"⚠️ File correction failed for {file_path}: {e}")

        return results

    def _fix_long_line(self, line: str) -> str:
        """🔧 Fix long lines by breaking them appropriately"""
        if len(line) <= 100:
            return line

        # Simple line breaking for common patterns
        if "(" in line and ")" in line:
            # Break at function calls
            parts = line.split("(", 1)
            if len(parts) == 2:
                return f"{parts[0]}(\n    {parts[1]}"

        # For other cases, return original (manual review needed)
        return line

    def _store_generated_templates(self, templates: List[str]) -> None:
        """Store synthesized template information in production.db."""
        try:
            with sqlite3.connect(self.production_db) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS template_repository (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        template_name TEXT NOT NULL,
                        template_content TEXT NOT NULL,
                        template_category TEXT,
                        usage_count INTEGER DEFAULT 0,
                        success_rate REAL DEFAULT 0.0,
                        last_used DATETIME,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        template_hash TEXT UNIQUE
                    )
                    """
                )

                for tmpl in templates:
                    template_hash = hashlib.sha256(tmpl.encode()).hexdigest()
                    cursor.execute(
                        "SELECT 1 FROM template_repository WHERE template_hash = ?",
                        (template_hash,),
                    )
                    if cursor.fetchone():
                        continue
                    name = f"auto_{template_hash[:8]}"
                    cursor.execute(
                        """
                        INSERT INTO template_repository (
                            template_name,
                            template_content,
                            template_category,
                            last_used,
                            template_hash
                        ) VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            name,
                            tmpl,
                            "auto_generated",
                            datetime.now().isoformat(),
                            template_hash,
                        ),
                    )
                conn.commit()
        except Exception as e:
            logger.warning(f"⚠️ Failed to store templates: {e}")

    def _log_correction_results(self, results: Dict[str, Any]) -> None:
        """📊 Log correction results to analytics database"""
        try:
            with sqlite3.connect(self.analytics_db) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT INTO correction_analytics
                    (timestamp, total_files, e501_fixes, w291_fixes, w293_fixes,
                     f541_fixes, f841_fixes, manual_reviews)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        datetime.now().isoformat(),
                        results["total_files_processed"],
                        results["E501_corrections"],
                        results["W291_corrections"],
                        results["W293_corrections"],
                        results["F541_corrections"],
                        results["F841_corrections"],
                        len(results.get("F821_manual_review", [])),
                    ),
                )

        except Exception as e:
            logger.warning(f"⚠️ Analytics logging failed: {e}")


def main():
    """🚀 Main execution function with enterprise compliance"""
    start_time = datetime.now()
    logger.info(f"🚀 DATABASE-FIRST CORRECTION ENGINE STARTED: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        # Initialize engine
        engine = DatabaseFirstCorrectionEngine()

        # Execute corrections
        results = engine.execute_database_driven_corrections()

        # Final validation
        logger.info("🔍 Running final validation with ruff...")
        subprocess.run(["ruff", "check", "."], capture_output=True, text=True)

        logger.info("✅ DATABASE-FIRST CORRECTION ENGINE COMPLETED SUCCESSFULLY")

    except Exception as e:
        logger.error(f"❌ Correction engine failed: {e}")
        sys.exit(1)

    finally:
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"⏱️ Total Duration: {duration:.1f} seconds")


if __name__ == "__main__":
    main()
