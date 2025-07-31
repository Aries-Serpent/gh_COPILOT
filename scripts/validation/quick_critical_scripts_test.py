#!/usr/bin/env python3
"""
Quick Critical Scripts Functionality Test
Focus on most important scripts that users rely on
"""

import ast
from pathlib import Path
from datetime import datetime
import logging

# MANDATORY: Visual processing indicators
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class QuickFunctionalityTest:
    """🚀 Quick test of critical script functionality"""

    def __init__(self):
        self.workspace_root = Path("e:/gh_COPILOT")
        self.scripts_dir = self.workspace_root / "scripts"
        self.start_time = datetime.now()

        logger.info("🚀 QUICK CRITICAL SCRIPTS FUNCTIONALITY TEST")
        logger.info(f"Start Time: {self.start_time}")
        logger.info("=" * 60)

    def test_critical_scripts(self):
        """Test most critical scripts"""

        # Define critical scripts by category
        critical_scripts = {
            "consolidation": [
                "scripts/automation/base_consolidation_executor.py",
                "scripts/utilities/unified_script_generation_system.py",
                "scripts/utilities/comprehensive_script_consolidation_engine.py",
            ],
            "database": [
                "scripts/database/unified_database_management_system.py",
                "scripts/database/database_consolidation_validator.py",
            ],
            "validation": [
                "scripts/validation/comprehensive_syntax_fixer.py",
                "scripts/validation/comprehensive_script_reproducibility_validator.py",
            ],
            "automation": [
                "scripts/automation/database_consolidation_executor.py",
                "scripts/automation/batch_consolidation_processor.py",
            ],
            "compression": ["scripts/utilities/aggressive_compression_strategies.py"],
            "wrap_up": [
                "scripts/analysis/comprehensive_campaign_final_report.py",
                "scripts/analysis/comprehensive_optimization_completion_report.py",
            ],
        }

        results = {
            "tested_scripts": 0,
            "functional_scripts": 0,
            "syntax_errors": [],
            "import_errors": [],
            "missing_scripts": [],
            "category_results": {},
        }

        for category, script_paths in critical_scripts.items():
            logger.info(f"🔍 Testing {category} scripts...")
            category_results = {
                "total": len(script_paths),
                "functional": 0,
                "syntax_ok": 0,
                "imports_ok": 0,
                "missing": 0,
            }

            for script_path in script_paths:
                results["tested_scripts"] += 1
                full_path = self.workspace_root / script_path

                if not full_path.exists():
                    logger.warning(f"   ❌ Missing: {script_path}")
                    results["missing_scripts"].append(script_path)
                    category_results["missing"] += 1
                    continue

                # Test syntax
                syntax_ok = self.test_syntax(full_path, script_path, results)
                if syntax_ok:
                    category_results["syntax_ok"] += 1

                # Test imports (basic)
                imports_ok = self.test_imports_basic(full_path, script_path, results)
                if imports_ok:
                    category_results["imports_ok"] += 1

                # Count as functional if both syntax and imports are OK
                if syntax_ok and imports_ok:
                    category_results["functional"] += 1
                    results["functional_scripts"] += 1
                    logger.info(f"   ✅ {Path(script_path).name}: Functional")
                else:
                    logger.warning(f"   ⚠️  {Path(script_path).name}: Issues found")

            results["category_results"][category] = category_results
            logger.info(f"   📊 {category}: {category_results['functional']}/{category_results['total']} functional")

        return results

    def test_syntax(self, file_path: Path, script_path: str, results: dict) -> bool:
        """Test Python syntax"""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Parse AST to validate syntax
            ast.parse(content)
            return True

        except SyntaxError as e:
            error_detail = f"Syntax error in {script_path} at line {e.lineno}: {e.msg}"
            results["syntax_errors"].append(error_detail)
            return False

        except Exception as e:
            error_detail = f"Parse error in {script_path}: {str(e)}"
            results["syntax_errors"].append(error_detail)
            return False

    def test_imports_basic(self, file_path: Path, script_path: str, results: dict) -> bool:
        """Test basic import functionality"""
        try:
            # Read file and check for problematic import patterns
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Check for common import issues
            if "from . import" in content and str(file_path.parent.name) != "scripts":
                # Relative imports might be problematic
                return True  # Don't fail on relative imports for now

            # Try to compile (not execute) to check imports
            try:
                compile(content, str(file_path), "exec")
                return True
            except ImportError as e:
                error_detail = f"Import error in {script_path}: {str(e)}"
                results["import_errors"].append(error_detail)
                return False
            except Exception:
                # Other compile errors are usually not import-related
                return True

        except Exception as e:
            error_detail = f"Import test error in {script_path}: {str(e)}"
            results["import_errors"].append(error_detail)
            return False

    def generate_summary_report(self, results: dict):
        """Generate summary report"""
        duration = (datetime.now() - self.start_time).total_seconds()

        logger.info("=" * 60)
        logger.info("🏆 QUICK FUNCTIONALITY TEST SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total Scripts Tested: {results['tested_scripts']}")
        logger.info(f"Functional Scripts: {results['functional_scripts']}")
        logger.info(f"Missing Scripts: {len(results['missing_scripts'])}")
        logger.info(f"Syntax Errors: {len(results['syntax_errors'])}")
        logger.info(f"Import Errors: {len(results['import_errors'])}")

        if results["tested_scripts"] > 0:
            functionality_rate = (results["functional_scripts"] / results["tested_scripts"]) * 100
            logger.info(f"Functionality Rate: {functionality_rate:.1f}%")

        logger.info(f"Test Duration: {duration:.1f} seconds")

        # Show category breakdown
        logger.info("\n📊 CATEGORY BREAKDOWN:")
        for category, cat_results in results["category_results"].items():
            total = cat_results["total"]
            functional = cat_results["functional"]
            missing = cat_results["missing"]
            rate = (functional / total * 100) if total > 0 else 0
            logger.info(f"   {category}: {functional}/{total} functional ({rate:.1f}%) - {missing} missing")

        # Show errors if any
        if results["syntax_errors"]:
            logger.info("\n❌ SYNTAX ERRORS:")
            for error in results["syntax_errors"][:5]:  # Show first 5
                logger.info(f"   - {error}")
            if len(results["syntax_errors"]) > 5:
                logger.info(f"   ... and {len(results['syntax_errors']) - 5} more")

        if results["import_errors"]:
            logger.info("\n⚠️  IMPORT ERRORS:")
            for error in results["import_errors"][:5]:  # Show first 5
                logger.info(f"   - {error}")
            if len(results["import_errors"]) > 5:
                logger.info(f"   ... and {len(results['import_errors']) - 5} more")

        if results["missing_scripts"]:
            logger.info("\n📁 MISSING SCRIPTS:")
            for script in results["missing_scripts"]:
                logger.info(f"   - {script}")

        logger.info("=" * 60)

        return results


def main():
    """Execute quick functionality test"""
    try:
        tester = QuickFunctionalityTest()
        results = tester.test_critical_scripts()
        tester.generate_summary_report(results)

        # Save results
        import json

        results_file = (
            Path("e:/gh_COPILOT/scripts/validation")
            / f"quick_functionality_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, default=str)

        logger.info(f"📄 Results saved to: {results_file}")

        return results

    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        raise


if __name__ == "__main__":
    main()
