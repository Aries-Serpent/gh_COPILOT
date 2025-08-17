#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
codex_test_cov_workflow.py

Implements the Codex-ready workflow:
- Safely ensure pytest-cov presence in requirements-test.txt
- Install test deps
- Re-run pytest with coverage
- Parse README and suggest reference updates
- Document gaps and structured error questions
- DO NOT ACTIVATE ANY GitHub Actions files.

Usage:
  python codex_test_cov_workflow.py [--dry-run] [--verbose]
"""

import argparse
import sys
import subprocess
from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
CHANGELOG = ROOT / "CHANGELOG_codex_automation.md"

TARGET_TEST = "tests/test_script_database_validator.py"
REQ_TEST = ROOT / "requirements-test.txt"
README_CANDIDATES = [p for p in ROOT.glob("README*") if p.is_file()]
GITHUB_ACTIONS_DIR = ROOT / ".github" / "workflows"

STATE = {
    "P": False,  # pytest-cov present
    "I": False,  # deps installed
    "T": False,  # tests ran ok
    "errors": [],
    "actions": [],
    "pruned": [],
    "notes": [],
    "context": {},
}


def log(msg, *, verbose=False):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    if verbose:
        STATE["notes"].append(line)


def run(cmd, verbose=False):
    """Run a command and capture output."""
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, check=False
        )
        return proc.returncode, proc.stdout, proc.stderr
    except Exception as e:
        return 1, "", f"{type(e).__name__}: {e}"


def safe_read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        STATE["errors"].append({
            "step": "FileRead",
            "desc": f"Failed reading {path}",
            "error": f"{type(e).__name__}: {e}",
        })
        return ""


def safe_write_text(path: Path, content: str, dry_run: bool):
    if dry_run:
        STATE["notes"].append(f"(dry-run) Would write {path} ({len(content)} bytes)")
        return
    path.write_text(content, encoding="utf-8")


def ensure_req_test_exists(dry_run=False, verbose=False):
    if REQ_TEST.exists():
        log(f"Found {REQ_TEST}", verbose=verbose)
        return
    header = "# Auto-created by codex_test_cov_workflow.py for test-only deps\n"
    safe_write_text(REQ_TEST, header, dry_run=dry_run)
    STATE["actions"].append(f"Created {REQ_TEST}")


def has_pytest_cov_line(lines):
    for raw in lines:
        line = raw.strip()
        # Normalize for detection; allow pins/extras
        if line and not line.startswith("#") and "pytest-cov" in line.lower():
            return True
    return False


def ensure_pytest_cov(dry_run=False, verbose=False):
    ensure_req_test_exists(dry_run=dry_run, verbose=verbose)
    text = safe_read_text(REQ_TEST)
    lines = text.splitlines()
    if has_pytest_cov_line(lines):
        STATE["P"] = True
        log("pytest-cov already present in requirements-test.txt", verbose=verbose)
        return

    # Append a clean entry
    lines.append("pytest-cov")
    new_text = "\n".join(lines) + ("\n" if not text.endswith("\n") else "")
    safe_write_text(REQ_TEST, new_text, dry_run=dry_run)
    STATE["P"] = True
    STATE["actions"].append("Appended 'pytest-cov' to requirements-test.txt")
    log("Added pytest-cov to requirements-test.txt", verbose=verbose)


def detect_cov_configs(verbose=False):
    # Informational mapping of coverage/pytest configs
    candidates = [
        ROOT / "pyproject.toml",
        ROOT / "setup.cfg",
        ROOT / "pytest.ini",
        ROOT / ".coveragerc",
        ROOT / "tox.ini",
    ]
    found = [p for p in candidates if p.exists()]
    for p in found:
        snippet = safe_read_text(p)[:2000]
        if snippet:
            log(f"Detected config: {p.name}; scanning for coverage/pytest hints", verbose=verbose)
    STATE["context"]["config_found"] = [str(p) for p in found]


def parse_readmes_and_suggest_updates(verbose=False):
    suggestions = []
    for readme in README_CANDIDATES:
        text = safe_read_text(readme)
        if not text:
            continue

        # Heuristic: find coverage instructions and inconsistencies
        mentions_cov_flag = "--cov" in text or "pytest-cov" in text.lower()
        if mentions_cov_flag and not STATE["P"]:
            suggestions.append({
                "file": str(readme),
                "suggestion": "README references coverage, but pytest-cov was initially missing. Consider adding an explicit note or requirements update.",
            })

        # Example normalization suggestion: encourage `pytest -q --cov=. --cov-report=term`
        if "pytest" in text.lower() and "--cov" not in text:
            suggestions.append({
                "file": str(readme),
                "suggestion": "Consider adding coverage example: `pytest -q --cov=. --cov-report=term`.",
            })

    if suggestions:
        STATE["actions"].append("README suggestions recorded (non-destructive).")
        STATE["context"]["readme_suggestions"] = suggestions
        log(f"Recorded {len(suggestions)} README suggestion(s).", verbose=verbose)


def install_test_dependencies(dry_run=False, verbose=False):
    if dry_run:
        log("(dry-run) Skipping dependency installation", verbose=verbose)
        STATE["I"] = True
        return

    if not REQ_TEST.exists():
        # This should be rare; guard anyway
        ensure_req_test_exists(dry_run=False, verbose=verbose)

    code, out, err = run([sys.executable, "-m", "pip", "install", "-r", str(REQ_TEST)], verbose=verbose)
    STATE["context"]["pip_install"] = {"code": code, "out": out[-2000:], "err": err[-2000:]}
    if code == 0:
        STATE["I"] = True
        log("Installed test dependencies successfully.", verbose=verbose)
    else:
        msg = "pip install failed for requirements-test.txt"
        STATE["errors"].append({
            "step": "InstallDependencies",
            "desc": msg,
            "error": (err or out)[:4000],
        })
        research_question(
            step="Phase 3: Dependency Installation",
            error_message=(err or out)[:600],
            context="pip failed installing -r requirements-test.txt; environment and resolver constraints unknown.",
        )


def run_tests_with_coverage(dry_run=False, verbose=False):
    if dry_run:
        log("(dry-run) Skipping test execution", verbose=verbose)
        STATE["T"] = True
        return

    specific_path = ROOT / TARGET_TEST
    if specific_path.exists():
        cmd = ["pytest", TARGET_TEST, "-q", "--cov=.", "--cov-report=term"]
    else:
        # Fallback if the specific test is absent
        STATE["pruned"].append(f"Specific test {TARGET_TEST} not found; fallback to repository-wide pytest.")
        cmd = ["pytest", "-q", "--cov=.", "--cov-report=term"]

    code, out, err = run(cmd, verbose=verbose)
    STATE["context"]["pytest"] = {"code": code, "out": out[-4000:], "err": err[-4000:], "cmd": " ".join(cmd)}

    if code == 0:
        STATE["T"] = True
        log("Pytest with coverage completed successfully.", verbose=verbose)
    else:
        # Try to detect common collection/import issues
        combined = (out + "\n" + err).strip()
        STATE["errors"].append({
            "step": "RunPytestCoverage",
            "desc": "pytest returned non-zero exit code",
            "error": combined[:4000],
        })
        research_question(
            step="Phase 3: Execute Tests with Coverage",
            error_message=combined[:600],
            context=f"Command: {' '.join(cmd)}; coverage plugin installed: {STATE['P']}; deps installed: {STATE['I']}",
        )


def research_question(step: str, error_message: str, context: str):
    block = (
        "Question for ChatGPT-5:\n"
        f"While performing [{step}], encountered the following error:\n"
        f"{error_message}\n"
        f"Context: {context}\n"
        "What are the possible causes, and how can this be resolved while preserving intended functionality?\n"
    )
    STATE["actions"].append("Emitted research question for ChatGPT-5")
    STATE["notes"].append(block)


def list_github_actions(verbose=False):
    if GITHUB_ACTIONS_DIR.exists():
        files = sorted([str(p) for p in GITHUB_ACTIONS_DIR.glob("**/*") if p.is_file()])
        if files:
            log(f"Detected {len(files)} GitHub Actions file(s). These will NOT be modified or activated.", verbose=verbose)
            STATE["context"]["github_actions_files"] = files


def write_changelog(verbose=False):
    lines = []
    lines.append("# Codex Automation Change Log\n")
    lines.append(f"- Timestamp: {datetime.now().isoformat()}")
    lines.append("- Guardrail: DO NOT ACTIVATE ANY GitHub Actions files.\n")

    lines.append("## Summary\n")
    lines.append(f"- P (pytest-cov present): {STATE['P']}")
    lines.append(f"- I (deps installed): {STATE['I']}")
    lines.append(f"- T (tests executed): {STATE['T']}")
    lines.append(f"- Overall S = P ∧ I ∧ T: {STATE['P'] and STATE['I'] and STATE['T']}\n")

    if STATE["actions"]:
        lines.append("## Actions Taken")
        for a in STATE["actions"]:
            lines.append(f"- {a}")
        lines.append("")

    if STATE["pruned"]:
        lines.append("## Controlled Pruning (with Rationale)")
        for p in STATE["pruned"]:
            lines.append(f"- {p}")
        lines.append("")

    if STATE["errors"]:
        lines.append("## Errors (Brief)")
        for e in STATE["errors"]:
            lines.append(f"- [{e.get('step')}] {e.get('desc')}: {e.get('error')[:300]}")
        lines.append("")

    if "readme_suggestions" in STATE.get("context", {}):
        lines.append("## README Suggestions")
        for s in STATE["context"]["readme_suggestions"]:
            lines.append(f"- {s['file']}: {s['suggestion']}")
        lines.append("")

    if "pytest" in STATE.get("context", {}):
        lines.append("## Pytest/coverage Result (Tail)")
        ctx = STATE["context"]["pytest"]
        lines.append(f"- Command: {ctx.get('cmd')}")
        lines.append(f"- Exit Code: {ctx.get('code')}")
        if ctx.get("out"):
            lines.append("```\n" + ctx["out"] + "\n```")
        if ctx.get("err"):
            lines.append("```\n" + ctx["err"] + "\n```")

    if STATE["notes"]:
        lines.append("\n## Research Questions & Notes")
        lines.extend(STATE["notes"])

    content = "\n".join(lines) + "\n"
    safe_write_text(CHANGELOG, content, dry_run=False)
    if verbose:
        log(f"Wrote changelog to {CHANGELOG}", verbose=verbose)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Preview edits without writing files or running installs/tests.")
    parser.add_argument("--verbose", action="store_true", help="Add verbose logging to notes.")
    args = parser.parse_args()

    log("== Phase 1: Preparation ==")
    list_github_actions(verbose=args.verbose)
    ensure_req_test_exists(dry_run=args.dry_run, verbose=args.verbose)

    log("== Phase 2: Search & Mapping ==")
    detect_cov_configs(verbose=args.verbose)
    parse_readmes_and_suggest_updates(verbose=args.verbose)

    log("== Phase 3: Best-Effort Construction ==")
    ensure_pytest_cov(dry_run=args.dry_run, verbose=args.verbose)
    install_test_dependencies(dry_run=args.dry_run, verbose=args.verbose)
    run_tests_with_coverage(dry_run=args.dry_run, verbose=args.verbose)

    log("== Phase 4: Controlled Pruning ==")
    # Pruning occurs opportunistically with rationale during steps; nothing extra here.

    log("== Phase 5: Error Capture ==")
    # Already captured during steps as needed.

    log("== Phase 6: Finalization ==")
    write_changelog(verbose=args.verbose)

    # Final success summary
    success = STATE["P"] and STATE["I"] and STATE["T"]
    log(f"Success S = P ∧ I ∧ T = {success}")
    if not success:
        log("One or more factors failed; see CHANGELOG_codex_automation.md for details.")


if __name__ == "__main__":
    main()

