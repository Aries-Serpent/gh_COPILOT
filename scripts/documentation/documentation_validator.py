"""Documentation validation and compliance automation."""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Iterable

__all__ = ["DocumentationValidator"]


class DocumentationValidator:
    """Validate documentation coverage and link integrity.

    The validator scans Markdown files for ``[text](link)`` patterns and
    ensures referenced local files exist. It also logs a simple coverage
    metric comparing the number of documents to tracked modules. The method
    returns ``True`` when no broken links are found.
    """

    LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    # ------------------------------------------------------------------
    def _iter_markdown(self, docs_path: Path) -> Iterable[Path]:
        """Yield markdown files under ``docs_path``."""
        return docs_path.rglob("*.md")

    # ------------------------------------------------------------------
    def _check_links(self, md_file: Path) -> list[str]:
        """Return broken local links found in ``md_file``."""
        text = md_file.read_text(encoding="utf-8")
        broken: list[str] = []
        for link in self.LINK_RE.findall(text):
            if link.startswith(("http://", "https://", "#")):
                continue
            target = (md_file.parent / link).resolve()
            if not target.exists():
                broken.append(link)
        return broken

    # ------------------------------------------------------------------
    def validate(self, docs_path: Path, *, min_coverage: float | None = None) -> bool:
        """Validate documentation in ``docs_path``.

        Parameters
        ----------
        docs_path:
            Directory containing documentation files.
        min_coverage:
            Optional minimum ratio of documentation files to project modules.

        Returns
        -------
        bool
            ``True`` if all checks pass, ``False`` otherwise.
        """

        md_files = list(self._iter_markdown(docs_path))
        broken_links: list[tuple[Path, str]] = []
        for md in md_files:
            for link in self._check_links(md):
                broken_links.append((md, link))

        modules = list(Path("scripts").rglob("*.py"))
        coverage = len(md_files) / max(len(modules), 1)

        for md, link in broken_links:
            self.logger.error("Broken link %s in %s", link, md)

        self.logger.info(
            "Documentation coverage %.2f%% (%d docs / %d modules)",
            coverage * 100,
            len(md_files),
            len(modules),
        )

        if min_coverage is not None and coverage < min_coverage:
            self.logger.warning("Coverage %.2f below minimum %.2f", coverage, min_coverage)
            return False

        return not broken_links
