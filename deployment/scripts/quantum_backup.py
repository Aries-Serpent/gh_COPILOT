#!/usr/bin/env python3
"""Quantum database backup helpers."""

from __future__ import annotations

from pathlib import Path

from .backup_manager import create_backup


def backup_quantum(backup_root: Path | None = None) -> Path:
    """Create a backup specifically for the quantum database."""
    return create_backup("quantum", backup_root)


__all__ = ["backup_quantum"]
