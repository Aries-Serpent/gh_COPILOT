"""Compliance monitoring helpers for the web GUI."""

from __future__ import annotations

from typing import Dict

__all__ = ["check_compliance"]


REQUIRED_KEYS = {"policy", "status"}


def check_compliance(data: Dict[str, str]) -> bool:
    """Naive compliance check ensuring required fields are present."""
    return REQUIRED_KEYS.issubset(data.keys())
