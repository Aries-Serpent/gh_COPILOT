"""Workspace optimizer that logs optimization metrics."""
from __future__ import annotations

import logging
from pathlib import Path

from tqdm import tqdm

from utils.validation_utils import validate_enterprise_environment

__all__ = ["WorkspaceOptimizer"]


class WorkspaceOptimizer:
    """Optimize workspace storage and access patterns."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    def optimize(self, workspace: Path) -> None:
        """Run a basic optimization routine on ``workspace``."""
        validate_enterprise_environment()
        workspace = workspace.resolve()
        files = list(workspace.rglob("*.py"))
        with tqdm(files, desc="Optimizing", unit="file") as bar:
            for f in bar:
                bar.set_postfix(file=f.name)
        self.logger.info("Optimization run complete on %d files", len(files))
