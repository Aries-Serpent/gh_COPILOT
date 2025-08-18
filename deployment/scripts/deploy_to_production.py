from __future__ import annotations

"""Deploy the web GUI to the production environment.

This script reflects the new ``web_gui`` directory layout at the repository
root.
"""

from pathlib import Path
import os
from dataclasses import dataclass

from .environment_migration import migrate_environment
from .backup_manager import create_backup
from .data_migration import migrate_data
from .quantum_deployment import deploy_quantum_modules

WORKSPACE = Path(os.environ.get("GH_COPILOT_WORKSPACE", Path(__file__).resolve().parents[2]))
WEB_GUI_PATH = WORKSPACE / "web_gui"


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


def deploy(request: DeploymentRequest) -> DeploymentResult:
    """Execute deployment based on ``request``."""

    validate_deployment_request(request)
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
    return DeploymentResult(message=message)


def deploy_to_production() -> DeploymentResult:
    """Backward compatible helper for production deployment."""

    return deploy(DeploymentRequest(environment="production"))


if __name__ == "__main__":
    deploy_to_production()
