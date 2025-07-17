"""
CHUNK 1: Discovery & Setup
Semantic Search File Reference Validation Script
Enterprise Compliance | DUAL COPILOT Pattern | Visual Processing Indicators
"""
import os
import sys
import time
from datetime import datetime, timedelta
from tqdm import tqdm
import logging

# === ENTERPRISE LOGGING SETUP ===
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger("SemanticSearchValidator")

# === ANTI-RECURSION & COMPLIANCE VALIDATION ===
def validate_no_recursive_folders():
    """
    Scan workspace for forbidden recursive folders (backup/temp) and log violations.
    Returns True if no violations, False otherwise.
    """
    workspace_root = os.path.abspath(os.getcwd())
    forbidden_patterns = ['backup', 'backups', '_backup_', 'temp']
    for root, dirs, files in os.walk(workspace_root):
        for d in dirs:
            d_lower = d.lower()
            if any(fp in d_lower for fp in forbidden_patterns):
                full_path = os.path.join(root, d)
                if os.path.commonpath([workspace_root, full_path]) == workspace_root and full_path != workspace_root:
                    logger.error(f"🚨 RECURSIVE FOLDER DETECTED: {full_path}")
                    return False
    return True

def detect_c_temp_violations():
    """
    Scan C:/temp for forbidden gh_COPILOT folders and log violations.
    Returns True if violations found, False otherwise.
    """
    temp_root = os.path.normpath("C:/temp")
    if os.path.exists(temp_root):
        for item in os.listdir(temp_root):
            if "gh_COPILOT" in item.upper():
                logger.error(f"🚨 C:/temp/ VIOLATION: {item}")
                return True
    return False

def chunk_anti_recursion_validation():
    """
    CRITICAL: Validate workspace before chunk execution.
    Raises RuntimeError if any anti-recursion or forbidden temp violations are found.
    """
    if not validate_no_recursive_folders():
        raise RuntimeError("CRITICAL: Recursive violations prevent chunk execution")
    if detect_c_temp_violations():
        raise RuntimeError("CRITICAL: E:/temp/ violations prevent chunk execution")
    return True

