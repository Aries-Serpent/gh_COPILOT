#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
codex_move_tqdm.py
Implements the sequential workflow:
- Move `tqdm` from requirements-test.txt -> requirements.txt (best-effort)
- Install and run validator
- Update README
- Controlled pruning with rationale
- Error capture as ChatGPT-5 research questions
- Finalization with change log

NOTE: DO NOT ACTIVATE ANY GitHub Actions files. This script never writes under .github/workflows.
"""

import re
import sys
import json
import shlex
import subprocess
from pathlib import Path
from datetime import datetime

# ---------------------------
# Config / Constants
# ---------------------------
D = "tqdm"
ROOT = Path(".").resolve()
LOG_DIR = ROOT / ".codex"
LOG_DIR.mkdir(exist_ok=True)
RUN_LOG = LOG_DIR / "run.log"
CHANGELOG = ROOT / "CHANGELOG_Codex_Auto.md"
ERRLOG = ROOT / "ERRORS_ChatGPT5.md"

REQ_MAIN_CANDIDATES = ["requirements.txt"]
REQ_TEST_CANDIDATES = ["requirements-test.txt", "test-requirements.txt"]
DEV_REQ_CANDIDATES = ["requirements-dev.txt", "dev-requirements.txt"]
PYPROJECT = ROOT / "pyproject.toml"
SETUPCFG = ROOT / "setup.cfg"
README_CANDS = ["README.md", "Readme.md", "readme.md"]

GITHUB_WORKFLOWS = ROOT / ".github" / "workflows"

# Regex for dependency lines (simple, robust enough for typical pins/extras)
DEP_RX = re.compile(r"^\s*([A-Za-z0-9_.\-]+)\s*(\[.*\])?\s*([<>=!~]=[^#\s]+)?", re.IGNORECASE)

# ---------------------------
# Utilities
# ---------------------------

def log_line(s: str):
    with RUN_LOG.open("a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().isoformat()}] {s}\n")

def append_changelog(section: str):
    header = f"\n## {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} — {section}\n"
    with CHANGELOG.open("a", encoding="utf-8") as f:
        f.write(header)

def append_changelog_text(text: str):
    with CHANGELOG.open("a", encoding="utf-8") as f:
        f.write(text.rstrip() + "\n")

def append_error_block(phase_step: str, err_msg: str, context: str):
    block = (
        "\nQuestion for ChatGPT-5:\n"
        f"While performing [{phase_step}], encountered the following error:\n"
        f"{err_msg}\n"
        f"Context: {context}\n"
        "What are the possible causes, and how can this be resolved while preserving intended functionality?\n"
    )
    with ERRLOG.open("a", encoding="utf-8") as f:
        f.write(block)
    log_line(f"[ERROR_CAPTURED] {phase_step}: {err_msg}")

def safe_write_text(path: Path, content: str):
    # NEVER write under GitHub Actions
    if GITHUB_WORKFLOWS in path.parents:
        raise RuntimeError(f"Refusing to write under {GITHUB_WORKFLOWS}")
    path.write_text(content, encoding="utf-8")

def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")

def find_first_existing(paths):
    for p in paths:
        candidate = ROOT / p
        if candidate.exists():
            return candidate
    return None

def parse_requirements(path: Path):
    deps = []
    if not path or not path.exists():
        return deps
    for line in read_text(path).splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        m = DEP_RX.match(line)
        if not m:
            continue
        name = m.group(1)
        extras = m.group(2) or ""
        pin = m.group(3) or ""
        if name:
            deps.append((name.lower(), name + extras + (pin if pin else "")))
    return deps

def add_dep_to_requirements(path: Path, dep_line: str):
    lines = []
    if path.exists():
        lines = read_text(path).splitlines()
        # avoid duplicates (case-insensitive)
        lname = dep_line.split("[")[0].split("==")[0].strip().lower()
        for line in lines:
            if line.strip().lower().startswith(lname):
                return False  # already present
    else:
        lines = []
    lines.append(dep_line)
    # sort lightly: keep comments, but sort dependencies alphabetically at block end
    deps = [line for line in lines if line and not line.strip().startswith("#")]
    comments = [line for line in lines if (not line) or line.strip().startswith("#")]
    deps_sorted = sorted(set(deps), key=lambda s: s.lower())
    content = "\n".join(comments + deps_sorted) + "\n"
    safe_write_text(path, content)
    return True

def remove_dep_from_requirements(path: Path, dep_name: str):
    if not path or not path.exists():
        return False
    name_l = dep_name.lower()
    new_lines = []
    changed = False
    for line in read_text(path).splitlines():
        if line.strip().lower().startswith(name_l):
            changed = True
            continue
        new_lines.append(line)
    if changed:
        safe_write_text(path, "\n".join(new_lines).rstrip() + "\n")
    return changed

def grep_import_usage(name: str):
    # Return list of files (outside tests) importing the module
    results = []
    for p in ROOT.rglob("*.py"):
        # skip common ignored dirs
        rel = p.relative_to(ROOT).as_posix()
        if any(seg in rel for seg in [".venv", "venv", ".git", "__pycache__", "site-packages"]):
            continue
        try:
            txt = read_text(p)
        except Exception:
            continue
        if re.search(rf"(^|\s)import\s+{re.escape(name)}(\s|$)|from\s+{re.escape(name)}\s+import\s", txt):
            # consider 'tests/' as test-only, others runtime
            if not rel.lower().startswith(("tests/", "test/", "testing/")):
                results.append(rel)
    return sorted(set(results))

def pick_best_pin(occurrences):
    """
    occurrences: list of full lines like 'tqdm==4.66.4' or 'tqdm>=4'
    Strategy: if multiple pins conflict, prefer existing pin in requirements.txt.
    Else choose any exact '==' highest version seen; else fallback to unpinned 'tqdm'.
    """
    exact_pins = []
    ge_pins = []
    any_unpinned = False
    for line in occurrences:
        m = re.search(r"==\s*([0-9][^,\s#]+)", line)
        if m:
            exact_pins.append(m.group(1))
        m2 = re.search(r">=\s*([0-9][^,\s#]+)", line)
        if m2:
            ge_pins.append(m2.group(1))
        if re.fullmatch(r"\s*tqdm\s*", line.strip(), re.IGNORECASE):
            any_unpinned = True
    def version_key(v):  # simplistic semver-ish split
        return tuple(int(x) if x.isdigit() else 0 for x in re.split(r"[^\d]+", v) if x != "")
    if exact_pins:
        best = sorted(exact_pins, key=version_key)[-1]
        return f"tqdm=={best}"
    if ge_pins:
        best = sorted(ge_pins, key=version_key)[-1]
        return f"tqdm>={best}"
    return "tqdm" if any_unpinned or not occurrences else occurrences[0]

def run_cmd(cmd, phase_step, env=None):
    try:
        log_line(f"$ {cmd}")
        p = subprocess.run(shlex.split(cmd), capture_output=True, text=True, env=env, cwd=str(ROOT))
        with RUN_LOG.open("a", encoding="utf-8") as f:
            f.write(p.stdout)
            f.write(p.stderr)
        if p.returncode != 0:
            raise RuntimeError(f"Command failed ({p.returncode}): {cmd}\n{p.stderr.strip()[:4000]}")
        return True
    except Exception as e:
        append_error_block(phase_step, str(e), f"cmd={cmd}")
        return False

def update_readme_with_note():
    readme = find_first_existing(README_CANDS)
    if not readme:
        # create minimal README note
        safe_write_text(ROOT / "README.md",
                        "# Installation\n\n```\npip install -r requirements.txt\n```\n\nRuntime dependencies include: `tqdm`.\n")
        append_changelog_text("- README.md created with installation section including `tqdm`.")
        return True
    content = read_text(readme)
    if "tqdm" in content:
        append_changelog_text(f"- {readme.name}: already mentions `tqdm` (no change).")
        return False
    # Insert a small note under first Installation/Usage section if found
    new_content = content
    inserted = False
    for heading in ["## Installation", "### Installation", "## Usage", "### Usage"]:
        if heading in content:
            idx = content.index(heading) + len(heading)
            insert_at = content.find("\n", idx)
            if insert_at == -1:
                insert_at = len(content)
            note = "\n\n> Runtime dependency note: this project uses `tqdm`. Ensure it’s installed via `pip install -r requirements.txt`.\n"
            new_content = content[:insert_at] + note + content[insert_at:]
            inserted = True
            break
    if not inserted:
        new_content = content.rstrip() + "\n\n### Installation\n\n```\npip install -r requirements.txt\n```\n\nRuntime dependencies include: `tqdm`.\n"
    safe_write_text(readme, new_content)
    append_changelog_text(f"- {readme.name}: added runtime dependency note for `tqdm`.")
    return True

def main():
    append_changelog("Move tqdm from test to main requirements (best-effort)")
    log_line("PHASE 1: Preparation")

    if GITHUB_WORKFLOWS.exists():
        log_line("GitHub workflows directory detected; script will not write there by policy.")

    req_main = find_first_existing(REQ_MAIN_CANDIDATES) or (ROOT / "requirements.txt")
    req_test = find_first_existing(REQ_TEST_CANDIDATES)
    req_dev = find_first_existing(DEV_REQ_CANDIDATES)

    # PHASE 2: Search & Mapping
    log_line("PHASE 2: Search & Mapping")
    occurrences = []
    locations = {}
    for fp in [req_main, req_test, req_dev]:
        if fp and fp.exists():
            deps = parse_requirements(fp)
            for name, raw in deps:
                if name.lower() == D:
                    occurrences.append(raw)
                    locations.setdefault(fp.name, []).append(raw)

    # Explore code usage
    usage_runtime = grep_import_usage(D)

    append_changelog_text(f"- Discovered occurrences: {json.dumps(locations, indent=2)}")
    append_changelog_text(f"- Runtime usage (non-test): {usage_runtime if usage_runtime else 'none detected'}")

    # PHASE 3: Best-Effort Construction
    log_line("PHASE 3: Best-Effort Construction")
    chosen = pick_best_pin(occurrences if occurrences else ["tqdm"])
    append_changelog_text(f"- Chosen pin/line for requirements.txt: `{chosen}`")

    # Ensure main requirements exists and contains tqdm
    added_to_main = add_dep_to_requirements(req_main, chosen)
    if added_to_main:
        append_changelog_text(f"- Added `{chosen}` to {req_main.name}.")
    else:
        append_changelog_text(f"- `{D}` already present in {req_main.name} (no change).")

    # PHASE 4: Validation
    log_line("PHASE 4: Validation")
    pip_ok = run_cmd(f"{shlex.quote(sys.executable)} -m pip install -r {req_main.name}", "PHASE 4: pip install")
    validator_exists = (ROOT / "secondary_copilot_validator.py").exists()
    validator_ok = True
    if validator_exists:
        validator_ok = run_cmd(f"{shlex.quote(sys.executable)} secondary_copilot_validator.py --validate",
                               "PHASE 4: validator run")
    else:
        append_changelog_text("- Validator not found: secondary_copilot_validator.py (skipping).")
        log_line("Validator script not found; skipping validation step.")

    # PHASE 5: Controlled Pruning
    log_line("PHASE 5: Controlled Pruning")
    pruned = False
    rationale = ""
    if req_test and req_test.exists():
        # Only prune if validation succeeded and dep present in main
        main_has = any(n == D for n, _ in parse_requirements(req_main))
        if main_has and pip_ok and validator_ok:
            pruned = remove_dep_from_requirements(req_test, D)
            if pruned:
                if usage_runtime:
                    rationale = f"Moved `tqdm` to runtime based on usage in: {usage_runtime}"
                else:
                    rationale = "Consolidated shared dependency into runtime requirements."
                append_changelog_text(f"- Pruned `{D}` from {req_test.name}. Rationale: {rationale}")
            else:
                append_changelog_text(f"- `{D}` not present in {req_test.name}` or already pruned.")
        else:
            append_changelog_text(
                f"- Deferred pruning from {req_test.name}: "
                f"{'validation failed' if (not pip_ok or not validator_ok) else 'runtime dep missing in main'}."
            )

    # README note
    log_line("Updating README with runtime note for tqdm")
    try:
        update_readme_with_note()
    except Exception as e:
        append_error_block("PHASE 3: README Update", str(e), "Attempted to insert dependency note for `tqdm`.")

    # PHASE 6: Error capture already done inline

    # PHASE 7: Finalization
    log_line("PHASE 7: Finalization")
    summary = {
        "added_to_main": added_to_main,
        "pruned_from_test": pruned,
        "pip_ok": pip_ok,
        "validator_ok": validator_ok,
        "rationale": rationale,
    }
    append_changelog_text(f"- Summary: {json.dumps(summary, indent=2)}")

    # Exit code logic
    if not pip_ok or not validator_ok:
        log_line("Exiting with failure due to validation/pip errors.")
        sys.exit(1)
    log_line("Completed successfully.")
    sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        append_error_block("TOPLEVEL: main()", str(e), "Unhandled exception in script execution")
        raise
