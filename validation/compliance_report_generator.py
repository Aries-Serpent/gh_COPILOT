from __future__ import annotations

import json
import logging
from utils.log_utils import _log_plain
from utils.validation_utils import calculate_composite_compliance_score
import os
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from tqdm import tqdm

DEFAULT_ANALYTICS_DB = Path("databases/analytics.db")
LOGS_DIR = Path("artifacts/logs/template_rendering")
LOGS_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOGS_DIR / f"compliance_report_generator_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler(sys.stdout)],
)


def validate_no_recursive_folders() -> None:
    workspace_root = Path(os.getenv("GH_COPILOT_WORKSPACE", Path.cwd()))
    forbidden_patterns = ["*backup*", "*_backup_*", "backups", "*temp*"]
    for pattern in forbidden_patterns:
        for folder in workspace_root.rglob(pattern):
            if folder.is_dir() and folder != workspace_root:
                logging.error(f"Recursive folder detected: {folder}")
                raise RuntimeError(f"CRITICAL: Recursive folder violation: {folder}")


def _parse_ruff(path: Path) -> Dict[str, Any]:
    """
    Parse Ruff output file for issue count.
    """
    issues = 0
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                issues += 1
    return {"issues": issues}


def _parse_pytest(path: Path) -> Dict[str, Any]:
    """
    Parse Pytest JSON report for test metrics.
    """
    if not path.exists():
        return {"total": 0, "passed": 0, "failed": 0}
    data = json.loads(path.read_text(encoding="utf-8"))
    summary = data.get("summary", {})
    return {
        "total": summary.get("total", 0),
        "passed": summary.get("passed", 0),
        "failed": summary.get("failed", 0),
    }


def calculate_etc(start_time: float, current_progress: int, total_work: int) -> str:
    elapsed = time.time() - start_time
    if current_progress > 0:
        total_estimated = elapsed / (current_progress / total_work)
        remaining = total_estimated - elapsed
        return f"{remaining:.2f}s remaining"
    return "N/A"


