"""Generate daily state report in Markdown and PDF formats."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Tuple

from PyPDF2 import PdfWriter
from PyPDF2.generic import AnnotationBuilder

import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from utils.validation_utils import run_dual_copilot_validation
OUTPUT_DIR = ROOT / "documentation" / "generated" / "daily state update"


def _write_markdown(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def _write_pdf(path: Path, content: str) -> None:
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    annot = AnnotationBuilder.free_text(content, rect=(50, 700, 562, 780))
    writer.add_annotation(page_number=0, annotation=annot)
    with path.open("wb") as handle:
        writer.write(handle)


def generate_daily_state(output_dir: Path | None = None) -> Tuple[Path, Path]:
    """Generate daily state report and return paths to created files."""
    out_dir = output_dir or OUTPUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d")
    content = f"# Daily State Report\n\nGenerated on {timestamp}\n"
    md_path = out_dir / f"daily_state_{timestamp}.md"
    pdf_path = out_dir / f"daily_state_{timestamp}.pdf"
    _write_markdown(md_path, content)
    _write_pdf(pdf_path, content)

    def _primary() -> bool:
        return md_path.exists()

    def _secondary() -> bool:
        return pdf_path.exists()

    run_dual_copilot_validation(_primary, _secondary)
    return md_path, pdf_path


def main() -> None:
    generate_daily_state()


if __name__ == "__main__":  # pragma: no cover
    main()
