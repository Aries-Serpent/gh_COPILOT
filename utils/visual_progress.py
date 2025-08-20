from __future__ import annotations

"""Helpers for standardized visual progress indicators."""

from contextlib import contextmanager
from datetime import datetime
from typing import Any, Iterator

from utils.progress import tqdm


def start_indicator(name: str) -> datetime:
    """Log start of a process and return the timestamp."""
    start = datetime.now()
    print(f"[START] {name} at {start.strftime('%Y-%m-%d %H:%M:%S')}")
    return start


@contextmanager
def progress_bar(total: int, **kwargs) -> Iterator[Any]:
    """Context manager yielding a ``tqdm``-like progress bar."""
    with tqdm(total=total, **kwargs) as bar:
        yield bar


def end_indicator(name: str, start_time: datetime) -> None:
    """Log process completion."""
    end = datetime.now()
    duration = (end - start_time).total_seconds()
    print(f"[END] {name} after {duration:.1f}s")
