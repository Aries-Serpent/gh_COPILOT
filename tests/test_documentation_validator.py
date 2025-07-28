from pathlib import Path
from scripts.documentation.documentation_validator import DocumentationValidator


def test_broken_link(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "index.md").write_text("[bad](missing.md)")
    validator = DocumentationValidator()
    assert not validator.validate(docs)


def test_valid_links(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    target = docs / "target.md"
    target.write_text("content")
    (docs / "index.md").write_text("[good](target.md)")
    validator = DocumentationValidator()
    assert validator.validate(docs)
