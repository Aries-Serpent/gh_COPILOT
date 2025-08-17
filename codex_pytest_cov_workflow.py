#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Codex workflow: ensure pytest-cov dev extra, document usage, and produce NON-ACTIVATED CI example.
Policy: DO NOT ACTIVATE ANY GitHub Actions files.

Features:
- README/testing doc parsing & insertion
- pyproject.toml dev extra enforcement for pytest-cov
- Gap documentation (CHANGELOG.codex.md)
- Error capture blocks formatted for ChatGPT-5 research
- Idempotent writes with backups

Usage:
    python codex_pytest_cov_workflow.py
"""
import sys
import re
import json
import shutil
import hashlib
import datetime
from pathlib import Path

ERRORS = []
ACTIONS = []
GAPS = []

ROOT = Path.cwd()
BACKUP_DIR = ROOT / "tools" / "_codex_backup" / datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
DOCS_DIR = ROOT / "docs"
CHANGELOG = ROOT / "CHANGELOG.codex.md"
CI_EXAMPLE = ROOT / "ci_examples" / "pytest_cov.yml.disabled"

TARGET_FILES = {
    "pyproject": ROOT / "pyproject.toml",
    "readme": ROOT / "README.md",
    "testing": DOCS_DIR / "testing.md",
}


def record_action(msg: str):
    ACTIONS.append(msg)


def record_gap(item: str, rationale: str):
    GAPS.append({"item": item, "rationale": rationale})


def emit_chatgpt5_block(step: str, error_message: str, context: str):
    block = (
        "**Question for ChatGPT-5:**\n"
        f"While performing **[{step}]**, encountered the following error:\n"
        f"**{error_message}**\n"
        f"**Context:** {context}\n"
        "What are the possible causes, and how can this be resolved while preserving intended functionality?\n"
    )
    ERRORS.append(block)


def sha256_of(path: Path) -> str:
    if not path.exists() or not path.is_file():
        return "MISSING"
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_backup(path: Path):
    try:
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        if path.exists():
            rel = path.relative_to(ROOT)
            out_path = BACKUP_DIR / rel
            out_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, out_path)
            record_action(f"Backup created: {rel} -> {out_path}")
    except Exception as e:
        emit_chatgpt5_block(
            "Phase 1: Preparation/Backup",
            repr(e),
            f"Attempting to backup {path}",
        )


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def write_text(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    record_action(f"Wrote file: {path.relative_to(ROOT)}")


def ensure_pytest_cov_in_pyproject(pyproject_path: Path) -> bool:
    """Best-effort TOML manipulation without external deps."""
    if not pyproject_path.exists():
        record_gap("r1", "pyproject.toml not found; cannot enforce dev extra.")
        return False

    safe_backup(pyproject_path)
    txt = load_text(pyproject_path)

    dev_block_pattern = re.compile(
        r"(?ms)^\[project\.optional-dependencies\]\s*(.*?)^(?=\[|\Z)"
    )
    m = dev_block_pattern.search(txt)

    if m:
        block = m.group(0)
        dev_array_pattern = re.compile(r'(?ms)^\s*dev\s*=\s*\[(.*?)\]', re.MULTILINE | re.DOTALL)
        m2 = dev_array_pattern.search(block)
        if m2:
            inner = m2.group(1)
            pkgs = [p.strip() for p in re.split(r",(?![^\[]*\])", inner) if p.strip()]
            norm = set()
            for p in pkgs:
                s = p.strip().strip('"').strip("'")
                if s:
                    norm.add(s)
            if "pytest-cov" not in norm:
                norm.add("pytest-cov")
                norm.add("pytest")
                new_inner = ", ".join(f'"{p}"' for p in sorted(norm))
                new_block = dev_array_pattern.sub(f"  dev = [{new_inner}]", block, count=1)
                txt = txt.replace(block, new_block)
                write_text(pyproject_path, txt)
                record_action("Added pytest-cov to dev extra.")
            else:
                record_action("pytest-cov already present in dev extra.")
        else:
            insertion = 'dev = ["pytest", "pytest-cov"]\n'
            new_block = block.rstrip() + "\n" + insertion + "\n"
            txt = txt.replace(block, new_block)
            write_text(pyproject_path, txt)
            record_action("Created dev extra under existing optional-dependencies.")
    else:
        appended = (
            "\n[project.optional-dependencies]\n"
            'dev = ["pytest", "pytest-cov"]\n'
        )
        txt_new = txt.rstrip() + "\n" + appended
        write_text(pyproject_path, txt_new)
        record_action("Appended [project.optional-dependencies] with dev extra.")

    final = load_text(pyproject_path)
    if re.search(r'(?ms)^\[project\.optional-dependencies\].*^\s*dev\s*=\s*\[.*"pytest-cov".*\]', final):
        return True
    record_gap("r1", "Unable to confirm pytest-cov presence in dev extra after edits.")
    return False


def upsert_testing_docs():
    targets = [TARGET_FILES["testing"], TARGET_FILES["readme"]]
    chosen = None
    for t in targets:
        if t.exists():
            chosen = t
            break
    if chosen is None:
        chosen = TARGET_FILES["testing"]

    safe_backup(chosen)
    content = load_text(chosen)
    if not content:
        content = "# Testing Guide\n\n"

    def upsert_section(title, body):
        nonlocal content
        header = re.escape(title)
        pattern = re.compile(rf"(?ms)^##\s+{header}\s*$.*?(?=^##\s+|\Z)")
        block = f"## {title}\n\n{body.strip()}\n\n"
        if pattern.search(content):
            content = pattern.sub(block, content, count=1)
        else:
            if not content.endswith("\n"):
                content += "\n"
            content += "\n" + block

    install_body = """\
