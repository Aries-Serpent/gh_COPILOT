"""Convert daily whitepaper PDFs to Markdown.

This utility scans the ``documentation/generated/daily state update``
folder for PDF files and converts each one to a Markdown file with the
same base name. Files that already have a corresponding ``.md`` file are
skipped. Conversion activity is logged to stdout.
"""
from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Iterable

try:  # pragma: no cover - optional dependency
    from PyPDF2 import PdfReader
except Exception:  # pragma: no cover - import guarding
    PdfReader = None  # type: ignore


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
        md_path = pdf_path.with_suffix(".md")
        if md_path.exists():
            messages.append(f"Skipping {pdf_path.name}: already converted")
            continue

        if PdfReader is None:
            messages.append(
                f"Cannot convert {pdf_path.name}: PyPDF2 not installed"
            )
            continue

        reader = PdfReader(str(pdf_path))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        md_path.write_text(text)
        messages.append(
            f"Converted {pdf_path.name} -> {md_path.name}"
        )
    return messages


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert daily whitepaper PDFs to Markdown"
    )
    default_dir = (
        Path("documentation")
        / "generated"
        / "daily state update"
    )
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
