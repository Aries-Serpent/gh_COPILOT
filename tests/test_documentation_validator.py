from __future__ import annotations

from pathlib import Path

from scripts.documentation.documentation_validator import DocumentationValidator


def test_broken_link(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "sample.md").write_text("[bad](missing.md)")
    validator = DocumentationValidator()
    result = validator.validate(docs)
    assert result is False
