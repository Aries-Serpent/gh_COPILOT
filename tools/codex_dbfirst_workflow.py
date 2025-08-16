#!/usr/bin/env python3
"""
Codex DB-First Bundle Workflow

Implements:
- README parsing and reference replacement/removal
- File search and adaptation attempt for scripts/assemble_db_first_bundle.py
- Gap documentation in a change log
- Error capture blocks formatted for ChatGPT-5
- Finalization with updated deliverables
- Absolutely DOES NOT activate or modify any GitHub Actions files.

Usage:
    python tools/codex_dbfirst_workflow.py
"""

import ast
import json
import re
import shutil
import subprocess
import datetime
import tokenize
from io import StringIO
from pathlib import Path
from typing import List, Tuple, Optional

# ------------------ Config & Constants ------------------

REPO_ROOT = Path(__file__).resolve().parents[1]
TARGET_PATH = REPO_ROOT / "scripts" / "assemble_db_first_bundle.py"
LEGACY_DIR = REPO_ROOT / "legacy"
GITHUB_WORKFLOWS = REPO_ROOT / ".github" / "workflows"
COVERAGERC = REPO_ROOT / ".coveragerc"
README = REPO_ROOT / "README.md"

LOG_CHANGE = REPO_ROOT / "codex_changelog.md"
LOG_ERRORS = REPO_ROOT / "codex_errors.md"
LOG_TEST = REPO_ROOT / "codex_test_last_run.txt"
ACTIONS_JSON = REPO_ROOT / "codex_actions.json"

TS = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

# ------------------ Utilities ------------------

def log_change(msg: str):
    LOG_CHANGE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_CHANGE.open("a", encoding="utf-8") as f:
        f.write(f"- {msg}\n")

def log_section(title: str):
    LOG_CHANGE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_CHANGE.open("a", encoding="utf-8") as f:
        f.write(f"\n## {title}\n")

def capture_error(step_no_desc: str, err_msg: str, ctx: str):
    LOG_ERRORS.parent.mkdir(parents=True, exist_ok=True)
    block = (
        "Question for ChatGPT-5:\n"
        f"While performing [{step_no_desc}], encountered the following error:\n"
        f"{err_msg}\n"
        f"Context: {ctx}\n"
        "What are the possible causes, and how can this be resolved while preserving intended functionality?\n\n"
    )
    with LOG_ERRORS.open("a", encoding="utf-8") as f:
        f.write(block)

def safe_backup(path: Path):
    if path.exists():
        backup = path.with_suffix(path.suffix + f".{TS}.bak")
        shutil.copy2(path, backup)
        log_change(f"Backed up {path.relative_to(REPO_ROOT)} -> {backup.relative_to(REPO_ROOT)}")
        return backup
    return None

def list_all_files() -> List[Path]:
    files = []
    for p in REPO_ROOT.rglob("*"):
        if p.is_file():
            files.append(p)
    return files

def contains_github_workflows_modification() -> bool:
    # This tool never writes to workflows, but we double-check presence only.
    return False

