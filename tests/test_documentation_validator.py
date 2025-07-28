import pytest
from pathlib import Path
from scripts.documentation.documentation_validator import DocumentationValidator


def test_validator_success(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "index.md").write_text("See [Other](other.md)")
    (docs / "other.md").write_text("content")
    validator = DocumentationValidator()
    assert validator.validate(docs)


def test_validator_broken_link(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "index.md").write_text("See [Missing](missing.md)")
    validator = DocumentationValidator()
    assert not validator.validate(docs)
