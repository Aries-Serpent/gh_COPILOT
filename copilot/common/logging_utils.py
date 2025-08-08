#!/usr/bin/env python3
import logging
from pathlib import Path


def setup_logging(log_file: Path) -> logging.Logger:
    """Set up a basic logger writing to the given file and stderr."""
    logger = logging.getLogger(log_file.stem)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(log_file)
        fh.setLevel(logging.INFO)
<<<<<<< HEAD
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
=======
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
>>>>>>> 072d1e7e (Nuclear fix: Complete repository rebuild - 2025-07-14 22:31:03)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

        sh = logging.StreamHandler()
        sh.setFormatter(formatter)
        logger.addHandler(sh)

    return logger