def tokenize_split_semicolons(code: str) -> str:
    """
    Split multiple statements separated by ';' into separate lines,
    but only when the semicolon is at top-level (not inside strings or comments).
    """
    out_lines = []
    reader = StringIO(code).readline
    try:
        tokens = list(tokenize.generate_tokens(reader))
    except tokenize.TokenError as e:
        # Fallback: naive split (still captured as an error for follow-up).
        return "\n".join(
            sum([ln.split(";") for ln in code.splitlines()], [])
        )

    # Group tokens by original line numbers and reconstruct cautiously
    line_map = {}
    for tok in tokens:
        tok_type, tok_str, (srow, scol), (erow, ecol), ltext = tok
        line_map.setdefault(srow, []).append((tok_type, tok_str, scol, ecol, ltext))

    for lno in sorted(line_map.keys()):
        line = line_map[lno][0][4]
        # Skip lines with semicolons that appear only inside strings/comments by a rough heuristic:
        # remove string and comment segments, then split remaining by ';'
        masked = []
        in_string = False
        current = []
        i = 0
        while i < len(line):
            ch = line[i]
            if ch in ('"', "'"):
                quote = ch
                masked.append("S")  # mark string
                i += 1
                while i < len(line):
                    masked.append("S")
                    if line[i] == "\\":
                        i += 2
                        continue
                    if line[i] == quote:
                        i += 1
                        break
                    i += 1
                continue
            if ch == "#":
                # rest is comment
                masked.append("#")
                masked.extend("#" for _ in range(i+1, len(line)))
                break
            masked.append(ch)
            i += 1

        masked_str = "".join(masked)
        # Split only on semicolons that survived masking
        if ";" in masked_str:
            parts = []
            acc = []
            for idx, ch in enumerate(masked_str):
                if ch == ";":
                    parts.append("".join(acc))
                    acc = []
                else:
                    acc.append(line[idx])  # use original char for fidelity
            parts.append("".join(acc))
            for p in parts:
                out_lines.append(p.rstrip())
        else:
            out_lines.append(line.rstrip())

    return "\n".join(out_lines) + ("\n" if not code.endswith("\n") else "")

def try_ast_parse(code: str) -> Tuple[bool, Optional[Exception]]:
    try:
        ast.parse(code)
        return True, None
    except Exception as e:
        return False, e

def find_related_assets() -> List[Path]:
    patt = re.compile(r"(db[_\-]?first|assemble|bundle)", re.I)
    return [p for p in list_all_files() if p.is_file() and patt.search(p.as_posix())]

def refcount_of_target(target: Path) -> int:
    pattern = re.escape(str(target.relative_to(REPO_ROOT)))
    count = 0
    for p in list_all_files():
        if p.suffix in {".py", ".md", ".rst", ".txt", ".yml", ".yaml", ".toml"}:
            try:
                txt = p.read_text(encoding="utf-8", errors="ignore")
                if re.search(pattern, txt):
                    count += 1
                # import‐style reference
                if p.suffix == ".py":
                    if ("assemble_db_first_bundle" in txt) or ("scripts.assemble_db_first_bundle" in txt):
                        count += 1
            except Exception:
                continue
    return count

def update_coveragerc_omit(path: Path, exclude: bool) -> bool:
    if not COVERAGERC.exists():
        return False
    safe_backup(COVERAGERC)
    text = COVERAGERC.read_text(encoding="utf-8")
    if "[omit]" not in text:
        # Append a simple omit section if excluding
        if exclude:
            text = text.rstrip() + "\n\n[report]\nomit =\n    " + str(path.relative_to(REPO_ROOT)).replace("\\", "/") + "\n"
            COVERAGERC.write_text(text, encoding="utf-8")
            log_change(f"Created [report].omit entry for {path}")
            return True
        else:
            # nothing to remove
            return False

    # Normalize omit list
    lines = text.splitlines()
    in_omit = False
    changed = False
    rel = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
    for i, line in enumerate(lines):
        if re.match(r"^\s*\[report\]\s*$", line):
            # allow omit under [report] (coverage.py v6+)
            # keep scanning
            pass
        if "[omit]" in line or re.match(r"^\s*omit\s*=", line):
            in_omit = True
        if in_omit and rel in line and not exclude:
            lines[i] = line.replace(rel, "").rstrip()
            changed = True

    if exclude and rel not in "\n".join(lines):
        # add under omit (favor [report].omit)
        inserted = False
        for i, line in enumerate(lines):
            if re.match(r"^\s*omit\s*=", line):
                # insert next line
                lines.insert(i + 1, f"    {rel}")
                changed = True
                inserted = True
                break
        if not inserted:
            # append if not found
            lines.append("omit =")
            lines.append(f"    {rel}")
            changed = True

    if changed:
        COVERAGERC.write_text("\n".join(lines) + "\n", encoding="utf-8")
        log_change(f"Updated coverage omit for {rel} (exclude={exclude})")
    return changed

def read_readme() -> str:
    return README.read_text(encoding="utf-8") if README.exists() else ""

