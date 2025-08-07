from tools.convert_daily_whitepaper import _sanitize_name, DEFAULT_PDF_DIR


def test_latest_daily_state_update_has_markdown():
    pdfs = sorted(DEFAULT_PDF_DIR.glob("*.pdf"))
    assert pdfs, "No PDF files found"
    latest_pdf = pdfs[-1]
    sanitized_md = latest_pdf.with_name(_sanitize_name(latest_pdf.stem) + ".md")
    original_md = latest_pdf.with_suffix(".md")
    assert original_md.exists() or sanitized_md.exists(), (
        f"Missing markdown for: {latest_pdf.name}"
    )
    