Use the development extras to install test tooling:

```bash
pip install .[dev]
```
"""

    run_body = """
Run tests with coverage:

```bash
pytest --cov --cov-report=term-missing
```

> Tip: if your package uses a `src/` layout, consider `--cov=<top_level_package>`.
"""

    upsert_section("Install test dependencies", install_body)
    upsert_section("Run tests with coverage", run_body)

    write_text(chosen, content)
    record_action(f"Updated testing docs in {chosen.relative_to(ROOT)}")
    return chosen


def write_ci_example():
    template = """# EXAMPLE ONLY — DO NOT MOVE INTO ACTIVE CI WITHOUT REVIEW

# This file is intentionally disabled and placed outside .github/workflows/.

# Policy: DO NOT ACTIVATE ANY GitHub Actions files.

name: example-pytest-cov
on: # intentionally omitted/disabled
workflow_dispatch: # kept as a comment/example, not active
# This block is non-functional by design.

jobs:
  tests:
    runs-on: ubuntu-latest
    steps:
      - name: Check out
        run: git clone --depth=1 "$REPO_URL" repo && cd repo || true
        # In normal usage within a workflow, you'd use actions/checkout@v4
      - name: Python setup (example)
        run: |
          python -m pip install --upgrade pip
          pip install .[dev]
      - name: Run tests with coverage
        run: |
          pytest --cov --cov-report=term-missing
