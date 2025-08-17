#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
codex_workflow.py — End-to-end helper for prioritized test repair against stub modules.

Capabilities:
- Parse docs/STUB_MODULE_STATUS.md for prioritized modules
- Map tests -> source modules via AST heuristics
- Best-effort construct missing modules/symbols
- README link fixups (safe replacements/removals)
- Run pytest, capture reports, and parse failures
- Change log + research question capture (ChatGPT-5 format)
- Explicitly does NOT activate GitHub Actions

Usage:
  python codex_workflow.py
"""

import ast
import re
import sys
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

# ------------------------------
# Constants & Paths
# ------------------------------
REPO_ROOT = Path(__file__).resolve().parent
TESTS_DIR = REPO_ROOT / "tests"
DOCS_DIR = REPO_ROOT / "docs"
REPORTS_DIR = REPO_ROOT / "reports"
CHANGELOG = REPO_ROOT / "codex_change_log.md"
QUESTIONS = REPO_ROOT / "codex_research_questions.md"
RUNLOG = REPO_ROOT / "codex_run.log"
README = REPO_ROOT / "README.md"
STUB_STATUS = DOCS_DIR / "STUB_MODULE_STATUS.md"
GHA_DIR = REPO_ROOT / ".github" / "workflows"
PYTEST_REPORT = REPORTS_DIR / "test_results.txt"

# Common source roots to probe
SOURCE_ROOTS = [
    REPO_ROOT / "src",
    REPO_ROOT,  # direct top-level modules
]

# ------------------------------
# Utilities
# ------------------------------


def log(msg: str):
    RUNLOG.parent.mkdir(parents=True, exist_ok=True)
    with RUNLOG.open("a", encoding="utf-8") as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    print(msg)


def append_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(content.rstrip() + "\n")


def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write(content)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def safe_rel(p: Path) -> str:
    try:
        return str(p.relative_to(REPO_ROOT))
    except ValueError:
        return str(p)


def run_pytest() -> Tuple[int, str]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", "-q"],
            cwd=REPO_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
        output = proc.stdout
        write_file(PYTEST_REPORT, output)
        return proc.returncode, output
    except Exception as e:
        msg = f"pytest invocation failed: {e}"
        append_research_question(
            step="11:Run full test suite",
            error_message=str(e),
            context="Could not execute pytest; environment or dependencies may be missing."
        )
        return 1, msg


def parse_stub_status(md: str) -> List[str]:
    """
    Very simple parser to extract module names mentioned as stubs.
    Accept lines like '- module_name' or table cells containing module paths.
    """
    modules = set()
    for line in md.splitlines():
        line = line.strip()
        # Bullet or table cell heuristic
        m = re.findall(r"([A-Za-z0-9_./\\-]+)\.py", line)
        for token in m:
            # Normalize pathish -> module stem
            stem = Path(token).stem
            if stem:
                modules.add(stem)
    return sorted(modules)


def find_tests() -> List[Path]:
    return sorted(TESTS_DIR.glob("test_*.py")) if TESTS_DIR.exists() else []


def ast_parse_symbols_from_test(test_path: Path) -> Dict[str, List[str]]:
    """
    Parse a test file to infer:
      - imports: modules under test
      - attribute usage: functions/classes likely required
    """
    content = read_text(test_path)
    info = {"imports": [], "attributes": []}
    try:
        tree = ast.parse(content)
    except Exception as e:
        append_research_question(
            step="5:Parse test AST",
            error_message=str(e),
            context=f"Failed parsing {safe_rel(test_path)}"
        )
        return info

    class Visitor(ast.NodeVisitor):
        def visit_Import(self, node: ast.Import):
            for n in node.names:
                info["imports"].append(n.name)

        def visit_ImportFrom(self, node: ast.ImportFrom):
            if node.module:
                info["imports"].append(node.module)

        def visit_Attribute(self, node: ast.Attribute):
            # Collect attribute names used; heuristic only.
            if isinstance(node.attr, str):
                info["attributes"].append(node.attr)
            self.generic_visit(node)

        def visit_Call(self, node: ast.Call):
            # capture function names used
            if isinstance(node.func, ast.Attribute) and isinstance(node.func.attr, str):
                info["attributes"].append(node.func.attr)
            elif isinstance(node.func, ast.Name):
                info["attributes"].append(node.func.id)
            self.generic_visit(node)

    Visitor().visit(tree)
    # Deduplicate while preserving order
    info["imports"] = list(dict.fromkeys(info["imports"]))
    info["attributes"] = list(dict.fromkeys(info["attributes"]))
    return info


def guess_module_paths(test_path: Path, imports: List[str]) -> List[Path]:
    """
    Given `tests/test_<name>.py`, try to locate a corresponding module.
    Heuristics:
      1) test_<name>.py -> <name>.py in SOURCE_ROOTS
      2) Prefer paths derived from explicit imports (e.g., package.module).
    """
    candidates = []

    # Heuristic from test filename
    name = test_path.stem.replace("test_", "", 1)
    if name:
        for root in SOURCE_ROOTS:
            candidates.append(root / f"{name}.py")

    # Heuristic from imports (package.module)
    for imp in imports:
        parts = imp.split(".")
        for root in SOURCE_ROOTS:
            if len(parts) >= 2:
                candidates.append(root.joinpath(*parts[:-1], f"{parts[-1]}.py"))
            else:
                candidates.append(root / f"{imp}.py")

    # Deduplicate
    uniq = []
    seen = set()
    for c in candidates:
        key = c.resolve()
        if key not in seen:
            seen.add(key)
            uniq.append(c)
    return uniq


def ensure_module_exists(module_path: Path, reason: str):
    if module_path.exists():
        return
    write_file(
        module_path,
        f'''"""
