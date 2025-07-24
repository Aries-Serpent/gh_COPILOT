#!/usr/bin/env python3
"""Continuous Operation Monitor."""
import argparse
import logging
import time
from pathlib import Path

from tqdm import tqdm
from utils.log_utils import _log_event


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
    start_payload = {"event": "operation_monitor_start"}
    _log_event(start_payload)
    for i in tqdm(range(iterations), desc="Operation Cycle"):
        logger.info("cycle check %d", i)
        _log_event({"event": "cycle", "index": i})
        time.sleep(0.1)
    logger.info("Continuous monitoring complete")
    result = _log_event({"event": "operation_monitor_complete"})
    if not result:
        logger.error("[ERROR] event logging failed")


def main() -> int:
    args = parse_args()
    logger = setup_logger(args.workspace)
    run_monitor(logger, args.iterations)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
