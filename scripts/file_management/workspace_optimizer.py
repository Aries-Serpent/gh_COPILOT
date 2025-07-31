"""Workspace optimizer that logs optimization metrics."""
from __future__ import annotations

import logging
from pathlib import Path
import sqlite3
import gzip
import shutil
from datetime import datetime, timedelta

from utils.cross_platform_paths import CrossPlatformPathManager
from scripts.validation.dual_copilot_orchestrator import DualCopilotOrchestrator

from tqdm import tqdm

from utils.validation_utils import validate_enterprise_environment

__all__ = ["WorkspaceOptimizer"]


class WorkspaceOptimizer:
    """Optimize workspace storage and access patterns."""

    DAYS_UNUSED = 365

    def __init__(self, db_path: Path | None = None) -> None:
        self.logger = logging.getLogger(__name__)
        self.db_path = db_path or CrossPlatformPathManager.get_workspace_path() / "databases" / "production.db"
        self.conn = sqlite3.connect(self.db_path)
        self._init_metrics_table()

    def _init_metrics_table(self) -> None:
        with self.conn:
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS workspace_optimization_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT NOT NULL,
                    action TEXT NOT NULL,
                    original_size INTEGER,
                    new_size INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def _get_old_files(self, workspace: Path) -> list[Path]:
        cutoff = datetime.now() - timedelta(days=self.DAYS_UNUSED)
        with self.conn:
            cur = self.conn.execute(
                "SELECT script_path FROM tracked_scripts WHERE last_modified < ?",
                (cutoff.strftime("%Y-%m-%d %H:%M:%S"),),
            )
            candidates = [workspace / row[0].lstrip("/") for row in cur.fetchall()]
        return [p for p in candidates if p.exists()]

    def _archive_file(self, file_path: Path, archive_dir: Path) -> tuple[int, int]:
        original_size = file_path.stat().st_size
        archive_dir.mkdir(parents=True, exist_ok=True)
        dest = archive_dir / f"{file_path.name}.gz"
        with open(file_path, "rb") as f_in, gzip.open(dest, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
        new_size = dest.stat().st_size
        file_path.unlink()
        return original_size, new_size

    def _log_metric(self, file_path: Path, original_size: int, new_size: int) -> None:
        with self.conn:
            self.conn.execute(
                "INSERT INTO workspace_optimization_metrics (file_path, action, original_size, new_size) VALUES (?, 'archive', ?, ?)",
                (str(file_path), original_size, new_size),
            )

    def optimize(self, workspace: Path) -> list[Path]:
        """Archive rarely used files under ``workspace`` and log metrics.

        Returns the list of archived files.
        """
        validate_enterprise_environment()
        workspace = workspace.resolve()
        archive_root = CrossPlatformPathManager.get_backup_root() / "workspace_archive"
        files = self._get_old_files(workspace)
        processed: list[Path] = []
        with tqdm(files, desc="Optimizing", unit="file") as bar:
            for f in bar:
                bar.set_postfix(file=f.name)
                orig, new = self._archive_file(f, archive_root)
                self._log_metric(f, orig, new)
                processed.append(f)
        self.logger.info("Optimization run complete on %d files", len(files))
        return processed


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Workspace optimization tool")
    parser.add_argument(
        "workspace",
        nargs="?",
        type=Path,
        default=CrossPlatformPathManager.get_workspace_path(),
        help="Workspace directory",
    )
    args = parser.parse_args(argv)

    optimizer = WorkspaceOptimizer()
    targets: list[str] = []

    def primary() -> bool:
        targets.extend(str(p) for p in optimizer.optimize(args.workspace))
        return True

    orchestrator = DualCopilotOrchestrator()
    orchestrator.run(primary, targets)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
