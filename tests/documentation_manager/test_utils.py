

from src.documentation_manager import ensure_accessible_formats

def test_pdf_requires_text_companion():
    assert ensure_accessible_formats(["PDF"]) == ["pdf", "md"]


def test_deduplicates_and_normalizes_order():
    formats = ["html", "pdf", "md", "PDF", "html"]
    assert ensure_accessible_formats(formats) == ["html", "pdf", "md"]


def test_no_extra_markdown_when_text_present():
    assert ensure_accessible_formats(["pdf", "HTML"]) == ["pdf", "html"]

