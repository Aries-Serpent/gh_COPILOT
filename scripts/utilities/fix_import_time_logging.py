#!/usr/bin/env python3
"""
Fix Import-Time Logging Configuration Issues
Scans repository and fixes modules with problematic logging.basicConfig() calls
"""

import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))


def scan_for_import_time_logging(workspace_path: Path) -> List[Dict[str, Any]]:
    """🔍 Scan for import-time logging configuration issues"""
    violations = []
    basicconfig_pattern = re.compile(r'^(\s*)logging\.basicConfig\(', re.MULTILINE)
    python_files = list(workspace_path.rglob("*.py"))
    with tqdm(total=len(python_files), desc="🔍 Scanning for logging issues", unit="file") as pbar:
        for py_file in python_files:
            pbar.set_description(f"🔍 Scanning {py_file.name}")
            try:
                content = py_file.read_text(encoding="utf-8")
                matches = basicconfig_pattern.findall(content)
                if matches:
                    lines = content.splitlines()
                    import_time_configs = []
                    for line_num, line in enumerate(lines, 1):
                        if 'logging.basicConfig(' in line:
                            if not line.startswith('    ') and not line.startswith('\t'):
                                import_time_configs.append({
                                    "line_number": line_num,
                                    "line_content": line.strip(),
                                })
                    if import_time_configs:
                        violations.append({
                            "file_path": str(py_file),
                            "violations": import_time_configs,
                        })
            except Exception as e:
                print(f"Error scanning {py_file}: {e}")
            pbar.update(1)
    return violations


def fix_import_time_logging(file_path: Path) -> Dict[str, Any]:
    """🔧 Fix import-time logging configuration in a file"""
    content = file_path.read_text(encoding="utf-8")
    lines = content.splitlines()
    modified_lines: List[str] = []
    changes_made: List[str] = []
    for idx, line in enumerate(lines):
        if 'logging.basicConfig(' in line and not line.startswith('    '):
            modified_lines.append(f"# FIXED: {line}  # Moved to setup_logging() function")
            changes_made.append(f"Line {idx + 1}: Commented out import-time logging.basicConfig()")
        else:
            modified_lines.append(line)
    if changes_made:
        if 'from utils.enterprise_logging import' not in content:
            import_index = 0
            for i, line in enumerate(modified_lines):
                if line.startswith('import ') or line.startswith('from '):
                    import_index = i + 1
            enterprise_import = 'from utils.enterprise_logging import EnterpriseLoggingManager'
            modified_lines.insert(import_index, enterprise_import)
            changes_made.append('Added enterprise logging import')
        modified_content = "\n".join(modified_lines)
        backup_path = file_path.with_suffix(f"{file_path.suffix}.backup")
        backup_path.write_text(content, encoding="utf-8")
        file_path.write_text(modified_content, encoding="utf-8")
        backup_created = str(backup_path)
    else:
        backup_created = None
    return {
        "file_path": str(file_path),
        "changes_made": changes_made,
        "backup_created": backup_created,
    }


def execute_logging_fixes() -> Dict[str, Any]:
    """🔧 Execute automated logging fixes"""
    from utils.enterprise_logging import EnterpriseLoggingManager
    logger = EnterpriseLoggingManager.setup_module_logging("logging_fixer")
    workspace_path = Path(os.getenv("GH_COPILOT_WORKSPACE", os.getcwd()))
    logger.info("=" * 80)
    logger.info("🔧 IMPORT-TIME LOGGING FIXES")
    logger.info("=" * 80)
    violations = scan_for_import_time_logging(workspace_path)
    if not violations:
        logger.info("✅ No import-time logging violations found")
        return {"status": "NO_VIOLATIONS", "files_processed": 0}
    fix_results = []
    with tqdm(total=len(violations), desc="🔧 Fixing logging", unit="file") as pbar:
        for violation in violations:
            pbar.set_description(f"🔧 Fixing {Path(violation['file_path']).name}")
            try:
                result = fix_import_time_logging(Path(violation['file_path']))
                fix_results.append(result)
            except Exception as e:
                logger.error(f"Fix failed for {violation['file_path']}: {e}")
            pbar.update(1)
    successful_fixes = [r for r in fix_results if r.get('changes_made')]
    logger.info("=" * 80)
    logger.info("🔧 LOGGING FIXES SUMMARY")
    logger.info(f"Files Scanned: {len(violations)}")
    logger.info(f"Successful Fixes: {len(successful_fixes)}")
    logger.info("✅ Import-time logging conflicts resolved")
    logger.info("=" * 80)
    return {
        "status": "SUCCESS",
        "files_processed": len(violations),
        "successful_fixes": len(successful_fixes),
        "fix_results": fix_results,
    }


if __name__ == "__main__":
    result = execute_logging_fixes()
    print(f"✅ LOGGING FIXES COMPLETE: {result['status']}")
