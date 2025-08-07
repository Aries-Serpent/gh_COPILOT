"""Convert daily whitepaper PDFs to Markdown.

This utility scans the ``documentation/generated/daily_state_update``
folder for PDF files and converts each one to a Markdown file with the
same base name. A single PDF can be converted by passing ``--pdf-file``.
Files that already have a corresponding ``.md`` file are skipped. Before
any conversion happens, the script ensures required Git LFS objects are
available locally by running ``git lfs fetch --all`` and ``git lfs
checkout``. If any PDF remains a pointer file after this step, conversion
is aborted with instructions for remediation. Conversion activity is
logged to stdout.
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Iterable, Iterator, Sequence
import subprocess

DEFAULT_PDF_DIR = Path("documentation") / "generated" / "daily_state_update"

# Some PDFs were produced with non-breaking hyphens in the filename.  The
# Markdown files should use plain ASCII hyphens so downstream tooling can
# reference them consistently.
NON_ASCII_HYPHENS = "\u2010\u2011\u2012\u2013\u2014\u2015"


def _sanitize_name(name: str) -> str:
    """Replace any non-ASCII hyphen characters with a standard hyphen."""
    for ch in NON_ASCII_HYPHENS:
        name = name.replace(ch, "-")
    return name

import PyPDF2  # noqa: F401
from PyPDF2 import PdfReader

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.documentation.update_daily_state_index import update_index


def convert_pdf(pdf_path: Path) -> str:
    """Convert a single PDF file to Markdown."""
    sanitized_md = pdf_path.with_name(_sanitize_name(pdf_path.stem) + ".md")
    original_md = pdf_path.with_suffix(".md")

    if original_md.exists() or sanitized_md.exists():
        return f"Skipping {pdf_path.name}: already converted"

    reader = PdfReader(str(pdf_path))
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    lines = text.splitlines()
    if lines:
        lines[0] = "# " + _sanitize_name(lines[0].strip())
    sanitized_md.write_text("\n".join(lines))
    return f"Converted {pdf_path.name} -> {sanitized_md.name}"


def convert_pdfs(pdf_dir: Path) -> Iterable[str]:
    """Convert all PDF files in ``pdf_dir`` to Markdown."""
    return (convert_pdf(pdf_path) for pdf_path in pdf_dir.glob("*.pdf"))


def _is_lfs_pointer(path: Path) -> bool:
    """Return True if ``path`` contains an unresolved Git LFS pointer."""
    try:
        with path.open("rb") as fh:
            head = fh.read(100)
    except OSError:
        return True
    return head.startswith(b"version https://git-lfs.github.com/spec/v1")


def _iter_pdfs(pdfs: Sequence[Path] | Path) -> Iterator[Path]:
    """Yield PDF paths from an iterable or directory."""
    if isinstance(pdfs, Path):
        if pdfs.is_dir():
            yield from pdfs.glob("*.pdf")
        else:
            yield pdfs
    else:
        yield from pdfs


def verify_lfs_pdfs(pdfs: Sequence[Path] | Path) -> None:
    """Ensure each PDF in ``pdfs`` is a materialized Git LFS file."""
    missing: list[str] = []
    for pdf_path in _iter_pdfs(pdfs):
        if not pdf_path.exists() or _is_lfs_pointer(pdf_path):
            missing.append(pdf_path.name)
    if missing:
        joined = ", ".join(missing)
        raise FileNotFoundError(
            f"Missing LFS content for: {joined}. "
            "Run 'git lfs fetch --all && git lfs checkout' and retry."
        )


def fetch_lfs_objects() -> None:
    """Fetch and checkout all Git LFS objects.

    Errors are logged but do not stop execution so that ``verify_lfs_pdfs``
    can surface a clearer remediation message.
    """
    for cmd in ("git lfs fetch --all", "git lfs checkout"):
        result = subprocess.run(cmd.split(), capture_output=True, text=True)
        if result.returncode != 0:
            logging.warning("%s failed: %s", cmd, result.stderr.strip())


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert daily whitepaper PDFs to Markdown",
    )
    default_dir = DEFAULT_PDF_DIR
    parser.add_argument(
        "--pdf-dir",
        default=default_dir,
        type=Path,
        help="Directory containing daily whitepaper PDFs",
    )
    parser.add_argument(
        "--pdf-file",
        type=Path,
        help="Convert only the specified PDF file",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    try:
        fetch_lfs_objects()
        targets = [args.pdf_file] if args.pdf_file else args.pdf_dir
        verify_lfs_pdfs(targets)
    except FileNotFoundError as exc:
        logging.error(str(exc))
        sys.exit(1)

    if args.pdf_file:
        logging.info(convert_pdf(args.pdf_file))
        index_dir = args.pdf_file.parent
    else:
        for message in convert_pdfs(args.pdf_dir):
            logging.info(message)
        index_dir = args.pdf_dir
    update_index(source_dir=index_dir)


if __name__ == "__main__":  # pragma: no cover
    main()
