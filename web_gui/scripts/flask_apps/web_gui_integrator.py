"""Web GUI integration layer for the enterprise dashboard."""
from __future__ import annotations

import logging
from pathlib import Path

__all__ = ["WebGUIIntegrator"]


class WebGUIIntegrator:
    """Integrate Flask dashboard with production database."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)

    def initialize(self) -> None:
        """Initialize the integration with Flask dashboard."""
        self.logger.info("Initialized Web GUI integrator with %s", self.db_path)