def generate_compliance_report(
    ruff_file: Path,
    pytest_file: Path,
    output_dir: Path,
    analytics_db: Path = DEFAULT_ANALYTICS_DB,
    timeout_minutes: int = 30,
) -> Dict[str, Any]:
    """Generate compliance report from Ruff and Pytest outputs.

    Parameters
    ----------
    ruff_file : Path
        Path to the Ruff output file.
    pytest_file : Path
        Path to the Pytest JSON report.
    output_dir : Path
        Directory where generated reports will be written.
    analytics_db : Path, optional
        Path to analytics database used for logging metrics.
    timeout_minutes : int, optional
        Maximum allowed runtime in minutes.

    Returns
    -------
    Dict[str, Any]
        Summary dictionary with Ruff and Pytest metrics.
    """
    validate_no_recursive_folders()
    start_time_dt = datetime.now()
    process_id = os.getpid()
    timeout_seconds = timeout_minutes * 60
    _log_plain("PROCESS STARTED: Compliance Report Generation")
    _log_plain(f"Start Time: {start_time_dt.strftime('%Y-%m-%d %H:%M:%S')}")
    _log_plain(f"Process ID: {process_id}")
    output_dir.mkdir(parents=True, exist_ok=True)
    total_steps = 4
    start_time = time.time()
    with tqdm(total=total_steps, desc="Compliance Report Generation", unit="step") as bar:
        bar.set_description("Parsing Ruff Output")
        ruff_metrics = _parse_ruff(ruff_file)
        bar.update(1)
        elapsed = time.time() - start_time
        etc = calculate_etc(start_time, 1, total_steps)
        bar.set_postfix(ETC=etc)
        if elapsed > timeout_seconds:
            raise TimeoutError(f"Process exceeded {timeout_minutes} minute timeout")

        bar.set_description("Parsing Pytest Output")
        pytest_metrics = _parse_pytest(pytest_file)
        bar.update(1)
        elapsed = time.time() - start_time
        etc = calculate_etc(start_time, 2, total_steps)
        bar.set_postfix(ETC=etc)
        if elapsed > timeout_seconds:
            raise TimeoutError(f"Process exceeded {timeout_minutes} minute timeout")

        timestamp = datetime.utcnow().isoformat()
        composite_score = calculate_composite_compliance_score(
            ruff_metrics["issues"],
            pytest_metrics["passed"],
            pytest_metrics["failed"],
        )
        summary = {
            "timestamp": timestamp,
            "ruff": ruff_metrics,
            "pytest": pytest_metrics,
            "composite_score": composite_score,
            "process_id": process_id,
            "start_time": start_time_dt.isoformat(),
        }

        bar.set_description("Writing Reports")
        json_path = output_dir / "compliance_report.json"
        json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        md_path = output_dir / "compliance_report.md"
        with open(md_path, "w", encoding="utf-8") as md:
            md.write("# Compliance Report\n\n")
            md.write(f"**Timestamp:** {summary['timestamp']}\n\n")
            md.write(f"**Process ID:** {process_id}\n")
            md.write(f"**Start Time:** {start_time_dt.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            md.write(f"## Ruff Issues: {ruff_metrics['issues']}\n")
            md.write(
                f"## Pytest Results: {pytest_metrics['passed']} passed / {pytest_metrics['failed']} failed of {pytest_metrics['total']} total\n"
            )
            md.write(
                f"## Composite Compliance Score: {composite_score:.2f}\n"
            )
        bar.update(1)
        elapsed = time.time() - start_time
        etc = calculate_etc(start_time, 3, total_steps)
        bar.set_postfix(ETC=etc)
        if elapsed > timeout_seconds:
            raise TimeoutError(f"Process exceeded {timeout_minutes} minute timeout")

        bar.set_description("Logging Metrics to Database")
        analytics_db.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(analytics_db) as conn:
            conn.execute(
                """CREATE TABLE IF NOT EXISTS code_quality_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ruff_issues INTEGER,
                    tests_passed INTEGER,
                    tests_failed INTEGER,
                    composite_score REAL,
                    ts TEXT,
                    process_id INTEGER
                )"""
            )
            try:
                conn.execute("ALTER TABLE code_quality_metrics ADD COLUMN composite_score REAL")
            except sqlite3.OperationalError:
                pass
            conn.execute(
                "INSERT INTO code_quality_metrics (ruff_issues, tests_passed, tests_failed, composite_score, ts, process_id) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    ruff_metrics["issues"],
                    pytest_metrics["passed"],
                    pytest_metrics["failed"],
                    composite_score,
                    summary["timestamp"],
                    process_id,
                ),
            )
            conn.commit()
        bar.update(1)
        elapsed = time.time() - start_time
        etc = calculate_etc(start_time, 4, total_steps)
        bar.set_postfix(ETC=etc)
        if elapsed > timeout_seconds:
            raise TimeoutError(f"Process exceeded {timeout_minutes} minute timeout")
    _log_plain(f"Compliance report generation completed in {elapsed:.2f}s | ETC: {etc}")
    return summary


def validate_report(output_dir: Path) -> bool:
    """
    Validate that compliance report JSON exists and is non-zero-byte.
    """
    json_path = output_dir / "compliance_report.json"
    return json_path.exists() and json_path.stat().st_size > 0


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate compliance report")
    parser.add_argument("--ruff", type=Path, required=True, help="Ruff output file")
    parser.add_argument("--pytest", type=Path, required=True, help="Pytest JSON report")
    parser.add_argument("--output", type=Path, default=Path("validation"), help="Output directory")
    parser.add_argument(
        "--db",
        type=Path,
        default=Path("databases") / "analytics.db",
        help="Analytics database path",
    )
    parser.add_argument("--timeout", type=int, default=30, help="Timeout in minutes")
    args = parser.parse_args()

    _log_plain("[START] Generating compliance report")
    result = generate_compliance_report(args.ruff, args.pytest, args.output, args.db, args.timeout)
    _log_plain("[SUCCESS] " + json.dumps(result, indent=2))

__all__ = ["generate_compliance_report", "validate_report"]
