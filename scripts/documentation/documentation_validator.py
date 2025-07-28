"""Documentation validation and compliance automation."""
from __future__ import annotations

import logging
from pathlib import Path
import re

__all__ = ["DocumentationValidator"]


class DocumentationValidator:
    """Validate documentation coverage and link integrity.

    The validator scans Markdown files for ``[text](link)`` patterns and
    ensures referenced local files exist. It also logs a simple coverage
    metric comparing the number of documents to tracked modules. The method
    returns ``True`` when no broken links are found.
    """

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    def validate(self, docs_path: Path) -> bool:
        """Validate documentation coverage under ``docs_path``.

        Parameters
        ----------
        docs_path:
            Path to the documentation root.

        Returns
        -------
        bool
            ``True`` if no broken links were found.
        """
        docs_path = docs_path.resolve()
        md_files = list(docs_path.rglob("*.md"))
        link_re = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
        broken: list[str] = []

        for md in md_files:
            text = md.read_text(errors="ignore")
            for target in link_re.findall(text):
                if "://" in target:
                    continue
                target_path = (md.parent / target.split("#")[0]).resolve()
                if not target_path.exists():
                    broken.append(f"{md}:{target}")

        modules = list(Path("enterprise_modules").rglob("*.py"))
        self.logger.info(
            "Documentation files: %d | Tracked modules: %d",
            len(md_files),
            len(modules),
        )

        for item in broken:
            self.logger.warning("Broken link: %s", item)

        return not broken
