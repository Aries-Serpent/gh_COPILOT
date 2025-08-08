"""Helper utilities for documentation management."""

from __future__ import annotations

from typing import Iterable, List

TEXT_FORMATS = {"md", "html"}


def ensure_accessible_formats(formats: Iterable[str]) -> List[str]:
    """Normalize and de-duplicate output formats.

    Ensures that if a PDF output is requested, at least one accessible text
    format (Markdown or HTML) is also present. Input format names are treated in
    a case-insensitive manner and returned in lower-case order of first
    appearance without duplicates.
    """

    seen: list[str] = []
    result: list[str] = []
    for fmt in formats:
        lower = fmt.lower()
        if lower not in seen:
            seen.append(lower)
            result.append(lower)
    if "pdf" in seen and not (TEXT_FORMATS & set(seen)):
        # Ensure markdown companion for PDF-only requests
        if "md" not in seen:
            result.append("md")
    return result

