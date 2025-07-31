"""Report generation helpers for gh_COPILOT."""

import json
from pathlib import Path
from typing import Any, Dict


def generate_json_report(data: Dict[str, Any], output_path: Path) -> Path:
    """Write ``data`` to ``output_path`` as JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
    return output_path


def generate_markdown_report(data: Dict[str, Any], output_path: Path, title: str = "Report") -> Path:
    """Write ``data`` to ``output_path`` in Markdown format."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"# {title}"]
    for key, value in data.items():
        lines.append(f"- **{key}**: {value}")
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def generate_text_report(data: Dict[str, Any], output_path: Path, title: str = "Report") -> Path:
    """Write ``data`` to ``output_path`` in a simple text table."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [title]
    for key, value in data.items():
        lines.append(f"{key}: {value}")
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path
