from pathlib import Path
import shutil

import pytest

from tools.convert_daily_whitepaper import PdfReader, convert_pdfs, _sanitize_name

pytestmark = pytest.mark.skipif(
    PdfReader is None, reason="PyPDF2 not installed"
)


def test_convert_creates_markdown(tmp_path):
    source_dir = Path("documentation") / "generated" / "daily_state_update"
    source_pdf = next(source_dir.glob("*.pdf"))
    shutil.copy(source_pdf, tmp_path / source_pdf.name)
    logs = list(convert_pdfs(tmp_path))
    md_name = _sanitize_name(source_pdf.stem) + ".md"
    md_file = tmp_path / md_name
    assert md_file.exists()
    assert any("Converted" in msg for msg in logs)
    assert md_file.read_text().strip()


def test_skip_existing_markdown(tmp_path):
    source_dir = Path("documentation") / "generated" / "daily_state_update"
    source_pdf = next(source_dir.glob("*.pdf"))
    target_pdf = tmp_path / source_pdf.name
    shutil.copy(source_pdf, target_pdf)
    md_file = target_pdf.with_suffix(".md")
    md_file.write_text("already here")
    logs = list(convert_pdfs(tmp_path))
    assert any("already converted" in msg for msg in logs)
    assert md_file.read_text() == "already here"