Auto-created by codex_workflow.py
Reason: {reason}
"""

# TODO(Codex): Implement real logic to satisfy tests while preserving intended behavior.
def _placeholder():
    """No-op placeholder to keep module importable."""
    return None
'''
    )
    append_change_log(f"Created stub module: {safe_rel(module_path)} (reason: {reason})")


def parse_module_symbols(module_path: Path) -> Dict[str, str]:
    """
    Return {symbol_name: 'function'|'class'|'other'}
    """
    content = read_text(module_path)
    out: Dict[str, str] = {}
    if not content:
        return out
    try:
        tree = ast.parse(content)
    except Exception as e:
        append_research_question(
            step="7:Parse source AST",
            error_message=str(e),
            context=f"Failed parsing {safe_rel(module_path)}"
        )
        return out

    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            out[node.name] = "function"
        elif isinstance(node, ast.AsyncFunctionDef):
            out[node.name] = "function"
        elif isinstance(node, ast.ClassDef):
            out[node.name] = "class"
        else:
            # ignore assignments / constants
            pass
    return out


def add_missing_symbol(module_path: Path, symbol: str, kind: str):
    content = read_text(module_path)
    if not content:
        ensure_module_exists(module_path, f"Initialize module for missing symbol {symbol}")
        content = read_text(module_path)

    snippet = ""
    if kind == "function":
        snippet = f"""

def {symbol}(*args, **kwargs):
    \"\"\"TODO(Codex): Implement {symbol} to satisfy tests without breaking contracts.\"\"\"
    # Minimal best-effort: return None or passthrough
    return None
"""
    elif kind == "class":
        snippet = f"""

class {symbol}:
    \"\"\"TODO(Codex): Implement class {symbol} with minimal viable interface.\"\"\"
    def __init__(self, *args, **kwargs):
        pass
"""
    else:
        snippet = f"""

# TODO(Codex): symbol '{symbol}' referenced by tests—add correct implementation.
{symbol} = None
"""

    write_file(module_path, content.rstrip() + "\n" + snippet)
    append_change_log(f"Added {kind} '{symbol}' to {safe_rel(module_path)} (best-effort).")


def classify_symbol_kind_from_test_usage(symbol: str) -> str:
    # Heuristic: names in ALL_CAPS → constant; CamelCase → class; else → function.
    if symbol.isupper():
        return "other"
    if re.match(r"[A-Z][A-Za-z0-9]+$", symbol):
        return "class"
    return "function"


def fix_readme_references():
    if not README.exists():
        return
    content = read_text(README)
    # Replace dead relative links to .py files that were created/moved
    # Heuristic: convert links pointing to non-existent targets into code literals.
    pattern = re.compile(r"\(([^)]+\.py)\)")

    def repl(m):
        target = m.group(1)
        path = REPO_ROOT / target
        if not path.exists():
            append_change_log(f"README: replaced dead link ({target}) with inline code.")
            return f"`{target}`"
        return f"({target})"

    new_content = re.sub(pattern, repl, content)
    if new_content != content:
        write_file(README, new_content)
        append_change_log("README: updated references (safe replacements/removals).")


def parse_pytest_failures(output: str) -> List[Dict[str, str]]:
    """
    Very heuristic parsing to capture failing tests and error heads.
    """
    failures = []
    lines = output.splitlines()
    current = None
    for ln in lines:
        if re.match(r"^=+ FAILURES =+$", ln):
            current = {"test": "", "error": ""}
            continue
        if current is not None:
            if ln.strip().startswith("___") and " ___" in ln:
                # Test header line e.g. "___ TestClass::test_name ___"
                if current["test"] or current["error"]:
                    failures.append(current)
                    current = {"test": "", "error": ""}
                current["test"] = ln.strip("_ ").strip()
            elif ln.startswith("E   "):
                current["error"] += ln + "\n"
            elif re.match(r"^=+ short test summary info =+$", ln):
                # close out
                if current["test"] or current["error"]:
                    failures.append(current)
                current = None
    return failures


def append_change_log(entry: str):
    append_file(CHANGELOG, f"- {entry}")


def append_research_question(step: str, error_message: str, context: str):
    block = f"""
