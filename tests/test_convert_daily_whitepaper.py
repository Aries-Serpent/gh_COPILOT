from pathlib import Path
import shutil

import pytest

from tools.convert_daily_whitepaper import PdfReader, convert_pdfs

pytestmark = pytest.mark.skipif(
    PdfReader is None, reason="PyPDF2 not installed"
)


def test_convert_creates_markdown(tmp_path):
    source_pdf = next(
        Path("documentation/generated/daily state update").glob("*.pdf")
    )
    shutil.copy(source_pdf, tmp_path / source_pdf.name)
    logs = list(convert_pdfs(tmp_path))
    md_file = (tmp_path / source_pdf.name).with_suffix(".md")
    assert md_file.exists()
    assert any("Converted" in msg for msg in logs)
    assert md_file.read_text().strip()


def test_skip_existing_markdown(tmp_path):
    source_pdf = next(
        Path("documentation/generated/daily state update").glob("*.pdf")
    )
    target_pdf = tmp_path / source_pdf.name
    shutil.copy(source_pdf, target_pdf)
    md_file = target_pdf.with_suffix(".md")
    md_file.write_text("already here")
    logs = list(convert_pdfs(tmp_path))
    assert any("already converted" in msg for msg in logs)
    assert md_file.read_text() == "already here"
