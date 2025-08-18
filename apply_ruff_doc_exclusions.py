#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_ruff_doc_exclusions.py
Purpose: Enforce Ruff exclusions for Markdown/ReST; update config & docs,
capture gaps and errors as research questions, and produce a changelog.

DO NOT ACTIVATE ANY GitHub Actions files.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Python 3.11+: tomllib in stdlib; fall back to "toml" if unavailable
try:
    import tomllib  # type: ignore[attr-defined]
    _USE_TOMLLIB = True
except Exception:
    try:
        import toml  # type: ignore
        _USE_TOMLLIB = False
    except Exception:
        toml = None
        _USE_TOMLLIB = None

# ---------- Config ----------
EXCLUDE_SET = ["*.md", "*.rst", "README.md"]
CHANGELOG = Path("ruff_exclusions_changelog.md")
QUESTIONS = Path("chatgpt5_questions.md")
TIMESTAMP = datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z")
ENC = "utf-8"

# Grep locations (we won't activate or edit GH Actions; just observe/log)
SCAN_PATHS = [
    Path(".github") / "workflows",
    Path("Makefile"),
    Path("package.json"),
    Path("scripts"),
    Path("README.md"),
    Path("CONTRIBUTING.md"),
]

# ---------- Utilities ----------
def file_hash(p: Path) -> str:
    if not p.exists() or not p.is_file():
        return ""
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def read_text(p: Path) -> str:
    return p.read_text(encoding=ENC) if p.exists() else ""

