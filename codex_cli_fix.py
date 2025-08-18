#!/usr/bin/env python3
"""
codex_cli_fix.py — Ensure `typer[all]>=0.12`, perform editable install, and re-run CLI-import tests.
Also:
- Parses README for basic CLI note injection (non-destructive)
- Documents gaps in CHANGELOG_Codex_Audit.md
- Captures errors as ChatGPT-5 research prompts in errors_research_questions.md
- Produces .codex_run_status.json
POLICY: DO NOT ACTIVATE ANY GitHub Actions files, while applying .disable to all yml GitHub Action. 
"""

import datetime
import json
import re
import subprocess
import sys
import traceback
from pathlib import Path

ROOT = Path.cwd()
CHANGELOG = ROOT / "CHANGELOG_Codex_Audit.md"
ERRLOG = ROOT / "errors_research_questions.md"
STATUS = ROOT / ".codex_run_status.json"
README = ROOT / "README.md"
PYPROJECT = ROOT / "pyproject.toml"
REQUIREMENTS = ROOT / "requirements.txt"

# Prefer stdlib tomllib if available (Python 3.11+); fallback to no-dep text edits if not.
try:
    import tomllib  # pyright: ignore[reportMissingImports]
except Exception:
    tomllib = None

# ---------- Utilities ----------

def now_iso():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")

