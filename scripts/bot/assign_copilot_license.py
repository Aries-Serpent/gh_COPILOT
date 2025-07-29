#!/usr/bin/env python3
"""Manage GitHub Copilot seat assignments via REST API."""
# pyright: reportMissingImports=false

from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import Any

import requests
from tqdm import tqdm

from utils.cross_platform_paths import (
    CrossPlatformPathManager,
    verify_environment_variables,
)
from scripts.validation.dual_copilot_orchestrator import DualCopilotOrchestrator

TEXT_INDICATORS = {
    "start": "[START]",
    "progress": "[PROGRESS]",
    "success": "[SUCCESS]",
    "error": "[ERROR]",
}

API_ROOT = "https://api.github.com"


def setup_logger() -> logging.Logger:
    backup_root = CrossPlatformPathManager.get_backup_root()
    log_dir = backup_root / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"copilot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    logging.basicConfig(
        level=logging.INFO,
        handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    return logging.getLogger(__name__)


def assign_license(username: str, enable: bool = True) -> bool:
    """Assign or revoke Copilot seat for ``username``."""
    logger = logging.getLogger(__name__)
    token = os.environ.get("GITHUB_TOKEN")
    org = os.environ.get("GITHUB_ORG")
    if not token or not org:
        logger.error("%s Missing GITHUB_TOKEN or GITHUB_ORG", TEXT_INDICATORS["error"])
        return False

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }
    operation = "assign" if enable else "unassign"
    url = f"{API_ROOT}/orgs/{org}/copilot/billing/{operation}s"
    payload: dict[str, Any] = {"usernames": [username]}
    with tqdm(total=1, desc=f"{TEXT_INDICATORS['progress']} {operation}", unit="op") as bar:
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        bar.update(1)

    if resp.status_code >= 400:
        logger.error("%s API error: %s", TEXT_INDICATORS["error"], resp.text)
        return False

    logger.info("%s %s seat for %s", TEXT_INDICATORS["success"], operation, username)
    return True


def main() -> None:
    verify_environment_variables()
    logger = setup_logger()
    start = datetime.now()
    logger.info("%s License manager started", TEXT_INDICATORS["start"])

    import argparse

    parser = argparse.ArgumentParser(description="Manage Copilot seats")
    parser.add_argument("username", help="GitHub username")
    parser.add_argument("--revoke", action="store_true", help="Revoke seat")
    args = parser.parse_args()

    orchestrator = DualCopilotOrchestrator(logger)

    def _primary() -> bool:
        return assign_license(args.username, not args.revoke)

    primary_success, validation_success = orchestrator.run(_primary, [__file__])

    duration = (datetime.now() - start).total_seconds()
    if primary_success and validation_success:
        logger.info(
            "%s Completed in %.2fs", TEXT_INDICATORS["success"], duration
        )
    else:
        logger.error("%s Failed in %.2fs", TEXT_INDICATORS["error"], duration)


if __name__ == "__main__":
    main()