def write_text(p: Path, s: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(s, encoding=ENC)

def append_question(step: str, err: str, ctx: str) -> None:
    QUESTIONS.parent.mkdir(parents=True, exist_ok=True)
    with QUESTIONS.open("a", encoding=ENC) as f:
        f.write(
            "Question for ChatGPT-5:\n"
            f"While performing [{step}], encountered the following error:\n"
            f"{err.strip()}\n"
            f"Context: {ctx.strip()}\n"
            "What are the possible causes, and how can this be resolved while preserving intended functionality?\n\n"
        )

def log_changelog(lines: list[str]) -> None:
    header = f"# Ruff Documentation Exclusion Change Log\n\n- Run: {TIMESTAMP}\n\n"
    if not CHANGELOG.exists():
        write_text(CHANGELOG, header)
    with CHANGELOG.open("a", encoding=ENC) as f:
        for line in lines:
            f.write(line.rstrip() + "\n")
        f.write("\n")

def parse_toml_bytes(b: bytes) -> dict:
    if _USE_TOMLLIB:
        return tomllib.loads(b.decode(ENC))
    elif _USE_TOMLLIB is False and toml:
        return toml.loads(b.decode(ENC))
    return {}

def dump_toml(d: dict) -> str:
    # Minimal TOML dump to avoid external deps if stdlib unavailable.
    # Prefer explicit formatting for known keys.
    # If "toml" is present, use it; otherwise, write simple blocks.
    if _USE_TOMLLIB is False and toml:
        return toml.dumps(d)

    # Naive dumper (handles basic cases in ruff sections)
    lines = []
    def write_table(path: list[str], tbl: dict):
        # path -> e.g., ["tool", "ruff"]
        lines.append("[" + ".".join(path) + "]")
        for k, v in tbl.items():
            if isinstance(v, list):
                arr = ", ".join(f"\"{item}\"" for item in v)
                lines.append(f'{k} = [{arr}]')
            elif isinstance(v, dict):
                # nested table
                lines.append("")  # spacing
                write_table(path + [k], v)
            elif isinstance(v, str):
                lines.append(f'{k} = "{v}"')
            elif isinstance(v, bool):
                lines.append(f'{k} = {str(v).lower()}')
            elif isinstance(v, int):
                lines.append(f'{k} = {v}')
            else:
                # fallback to JSON-ish
                lines.append(f'{k} = {json.dumps(v)}')
        lines.append("")  # spacing

    for key, val in d.items():
        if isinstance(val, dict):
            write_table([key], val)
        else:
            # root-level assignment
            if isinstance(val, str):
                lines.append(f'{key} = "{val}"')
            else:
                lines.append(f'{key} = {json.dumps(val)}')
    return "\n".join(lines).strip() + "\n"

def ensure_list(x) -> list:
    if x is None:
        return []
    if isinstance(x, list):
        return x
    return [x]

# ---------- Core Steps ----------
def find_ruff_config() -> Path:
    # Prefer pyproject.toml if it defines tool.ruff; else fallback
    pyproj = Path("pyproject.toml")
    ruff_toml = Path(".ruff.toml")
    if pyproj.exists():
        try:
            data = parse_toml_bytes(pyproj.read_bytes())
            if "tool" in data and isinstance(data["tool"], dict) and "ruff" in data["tool"]:
                return pyproj
        except Exception:
            pass
    if ruff_toml.exists():
        return ruff_toml
    # If neither exists, create .ruff.toml
    return ruff_toml

def load_config(p: Path) -> dict:
    if p.exists():
        try:
            return parse_toml_bytes(p.read_bytes())
        except Exception as e:
            append_question(
                "Phase 2: Parse Ruff Config",
                f"Failed to parse {p}: {e}",
                "Attempting to rebuild minimal config."
            )
    # minimal skeleton for .ruff.toml if absent or unreadable
    if p.name == ".ruff.toml":
        return {"tool": {"ruff": {}}}
    # minimal for pyproject.toml if file exists but no ruff section
    return {"tool": {"ruff": {}}}

def merge_extend_exclude(cfg: dict, excludes: list[str]) -> tuple[dict, list[str]]:
    notes = []
    tool = cfg.setdefault("tool", {})
    ruff = tool.setdefault("ruff", {})
    existing = ensure_list(ruff.get("extend-exclude"))
    # Deduplicate with case-sensitive compare; preserve existing order
    merged = existing[:]
    for patt in excludes:
        if patt not in merged:
            merged.append(patt)
    ruff["extend-exclude"] = merged
    notes.append(f"- Merged extend-exclude => {merged}")
    return cfg, notes

def update_readme(readme: Path) -> list[str]:
    notes = []
    if not readme.exists():
        notes.append("- README.md not found; logged as gap.")
        return notes
    content = readme.read_text(encoding=ENC)
    original = content

    # Remove explicit "ruff README.md" commands
    content = re.sub(r"(?mi)^\s*ruff\s+README\.md\s*$", "# (removed) ruff README.md", content)

    # Add a short policy note if not present
    policy_line = "Ruff is configured for Python files only; docs (*.md, *.rst) are excluded."
    if policy_line not in content:
        # Insert near top under first heading or append
        m = re.search(r"(?m)^#\s+.*$", content)
        if m:
            insert_at = m.end()
            content = content[:insert_at] + f"\n\n> {policy_line}\n" + content[insert_at:]
        else:
            content += f"\n\n> {policy_line}\n"

    if content != original:
        write_text(readme, content)
        notes.append("- README.md updated: removed doc-lint commands and added exclusion policy note.")
    else:
        notes.append("- README.md unchanged (no conflicting instructions found).")
    return notes

def update_contributing(contrib: Path) -> list[str]:
    notes = []
    if not contrib.exists():
        notes.append("- CONTRIBUTING.md not found; created with linting scope note.")
        write_text(contrib,
                   "# Contributing\n\n"
                   "## Linting Scope\n"
                   "- Ruff targets Python files.\n"
                   "- Documentation files (`*.md`, `*.rst`, including `README.md`) are excluded via `extend-exclude`.\n")
        return notes
    content = contrib.read_text(encoding=ENC)
    original = content
    block = (
        "## Linting Scope\n"
        "- Ruff targets Python files.\n"
        "- Documentation files (`*.md`, `*.rst`, including `README.md`) are excluded via `extend-exclude`.\n"
    )
    if "## Linting Scope" not in content:
        content += ("\n" if not content.endswith("\n") else "") + block
        write_text(contrib, content)
        notes.append("- CONTRIBUTING.md updated: added linting scope.")
    else:
        notes.append("- CONTRIBUTING.md already includes linting scope.")
    return notes

def scan_for_ruff_references() -> tuple[list[str], list[str]]:
    notes, gaps = [], []
    pattern = re.compile(r"\bruff\b", re.IGNORECASE)
    for path in SCAN_PATHS:
        if path.is_dir():
            for p in path.rglob("*"):
                if p.is_file():
                    try:
                        txt = read_text(p)
                        if pattern.search(txt):
                            notes.append(f"- Found Ruff reference in: {p}")
                    except Exception as e:
                        gaps.append(f"- Unable to read {p}: {e}")
        elif path.exists():
            try:
                txt = read_text(path)
                if pattern.search(txt):
                    notes.append(f"- Found Ruff reference in: {path}")
            except Exception as e:
                gaps.append(f"- Unable to read {path}: {e}")
        else:
            # Not present is fine; only log when helpful
            pass
    if any(str(p).startswith(".github/workflows") for p in SCAN_PATHS):
        notes.append("- Scanned GH Actions for Ruff references (no modifications applied).")
        notes.append("  NOTE: DO NOT ACTIVATE ANY GitHub Actions files. Review manually if needed.")
    return notes, gaps

def run_ruff_check() -> tuple[str, str, int]:
    try:
        proc = subprocess.run(
            ["ruff", "check", "."],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        return proc.stdout, proc.stderr, proc.returncode
    except FileNotFoundError as e:
        return "", str(e), 127
    except Exception as e:
        return "", str(e), 1

def main() -> int:
    summary = []
    gaps = []
    errors = []

    # Phase 1: Prep
    summary.append(f"## Phase 1: Preparation @ {TIMESTAMP}")
    repo = Path.cwd()
    summary.append(f"- Repo root: {repo}")

    cfg_path = find_ruff_config()
    summary.append(f"- Ruff config target: {cfg_path}")

    # Snapshot hashes
    tracked = [Path("pyproject.toml"), Path(".ruff.toml"), Path("README.md"), Path("CONTRIBUTING.md")]
    before = {str(p): file_hash(p) for p in tracked}

    # Phase 2/3: Mapping + Best-Effort Construction
    try:
        cfg = load_config(cfg_path)
        cfg, notes = merge_extend_exclude(cfg, EXCLUDE_SET)
        summary.extend(notes)

        # Persist config
        # Determine if using pyproject vs .ruff.toml:
        if cfg_path.name == "pyproject.toml":
            # Merge back into pyproject content
            # Load entire TOML; update tool.ruff; dump back
            try:
                full = parse_toml_bytes(cfg_path.read_bytes()) if cfg_path.exists() else {}
            except Exception:
                full = {}
            full.setdefault("tool", {}).setdefault("ruff", {})
            full["tool"]["ruff"].update(cfg["tool"]["ruff"])
            text = dump_toml(full)
            write_text(cfg_path, text)
            summary.append("- Updated pyproject.toml with extend-exclude.")
        else:
            # .ruff.toml (standalone)
            text = dump_toml(cfg)
            write_text(cfg_path, text)
            summary.append("- Wrote .ruff.toml with extend-exclude.")
    except Exception as e:
        msg = f"Config update failed: {e}"
        errors.append(msg)
        append_question("Phase 3: Update Config", msg, f"Config path: {cfg_path}")
    
    # README & CONTRIBUTING updates
    try:
        summary.extend(update_readme(Path("README.md")))
    except Exception as e:
        msg = f"README update failed: {e}"
        errors.append(msg)
        append_question("Phase 3: Update README", msg, "Removing any 'ruff README.md' guidance and adding policy note.")

    try:
        summary.extend(update_contributing(Path("CONTRIBUTING.md")))
    except Exception as e:
        msg = f"CONTRIBUTING update failed: {e}"
        errors.append(msg)
        append_question("Phase 3: Update CONTRIBUTING", msg, "Adding linting scope to exclude docs.")
    
    # Phase 2: Scan for references (no CI activation)
    try:
        notes, gaps2 = scan_for_ruff_references()
        summary.extend(notes)
        gaps.extend(gaps2)
    except Exception as e:
        msg = f"Reference scan failed: {e}"
        errors.append(msg)
        append_question("Phase 2: Scan for Ruff References", msg, "Scanning GH Actions, Makefile, scripts for 'ruff' mentions.")
    
    # Phase 5: Try running Ruff (optional)
    out, err, code = run_ruff_check()
    if code == 0:
        summary.append("- Ruff check ran successfully (0 exit).")
    elif code == 127:
        summary.append("- Ruff not found; skipped run. Logged a research question.")
        append_question("Phase 6: Optional Ruff Run", "Executable 'ruff' not found (exit 127).",
                        "Ensure Ruff is installed in the environment to validate exclusion behavior.")
    else:
        summary.append(f"- Ruff check exited with code {code}. See 'ruff_output.txt' and 'ruff_error.txt'.")
        write_text(Path("ruff_output.txt"), out)
        write_text(Path("ruff_error.txt"), err)
        append_question("Phase 6: Optional Ruff Run",
                        f"Non-zero exit code: {code}\nSTDERR:\n{err[:800]}",
                        "Post-exclusion Ruff check encountered issues; need guidance to preserve intended scope.")

    # Phase 4: Controlled Pruning (document only; no automatic destructive edits)
    # In this scenario, we don't need to prune files—just document if any scripts insist on linting docs.
    # If such cases were detected, we record them as gaps rather than modifying.
    if gaps:
        summary.append("- Gaps detected that may require manual review (see list below).")

    # Finalization: write changelog
    after = {str(p): file_hash(p) for p in tracked}
    changed = [p for p in tracked if before.get(str(p)) != after.get(str(p))]
    summary.append("## Finalization")
    summary.append(f"- Updated files: {', '.join(str(p) for p in changed) if changed else 'None'}")
    if gaps:
        summary.append("- Gaps requiring manual follow-up:")
        summary.extend(f"  {g}" for g in gaps)
    if errors:
        summary.append("- Errors occurred (see research questions file):")
        summary.extend(f"  - {e}" for e in errors)

    # Symbolic confirmation of goal:
    summary.append("\n**Symbolic Check:** Target set T' = T \\ E, where E = {\"*.md\", \"*.rst\", \"README.md\"}.")
    summary.append("Config now ensures Ruff excludes E globally via `extend-exclude`.")

    log_changelog(summary)
    print("\n".join(summary))
    print("\nNOTE: DO NOT ACTIVATE ANY GitHub Actions files.")
    return 0 if not errors else 1

if __name__ == "__main__":
    sys.exit(main())
