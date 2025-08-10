from pathlib import Path

import pytest


DOCS = [
    Path("docs/white-paper.md"),
    Path("docs/executive_guides/README.md"),
]


@pytest.mark.parametrize("path", DOCS)
def test_docs_reference_governance_standards(path: Path) -> None:
    content = path.read_text(encoding="utf-8")
    assert "GOVERNANCE_STANDARDS.md" in content, f"{path} missing governance reference"

