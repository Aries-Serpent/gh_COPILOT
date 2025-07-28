"""Documentation validation and compliance automation."""
from __future__ import annotations

import logging
from pathlib import Path
import re

__all__ = ["DocumentationValidator"]


class DocumentationValidator:
    """Validate documentation coverage and link integrity.

    Parameters
    ----------
    docs_path:
        Root directory containing documentation files. Markdown files will be
        scanned for missing targets and invalid links.
    min_ratio:
        Optional minimum ratio of markdown files to tracked Python modules.
        If provided, the validator will warn when documentation coverage falls
        below this threshold.
    """

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    def _find_markdown_files(self, docs_path: Path) -> list[Path]:
        """Return all markdown files under ``docs_path``."""
        if not docs_path.exists():
            self.logger.error("Documentation path %s does not exist", docs_path)
            return []
        return list(docs_path.rglob("*.md"))

    def _check_links(self, md_file: Path) -> bool:
        """Return ``True`` if all local links in ``md_file`` exist."""
        pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
        content = md_file.read_text(encoding="utf-8")
        success = True
        for match in pattern.findall(content):
            link = match.split("#", 1)[0]
            if re.match(r"^[a-z]+://", link) or not link or link.startswith("#"):
                continue
            target = (md_file.parent / link).resolve()
            if not target.exists():
                self.logger.error("Broken link in %s: %s", md_file, link)
                success = False
        return success

    def _coverage_ratio(self, docs: list[Path], modules_root: Path) -> float:
        """Return documentation coverage ratio."""
        modules = list(modules_root.rglob("*.py"))
        if not modules:
            return 1.0
        return len(docs) / len(modules)

    def validate(self, docs_path: Path, *, min_ratio: float | None = None) -> bool:
        """Validate documentation under ``docs_path``.

        Parameters
        ----------
        docs_path:
            Directory containing markdown documentation.
        min_ratio:
            Optional minimum documentation-to-module ratio.

        Returns
        -------
        bool
            ``True`` if no issues are detected, ``False`` otherwise.
        """
        md_files = self._find_markdown_files(docs_path)
        if not md_files:
            self.logger.warning("No markdown files found under %s", docs_path)
            return False

        success = True
        for md in md_files:
            if not self._check_links(md):
                success = False

        if min_ratio is not None:
            ratio = self._coverage_ratio(md_files, Path("scripts"))
            if ratio < min_ratio:
                self.logger.warning(
                    "Documentation coverage %.2f below minimum %.2f", ratio, min_ratio
                )
                success = False

        self.logger.info(
            "Validated %s markdown files under %s", len(md_files), docs_path
        )
        return success
