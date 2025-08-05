from __future__ import annotations

import argparse
import json
import re
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from tqdm import tqdm

from enterprise_modules.compliance import validate_enterprise_operation
from dashboard.compliance_metrics_updater import ComplianceMetricsUpdater
from utils.log_utils import log_message


TEXT = {
    "start": "[START]",
    "success": "[SUCCESS]",
    "error": "[ERROR]",
    "info": "[INFO]",
    "progress": "[PROGRESS]",
    "complete": "[COMPLETE]",
}


def _parse_report(path: Path) -> List[Dict[str, str]]:
    """Return tasks extracted from a JSON or Markdown report."""

    if path.suffix.lower() == ".md":
        tasks: List[Dict[str, str]] = []
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            match = re.match(r"- \[ \] (.*)", line)
            if not match:
                continue
            desc = match.group(1)
            file_match = re.search(r" in (.*):(\d+)", desc)
            pattern_match = re.search(r"Remove (.*?) in", desc)
            context_match = re.search(r" - (.*)$", desc)
            tasks.append(
                {
                    "task": desc,
                    "file": file_match.group(1) if file_match else "",
                    "line": file_match.group(2) if file_match else "0",
                    "pattern": pattern_match.group(1) if pattern_match else "",
                    "context": context_match.group(1) if context_match else "",
                }
            )
        return tasks
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "tasks" in data:
        return data["tasks"]
    return data


def _open_stub(task: Dict[str, str], ticket_dir: Path) -> Path:
    """Create a tracking ticket/PR stub for ``task``."""

    ticket_dir.mkdir(parents=True, exist_ok=True)
    validate_enterprise_operation(str(ticket_dir))
    name = f"{Path(task['file']).name}_{task['line']}_{task['pattern']}".replace(" ", "_")
    stub = ticket_dir / f"{name}.md"
    content = (
        f"# Placeholder Resolution\n\n{task['task']}\n\n"
        f"Created: {datetime.now().isoformat()}\n"
    )
    stub.write_text(content, encoding="utf-8")
    return stub


def _update_tracking(db_path: Path, task: Dict[str, str]) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            UPDATE todo_fixme_tracking
               SET status='ticketed'
             WHERE file_path=? AND line_number=? AND placeholder_type=? AND resolved=0
            """,
            (task["file"], int(task["line"]), task["pattern"]),
        )
        conn.commit()


def main(
    *,
    report: str,
    analytics_db: str,
    ticket_dir: str = "reports/placeholder_tickets",
    dashboard_dir: str = "dashboard/compliance",
    simulate: bool = False,
) -> int:
    """Read placeholder report and open tracking stubs."""

    report_path = Path(report)
    analytics = Path(analytics_db)
    tickets = Path(ticket_dir)
    tasks = _parse_report(report_path)

    log_message(__name__, f"{TEXT['start']} enforcing {len(tasks)} placeholders")
    created = 0
    with tqdm(total=len(tasks), desc=f"{TEXT['progress']} enforcing", unit="task") as bar:
        for task in tasks:
            _open_stub(task, tickets)
            if not simulate:
                _update_tracking(analytics, task)
            created += 1
            bar.update(1)
    if not simulate:
        updater = ComplianceMetricsUpdater(Path(dashboard_dir), test_mode=simulate)
        updater.update(simulate=simulate)
        updater.validate_update()
    log_message(__name__, f"{TEXT['complete']} created {created} stubs")
    return created


def parse_args(argv: List[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create tracking tickets or PR stubs from placeholder report",
    )
    parser.add_argument("--report", required=True, help="Path to placeholder task report")
    parser.add_argument("--analytics-db", required=True, help="analytics.db location")
    parser.add_argument(
        "--ticket-dir",
        default="reports/placeholder_tickets",
        help="Directory to write ticket stubs",
    )
    parser.add_argument(
        "--dashboard-dir",
        default="dashboard/compliance",
        help="Dashboard compliance directory",
    )
    parser.add_argument(
        "--simulate",
        action="store_true",
        help="Run in test mode without database writes",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    args = parse_args()
    main(
        report=args.report,
        analytics_db=args.analytics_db,
        ticket_dir=args.ticket_dir,
        dashboard_dir=args.dashboard_dir,
        simulate=args.simulate,
    )