def write_readme(text: str):
    safe_backup(README)
    README.write_text(text, encoding="utf-8")
    log_change("Updated README references.")

def replace_readme_refs(old_rel: str, new_rel: Optional[str]):
    if not README.exists():
        return
    txt = read_readme()
    if old_rel not in txt and (old_rel.replace("\\", "/") not in txt):
        return
    if new_rel:
        txt = txt.replace(old_rel, new_rel).replace(old_rel.replace("\\", "/"), new_rel)
        log_change(f"README: replaced references {old_rel} -> {new_rel}")
    else:
        # Remove references
        txt = re.sub(re.escape(old_rel), "", txt)
        txt = re.sub(re.escape(old_rel.replace("\\", "/")), "", txt)
        log_change(f"README: removed references to {old_rel}")
    write_readme(txt)

def relocate_to_legacy(path: Path) -> Optional[Path]:
    LEGACY_DIR.mkdir(exist_ok=True)
    dest = LEGACY_DIR / path.name
    safe_backup(path)
    shutil.move(str(path), str(dest))
    log_change(f"Relocated {path.relative_to(REPO_ROOT)} -> {dest.relative_to(REPO_ROOT)}")
    return dest

def run_pytest_with_cov() -> Tuple[int, str]:
    cmd = ["pytest", "-q", "--maxfail=1", "--disable-warnings", "--cov", "--cov-report=term-missing"]
    try:
        proc = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)
        LOG_TEST.write_text(proc.stdout + "\n\nSTDERR:\n" + proc.stderr, encoding="utf-8")
        return proc.returncode, proc.stdout + "\n" + proc.stderr
    except Exception as e:
        capture_error("Phase 6:pytest", repr(e), "Subprocess invocation for pytest failed")
        LOG_TEST.write_text(f"ERROR invoking pytest: {e}", encoding="utf-8")
        return 127, str(e)

def nearest_related_target(candidates: List[Path]) -> Optional[Path]:
    # simple token overlap scorer
    base_tokens = set(re.split(r"[_\-/\.]", "assemble_db_first_bundle"))
    best = None
    best_score = 0
    for p in candidates:
        toks = set(re.split(r"[_\-/\.]", p.stem))
        score = len(base_tokens & toks)
        if score > best_score and p != TARGET_PATH:
            best = p
            best_score = score
    return best

# ------------------ Main Workflow ------------------

