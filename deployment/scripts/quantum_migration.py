#!/usr/bin/env python3
"""Quantum-specific migration helpers."""

from __future__ import annotations

from .environment_migration import migrate_environment


def migrate_quantum() -> list[str]:
    """Run migrations for the quantum database."""
    return migrate_environment(["quantum"])


__all__ = ["migrate_quantum"]
