#!/usr/bin/env python3
"""Track disk and network resource utilisation."""

from __future__ import annotations

import argparse
from typing import Dict

import psutil

__all__ = ["main", "collect_resource_snapshot"]


def collect_resource_snapshot(path: str = "/") -> Dict[str, float]:
    """Return a snapshot of disk and network usage."""

    disk = psutil.disk_usage(path)
    net = psutil.net_io_counters()
    return {
        "disk_usage_percent": float(disk.percent),
        "net_bytes_sent": float(net.bytes_sent),
        "net_bytes_recv": float(net.bytes_recv),
    }


def main(argv: list[str] | None = None) -> int:
    """CLI entry point printing a resource snapshot."""

    ap = argparse.ArgumentParser(description="Print resource usage snapshot")
    ap.add_argument("--path", default="/", help="Filesystem path for disk usage")
    ns = ap.parse_args(argv)
    snapshot = collect_resource_snapshot(ns.path)
    print(snapshot)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