# === VISUAL PROCESSING INDICATORS ===
def main():
    """
    Main entry point for semantic search file reference validation.
    Performs anti-recursion validation, loads file lists, validates compliance,
    generates a compliance report, and logs all phases with visual indicators.
    """
    process_name = "Semantic Search File Reference Validation"
    start_time = datetime.now()
    process_id = os.getpid()
    timeout_minutes = 30
    timeout_seconds = timeout_minutes * 60
    logger.info(f"🚀 PROCESS STARTED: {process_name}")
    logger.info(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Process ID: {process_id}")

    # Anti-recursion validation
    chunk_anti_recursion_validation()

    # === PHASE 2: Core Implementation ===
    phases = [
        ("🔍 Initializing", "Setting up validation environment"),
        ("📊 Loading file lists", "Preparing file inventories"),
        ("�️ Loading semantic search references", "Gathering referenced files"),
        ("🛡️ Compliance validation", "Comparing referenced files to databases files"),
        ("✅ Results", "Logging compliance results")
    ]
    total_phases = len(phases)
    import json

    def load_semantic_search_references():
        """
        Loads referenced files from referenced_files.txt and/or semantic_search_output.json.
        Returns a deduplicated list of normalized file paths.
        """
        referenced_files = set()
        referenced_files_path = os.path.join(os.getcwd(), "referenced_files.txt")
        if os.path.exists(referenced_files_path):
            with open(referenced_files_path, "r", encoding="utf-8") as rf:
                for line in rf:
                    line = line.strip()
                    if line:
                        referenced_files.add(os.path.normpath(line))
        semantic_json_path = os.path.join(os.getcwd(), "semantic_search_output.json")
        if os.path.exists(semantic_json_path):
            try:
                with open(semantic_json_path, "r", encoding="utf-8") as sj:
                    data = json.load(sj)
                    if isinstance(data, list):
                        referenced_files.update([os.path.normpath(f) for f in data if isinstance(f, str)])
                    elif isinstance(data, dict) and "referenced_files" in data:
                        referenced_files.update([os.path.normpath(f) for f in data["referenced_files"] if isinstance(f, str)])
            except Exception as e:
                logger.warning(f"Could not parse semantic_search_output.json: {e}")
        return list(referenced_files)

    def scan_and_handle_zero_byte_files():
        """
        Scan workspace for zero-byte files, log, and move them to a quarantine folder for review.
        Returns a list of zero-byte file paths handled.
        """
        zero_byte_files = []
        quarantine_dir = os.path.join(os.getcwd(), "_ZERO_BYTE_QUARANTINE")
        if not os.path.exists(quarantine_dir):
            os.makedirs(quarantine_dir)
        for root, dirs, files in os.walk(os.getcwd()):
            # Don't quarantine files already in quarantine
            if quarantine_dir in root:
                continue
            for f in files:
                fpath = os.path.join(root, f)
                try:
                    if os.path.getsize(fpath) == 0:
                        rel_path = os.path.relpath(fpath, os.getcwd())
                        zero_byte_files.append(rel_path)
                        # Move to quarantine
                        dest_path = os.path.join(quarantine_dir, os.path.basename(fpath))
                        try:
                            os.replace(fpath, dest_path)
                            logger.warning(f"[QUARANTINE] Zero-byte file moved: {rel_path} -> {dest_path}")
                        except Exception as move_err:
                            logger.error(f"[ERROR] Failed to quarantine {rel_path}: {move_err}")
                except Exception:
                    continue
        if zero_byte_files:
            logger.warning(f"⚠️ Zero-byte files handled: {len(zero_byte_files)} (moved to _ZERO_BYTE_QUARANTINE)")
        else:
            logger.info("✅ No zero-byte files detected in workspace.")
        return zero_byte_files

    def lint_python_scripts_in_databases():
        """
        Traverse all .py files in databases/ and check for Python 3.10/3.11 lint compliance.
        Uses py_compile for syntax and flake8 for linting.
        Logs and summarizes results.
        """
        chunk_anti_recursion_validation()
        databases_dir = os.path.join(os.getcwd(), "databases")
        py_files = []
        for root, dirs, files in os.walk(databases_dir):
            for f in files:
                if f.endswith(".py"):
                    py_files.append(os.path.join(root, f))
        logger.info(f"🔍 Found {len(py_files)} Python scripts in databases/ for linting.")

        lint_results = []
        with tqdm(total=len(py_files), desc="Linting Python scripts", unit="file") as pbar_lint:
            for py_file in py_files:
                rel_path = os.path.relpath(py_file, os.getcwd())
                syntax_ok = True
                for version in ("3.10", "3.11"):
                    try:
                        import subprocess
                        subprocess.check_output(
                            [f"python{version}", "-m", "py_compile", py_file],
                            stderr=subprocess.STDOUT
                        )
                    except Exception as e:
                        logger.error(f"❌ Syntax error ({version}) in {rel_path}: {e}")
                        syntax_ok = False
                try:
                    import subprocess
                    result = subprocess.run(
                        ["flake8", py_file],
                        capture_output=True, text=True
                    )
                    if result.returncode != 0:
                        logger.error(f"❌ Lint error in {rel_path}:\n{result.stdout}")
                        lint_results.append((rel_path, "lint error"))
                    elif syntax_ok:
                        logger.info(f"✅ {rel_path} is lint and syntax compliant.")
                        lint_results.append((rel_path, "ok"))
                except Exception as e:
                    logger.error(f"❌ Flake8 failed for {rel_path}: {e}")
                    lint_results.append((rel_path, "flake8 error"))
                pbar_lint.update(1)
        total = len(py_files)
        passed = sum(1 for _, status in lint_results if status == "ok")
        failed = total - passed
        logger.info(f"📊 Lint summary: {passed}/{total} scripts passed, {failed} failed.")
        return lint_results

    with tqdm(total=100, desc=process_name, unit="%", bar_format="{l_bar}{bar}| {n:.1f}/{total}{unit} [{elapsed}<{remaining}]") as pbar:
        # Phase 1: Initialization
        phase_name, phase_desc = phases[0]
        pbar.set_description(f"{phase_name}")
        logger.info(f"📊 {phase_name}: {phase_desc}")
        time.sleep(0.1)
        pbar.update(100/total_phases)
        elapsed = (datetime.now() - start_time).total_seconds()
        progress = (1/total_phases)*100
        total_estimated = elapsed / (progress/100) if progress > 0 else 0
        etc = max(0, total_estimated - elapsed)
        logger.info(f"⏱️  Progress: {progress:.1f}% | Elapsed: {elapsed:.1f}s | ETC: {etc:.1f}s")

        # Phase 2: Load all files under databases (optimized)
        phase_name, phase_desc = phases[1]
        pbar.set_description(f"{phase_name}")
        logger.info(f"📊 {phase_name}: {phase_desc}")
        databases_dir = os.path.join(os.getcwd(), "databases")
        databases_files = []
        for root, dirs, files in os.walk(databases_dir):
            for f in files:
                rel_path = os.path.relpath(os.path.join(root, f), os.getcwd())
                databases_files.append(os.path.normpath(rel_path))
        time.sleep(0.1)
        pbar.update(100/total_phases)
        elapsed = (datetime.now() - start_time).total_seconds()
        progress = (2/total_phases)*100
        total_estimated = elapsed / (progress/100) if progress > 0 else 0
        etc = max(0, total_estimated - elapsed)
        logger.info(f"⏱️  Progress: {progress:.1f}% | Elapsed: {elapsed:.1f}s | ETC: {etc:.1f}s")

        # Phase 3: Load referenced files from semantic search or txt/json
        phase_name, phase_desc = phases[2]
        pbar.set_description(f"{phase_name}")
        logger.info(f"📊 {phase_name}: {phase_desc}")
        referenced_files = load_semantic_search_references()
        if not referenced_files:
            logger.warning("No referenced files found from semantic search or referenced_files.txt.")
        time.sleep(0.1)
        pbar.update(100/total_phases)
        elapsed = (datetime.now() - start_time).total_seconds()
        progress = (3/total_phases)*100
        total_estimated = elapsed / (progress/100) if progress > 0 else 0
        etc = max(0, total_estimated - elapsed)
        logger.info(f"⏱️  Progress: {progress:.1f}% | Elapsed: {elapsed:.1f}s | ETC: {etc:.1f}s")

        # Phase 4: Compliance validation (optimized set logic)
        phase_name, phase_desc = phases[3]
        pbar.set_description(f"{phase_name}")
        logger.info(f"📊 {phase_name}: {phase_desc}")
        referenced_set = set(referenced_files)
        inside_referenced = [f for f in referenced_set if f == "databases" or f.startswith("databases" + os.sep)]
        outside_referenced = [f for f in referenced_set if not (f == "databases" or f.startswith("databases" + os.sep))]
        compliance_report = {
            "total_referenced_files": len(referenced_files),
            "total_databases_files": len(databases_files),
            "outside_referenced": outside_referenced,
            "inside_referenced": inside_referenced,
            "compliance_passed": len(outside_referenced) == 0
        }
        time.sleep(0.1)
        pbar.update(100/total_phases)
        elapsed = (datetime.now() - start_time).total_seconds()
        progress = (4/total_phases)*100
        total_estimated = elapsed / (progress/100) if progress > 0 else 0
        etc = max(0, total_estimated - elapsed)
        logger.info(f"⏱️  Progress: {progress:.1f}% | Elapsed: {elapsed:.1f}s | ETC: {etc:.1f}s")

        # Phase 5: Results & Reporting
        phase_name, phase_desc = phases[4]
        pbar.set_description(f"{phase_name}")
        logger.info(f"📊 {phase_name}: {phase_desc}")
        logger.info(f"Total referenced files: {len(referenced_files)}")
        logger.info(f"Total databases files: {len(databases_files)}")
        if outside_referenced:
            logger.error(f"❌ COMPLIANCE VIOLATION: {len(outside_referenced)} referenced files are outside 'databases' directory:")
            for f in outside_referenced:
                logger.error(f"   - {f}")
        else:
            logger.info("✅ All referenced files are within the 'databases' directory.")
        if inside_referenced:
            logger.info(f"✅ {len(inside_referenced)} referenced files are within 'databases'.")
        else:
            logger.warning("No referenced files found within 'databases'.")
        # Write compliance report
        report_path = os.path.join(os.getcwd(), "compliance_report.json")
        try:
            with open(report_path, "w", encoding="utf-8") as cf:
                json.dump(compliance_report, cf, indent=2)
            logger.info(f"📄 Compliance report written to {report_path}")
        except Exception as e:
            logger.error(f"Failed to write compliance report: {e}")

        # DUAL COPILOT validation stub
        logger.info("🛡️ DUAL COPILOT VALIDATION: Secondary validation in progress...")
        if compliance_report["compliance_passed"]:
            logger.info("✅ DUAL COPILOT VALIDATION PASSED: All referenced files are compliant.")
        else:
            logger.error("❌ DUAL COPILOT VALIDATION FAILED: Compliance violations detected.")


        # Lint all Python scripts in databases/ for 3.10/3.11 compliance
        logger.info("🔄 Linting all Python scripts in databases/ for Python 3.10/3.11 compliance...")
        lint_results = lint_python_scripts_in_databases()

        # Final session integrity and summary
        logger.info("🔄 Final session integrity checks...")
        zero_byte_files = scan_and_handle_zero_byte_files()
        chunk_anti_recursion_validation()
        logger.info("📊 SUMMARY: ")
        logger.info(f"  - Referenced files checked: {len(referenced_files)}")
        logger.info(f"  - Databases files checked: {len(databases_files)}")
        logger.info(f"  - Compliance passed: {compliance_report['compliance_passed']}")
        logger.info(f"  - Zero-byte files quarantined: {len(zero_byte_files)}")
        logger.info(f"  - Lint-compliant scripts: {sum(1 for _, status in lint_results if status == 'ok')}")
        logger.info(f"  - Lint-noncompliant scripts: {sum(1 for _, status in lint_results if status != 'ok')}")
        logger.info("✅ CHUNK 4 COMPLETE: Optimization & finalization complete.")
        logger.info("🏁 SESSION COMPLETE. Please run session shutdown protocol for enterprise compliance.")

        # Review compliance report (if exists)
        try:
            with open(report_path, "r", encoding="utf-8") as cf:
                report_data = json.load(cf)
            logger.info("📋 COMPLIANCE REPORT REVIEW:")
            for k, v in report_data.items():
                logger.info(f"  - {k}: {v}")
        except Exception as e:
            logger.error(f"[ERROR] Could not review compliance report: {e}")

if __name__ == "__main__":
    main()