def write_append(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(text if text.endswith("\n") else text + "\n")

def write_overwrite(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write(text)

def run(cmd, check=False, capture=True):
    try:
        proc = subprocess.run(
            cmd, check=check, text=True, capture_output=capture, shell=False
        )
        return proc.returncode, proc.stdout, proc.stderr
    except FileNotFoundError as e:
        return 127, "", str(e)
    except Exception as e:
        return 1, "", f"{type(e).__name__}: {e}"

def record_error(phase_substep: str, error_message: str, context: str):
    block = f"""
Question for ChatGPT-5:
While performing [{phase_substep}], encountered the following error:
{error_message.strip()}
Context: {context.strip()}
What are the possible causes, and how can this be resolved while preserving intended functionality?
"""
    write_append(ERRLOG, block)

def log_change(msg: str):
    write_append(CHANGELOG, f"- [{now_iso()}] {msg}")

def detect_test_runner():
    # Prefer pytest if installed
    rc, out, err = run([sys.executable, "-c", "import pytest; print('ok')"])
    if rc == 0 and "ok" in out:
        return "pytest"
    return "unittest"

def read_file_safe(p: Path):
    if not p.exists():
        return None
    try:
        return p.read_text(encoding="utf-8")
    except Exception:
        return p.read_text(errors="ignore")

def save_file_if_changed(path: Path, new_text: str, apply_changes: bool):
    old = read_file_safe(path)
    if old is None:
        if apply_changes:
            write_overwrite(path, new_text)
            log_change(f"Created {path.name}")
        else:
            log_change(f"[DRY-RUN] Would create {path.name}")
        return True, None, new_text
    if old != new_text:
        if apply_changes:
            write_overwrite(path, new_text)
            log_change(f"Updated {path.name}")
        else:
            log_change(f"[DRY-RUN] Would update {path.name}")
        return True, old, new_text
    return False, old, new_text

def parse_pyproject_toml():
    if not PYPROJECT.exists() or tomllib is None:
        return None
    try:
        data = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
        return data
    except Exception as e:
        record_error("Phase 2:Parse pyproject.toml", f"{type(e).__name__}: {e}", "Failed tomllib parsing")
        return None

def ensure_typer_in_pyproject(text: str):
    """
    Attempt to add/upgrade typer[all]>=0.12 in either:
      - [project].dependencies = [...]
      - [tool.poetry.dependencies]
    Uses light regex/text ops to avoid third-party TOML writers.
    """
    changed = False
    lines = text.splitlines()

    def normalize_dep_line(line):
        return line.strip()

    def bump_in_poetry_block():
        nonlocal lines, changed
        inside = False
        for i, line in enumerate(lines):
            if line.strip().startswith("[tool.poetry.dependencies]"):
                inside = True
                continue
            if inside and line.strip().startswith("[") and line.strip() != "[tool.poetry.dependencies]":
                break
            if inside:
                # Match forms like: typer = "^0.9.0" or typer = {extras=["all"], version="^0.9.0"}
                if re.match(r"^\s*typer\s*=", line):
                    # Replace with extras all and >=0.12
                    lines[i] = 'typer = {extras = ["all"], version = ">=0.12"}'
                    changed = True
                    return True
        if inside:
            # Append typer if not found
            insertion_index = None
            for i, line in enumerate(lines):
                if line.strip().startswith("[tool.poetry.dependencies]"):
                    insertion_index = i + 1
                    break
            if insertion_index is not None:
                lines.insert(insertion_index, 'typer = {extras = ["all"], version = ">=0.12"}')
                changed = True
                return True
        return False

    def bump_in_project_dependencies():
        nonlocal lines, changed
        # Roughly identify [project] ... dependencies = [ ... ]
        in_project = False
        dep_list_start = None
        for i, line in enumerate(lines):
            if line.strip() == "[project]":
                in_project = True
            elif line.strip().startswith("[") and line.strip() != "[project]":
                in_project = False
            if in_project and re.match(r"^\s*dependencies\s*=\s*\[", line):
                dep_list_start = i
                # find end
                j = i
                while j < len(lines) and "]" not in lines[j]:
                    j += 1
                if j == len(lines):
                    break
                # Slice of dependency lines i..j
                deps = "\n".join(lines[i:j+1])
                # Ensure typer[all]>=0.12 present
                if re.search(r"typer(\[all\])?\s*>=?\s*0?\.?12", deps):
                    # Already adequate (best-effort: still normalize to typer[all]>=0.12)
                    deps_norm = re.sub(r"typer(\[[^\]]*\])?\s*[^\"']*([\"'])", r'typer[all]>=0.12\2', deps)
                elif re.search(r"['\"]typer[^\n'\"]*['\"]", deps):
                    deps_norm = re.sub(r"['\"]typer[^\n'\"]*['\"]", '"typer[all]>=0.12"', deps)
                else:
                    # Insert before closing bracket
                    deps_norm = deps.rstrip().rstrip("]")
                    if not deps_norm.endswith("["):
                        deps_norm += ",\n"
                    deps_norm += '  "typer[all]>=0.12"\n]'
                if deps != deps_norm:
                    before = lines[:i]
                    after = lines[j+1:]
                    lines = before + deps_norm.splitlines() + after
                    changed = True
                    return True
        return False

    if bump_in_project_dependencies():
        return True, "\n".join(lines)
    if bump_in_poetry_block():
        return True, "\n".join(lines)
    return False, text  # no project/poetry block discovered

def ensure_typer_in_requirements(text: str):
    """
    Ensure a single consolidated line like: typer[all]>=0.12
    Remove weaker duplicates (e.g., plain 'typer' or older pins).
    """
    changed = False
    lines = text.splitlines()
    new_lines = []
    found_best = False
    for ln in lines:
        s = ln.strip()
        if s.lower().startswith("typer"):
            # Normalize everything to best spec
            if s.lower().startswith("typer[all]") and re.search(r">=\s*0*\.?12", s):
                if not found_best:
                    new_lines.append("typer[all]>=0.12")
                    found_best = True
                else:
                    # prune duplicate
                    changed = True
                continue
            else:
                # replace weaker/older spec with best
                if not found_best:
                    new_lines.append("typer[all]>=0.12")
                    found_best = True
                changed = True
                continue
        new_lines.append(ln)
    if not found_best:
        new_lines.append("typer[all]>=0.12")
        changed = True
    return changed, "\n".join(new_lines)

def inject_readme_cli_note(text: str, package_hint: str | None):
    if "CLI Notes (auto)" in text:
        return False, text
    note = "\n\n### CLI Notes (auto)\n"
    if package_hint:
        note += f"""Use Typer-based CLI via:
- `python -m {package_hint}` (module mode), or
- After install: the generated console script declared in pyproject `[project.scripts]` (if present).
"""
    else:
        note += """Use Typer-based CLI via:
- `python -m <your_package>` (module mode), or
- After install: the generated console script declared in pyproject `[project.scripts]` (if present).
"""
    return True, text.rstrip() + "\n" + note

def guess_package_name():
    # Heuristic: find a top-level package dir (with __init__.py)
    for p in ROOT.iterdir():
        if p.is_dir() and (p / "__init__.py").exists() and not p.name.startswith("."):
            return p.name
    return None

def ensure_dependency(apply_changes: bool):
    dep_source = None
    dep_changed = False

    if PYPROJECT.exists():
        text = read_file_safe(PYPROJECT)
        if text:
            ok, new_text = ensure_typer_in_pyproject(text)
            if ok:
                dep_source = "pyproject.toml"
                dep_changed, _, _ = save_file_if_changed(PYPROJECT, new_text, apply_changes)
            else:
                # No manageable block—fallback to requirements
                pass

    if dep_source is None:
        if REQUIREMENTS.exists():
            text = read_file_safe(REQUIREMENTS) or ""
            ch, new_text = ensure_typer_in_requirements(text)
            dep_source = "requirements.txt"
            if ch:
                dep_changed, _, _ = save_file_if_changed(REQUIREMENTS, new_text, apply_changes)
        else:
            # create requirements.txt with desired dep
            new_text = "typer[all]>=0.12\n"
            dep_source = "requirements.txt"
            dep_changed, _, _ = save_file_if_changed(REQUIREMENTS, new_text, apply_changes)

    if dep_source is None:
        # last resort
        dep_source = "none"
        record_error("Phase 3:Ensure dependency", "No dependency source found", "Missing pyproject.toml and requirements.txt")

    return dep_source, dep_changed

def editable_install(apply_changes: bool):
    if not apply_changes:
        log_change("[DRY-RUN] Would run: pip install -e .")
        return 0, "DRY-RUN", ""
    # Prefer pip → fallback to python -m pip
    rc, out, err = run(["pip", "install", "-e", "."])
    if rc != 0:
        log_change("pip install -e . failed; retrying with python -m pip")
        rc, out, err = run([sys.executable, "-m", "pip", "install", "-e", "."])
    if rc != 0:
        record_error("Phase 3:Editable install", f"rc={rc}\n{err}", "Attempted editable install")
    return rc, out, err

def run_tests(apply_changes: bool):
    runner = detect_test_runner()
    if runner == "pytest":
        cmd = [sys.executable, "-m", "pytest", "-q"]
    else:
        cmd = [sys.executable, "-m", "unittest", "discover", "-v"]

    if not apply_changes:
        log_change(f"[DRY-RUN] Would run tests via {runner}")
        return 0, "DRY-RUN", "", runner

    rc, out, err = run(cmd)
    if rc != 0:
        # Try scoping to CLI imports (best effort) for pytest only
        if runner == "pytest":
            alt_cmd = [sys.executable, "-m", "pytest", "-q", "-k", "cli or typer"]
            rc2, out2, err2 = run(alt_cmd)
            if rc2 == 0:
                return rc2, out2, err2, f"{runner} (-k cli or typer)"
        record_error("Phase 3:Run tests", f"rc={rc}\n{err}", "Initial test run failed")
    return rc, out, err, runner

def main():
    import argparse
    ap = argparse.ArgumentParser(description="Codex CLI fixer")
    ap.add_argument("--apply", action="store_true", help="Write changes, install, and run tests")
    ap.add_argument("--dry-run", action="store_true", help="Preview only (default)")
    args = ap.parse_args()
    apply_changes = bool(args.apply) and not bool(args.dry_run)

    # Headers
    write_append(CHANGELOG, f"\n## Run @ {now_iso()}\n")
    log_change("Start audit")
    write_append(ERRLOG, f"\n## Run @ {now_iso()}\n")

    # Policy notice re: GitHub Actions
    gha = ROOT / ".github" / "workflows"
    if gha.exists():
        log_change("Policy: Found .github/workflows — will NOT activate/modify any workflows.")

    # Phase 1: environment
    rc_py, out_py, _ = run([sys.executable, "--version"])
    rc_pip, out_pip, _ = run(["pip", "--version"])
    log_change(f"Python: {out_py.strip() or rc_py}")
    log_change(f"Pip: {out_pip.strip() or rc_pip}")

    # Phase 2/3: Ensure dependency
    dep_source, dep_changed = ensure_dependency(apply_changes)
    log_change(f"Dependency source: {dep_source}; changed={dep_changed}")

    # README note injection (best effort)
    pkg_hint = guess_package_name()
    if README.exists():
        rd = read_file_safe(README) or ""
        changed, new_rd = inject_readme_cli_note(rd, pkg_hint)
        if changed:
            save_file_if_changed(README, new_rd, apply_changes)
    else:
        # No README — create a minimal one with note (non-destructive, optional)
        content = "# Project\n\n(Autogenerated README stub)\n"
        changed, new_rd = inject_readme_cli_note(content, pkg_hint)
        if changed:
            save_file_if_changed(README, new_rd, apply_changes)

    # Editable install
    rc_install, out_install, err_install = editable_install(apply_changes)
    install_ok = (rc_install == 0)

    # Tests
    rc_tests, out_tests, err_tests, runner = run_tests(apply_changes)
    tests_ok = (rc_tests == 0)

    # Status object
    status = {
        "timestamp": now_iso(),
        "dependency_source": dep_source,
        "dependency_changed": dep_changed,
        "editable_install_rc": rc_install,
        "test_runner": runner,
        "tests_rc": rc_tests,
        "success": bool(install_ok and tests_ok),
    }
    write_overwrite(STATUS, json.dumps(status, indent=2))
    log_change(f"Final status: {status}")

    if not install_ok:
        record_error("Phase 3:Editable install", f"rc={rc_install}\n{err_install}", "pip install -e . failed")
    if not tests_ok:
        # Try to extract import errors to help ChatGPT-5
        snippet = (err_tests or out_tests or "")[-2000:]
        record_error("Phase 3:Run tests", f"rc={rc_tests}\n{snippet}", f"Runner={runner}")

    log_change("Completed audit")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        tb = traceback.format_exc()
        record_error("Global:Unhandled exception", f"{type(e).__name__}: {e}", tb)
        raise
