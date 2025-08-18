from __future__ import annotations

"""Deploy the web GUI to the production environment.

This script reflects the new ``web_gui`` directory layout at the repository
root.
"""

from pathlib import Path
import os
from dataclasses import dataclass
from datetime import datetime
import sqlite3
import argparse
from typing import Optional

from .environment_migration import migrate_environment
from .backup_manager import create_backup
from .data_migration import migrate_data
from .quantum_deployment import deploy_quantum_modules
from .rollback_procedures import rollback

WORKSPACE = Path(os.environ.get("GH_COPILOT_WORKSPACE", Path(__file__).resolve().parents[2]))
WEB_GUI_PATH = WORKSPACE / "web_gui"
ANALYTICS_DB = Path(os.environ.get("GH_COPILOT_ANALYTICS_DB", WORKSPACE / "analytics.db"))
DEPLOYMENT_LOCK = WORKSPACE / "deployment.lock"


def log_deployment_event(event: str, status: str = "", db_path: Optional[Path] = None) -> None:
    """Record a deployment event in ``deployment_events`` table."""

    if db_path is None:
        db_path = ANALYTICS_DB
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    try:
        cur = conn.cursor()
        cur.execute(
            "CREATE TABLE IF NOT EXISTS deployment_events (event TEXT, status TEXT, timestamp TEXT)"
        )
        cur.execute(
            "INSERT INTO deployment_events (event, status, timestamp) VALUES (?, ?, ?)",
            (event, status, datetime.utcnow().isoformat()),
        )
        conn.commit()
    finally:
        conn.close()


@dataclass
class DeploymentRequest:
    """Contract for deployment input."""

    environment: str
    include_quantum: bool = True


@dataclass
class DeploymentResult:
    """Contract for deployment output."""

    message: str
    success: bool = True


def validate_deployment_request(request: DeploymentRequest) -> None:
    """Assert that the deployment request complies with the contract."""

    if request.environment != "production":
        raise ValueError("environment must be 'production'")


def deploy(request: DeploymentRequest, *, dry_run: bool = False) -> DeploymentResult:
    """Execute deployment based on ``request``."""

    validate_deployment_request(request)
    if DEPLOYMENT_LOCK.exists():
        raise RuntimeError("another deployment is in progress")
    DEPLOYMENT_LOCK.write_text(str(os.getpid()))
    try:
        if dry_run:
            plan = [
                f"migrate environment {request.environment}",
                "migrate analytics data",
                f"create backup for {request.environment}",
            ]
            if request.include_quantum:
                plan.append("deploy quantum modules")
            message = "Dry run deployment plan:\n- " + "\n- ".join(plan)
            print(message)
            log_deployment_event("dry_run", "planned")
            return DeploymentResult(message=message)

        log_deployment_event("start", "pending")
        try:
            migrate_environment([request.environment])
            migrate_data("analytics", request.environment)
            create_backup(request.environment)
            if request.include_quantum:
                deploy_quantum_modules()
            message = (
                f"Deploying web GUI from {WEB_GUI_PATH} to {request.environment} environment"
            )
            if request.include_quantum:
                message += " with quantum modules"
            print(message)
            log_deployment_event("success", "completed")
            return DeploymentResult(message=message)
        except Exception as exc:  # pragma: no cover - exercised via tests
            log_deployment_event("failure", str(exc))
            rollback()
            log_deployment_event("rolled_back", "completed")
            return DeploymentResult(message=str(exc), success=False)
    finally:
        if DEPLOYMENT_LOCK.exists():
            DEPLOYMENT_LOCK.unlink()


def deploy_to_production(*, dry_run: bool = False) -> DeploymentResult:
    """Backward compatible helper for production deployment."""

    return deploy(DeploymentRequest(environment="production"), dry_run=dry_run)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Deploy web GUI to production")
    parser.add_argument("--dry-run", action="store_true", help="plan deployment without executing")
    return parser


if __name__ == "__main__":
    args = _build_parser().parse_args()
    deploy_to_production(dry_run=args.dry_run)
