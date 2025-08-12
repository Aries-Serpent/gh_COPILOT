"""CLI wrapper for running :meth:`SyncWatcher.watch_pairs`."""

from __future__ import annotations

import argparse
import threading
from pathlib import Path
from typing import Iterable, List, Tuple

from database_first_synchronization_engine import SyncWatcher


def run_watch_pairs(
    pairs: Iterable[Tuple[Path | str, Path | str]],
    *,
    interval: float = 1.0,
    stop_event: threading.Event | None = None,
) -> None:
    """Run ``SyncWatcher.watch_pairs`` for ``pairs``."""

    watcher = SyncWatcher()
    watcher.watch_pairs(list(pairs), interval=interval, stop_event=stop_event)


def _parse_pair(arg: str) -> Tuple[Path, Path]:
    try:
        a, b = arg.split(":", 1)
    except ValueError as exc:  # pragma: no cover - argparse validates
        raise argparse.ArgumentTypeError("pairs must be formatted as 'A:B'") from exc
    return Path(a), Path(b)


def main() -> int:
    parser = argparse.ArgumentParser(description="Watch database pairs for changes")
    parser.add_argument(
        "pairs",
        nargs="+",
        help="Database pairs formatted as 'DB_A:DB_B'",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=1.0,
        help="Polling interval in seconds",
    )

    args = parser.parse_args()
    pairs: List[Tuple[Path, Path]] = [_parse_pair(p) for p in args.pairs]
    stop = threading.Event()
    try:
        run_watch_pairs(pairs, interval=args.interval, stop_event=stop)
    except KeyboardInterrupt:  # pragma: no cover - interactive stop
        stop.set()
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