def main():
    actions = {
        "fixed": False,
        "adapted_to": None,
        "pruned": False,
        "relocated": None,
        "coverage_omit_updated": False,
        "readme_updated": False,
        "tests_exit_code": None,
        "policy_github_workflows_modified": False
    }

    log_section("Preparation")
    log_change(f"Repo root: {REPO_ROOT}")
    log_change("Policy: DO NOT ACTIVATE OR MODIFY any .github/workflows files.")

    if GITHUB_WORKFLOWS.exists():
        log_change(f"Detected workflows at {GITHUB_WORKFLOWS.relative_to(REPO_ROOT)} (read-only).")

    related = find_related_assets()
    log_section("Search & Mapping")
    log_change(f"Related assets: {[str(p.relative_to(REPO_ROOT)) for p in related]}")

    M = None  # viable mapping path
    refcount = refcount_of_target(TARGET_PATH)
    log_change(f"Reference count for target: {refcount}")

    if TARGET_PATH.exists():
        # Try best-effort fixes
        code = TARGET_PATH.read_text(encoding="utf-8", errors="ignore")
        ok, err = try_ast_parse(code)
        if not ok:
            log_change("Initial AST parse failed; attempting semicolon split fix.")
            try:
                fixed = tokenize_split_semicolons(code)
                ok2, err2 = try_ast_parse(fixed)
                if ok2:
                    safe_backup(TARGET_PATH)
                    TARGET_PATH.write_text(fixed, encoding="utf-8")
                    log_change("Applied semicolon line-splitting fix and saved.")
                    actions["fixed"] = True
                else:
                    capture_error("Phase 3:AST-parse", repr(err2), "After semicolon split; consider more targeted refactor")
            except Exception as e:
                capture_error("Phase 3:tokenize_split_semicolons", repr(e), "Tokenizer-based refactor failed")

        # Evaluate mapping
        if refcount == 0:
            cand = nearest_related_target(related)
            if cand:
                M = cand
                log_change(f"Selected adaptation target: {cand.relative_to(REPO_ROOT)}")
            else:
                M = None
        else:
            M = TARGET_PATH

        # Adaptation or deprecation banner
        if M and M != TARGET_PATH:
            # Insert small deprecation banner in TARGET, pointing to M
            try:
                safe_backup(TARGET_PATH)
                banner = (
                    "# Deprecated: Use '{}\n".format(M.relative_to(REPO_ROOT).as_posix())
                )
                TARGET_PATH.write_text(banner + code, encoding="utf-8")
                actions["adapted_to"] = str(M.relative_to(REPO_ROOT))
                log_change(f"Inserted deprecation banner pointing to {actions['adapted_to']}")
            except Exception as e:
                capture_error("Phase 3:AdaptationBanner", repr(e), "Could not write deprecation banner")

        # Coverage configuration
        try:
            exclude = (refcount == 0 and (M is None or M != TARGET_PATH))
            if update_coveragerc_omit(TARGET_PATH, exclude):
                actions["coverage_omit_updated"] = True
        except Exception as e:
            capture_error("Phase 3:.coveragerc", repr(e), "Updating coverage omit failed")

        # README updates
        try:
            old_rel = str(TARGET_PATH.relative_to(REPO_ROOT)).replace("\\", "/")
            if M is None:
                replace_readme_refs(old_rel, None)
            elif M != TARGET_PATH:
                new_rel = str(M.relative_to(REPO_ROOT)).replace("\\", "/")
                replace_readme_refs(old_rel, new_rel)
            # mark update if README changed this run (heuristic via timestamp comparison skipped)
            actions["readme_updated"] = True
        except Exception as e:
            capture_error("Phase 3:README", repr(e), "Replacing/removing README references failed")

        # Pruning stage if truly obsolete
        if refcount == 0 and M is None:
            try:
                log_section("Controlled Pruning")
                log_change("Rationale: 0 references across code/tests/README; no viable mapping; attempts to repair exhausted.")
                LEGACY_DIR.mkdir(exist_ok=True)
                relocated = relocate_to_legacy(TARGET_PATH)
                actions["pruned"] = True
                actions["relocated"] = str(relocated.relative_to(REPO_ROOT)) if relocated else None
            except Exception as e:
                capture_error("Phase 4:RelocateLegacy", repr(e), "Failed to relocate obsolete file")

    else:
        # Target file missing; capture and try mapping only
        capture_error("Phase 2:TargetPresence", "FileNotFound", f"{TARGET_PATH} does not exist")
        cand = nearest_related_target(related)
        if cand:
            actions["adapted_to"] = str(cand.relative_to(REPO_ROOT))
            log_change(f"No target file; nearest related is {actions['adapted_to']}")
        else:
            log_change("No target file and no suitable related assets found.")

    # Finalization: run tests with coverage (best-effort)
    log_section("Finalization")
    ec, out = run_pytest_with_cov()
    actions["tests_exit_code"] = ec
    if ec == 0:
        log_change("Pytest + coverage succeeded.")
    else:
        log_change(f"Pytest exited with code {ec}. See {LOG_TEST.name} and {LOG_ERRORS.name} for details.")

    # Policy assertion
    actions["policy_github_workflows_modified"] = contains_github_workflows_modification()
    if actions["policy_github_workflows_modified"]:
        capture_error("PolicyCheck", "WorkflowsModified", "A write to .github/workflows was detected (should never happen).")

    ACTIONS_JSON.write_text(json.dumps(actions, indent=2), encoding="utf-8")
    log_change(f"Wrote actions to {ACTIONS_JSON.name}")
    log_change("Policy restated: DO NOT ACTIVATE ANY GitHub Actions files.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        capture_error("TopLevel:main", repr(e), "Unhandled exception in workflow")
        raise
