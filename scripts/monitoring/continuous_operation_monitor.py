#!/usr/bin/env python3
"""Continuous Operation Monitor."""
import argparse
import logging
import time
from pathlib import Path

from tqdm import tqdm

__all__ = ["ContinuousOperationMonitor", "main"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Continuous Operation Monitor")
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    parser.add_argument("--iterations", type=int, default=3)
    return parser.parse_args()


def setup_logger(workspace: Path) -> logging.Logger:
    log_dir = workspace / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("continuous_operation_monitor")
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(log_dir / "continuous_operation_monitor.log")
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)
    return logger


def run_monitor(logger: logging.Logger, iterations: int) -> None:
    """Run monitoring loop logging each cycle."""
    for _ in tqdm(range(iterations), desc="Operation Cycle"):
        logger.info("cycle check")
        time.sleep(0.1)
    logger.info("Continuous monitoring complete")


class ContinuousOperationMonitor:
    """Utility wrapper with :py:meth:`run` for tests."""

    def __init__(self, workspace: Path | None = None, interval: int = 3) -> None:
        self.workspace = workspace or Path.cwd()
        self.iterations = interval
        self.logger = setup_logger(self.workspace)

    def run(self) -> bool:
        """Execute monitor cycles."""
        run_monitor(self.logger, self.iterations)
        return True


def main() -> int:
    """CLI entry point."""
    args = parse_args()
    logger = setup_logger(args.workspace)
    run_monitor(logger, args.iterations)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
