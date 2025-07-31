#!/usr/bin/env python3
# isort: skip_file
"""Move zero-byte log files to _ZERO_BYTE_QUARANTINE."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from utils.file_utils import quarantine_zero_byte_files
import logging


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    quarantine_dir = Path("_ZERO_BYTE_QUARANTINE")
    moved = quarantine_zero_byte_files(Path("logs"), quarantine_dir)
    logging.info("Moved %s zero-byte log file(s) to %s", moved, quarantine_dir)


if __name__ == "__main__":
    main()
