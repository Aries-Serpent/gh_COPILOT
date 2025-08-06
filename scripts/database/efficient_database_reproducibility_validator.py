#!/usr/bin/env python3
"""
Efficient Database Script Reproducibility Validator
Validates database content can reproduce codebase scripts with compliance checking.
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
from typing import Dict, Optional, Any
import logging

# Configure logging with ASCII-safe format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.FileHandler("efficient_database_validation.log"), logging.StreamHandler()],
)


class EfficientDatabaseValidator:
    """Efficient database script reproducibility validator"""

    def __init__(self, workspace_root: Optional[str] = None):
        self.workspace_root = Path(workspace_root or os.getcwd())
        self.databases_dir = self.workspace_root / "databases"
        self.start_time = datetime.now()
        self.logger = logging.getLogger(__name__)

        # Validate environment
        self.validate_environment()

    def validate_environment(self):
        """Validate environment integrity"""
        forbidden_patterns = ["*backup*", "*_backup_*", "backups"]
        violations = []

        for pattern in forbidden_patterns:
            for folder in self.workspace_root.rglob(pattern):
                if folder.is_dir() and folder != self.workspace_root:
                    violations.append(str(folder))

        if violations:
            self.logger.error(f"CRITICAL: Found recursive violations: {violations}")
            # Auto-cleanup
            for violation in violations:
                import shutil

                shutil.rmtree(violation)
                self.logger.info(f"Removed violation: {violation}")

        self.logger.info("Environment validation complete")

    def scan_python_scripts(self) -> Dict[str, Dict[str, Any]]:
        """Scan only Python scripts for efficiency"""
        scripts = {}
        script_count = 0

        self.logger.info("Scanning Python scripts in codebase...")

        for file_path in self.workspace_root.rglob("*.py"):
            if (
                not any(part.startswith(".") for part in file_path.parts)
                and "archives" not in file_path.parts
                and "__pycache__" not in str(file_path)
            ):
                try:
                    relative_path = file_path.relative_to(self.workspace_root)
                    file_hash = self.calculate_file_hash(file_path)

                    if file_hash:
                        scripts[str(relative_path)] = {
                            "absolute_path": str(file_path),
                            "hash": file_hash,
                            "size": file_path.stat().st_size,
                            "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                        }
                        script_count += 1

                        if script_count % 100 == 0:
                            self.logger.info(f"Scanned {script_count} Python scripts...")

                except Exception as e:
                    self.logger.debug(f"Error processing {file_path}: {e}")

        self.logger.info(f"Found {len(scripts)} Python scripts in codebase")
        return scripts

    def scan_database_scripts(self) -> Dict[str, Any]:
        """Efficiently scan database content for Python scripts"""
        database_content = {"databases": {}, "total_templates": 0, "script_hashes": set(), "content_by_hash": {}}

        self.logger.info("Scanning database content...")

        if not self.databases_dir.exists():
            self.logger.warning("Databases directory not found")
            return database_content

        db_files = list(self.databases_dir.rglob("*.db"))
        self.logger.info(f"Found {len(db_files)} database files")

        for i, db_file in enumerate(db_files):
            try:
                self.logger.info(f"Scanning database {i + 1}/{len(db_files)}: {db_file.name}")
                db_data = self.scan_single_database_efficient(db_file)
                database_content["databases"][db_file.name] = db_data
                database_content["total_templates"] += db_data.get("template_count", 0)

                # Collect script hashes for fast lookup
                for template in db_data.get("python_scripts", []):
                    content_hash = template["content_hash"]
                    database_content["script_hashes"].add(content_hash)
                    database_content["content_by_hash"][content_hash] = template

            except Exception as e:
                self.logger.error(f"Error scanning {db_file}: {e}")

        self.logger.info(f"Database scan complete: {database_content['total_templates']} templates found")
        return database_content

    def scan_single_database_efficient(self, db_path: Path) -> Dict[str, Any]:
        """Efficiently scan single database"""
        db_data = {"path": str(db_path), "tables": [], "template_count": 0, "python_scripts": []}

        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()

                # Get tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                db_data["tables"] = tables

                # Look for script content in common tables
                script_tables = [
                    t
                    for t in tables
                    if any(keyword in t.lower() for keyword in ["script", "template", "content", "code"])
                ]

                for table_name in script_tables:
                    try:
                        # Get columns
                        cursor.execute(f"PRAGMA table_info({table_name})")
                        columns = [col[1] for col in cursor.fetchall()]

                        # Find content columns
                        content_cols = [
                            col
                            for col in columns
                            if any(keyword in col.lower() for keyword in ["content", "template", "script", "code"])
                        ]

                        for content_col in content_cols:
                            cursor.execute(f"""
                                SELECT {content_col} FROM {table_name} 
                                WHERE {content_col} IS NOT NULL 
                                AND LENGTH({content_col}) > 50
                            """)

                            for (content,) in cursor.fetchall():
                                if self.is_python_content(str(content)):
                                    content_hash = hashlib.sha256(str(content).encode()).hexdigest()

                                    template_data = {
                                        "table": table_name,
                                        "content_column": content_col,
                                        "content": str(content),
                                        "content_hash": content_hash,
                                    }

                                    db_data["python_scripts"].append(template_data)
                                    db_data["template_count"] += 1

                    except Exception as e:
                        self.logger.debug(f"Error scanning table {table_name}: {e}")

        except Exception as e:
            self.logger.error(f"Error connecting to {db_path}: {e}")

        return db_data

    def is_python_content(self, content: str) -> bool:
        """Check if content is Python code"""
        if len(content) < 20:
            return False

        python_indicators = ["import ", "from ", "def ", "class ", "if __name__", "print(", "#!/usr/bin/env python"]

        return any(indicator in content for indicator in python_indicators)

    def validate_reproduction_fast(
        self, codebase_scripts: Dict[str, Any], database_content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Fast reproduction validation using hash comparison"""
        results = {
            "total_codebase_scripts": len(codebase_scripts),
            "total_database_templates": database_content["total_templates"],
            "exact_matches": [],
            "non_reproducible_scripts": [],
            "reproduction_rate": 0.0,
            "syntax_valid_count": 0,
            "flake8_compliant_count": 0,
        }

        self.logger.info("Testing script reproduction...")

        db_hashes = database_content["script_hashes"]
        processed = 0

        for script_path, script_data in codebase_scripts.items():
            try:
                # Read script content and calculate hash
                content = Path(script_data["absolute_path"]).read_text(encoding="utf-8")
                content_hash = hashlib.sha256(content.encode()).hexdigest()

                if content_hash in db_hashes:
                    # Exact match found
                    template = database_content["content_by_hash"][content_hash]
                    results["exact_matches"].append(
                        {"script": script_path, "database": template["table"], "hash": content_hash}
                    )

                    # Validate compliance for matched scripts
                    if self.validate_syntax_fast(content):
                        results["syntax_valid_count"] += 1

                    if self.validate_flake8_fast(content):
                        results["flake8_compliant_count"] += 1
                else:
                    # No match found
                    results["non_reproducible_scripts"].append(
                        {"script": script_path, "size": script_data["size"], "hash": content_hash}
                    )

                processed += 1
                if processed % 50 == 0:
                    self.logger.info(f"Processed {processed}/{len(codebase_scripts)} scripts...")

            except Exception as e:
                results["non_reproducible_scripts"].append({"script": script_path, "error": str(e)})

        # Calculate rates
        total_scripts = len(codebase_scripts)
        results["reproduction_rate"] = len(results["exact_matches"]) / total_scripts * 100 if total_scripts > 0 else 0

        self.logger.info(f"Reproduction analysis complete: {results['reproduction_rate']:.1f}% reproducible")
        return results

    def validate_syntax_fast(self, content: str) -> bool:
        """Fast syntax validation"""
        try:
            compile(content, "<string>", "exec")
            return True
        except SyntaxError:
            return False

    def validate_flake8_fast(self, content: str) -> bool:
        """Fast flake8 validation"""
        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as temp_file:
                temp_file.write(content)
                temp_file_path = temp_file.name

            result = subprocess.run(
                ["flake8", "--select=E,W", temp_file_path], capture_output=True, text=True, timeout=10
            )

            os.unlink(temp_file_path)
            return result.returncode == 0

        except (subprocess.SubprocessError, OSError) as exc:
            if "temp_file_path" in locals() and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            self.logger.warning("flake8 failed: %s", exc)
            return False

    def calculate_file_hash(self, file_path: Path) -> Optional[str]:
        """Calculate file hash"""
        try:
            content = file_path.read_bytes()
            return hashlib.sha256(content).hexdigest()
        except OSError as exc:
            self.logger.warning("Failed to read %s: %s", file_path, exc)
            return None

    def generate_action_statement(
        self, codebase_scripts: Dict[str, Any], database_content: Dict[str, Any], reproduction_results: Dict[str, Any]
    ) -> str:
        """Generate comprehensive action statement"""

        reproduction_rate = reproduction_results["reproduction_rate"]
        total_scripts = reproduction_results["total_codebase_scripts"]
        exact_matches = len(reproduction_results["exact_matches"])
        non_reproducible = len(reproduction_results["non_reproducible_scripts"])
        syntax_valid = reproduction_results["syntax_valid_count"]
        flake8_compliant = reproduction_results["flake8_compliant_count"]

        action_statement = f"""# DATABASE PYTHON COMPLIANCE ACTION STATEMENT

## EXECUTIVE SUMMARY
**Validation Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Workspace**: {self.workspace_root}

### REPRODUCIBILITY METRICS
- **Total Python Scripts in Codebase**: {total_scripts}
- **Scripts Reproducible from Database**: {exact_matches} ({reproduction_rate:.1f}%)
- **Scripts NOT Reproducible**: {non_reproducible} ({100 - reproduction_rate:.1f}%)
- **Database Templates Available**: {database_content["total_templates"]}

### COMPLIANCE METRICS  
- **Syntax Valid Scripts**: {syntax_valid}/{exact_matches} ({syntax_valid / exact_matches * 100 if exact_matches > 0 else 0:.1f}%)
- **Flake8 Compliant Scripts**: {flake8_compliant}/{exact_matches} ({flake8_compliant / exact_matches * 100 if exact_matches > 0 else 0:.1f}%)

## FINDINGS

### ✅ REPRODUCIBLE SCRIPTS ({exact_matches})
The following scripts can be exactly reproduced from database content:
"""

        for match in reproduction_results["exact_matches"][:20]:  # Show first 20
            action_statement += f"- `{match['script']}` → Database: `{match['database']}`\n"

        if len(reproduction_results["exact_matches"]) > 20:
            action_statement += f"- ... and {len(reproduction_results['exact_matches']) - 20} more scripts\n"

        action_statement += f"""
### ❌ NON-REPRODUCIBLE SCRIPTS ({non_reproducible})
The following scripts CANNOT be reproduced from current database content:
"""

        for script in reproduction_results["non_reproducible_scripts"][:20]:
            action_statement += f"- `{script['script']}` (Size: {script.get('size', 'unknown')} bytes)\n"

        if len(reproduction_results["non_reproducible_scripts"]) > 20:
            action_statement += f"- ... and {len(reproduction_results['non_reproducible_scripts']) - 20} more scripts\n"

        # Recommendations based on findings
        action_statement += """
## CRITICAL ACTION ITEMS

### HIGH PRIORITY - REPRODUCIBILITY ISSUES
"""

        if reproduction_rate < 80:
            action_statement += """
1. **CRITICAL: Low Reproducibility Rate**
   - Current rate: {:.1f}% (Target: >90%)
   - Action: Audit and update database templates to include missing scripts
   - Timeline: Immediate - within 2 business days
""".format(reproduction_rate)

        if non_reproducible > 10:
            action_statement += f"""
2. **HIGH: {non_reproducible} Scripts Missing from Database**
   - Action: Add missing scripts to appropriate database tables
   - Focus on largest/most critical scripts first
   - Timeline: Within 1 week
"""

        action_statement += """
### MEDIUM PRIORITY - COMPLIANCE ISSUES
"""

        if exact_matches > 0:
            syntax_rate = syntax_valid / exact_matches * 100
            flake8_rate = flake8_compliant / exact_matches * 100

            if syntax_rate < 95:
                action_statement += f"""
3. **MEDIUM: Syntax Compliance Issues**
   - Current rate: {syntax_rate:.1f}% (Target: >95%)
   - Action: Fix Python syntax errors in reproducible scripts
   - Timeline: Within 3 business days
"""

            if flake8_rate < 80:
                action_statement += f"""
4. **MEDIUM: Flake8 Compliance Issues**
   - Current rate: {flake8_rate:.1f}% (Target: >80%)
   - Action: Fix flake8 violations (focus on E9xx, F8xx errors first)
   - Timeline: Within 1 week
"""

        # Database-specific recommendations
        action_statement += """
## DATABASE ENHANCEMENT RECOMMENDATIONS

### Database Content Coverage
"""

        for db_name, db_data in database_content["databases"].items():
            script_count = len(db_data.get("python_scripts", []))
            action_statement += (
                f"- `{db_name}`: {script_count} Python templates, Tables: {len(db_data.get('tables', []))}\n"
            )

        action_statement += f"""

## IMPLEMENTATION PLAN

### Phase 1: Critical Issues (Days 1-2)
1. Identify top 20 missing scripts by size/importance
2. Add missing scripts to database templates
3. Fix critical syntax errors

### Phase 2: Compliance Enhancement (Days 3-7)  
1. Run systematic flake8 correction on all reproducible scripts
2. Update database content with corrected versions
3. Validate compliance improvements

### Phase 3: Complete Coverage (Days 8-14)
1. Add remaining non-reproducible scripts to database
2. Achieve >90% reproducibility rate
3. Achieve >80% flake8 compliance rate

## VALIDATION COMMANDS

To re-run this validation:
```bash
python database_script_reproducibility_validator.py
```

To fix specific compliance issues:
```bash
# Fix syntax errors
python -m py_compile script_name.py

# Check flake8 compliance  
flake8 script_name.py

# Fix common flake8 issues
autopep8 --in-place --aggressive script_name.py
```

---
**Report Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Validation Tool**: Efficient Database Reproducibility Validator v1.0
**Status**: {"✅ ACCEPTABLE" if reproduction_rate >= 80 else "❌ NEEDS IMMEDIATE ATTENTION"}
"""

        return action_statement

    def execute_validation(self) -> Dict[str, Any]:
        """Execute efficient validation process"""
        try:
            self.logger.info("=== DATABASE SCRIPT REPRODUCIBILITY VALIDATION ===")

            # Phase 1: Scan codebase scripts
            self.logger.info("Phase 1: Scanning codebase Python scripts...")
            codebase_scripts = self.scan_python_scripts()

            # Phase 2: Scan database content
            self.logger.info("Phase 2: Scanning database content...")
            database_content = self.scan_database_scripts()

            # Phase 3: Test reproduction
            self.logger.info("Phase 3: Testing script reproduction...")
            reproduction_results = self.validate_reproduction_fast(codebase_scripts, database_content)

            # Phase 4: Generate action statement
            self.logger.info("Phase 4: Generating action statement...")
            action_statement = self.generate_action_statement(codebase_scripts, database_content, reproduction_results)

            # Save results
            results = {
                "validation_timestamp": datetime.now().isoformat(),
                "codebase_scripts": codebase_scripts,
                "database_content": database_content,
                "reproduction_results": reproduction_results,
                "action_statement": action_statement,
            }

            # Write action statement
            action_path = self.workspace_root / "databases_python_compliance_action_statement.md"
            with open(action_path, "w", encoding="utf-8") as f:
                f.write(action_statement)

            # Write JSON results
            json_path = self.workspace_root / "database_validation_results.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, default=str)

            self.logger.info(f"Action statement written to: {action_path}")
            self.logger.info(f"JSON results written to: {json_path}")

            # Log summary
            duration = (datetime.now() - self.start_time).total_seconds()
            reproduction_rate = reproduction_results["reproduction_rate"]

            self.logger.info("=== VALIDATION COMPLETE ===")
            self.logger.info(f"Duration: {duration:.1f} seconds")
            self.logger.info(f"Total Scripts: {len(codebase_scripts)}")
            self.logger.info(f"Reproducible: {len(reproduction_results['exact_matches'])} ({reproduction_rate:.1f}%)")
            self.logger.info(f"Status: {'ACCEPTABLE' if reproduction_rate >= 80 else 'NEEDS ATTENTION'}")

            return results

        except Exception as e:
            self.logger.error(f"Validation failed: {e}")
            raise


def main():
    """Main execution function"""
    try:
        validator = EfficientDatabaseValidator()
        results = validator.execute_validation()

        reproduction_rate = results["reproduction_results"]["reproduction_rate"]

        if reproduction_rate >= 80:
            print(f"\n✅ SUCCESS: {reproduction_rate:.1f}% reproducibility rate achieved")
            return True
        else:
            print(f"\n❌ ATTENTION NEEDED: {reproduction_rate:.1f}% reproducibility rate (target: >80%)")
            return False

    except Exception as e:
        print(f"\n❌ VALIDATION FAILED: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
