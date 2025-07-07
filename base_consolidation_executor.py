#!/usr/bin/env python3
"""Base class providing shared consolidation utilities."""

from __future__ import annotations

import hashlib
import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


class BaseConsolidationExecutor:
    """Common utilities for consolidation executors."""

    def __init__(self, workspace_root: str, archive_root: str, group_name: str, logger: logging.Logger) -> None:
        self.workspace_root = Path(workspace_root)
        self.archive_root = Path(archive_root)
        self.group_name = group_name
        self.logger = logger
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        self.archive_dir = self.archive_root / \
            "consolidated_scripts" / group_name / self.timestamp
        self.manifest_dir = self.archive_root / "manifests"
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        self.manifest_dir.mkdir(parents=True, exist_ok=True)

    def discover_files(self, patterns: Iterable[str], exclude_names: Iterable[str] | None = None) -> List[Path]:
        """Discover files in the workspace matching patterns."""
        exclude_names = set(exclude_names or [])
        discovered: List[Path] = []

        for pattern in patterns:
            try:
                for path in self.workspace_root.rglob(pattern):
                    if path.is_file() and path.name not in exclude_names:
                        discovered.append(path)
            except Exception as exc:  # pragma: no cover - logging only
                self.logger.warning(
                    "Pattern search failed for %s: %s", pattern, exc)

        self.logger.info("Discovered %s files", len(discovered))
        return discovered

    def archive_files(self, files: Iterable[Path]) -> List[Tuple[Path, Path]]:
        """Archive files preserving relative paths.

        Returns a list of ``(source, target)`` tuples for successfully archived
        files.
        """
        archived: List[Tuple[Path, Path]] = []
        for path in files:
            try:
                relative = path.relative_to(self.workspace_root)
                target = self.archive_dir / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, target)
                archived.append((path, target))
            except Exception as exc:  # pragma: no cover - logging only
                self.logger.error("Failed to archive %s: %s", path, exc)
        self.logger.info("Archived %s files", len(archived))
        return archived

    @staticmethod
    def calculate_file_hash(file_path: Path) -> str:
        """Return SHA256 hash of a file."""
        try:
            hash_sha = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha.update(chunk)
            return hash_sha.hexdigest()
        except Exception:  # pragma: no cover - logging only
            return "HASH_ERROR"

    def generate_manifest(self, manifest_data: Dict) -> str:
        """Write manifest JSON to disk and return the path."""
        manifest_path = self.manifest_dir / \
            f"{self.group_name}_consolidation_{self.timestamp}.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, indent=2, default=str)
        self.logger.info("Manifest written to %s", manifest_path)
        return str(manifest_path)