Question for ChatGPT-5:
While performing [{step}], encountered the following error:
{error_message}
Context: {context}
What are the possible causes, and how can this be resolved while preserving intended functionality?
"""
    append_file(QUESTIONS, block.strip() + "\n")


def assert_no_gha_activation():
    if GHA_DIR.exists():
        # Just log their presence; do not modify/enable anything.
        append_change_log("Confirmed presence of .github/workflows; no activation performed.")


# ------------------------------
# Main Workflow
# ------------------------------


def main():
    # Phase 1: Preparation
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    write_file(CHANGELOG, "# Codex Change Log\n\n")
    write_file(QUESTIONS, "# Codex Research Questions\n\n")
    write_file(RUNLOG, "")

    log("Phase 1: Preparation started.")
    stub_modules = parse_stub_status(read_text(STUB_STATUS))
    all_tests = find_tests()

    # Prioritize tests matching stub modules (by stem heuristic)
    prioritized = []
    others = []
    stub_set = set(stub_modules)
    for t in all_tests:
        name = t.stem.replace("test_", "", 1)
        if name in stub_set:
            prioritized.append(t)
        else:
            others.append(t)
    test_order = prioritized + others

    append_change_log(f"Discovered {len(all_tests)} tests; prioritized {len(prioritized)} by stub status.")
    log(f"Prioritized tests: {[safe_rel(p) for p in prioritized]}")

    # Phase 2 & 3: Search/Mapping & Best-Effort Construction
    for idx, test_path in enumerate(test_order, start=1):
        step_tag = f"5..9:Process test {safe_rel(test_path)}"
        try:
            info = ast_parse_symbols_from_test(test_path)
            imports = info["imports"]
            attrs = info["attributes"]

            module_candidates = guess_module_paths(test_path, imports)
            target_module = None
            for cand in module_candidates:
                if cand.exists():
                    target_module = cand
                    break
            if target_module is None and module_candidates:
                target_module = module_candidates[0]
                ensure_module_exists(target_module, f"Derived from {safe_rel(test_path)}")

            if target_module is None:
                append_change_log(f"No module candidate found for {safe_rel(test_path)}; skipping.")
                continue

            # Ensure needed symbols exist
            existing = parse_module_symbols(target_module)
            for sym in attrs:
                # Ignore pytest fixtures / common names
                if sym in ("fixture", "parametrize", "raises", "skip", "mark"):
                    continue
                if sym not in existing:
                    kind = classify_symbol_kind_from_test_usage(sym)
                    add_missing_symbol(target_module, sym, kind)

        except Exception as e:
            append_research_question(
                step=step_tag,
                error_message=str(e),
                context=f"While mapping/constructing for {safe_rel(test_path)}"
            )

    # Phase 5: Execute & Document
    log("Running pytest...")
    rc, output = run_pytest()
    if output:
        failures = parse_pytest_failures(output)
        if failures:
            append_change_log("Remaining test failures:")
            for f in failures:
                append_change_log(f"  * {f.get('test','(unknown)')}")
                append_research_question(
                    step="12:Parse failures",
                    error_message=f.get("error", "(no error excerpt)"),
                    context=f"From {PYTEST_REPORT}"
                )
        else:
            append_change_log("All tests passed or no failure blocks parsed.")

    # Phase 7: README fixes
    fix_readme_references()

    # Phase 8: Finalization
    assert_no_gha_activation()
    summary = f"""
## Summary
- Tests discovered: {len(all_tests)}
- Prioritized by stubs: {len(prioritized)}
- Pytest return code: {rc}
- Reports: {safe_rel(PYTEST_REPORT)}
"""
    append_file(CHANGELOG, summary.strip() + "\n")
    log("Workflow complete.")
    sys.exit(rc)


if __name__ == "__main__":
    main()

