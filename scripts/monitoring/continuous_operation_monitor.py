#!/usr/bin/env python3
"""Continuous Operation Monitor."""

import argparse
import logging
import time
from pathlib import Path

from tqdm import tqdm
from utils.log_utils import _log_event

from scripts.continuous_operation_orchestrator import validate_enterprise_operation

TEXT_INDICATORS = {
    "start": "[START]",
    "info": "[INFO]",
    "success": "[SUCCESS]",
    "error": "[ERROR]",
}


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
    if logger.hasHandlers():
        logger.handlers.clear()
    logger.addHandler(handler)
    return logger


def run_monitor(logger: logging.Logger, iterations: int) -> None:
    # Enterprise validation at star
    validate_enterprise_operation()
    start_payload = {"event": "operation_monitor_start"}
    _log_event(start_payload)
    logger.info("%s Monitoring cycles: %d", TEXT_INDICATORS["start"], iterations)
    for i in tqdm(range(iterations), desc="Operation Cycle"):
        logger.info("%s cycle check %d", TEXT_INDICATORS["info"], i)
        _log_event({"event": "cycle", "index": i})
        time.sleep(0.1)
    logger.info("%s Continuous monitoring complete", TEXT_INDICATORS["success"])
    result = _log_event({"event": "operation_monitor_complete"})
    if not result:
        logger.error("%s event logging failed", TEXT_INDICATORS["error"])


def main() -> int:
    args = parse_args()
    logger = setup_logger(args.workspace)
    run_monitor(logger, args.iterations)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
