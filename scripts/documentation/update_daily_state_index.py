"""Rebuild ``daily_state_index.md`` from available daily white‑paper files."""

from __future__ import annotations

import argparse
import re
import urllib.parse
from pathlib import Path
from typing import Dict, Tuple

DEFAULT_SOURCE_DIR = Path("documentation") / "generated" / "daily_state_update"
INDEX_PATH = Path("documentation") / "generated" / "daily_state_index.md"

DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")
NON_ASCII_HYPHENS = "\u2010\u2011\u2012\u2013\u2014\u2015"


def _scan(source_dir: Path) -> Dict[str, Dict[str, Path]]:
    """Return mapping of dates to available PDF/Markdown paths."""

    results: Dict[str, Dict[str, Path]] = {}
    for path in source_dir.iterdir():
        if not path.is_file():
            continue
        sanitized = path.name
        for ch in NON_ASCII_HYPHENS:
            sanitized = sanitized.replace(ch, "-")
        match = DATE_RE.search(sanitized)
        if not match:
            continue
        date = match.group(1)
        record = results.setdefault(date, {"pdf": None, "md": None})
        suffix = path.suffix.lower()
        if suffix == ".pdf":
            record["pdf"] = path
        elif suffix == ".md" and path.name.lower() != "readme.md":
            record["md"] = path
    return results


def _format_link(path: Path, index_dir: Path) -> str:
    """Return Markdown link for ``path`` relative to ``index_dir``."""

    rel = path.relative_to(index_dir).as_posix()
    return f"<{urllib.parse.quote(rel, safe='/')}>"


def update_index(
    source_dir: Path = DEFAULT_SOURCE_DIR, index_path: Path = INDEX_PATH
) -> Path:
    """Write ``daily_state_index.md`` linking to all daily reports."""

    index_dir = index_path.parent
    data = _scan(source_dir)
    lines = [
        "# Daily State White‑Paper Index",
        "",
        "| Date | Summary | PDF | Markdown |",
        "|------|---------|-----|----------|",
    ]

    for date in sorted(data):
        record = data[date]
        pdf = (
            f"[PDF]({_format_link(record['pdf'], index_dir)})" if record["pdf"] else "-"
        )
        md = (
            f"[Markdown]({_format_link(record['md'], index_dir)})"
            if record["md"]
            else "-"
        )
        summary = f"Snapshot of gh_COPILOT project state for {date}"
        lines.append(f"| {date} | {summary} | {pdf} | {md} |")

    index_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return index_path


def main(argv: Tuple[str, ...] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Update daily_state_index.md with links to available reports"
    )
    parser.add_argument(
        "--source-dir",
        default=DEFAULT_SOURCE_DIR,
        type=Path,
        help="Directory containing daily state PDF/Markdown files",
    )
    parser.add_argument(
        "--index-path",
        default=INDEX_PATH,
        type=Path,
        help="Path to write the generated index",
    )
    args = parser.parse_args(argv)

    update_index(source_dir=args.source_dir, index_path=args.index_path)


if __name__ == "__main__":  # pragma: no cover
    main()

