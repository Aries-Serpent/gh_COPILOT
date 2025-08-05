import json
import re
from pathlib import Path
from urllib.parse import unquote

DOC_DIRS = [Path("docs"), Path("documentation")]

_link_re = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def _local_links(text):
    for match in _link_re.finditer(text):
        link = unquote(match.group(1).strip()).strip("<>")
        if (
            link.startswith(("http://", "https://", "#", "file://"))
            or "commit/" in link
            or link.endswith((".py", ".png"))
            or link == "data"
            or not link
        ):
            continue
        link = link.split("#", 1)[0]
        yield link


def test_markdown_links_exist():
    for base in DOC_DIRS:
        if not base.exists():
            continue
        for md in base.rglob("*.md"):
            text = md.read_text(errors="ignore")
            for link in _local_links(text):
                target = (md.parent / link).resolve()
                if not target.exists():
                    target = Path(link).resolve()
                assert target.exists(), f"Broken link {link} in {md}"


def test_placeholder_summary_schema_present():
    content = Path("dashboard/README.md").read_text()
    pattern = r"placeholder_summary\.json`[^`]+```json\n(\{[^`]+\})\n```"
    m = re.search(pattern, content, flags=re.DOTALL)
    assert m, "placeholder_summary.json schema missing"
    data = json.loads(m.group(1))
    for key in ["timestamp", "findings", "resolved_count", "compliance_score", "progress_status"]:
        assert key in data
