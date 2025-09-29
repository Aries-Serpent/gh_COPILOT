#!/usr/bin/env python3
from __future__ import annotations

"""Minimal Markdown code fence validator (local use).

Validates that code fences specify a language and are properly closed. Optionally
warns or fails on nested fence markers inside a fenced block.
"""

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence

FENCE_BACKTICK = "```"
FENCE_TILDE = "~~~"


@dataclass(slots=True)
class FenceError:
    path: Path
    line: int
    message: str

    def format(self) -> str:
        return f"{self.path}:{self.line}: {self.message}"


def _iter_lines(path: Path) -> Iterable[tuple[int, str]]:
    with path.open("r", encoding="utf-8") as handle:
        for index, line in enumerate(handle, start=1):
            yield index, line


def validate_file(path: Path, strict_inner: bool, *, warn_inner: bool = False) -> List[FenceError]:
    errors: List[FenceError] = []
    inside_fence = False
    fence_marker = ""
    fence_start_line = 0

    for line_no, line in _iter_lines(path):
        stripped = line.lstrip()
        if stripped.startswith(FENCE_BACKTICK) or stripped.startswith(FENCE_TILDE):
            if not inside_fence:
                inside_fence = True
                fence_marker = (
                    FENCE_BACKTICK if stripped.startswith(FENCE_BACKTICK) else FENCE_TILDE
                )
                fence_start_line = line_no
                language = stripped[len(fence_marker) :].strip()
                if not language:
                    errors.append(
                        FenceError(
                            path=path,
                            line=line_no,
                            message="Code fence is missing a language tag (e.g. ```python).",
                        )
                    )
            else:
                inside_fence = False
                fence_marker = ""
            continue

        if inside_fence and strict_inner and fence_marker in line:
            if warn_inner:
                # Report but do not fail; the caller decides how to surface warnings.
                errors.append(
                    FenceError(
                        path=path,
                        line=line_no,
                        message="Detected nested code fence inside a fenced block (warning).",
                    )
                )
            else:
                errors.append(
                    FenceError(
                        path=path,
                        line=line_no,
                        message="Detected nested code fence inside a fenced block.",
                    )
                )

    if inside_fence:
        errors.append(
            FenceError(
                path=path,
                line=fence_start_line,
                message="Code fence opened but not closed before end of file.",
            )
        )

    return errors


def _collect_targets(paths: Sequence[str] | None) -> List[Path]:
    inputs = [Path(p) for p in paths] if paths else []
    candidates: List[Path] = []
    for target in inputs:
        if target.is_dir():
            for extension in (".md", ".mdx"):
                for found in sorted(target.rglob(f"*{extension}")):
                    candidates.append(found)
        elif target.suffix.lower() in {".md", ".mdx"}:
            candidates.append(target)
    unique: List[Path] = []
    seen: set[Path] = set()
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        unique.append(candidate)
    return unique


def validate_paths(
    paths: Sequence[str] | None, strict_inner: bool, *, warn_inner: bool = False
) -> List[FenceError]:
    errors: List[FenceError] = []
    for path in _collect_targets(paths):
        errors.extend(validate_file(path, strict_inner, warn_inner=warn_inner))
    return errors


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", help="Markdown files or directories to validate.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--strict-inner", action="store_true", help="Fail on nested fences inside a block."
    )
    mode.add_argument(
        "--warn-inner", action="store_true", help="Warn (but do not fail) on nested fences."
    )
    args = parser.parse_args(argv)

    strict = True if not args.warn_inner and not args.strict_inner else args.strict_inner
    errs = validate_paths(args.paths or [], strict, warn_inner=args.warn_inner)
    for e in errs:
        print(e.format())
    return 1 if any(e for e in errs if "warning" not in e.message.lower()) else 0


if __name__ == "__main__":
    raise SystemExit(main())