"""

    safe_backup(CI_EXAMPLE)
    write_text(CI_EXAMPLE, template)
    record_action(f"Wrote NON-ACTIVATED CI example: {CI_EXAMPLE.relative_to(ROOT)}")


def write_changelog(before_hashes: dict, after_hashes: dict):
    lines = []
    lines.append(f"## Codex pytest-cov workflow — {datetime.datetime.now().isoformat(timespec='seconds')}\n")
    lines.append("### Symbolic Model\n")
    lines.append("- Required R = {r1: dev extra includes pytest-cov, r2: docs show `pip install .[dev]`, r3: CI example for `pytest --cov` (non-activated)}\n")
    lines.append("### Actions\n")
    for a in ACTIONS:
        lines.append(f"- {a}")
    lines.append("\n### Gaps & Rationales\n")
    if not GAPS:
        lines.append("- None (G = ∅)")
    else:
        for g in GAPS:
            lines.append(f"- {g['item']}: {g['rationale']}")
    if ERRORS:
        lines.append("\n### Error Capture (ChatGPT-5 Research Questions)\n")
        for e in ERRORS:
            lines.append(e.rstrip() + "\n")
    lines.append("\n### File Hashes (before → after)\n")
    for label, path in TARGET_FILES.items():
        b = before_hashes.get(label, "N/A")
        a = after_hashes.get(label, "N/A")
        rel = path.relative_to(ROOT)
        lines.append(f"- {rel}: {b} → {a}")
    lines.append(f"- {CI_EXAMPLE.relative_to(ROOT)}: (created if not present)")
    lines.append("\n### Next Steps (Manual)\n")
    lines.append("- If you choose to activate CI, **manually** copy the example into your CI system and review.")
    lines.append("- Confirm coverage thresholds and reports as desired.")
    lines.append("")
    safe_backup(CHANGELOG)
    write_text(CHANGELOG, "\n".join(lines))


def main():
    before_hashes = {k: sha256_of(p) for k, p in TARGET_FILES.items()}
    try:
        for p in TARGET_FILES.values():
            if p is not None:
                safe_backup(p)
    except Exception as e:
        emit_chatgpt5_block("Phase 1: Preparation", repr(e), "Backing up initial files")

    try:
        r1_ok = ensure_pytest_cov_in_pyproject(TARGET_FILES["pyproject"])
    except Exception as e:
        r1_ok = False
        emit_chatgpt5_block("Phase 3: r1 enforce pytest-cov", repr(e), "Editing pyproject.toml")

    testing_doc = None
    try:
        testing_doc = upsert_testing_docs()
        r2_ok = True
    except Exception as e:
        r2_ok = False
        emit_chatgpt5_block("Phase 3: r2 update testing docs", repr(e), "Editing README.md/docs/testing.md")

    try:
        write_ci_example()
        r3_ok = True
    except Exception as e:
        r3_ok = False
        emit_chatgpt5_block("Phase 3: r3 create CI example", repr(e), "Writing ci_examples/pytest_cov.yml.disabled")

    if not r1_ok:
        record_gap("r1", "Failed to ensure pytest-cov in dev extra. See error capture.")
    if not r2_ok:
        record_gap("r2", "Failed to update testing documentation. See error capture.")
    if not r3_ok:
        record_gap("r3", "Failed to write CI example. See error capture.")

    after_hashes = {k: sha256_of(p) for k, p in TARGET_FILES.items()}
    try:
        write_changelog(before_hashes, after_hashes)
    except Exception as e:
        emit_chatgpt5_block("Phase 6: Finalization/write changelog", repr(e), "Writing CHANGELOG.codex.md")

    summary = {
        "actions": ACTIONS,
        "gaps": GAPS,
        "errors_count": len(ERRORS),
        "docs_target": str(testing_doc.relative_to(ROOT)) if testing_doc and testing_doc.exists() else None,
        "ci_example": str(CI_EXAMPLE.relative_to(ROOT)),
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    try:
        main()
        sys.exit(0)
    except Exception as e:
        emit_chatgpt5_block("Top-level execution", repr(e), "Unexpected failure")
        try:
            if not CHANGELOG.exists():
                CHANGELOG.parent.mkdir(parents=True, exist_ok=True)
                CHANGELOG.write_text("", encoding="utf-8")
            with CHANGELOG.open("a", encoding="utf-8") as f:
                f.write("\n\n### Emergency Error Capture\n")
                for blk in ERRORS:
                    f.write(blk + "\n")
        except Exception:
            pass
        print(json.dumps({"fatal_error": repr(e)}, indent=2))
        sys.exit(1)

