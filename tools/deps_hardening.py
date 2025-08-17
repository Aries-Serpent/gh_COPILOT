#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
deps_hardening.py
Guarantee Typer availability (dev/test), ensure global tqdm, align README and CI (non-activating),
add smoke tests, and capture errors as ChatGPT-5 research questions.

USAGE:
  python tools/deps_hardening.py --repo-root . --run-validator --run-tests

DO NOT ACTIVATE ANY GitHub Actions files.
"""
import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple, Optional

REPO_FILES = {
    "pyproject": "pyproject.toml",
    "setup_cfg": "setup.cfg",
    "setup_py": "setup.py",
    "req_base": "requirements.txt",
    "req_dev_candidates": ["requirements-dev.txt", "dev-requirements.txt", "requirements_test.txt"],
    "readme": "README.md",
    "tests_dir": "tests",
    "ci_dir": ".github/workflows",
}
CHANGELOG = "CHANGELOG_DEP_FIX.md"
ERROR_LOG = ".codex_error_log.md"

STEP_CTX = {
    "P1": "Phase 1 Preparation",
    "P2": "Phase 2 Search & Mapping",
    "P3": "Phase 3 Best-Effort Construction",
    "P4": "Phase 4 Controlled Pruning",
    "P5": "Phase 5 Error Capture",
    "P6": "Phase 6 Finalization",
}

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def append_error(phase_step: str, err: Exception, context: str):
    msg = str(err).strip()
    block = (
        "Question for ChatGPT-5:\n"
        f"While performing [{phase_step}], encountered the following error:\n"
        f"{msg}\n"
        f"Context: {context}\n"
        "What are the possible causes, and how can this be resolved while preserving intended functionality?\n\n"
    )
    Path(ERROR_LOG).write_text(Path(ERROR_LOG).read_text() + block if Path(ERROR_LOG).exists() else block, encoding="utf-8")

def safe_write(path: Path, content: str, phase_step: str, ctx: str):
    try:
        if path.exists():
            bak = path.with_suffix(path.suffix + ".bak")
            shutil.copy2(path, bak)
        path.write_text(content, encoding="utf-8")
    except Exception as e:
        append_error(phase_step, e, ctx)
        raise

def ensure_line(path: Path, predicate, line_to_add: str) -> bool:
    """
    For requirements.txt-like files: add line if missing.
    Returns True if modified.
    """
    if not path.exists():
        return False
    lines = path.read_text(encoding="utf-8").splitlines()
    if any(predicate(ln) for ln in lines):
        return False
    lines.append(line_to_add)
    safe_write(path, "\n".join(lines) + "\n", "P3:8 ensure_line", f"Add '{line_to_add}' to {path}")
    return True

def find_dev_req_file(repo: Path) -> Optional[Path]:
    for cand in REPO_FILES["req_dev_candidates"]:
        p = repo / cand
        if p.exists():
            return p
    return None

def add_to_pyproject_dependencies(pyproject: Path, package: str, dev: bool) -> Tuple[bool, str]:
    """
    Minimal, tolerant text manipulation without external TOML libs:
    - For base deps: under [project] dependencies = [...]
    - For dev: under [project.optional-dependencies].dev = [...]
    Returns (modified, rationale).
    """
    if not pyproject.exists():
        return (False, "pyproject.toml not present")
    text = pyproject.read_text(encoding="utf-8")

    def list_has(pkg_line: str, lst: str) -> bool:
        pattern = rf"['\"]{re.escape(pkg_line)}(['\"][^,)]*)?"
        return re.search(pattern, lst) is not None

    modified = False
    rationale = []

    if dev:
        # Ensure [project.optional-dependencies]
        if "[project.optional-dependencies]" not in text:
            text += "\n[project.optional-dependencies]\n"
            modified = True
            rationale.append("created [project.optional-dependencies]")

        # Ensure dev array
        if re.search(r"^\s*dev\s*=\s*\[", text, flags=re.M) is None:
            text += "dev = []\n"
            modified = True
            rationale.append("created dev extras list")

        # Insert package if missing
        text = re.sub(
            r"(^\s*dev\s*=\s*\[)([^\]]*)(\])",
            lambda m: m.group(1)
            + (m.group(2) + ("" if m.group(2).strip() == "" else ", "))
            + f"\"{package}\""
            + m.group(3)
            if not list_has(package, m.group(2))
            else m.group(0),
            text, flags=re.M
        )
        if text != pyproject.read_text(encoding="utf-8"):
            modified = True
            rationale.append(f"added {package} to dev extras")
    else:
        # Base dependencies
        if "[project]" not in text:
            # Try to create a minimal [project] with deps
            text += "\n[project]\ndependencies = []\n"
            modified = True
            rationale.append("created [project] with empty dependencies")

        # Ensure dependencies list exists
        if re.search(r"^\s*dependencies\s*=\s*\[", text, flags=re.M) is None:
            text = re.sub(r"(\[project\][^\n]*\n)", r"\1dependencies = []\n", text)
            modified = True
            rationale.append("created dependencies list")

        # Insert package if missing
        def add_pkg(m):
            inner = m.group(2)
            if not list_has(package, inner):
                return m.group(1) + (inner + ("" if inner.strip() == "" else ", ")) + f"\"{package}\"" + m.group(3)
            return m.group(0)

        new_text = re.sub(r"(^\s*dependencies\s*=\s*\[)([^\]]*)(\])", add_pkg, text, flags=re.M)
        if new_text != text:
            text = new_text
            modified = True
            rationale.append(f"added {package} to base dependencies")

    if modified:
        safe_write(pyproject, text, "P3:8-9 add_to_pyproject_dependencies", f"Ensure {package} (dev={dev})")
    return (modified, "; ".join(rationale) if rationale else "no change")

def add_to_setup_cfg(setup_cfg: Path, package: str, dev: bool) -> Tuple[bool, str]:
    if not setup_cfg.exists():
        return (False, "setup.cfg not present")
    text = setup_cfg.read_text(encoding="utf-8")
    modified = False
    rationale = []

    if dev:
        # extras_require dev =
        if "[options.extras_require]" not in text:
            text += "\n[options.extras_require]\n"
            modified = True
            rationale.append("created [options.extras_require]")
        if re.search(r"^\s*dev\s*=", text, flags=re.M) is None:
            text += "dev =\n"
            modified = True
            rationale.append("created dev extras key")
        # Insert line under dev =
        text = re.sub(
            r"(^\s*dev\s*=\s*\n(?:^\s+.*\n)*)",
            lambda m: m.group(1) + f"    {package}\n"
            if f"    {package}\n" not in m.group(1)
            else m.group(1),
            text, flags=re.M
        )
        if text != setup_cfg.read_text(encoding="utf-8"):
            modified = True
            rationale.append(f"added {package} to dev extras")
    else:
        # install_requires
        if "[options]" not in text:
            text += "\n[options]\ninstall_requires =\n"
            modified = True
            rationale.append("created [options] with install_requires")
        if re.search(r"^\s*install_requires\s*=", text, flags=re.M) is None:
            text = re.sub(r"(\[options\][^\n]*\n)", r"\1install_requires =\n", text)
            modified = True
            rationale.append("created install_requires")
        text = re.sub(
            r"(^\s*install_requires\s*=\s*\n(?:^\s+.*\n)*)",
            lambda m: m.group(1) + f"    {package}\n"
            if f"    {package}\n" not in m.group(1)
            else m.group(1),
            text, flags=re.M
        )
        new_text = text
        if new_text != setup_cfg.read_text(encoding="utf-8"):
            modified = True
            rationale.append(f"added {package} to install_requires")
        text = new_text

    if modified:
        safe_write(setup_cfg, text, "P3:8-9 add_to_setup_cfg", f"Ensure {package} (dev={dev})")
    return (modified, "; ".join(rationale) if rationale else "no change")

def ensure_readme_alignment(readme: Path, has_dev_extras: bool) -> Tuple[bool, str]:
    if not readme.exists():
        return (False, "README.md not present")
    text = readme.read_text(encoding="utf-8")
    original = text

    # Normalize install guidance
    if has_dev_extras:
        text = re.sub(r"pip install\s+(-r\s+\S+|\.\[dev\]|\.)",
                      "pip install .[dev]", text)
    else:
        # Prefer dev requirements file guidance if exists
        text = re.sub(r"pip install\s+(\.\[dev\]|\.)",
                      "pip install -r requirements-dev.txt", text)

    if text != original:
        safe_write(readme, text, "P3:10 ensure_readme_alignment", f"README install guidance updated (dev_extras={has_dev_extras})")
        return (True, "updated README install guidance")
    return (False, "no README changes")

def suggest_ci_amendments(ci_dir: Path, has_dev_extras: bool) -> List[str]:
    suggestions = []
    if not ci_dir.exists():
        return suggestions
    for f in ci_dir.glob("*.y*ml"):
        try:
            body = f.read_text(encoding="utf-8")
            if re.search(r"pip install\s+\.\[dev\]", body):
                continue
            # Only suggest; do not modify workflow execution semantics
            suggestions.append(
                f"- Suggest adding `pip install .[dev]` before test steps in {f.name} (NOT auto-applied)."
                if has_dev_extras else
                f"- Suggest adding `pip install -r requirements-dev.txt` before test steps in {f.name} (NOT auto-applied)."
            )
        except Exception as e:
            append_error("P3:11 suggest_ci_amendments", e, f"Reading {f}")
    return suggestions

def run_cmd(cmd: List[str], cwd: Path, phase_step: str, context: str) -> Tuple[int, str, str]:
    try:
        proc = subprocess.Popen(cmd, cwd=str(cwd), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        out, err = proc.communicate()
        code = proc.returncode
        if code != 0:
            append_error(phase_step, Exception(f"exit {code}: {err.strip()}"), context)
        return code, out, err
    except Exception as e:
        append_error(phase_step, e, context)
        return 1, "", str(e)

def ensure_tests(repo: Path) -> Tuple[bool, Path]:
    tests_dir = repo / REPO_FILES["tests_dir"]
    tests_dir.mkdir(parents=True, exist_ok=True)
    test_file = tests_dir / "test_dependencies_imports.py"
    if not test_file.exists():
        test_file.write_text(
            "def test_dependencies_imports():\n"
            "    missing = []\n"
            "    try:\n"
            "        import tqdm  # noqa: F401\n"
            "    except Exception as e:\n"
            "        missing.append(f\"tqdm: {e}\")\n"
            "    try:\n"
            "        import typer  # noqa: F401\n"
            "    except Exception as e:\n"
            "        missing.append(f\"typer: {e}\")\n"
            "    assert not missing, f\"Missing dependencies: {missing}\"\n",
            encoding="utf-8"
        )
        return True, test_file
    return False, test_file

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--run-validator", action="store_true", help="Run secondary_copilot_validator.py --validate if present")
    parser.add_argument("--run-tests", action="store_true", help="Attempt to run pytest if present")
    args = parser.parse_args()

    repo = Path(args.repo_root).resolve()
    os.chdir(repo)

    changes: List[str] = []
    errors_blocking = False

    # Phase 1: Preparation
    try:
        pre_snapshot = {}
        for key in ["pyproject", "setup_cfg", "setup_py", "req_base", "readme"]:
            p = repo / REPO_FILES.get(key, "")
            if p and p.exists():
                pre_snapshot[str(p)] = sha256(p)
        Path(CHANGELOG).write_text("# Dependency Hardening Change Log\n\n", encoding="utf-8")
    except Exception as e:
        append_error("P1:1-4 Preparation", e, f"repo={repo}")
        errors_blocking = True

    # Phase 2: Search & Mapping
    pyproject = repo / REPO_FILES["pyproject"]
    setup_cfg = repo / REPO_FILES["setup_cfg"]
    setup_py  = repo / REPO_FILES["setup_py"]
    req_base  = repo / REPO_FILES["req_base"]
    readme    = repo / REPO_FILES["readme"]
    ci_dir    = repo / REPO_FILES["ci_dir"]

    # Heuristics for which packaging is active
    uses_pyproject = pyproject.exists()
    uses_setup_cfg = setup_cfg.exists()
    has_dev_extras = False

    # Phase 3: Best-Effort Construction
    # Ensure tqdm in base
    try:
        base_changed = False
        rationale = ""
        if uses_pyproject:
            ch, why = add_to_pyproject_dependencies(pyproject, "tqdm", dev=False)
            base_changed |= ch
            rationale += ("; " if rationale else "") + why
        elif uses_setup_cfg:
            ch, why = add_to_setup_cfg(setup_cfg, "tqdm", dev=False)
            base_changed |= ch
            rationale += ("; " if rationale else "") + why
        else:
            # fallback to requirements.txt
            if req_base.exists():
                base_changed = ensure_line(req_base, lambda s: s.strip().startswith("tqdm"), "tqdm")
                rationale = "added tqdm to requirements.txt" if base_changed else "tqdm already present in requirements.txt"
            else:
                # create requirements.txt
                safe_write(req_base, "tqdm\n", "P3:8 fallback requirements.txt", "created base requirements.txt with tqdm")
                base_changed = True
                rationale = "created requirements.txt with tqdm"
        if base_changed:
            changes.append(f"* Ensured global tqdm in base deps: {rationale}")
    except Exception as e:
        append_error("P3:8 Ensure tqdm globally", e, "Add tqdm to base deps")
        errors_blocking = False  # not blocking yet

    # Ensure typer in dev
    try:
        dev_changed = False
        rationale = ""
        if uses_pyproject:
            ch, why = add_to_pyproject_dependencies(pyproject, "typer", dev=True)
            dev_changed |= ch
            rationale += ("; " if rationale else "") + why
            # best-effort check for dev extras presence
            has_dev_extras = "added typer to dev extras" in rationale or "[project.optional-dependencies]" in pyproject.read_text(encoding="utf-8")
        elif uses_setup_cfg:
            ch, why = add_to_setup_cfg(setup_cfg, "typer", dev=True)
            dev_changed |= ch
            rationale += ("; " if rationale else "") + why
            has_dev_extras = True if "added typer to dev extras" in rationale or "[options.extras_require]" in setup_cfg.read_text(encoding="utf-8") else False
        else:
            dev_req = find_dev_req_file(repo)
            if dev_req is None:
                dev_req = repo / "requirements-dev.txt"
                safe_write(dev_req, "typer\n", "P3:9 create dev requirements", "created requirements-dev.txt with typer")
                dev_changed = True
            else:
                dev_changed |= ensure_line(dev_req, lambda s: s.strip().startswith("typer"), "typer")
            rationale = f"ensured typer in {dev_req.name}"
        if dev_changed:
            changes.append(f"* Ensured typer available in dev/test: {rationale}")
    except Exception as e:
        append_error("P3:9 Ensure typer in dev", e, "Add typer to dev deps")
        errors_blocking = False

    # README alignment
    try:
        ch, why = ensure_readme_alignment(readme, has_dev_extras=has_dev_extras)
        if ch:
            changes.append(f"* README alignment: {why}")
    except Exception as e:
        append_error("P3:10 README alignment", e, f"readme={readme}")
        errors_blocking = False

    # CI recommendations (non-activating)
    try:
        suggestions = suggest_ci_amendments(ci_dir, has_dev_extras=has_dev_extras)
        if suggestions:
            changes.append("* CI (non-activating) recommendations:\n" + "\n".join(suggestions))
    except Exception as e:
        append_error("P3:11 CI suggestions", e, f"ci_dir={ci_dir}")
        errors_blocking = False

    # Regression hooks
    if args.run_validator and (repo / "secondary_copilot_validator.py").exists():
        code, out, err = run_cmd([sys.executable, "secondary_copilot_validator.py", "--validate"], repo, "P3:12 validator", "secondary_copilot_validator.py --validate")
        changes.append(f"* Validator run exit={code}")
        if code != 0:
            errors_blocking = True

    # Test scaffold
    try:
        created, test_path = ensure_tests(repo)
        if created:
            changes.append(f"* Created smoke test: {test_path.relative_to(repo)}")
    except Exception as e:
        append_error("P3:12 Create tests", e, f"tests_dir={REPO_FILES['tests_dir']}")
        errors_blocking = False

    # Phase 4: Controlled Pruning — (Advisory; no auto deletion)
    # We only document if duplicate declarations were detected (heuristic)
    try:
        dup_note = []
        if uses_pyproject and (uses_setup_cfg or (repo / REPO_FILES["req_base"]).exists()):
            dup_note.append("- Detected multiple dependency declaration surfaces; prefer pyproject.toml as source-of-truth. Consider pruning duplicates.")
        if dup_note:
            changes.append("* Pruning advisories:\n" + "\n".join(dup_note))
    except Exception as e:
        append_error("P4:13 Pruning advisories", e, "dup detection")
        errors_blocking = False

    # Optional: run pytest if requested
    if args.run_tests:
        if (repo / "pytest.ini").exists() or (repo / "pyproject.toml").exists() or (repo / "tests").exists():
            code, out, err = run_cmd(["pytest", "-q"], repo, "P3:12 pytest", "pytest -q for smoke deps")
            changes.append(f"* pytest run exit={code}")
            if code != 0:
                errors_blocking = True

    # Phase 6: Finalization
    try:
        with Path(CHANGELOG).open("a", encoding="utf-8") as chlog:
            chlog.write("## Summary of Changes\n\n")
            for c in changes:
                chlog.write(c.strip() + "\n")
            chlog.write("\n### Notes\n- DO NOT ACTIVATE ANY GitHub Actions files; suggestions are non-executable guidance only.\n")
            chlog.write("\n### Remaining Errors\n")
            if Path(ERROR_LOG).exists():
                chlog.write(f"- See {ERROR_LOG} for research-ready questions.\n")
            else:
                chlog.write("- None recorded.\n")
    except Exception as e:
        append_error("P6:15-16 Finalization", e, f"write {CHANGELOG}")
        errors_blocking = True

    # Terminal summary
    print("=== Dependency Hardening Summary ===")
    for c in changes:
        print(c)
    if Path(ERROR_LOG).exists():
        print(f"\nErrors captured. See {ERROR_LOG}")
    print("\nPolicy: DO NOT ACTIVATE ANY GitHub Actions files.")
    sys.exit(1 if errors_blocking else 0)

if __name__ == "__main__":
    main()
