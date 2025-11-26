"""Checkpoint management with RNG state support."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import torch

LOGGER = logging.getLogger(__name__)


@dataclass
class CheckpointState:
    """Container for checkpoint state including RNG."""

    model_state: Dict[str, Any]
    optimizer_state: Optional[Dict[str, Any]] = None
    scheduler_state: Optional[Dict[str, Any]] = None
    rng_state: Optional[Dict[str, Any]] = None


class CheckpointManager:
    """Manages saving and loading checkpoints with RNG state."""

    def __init__(self, root: Path) -> None:
        self._root = root
        self._root.mkdir(parents=True, exist_ok=True)

    def save(self, name: str, state: CheckpointState) -> Path:
        path = self._root / f"{name}.pt"
        torch.save(state.__dict__, path)
        LOGGER.info("Saved checkpoint: %s", path)
        return path

    def load(self, name: str) -> CheckpointState:
        path = self._root / f"{name}.pt"
        payload = torch.load(path, map_location="cpu")
        LOGGER.info("Loaded checkpoint: %s", path)
        return CheckpointState(**payload)