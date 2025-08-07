"""Convert daily whitepaper PDFs to Markdown.

This utility scans the ``documentation/generated/daily_state_update``
folder for PDF files and converts each one to a Markdown file with the
same base name. Files that already have a corresponding ``.md`` file are
skipped. Conversion activity is logged to stdout.
"""
from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Iterable

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


def convert_pdfs(pdf_dir: Path) -> Iterable[str]:
    """Convert all PDF files in ``pdf_dir`` to Markdown.

    Parameters
    ----------
    pdf_dir:
        Directory containing the PDF files to convert.

    Returns
    -------
    Iterable[str]
        Iterable of log messages describing actions performed.
    """
    messages: list[str] = []
    for pdf_path in pdf_dir.glob("*.pdf"):
        sanitized_md = pdf_path.with_name(_sanitize_name(pdf_path.stem) + ".md")
        original_md = pdf_path.with_suffix(".md")

        if original_md.exists() or sanitized_md.exists():
            messages.append(f"Skipping {pdf_path.name}: already converted")
            continue

        reader = PdfReader(str(pdf_path))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        lines = text.splitlines()
        if lines:
            lines[0] = "# " + _sanitize_name(lines[0].strip())
        sanitized_md.write_text("\n".join(lines))
        messages.append(f"Converted {pdf_path.name} -> {sanitized_md.name}")
    return messages


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert daily whitepaper PDFs to Markdown"
    )
    default_dir = DEFAULT_PDF_DIR
    parser.add_argument(
        "--pdf-dir",
        default=default_dir,
        type=Path,
        help="Directory containing daily whitepaper PDFs",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    for message in convert_pdfs(args.pdf_dir):
        logging.info(message)


if __name__ == "__main__":  # pragma: no cover
    main()
