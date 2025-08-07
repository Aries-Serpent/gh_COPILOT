from pathlib import Path
import shutil

import pytest

from tools.convert_daily_whitepaper import (
    PdfReader,
    convert_pdfs,
    convert_pdf,
    _sanitize_name,
    verify_lfs_pdfs,
)

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


def test_verify_lfs_pdfs_detects_pointer(tmp_path):
    pointer = tmp_path / "fake.pdf"
    pointer.write_text("version https://git-lfs.github.com/spec/v1\n")
    with pytest.raises(FileNotFoundError):
        verify_lfs_pdfs(tmp_path)


def test_convert_pdf_single_file(tmp_path):
    source_dir = Path("documentation") / "generated" / "daily_state_update"
    source_pdf = next(source_dir.glob("*.pdf"))
    target_pdf = tmp_path / source_pdf.name
    shutil.copy(source_pdf, target_pdf)
    message = convert_pdf(target_pdf)
    md_name = _sanitize_name(source_pdf.stem) + ".md"
    md_file = tmp_path / md_name
    assert md_file.exists()
    assert "Converted" in message
