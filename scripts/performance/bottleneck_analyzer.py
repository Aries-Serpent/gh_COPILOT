#!/usr/bin/env python3
"""Bottleneck Analyzer with auto-discovery.

Usage:
    python scripts/performance/bottleneck_analyzer.py --module pkg.mod:func [--repeat N] [--profile]

When ``--module`` is omitted, the script scans ``scripts/performance`` for
callables that take no required arguments and profiles each of them.
"""
from __future__ import annotations

import argparse
import cProfile
import importlib
import importlib.util
import inspect
import io
from pathlib import Path
import pstats
import time
from typing import Callable, List, Tuple


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Analyze potential bottlenecks in code execution."
    )
    ap.add_argument("--module", help="Format: pkg.mod:callable")
    ap.add_argument(
        "--repeat",
        type=int,
        default=1,
        help="Number of times to run the callable for averaging.",
    )
    ap.add_argument(
        "--profile", action="store_true", help="Enable cProfile detailed profiling."
    )
    return ap.parse_args(argv)


def run_target(mod_fn: str) -> Callable[[], None]:
    """Load and return the specified callable."""
    mod, fn = mod_fn.split(":")
    func = getattr(importlib.import_module(mod), fn)
    return func


def discover_targets(directory: Path | None = None) -> List[Tuple[str, Callable[[], None]]]:
    """Discover zero-argument callables in Python files within ``directory``."""
    directory = directory or Path(__file__).resolve().parent
    targets: List[Tuple[str, Callable[[], None]]] = []
    for py_file in directory.glob("*.py"):
        if py_file.name == Path(__file__).name:
            continue
        spec = importlib.util.spec_from_file_location(py_file.stem, py_file)
        if not spec or not spec.loader:
            continue
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore[attr-defined]
        for name, obj in inspect.getmembers(module, inspect.isfunction):
            if obj.__module__ != module.__name__:
                continue
            sig = inspect.signature(obj)
            if any(
                p.default is inspect._empty
                and p.kind in (
                    inspect.Parameter.POSITIONAL_ONLY,
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                )
                for p in sig.parameters.values()
            ):
                continue
            targets.append((f"{py_file.stem}:{name}", obj))
    return targets


def profile_callable(name: str, func: Callable[[], None], repeat: int, do_profile: bool) -> None:
    if do_profile:
        profiler = cProfile.Profile()
        profiler.enable()
        for _ in range(repeat):
            func()
        profiler.disable()
        buffer = io.StringIO()
        stats = pstats.Stats(profiler, stream=buffer).sort_stats("cumulative")
        stats.print_stats(10)
        print(buffer.getvalue())
    else:
        total = 0.0
        for _ in range(repeat):
            start = time.perf_counter()
            func()
            total += time.perf_counter() - start
        average = total / repeat
        print(f"[stub] {name} ran in {average:.4f}s on average")


def main(argv: List[str] | None = None) -> None:
    args = parse_args(argv)
    if args.module:
        func = run_target(args.module)
        profile_callable(args.module, func, args.repeat, args.profile)
    else:
        targets = discover_targets()
        if not targets:
            print("[stub] No callable targets found in scripts/performance.")
            return
        print("[stub] Discovered targets:" + ", ".join(name for name, _ in targets))
        for name, func in targets:
            profile_callable(name, func, args.repeat, args.profile)


if __name__ == "__main__":  # pragma: no cover - direct execution
    main()
