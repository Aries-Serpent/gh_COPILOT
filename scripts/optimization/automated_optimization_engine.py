"""Automated optimization engine for continuous improvements.

This engine removes simple sources of bloat such as trailing whitespace and
dead ``pass`` statements. Each optimization is logged to ``analytics.db`` using
``_log_event`` so progress can be tracked over time.
"""
from __future__ import annotations

import argparse
import logging
import os
from pathlib import Path

from tqdm import tqdm
from utils.log_utils import _log_event

__all__ = ["AutomatedOptimizationEngine", "parse_args", "main"]


class AutomatedOptimizationEngine:
    """Continuously optimize Python files inside a workspace."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def _strip_dead_code(text: str) -> str:
        """Remove ``pass`` statements that are the sole body of a block."""

        lines = text.splitlines()
        cleaned: list[str] = []
        for idx, line in enumerate(lines):
            stripped = line.strip()
            if stripped == "pass":
                prev = lines[idx - 1] if idx > 0 else ""
                if prev.rstrip().endswith(":"):
                    continue
            cleaned.append(line.rstrip())
        return "\n".join(cleaned) + ("\n" if cleaned else "")

    def _optimize_file(self, path: Path) -> int:
        try:
            original = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return 0

        optimized = self._strip_dead_code(original)
        if optimized != original:
            path.write_text(optimized, encoding="utf-8")
        return len(original) - len(optimized)

    def optimize(self, workspace: Path) -> None:
        """Perform optimization over ``workspace`` and log metrics."""

        workspace = workspace.resolve()
        analytics_db = workspace / "databases" / "analytics.db"
        files = list(workspace.rglob("*.py"))
        total_reduction = 0
        with tqdm(files, desc="Optimizing", unit="file") as bar:
            for f in bar:
                bar.set_postfix(file=f.name)
                reduction = self._optimize_file(f)
                total_reduction += reduction
                _log_event(
                    {
                        "event": "optimization_metric",
                        "file": f.name,
                        "size_reduction": reduction,
                    },
                    table="optimization_metrics",
                    db_path=analytics_db,
                )
        self.logger.info(
            "Optimization completed on %d files | total bytes saved=%d",
            len(files),
            total_reduction,
        )


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run automated optimization")
    parser.add_argument(
        "workspace",
        nargs="?",
        type=Path,
        default=Path(os.getenv("GH_COPILOT_WORKSPACE", ".")),
        help="Workspace path",
    )
    return parser.parse_args(args)


def main(args: list[str] | None = None) -> int:
    ns = parse_args(args)
    AutomatedOptimizationEngine().optimize(ns.workspace)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
