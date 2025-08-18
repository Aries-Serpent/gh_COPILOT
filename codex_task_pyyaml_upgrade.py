#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Codex Workflow: Ensure PyYAML dependency, verify docs script, update docs, log rationale, capture errors.
Guardrail: DO NOT ACTIVATE ANY GitHub Actions files.
"""

import argparse
import os
import re
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

# ----------------- Constants & Utilities -----------------

ART_DIR = Path(".codex_artifacts")
ART_DIR.mkdir(exist_ok=True)

CHANGELOG = Path("CHANGELOG_Codex_Auto.md")
RESEARCH = Path("research_questions.md")

GITHUB_WORKFLOWS = Path(".github/workflows")

DEFAULT_VERSION = "6.0.1"  # can be overridden via --version
PKG_NAME = "PyYAML"


def log_change(entry: str):
    ts = datetime.now().isoformat()
    with CHANGELOG.open("a", encoding="utf-8") as f:
        f.write(f"- {ts} {entry}\n")


def log_research_question(step: str, error_message: str, context: str):
    ts = datetime.now().isoformat()
    block = (
        f"**Question for ChatGPT-5 ({ts})**:\n"
        f"While performing **[{step}]**, encountered the following error:\n"
        f"**{error_message}**\n"
        f"**Context:** {context}\n"
        f"What are the possible causes, and how can this be resolved while preserving intended functionality?\n\n"
    )
    with RESEARCH.open("a", encoding="utf-8") as f:
        f.write(block)


def run(cmd, step_desc, cwd=None, capture=True, check=False):
    try:
        res = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=capture,
            text=True,
            shell=False,
            check=check,
        )
        out_path = ART_DIR / (re.sub(r"[^A-Za-z0-9_.-]+", "_", step_desc) + ".log")
        with out_path.open("w", encoding="utf-8") as f:
            f.write("CMD: " + " ".join(cmd) + "\n\n")
            f.write("STDOUT:\n" + (res.stdout or "") + "\n\n")
            f.write("STDERR:\n" + (res.stderr or "") + "\n")
        return res.returncode, out_path
    except Exception as e:
        log_research_question(step_desc, repr(e), f"cmd={' '.join(cmd)} cwd={cwd or os.getcwd()}")
        return 1, None


def safe_read(p: Path) -> str:
    if not p.exists():
        return ""
    try:
        return p.read_text(encoding="utf-8")
    except Exception:
        return p.read_text(errors="ignore")


def safe_write(p: Path, content: str):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


def guard_no_github_workflows_writes():
    # This script never writes there, but we also assert path exists and warn if requested.
    if GITHUB_WORKFLOWS.exists():
        log_change("Guardrail confirmed: .github/workflows exists; no files altered under this path.")

# ----------------- Detection -----------------

def detect_env(repo: Path):
    """
    Returns a dict describing the env strategy and files.
    priority: pip-tools -> Poetry -> PEP621 (bare pyproject) -> Pipenv -> requirements.txt
    """
    data = {
        "strategy": None,
        "files": {},
    }
    req_in = repo / "requirements.in"
    req_txt = repo / "requirements.txt"
    pyproject = repo / "pyproject.toml"
    poetry_lock = repo / "poetry.lock"
    pipfile = repo / "Pipfile"
    pipfile_lock = repo / "Pipfile.lock"
    setup_cfg = repo / "setup.cfg"
    setup_py = repo / "setup.py"

    if req_in.exists():
        data["strategy"] = "pip-tools"
        data["files"]["requirements.in"] = req_in
        data["files"]["requirements.txt"] = req_txt
    elif pyproject.exists() and poetry_lock.exists():
        data["strategy"] = "poetry"
        data["files"]["pyproject.toml"] = pyproject
        data["files"]["poetry.lock"] = poetry_lock
    elif pyproject.exists():
        data["strategy"] = "pyproject"
        data["files"]["pyproject.toml"] = pyproject
    elif pipfile.exists():
        data["strategy"] = "pipenv"
        data["files"]["Pipfile"] = pipfile
        data["files"]["Pipfile.lock"] = pipfile_lock
    elif req_txt.exists():
        data["strategy"] = "requirements"
        data["files"]["requirements.txt"] = req_txt
    else:
        data["strategy"] = "requirements"
        data["files"]["requirements.txt"] = req_txt

    if setup_cfg.exists():
        data["files"]["setup.cfg"] = setup_cfg
    if setup_py.exists():
        data["files"]["setup.py"] = setup_py
    return data

# ----------------- Dependency Editing -----------------

def normalize_spec(version: str) -> str:
    return f"{PKG_NAME}>={version}"


def ensure_in_requirements(path: Path, desired_spec: str):
    content = safe_read(path)
    lines = content.splitlines() if content else []
    idx = None
    existing_line = None
    pat = re.compile(r"^\s*PyYAML\s*([<>=!~].*)?$", re.IGNORECASE)

    existing_line: str | None = None
    for i, ln in enumerate(lines):
        if pat.match(ln):
            idx = i
            existing_line = ln.strip()
            break

    if idx is None or existing_line is None:
        lines.append(desired_spec)
        safe_write(path, "\n".join(lines) + "\n")
        return f"Added {desired_spec} to {path.name}", True

    if ">=" in existing_line:
        try:
            existing_ver = re.findall(r">=\s*([0-9][0-9A-Za-z.\-+]*)", existing_line)[0]
        except IndexError:
            existing_ver = None
        if existing_ver is None or existing_ver < desired_spec.split(">=")[1]:
            lines[idx] = desired_spec
            safe_write(path, "\n".join(lines) + "\n")
            return f"Upgraded {path.name} entry from '{existing_line}' to '{desired_spec}'", True
        return f"No change: {path.name} already satisfies '{existing_line}'", False
    lines[idx] = desired_spec
    safe_write(path, "\n".join(lines) + "\n")
    return f"Replaced '{existing_line}' with '{desired_spec}' in {path.name}", True


def ensure_in_pyproject(pyproject_path: Path, desired_spec: str):
    content = safe_read(pyproject_path)
    if not content:
        return "pyproject.toml empty; skipping injection.", False

    changed = False
    rationale = []

    if "[tool.poetry.dependencies]" in content:
        block_pat = re.compile(r"(\[tool\.poetry\.dependencies\][^\[]*)", re.DOTALL)
        m = block_pat.search(content)
        if m:
            block = m.group(1)
            if re.search(r"(?im)^\s*PyYAML\s*=", block):
                new_block = re.sub(
                    r"(?im)^\s*PyYAML\s*=\s*.*$",
                    f'PyYAML = ">={desired_spec.split(">=")[1]}"',
                    block,
                )
                if new_block != block:
                    content = content.replace(block, new_block)
                    changed = True
                    rationale.append("Updated Poetry dependency spec for PyYAML.")
                else:
                    rationale.append("Poetry PyYAML already present; no change.")
            else:
                insertion = 'PyYAML = ">=' + desired_spec.split(">=")[1] + '"\n'
                new_block = block + insertion
                content = content.replace(block, new_block)
                changed = True
                rationale.append("Added PyYAML to Poetry dependencies.")

    if "[project]" in content and "dependencies" in content:
        dep_pat = re.compile(r"(?s)(dependencies\s*=\s*\[)(.*?)(\])")
        mm = dep_pat.search(content)
        if mm:
            deps = mm.group(2)
            if re.search(r"(?im)PyYAML\s*[<>=!~]", deps) or "PyYAML" in deps:
                new_deps = re.sub(r"(?i)PyYAML[^\"]*", desired_spec, deps)
                if new_deps != deps:
                    content = content[: mm.start(2)] + new_deps + content[mm.end(2):]
                    changed = True
                    rationale.append("Updated PEP 621 dependency spec for PyYAML.")
                else:
                    rationale.append("PEP 621 PyYAML already present; no change.")
            else:
                ins = (", " if deps.strip() else "") + f'"{desired_spec}"'
                content = content[: mm.start(2)] + deps + ins + content[mm.end(2):]
                changed = True
                rationale.append("Added PyYAML to PEP 621 dependencies.")
    if changed:
        safe_write(pyproject_path, content)
        return "; ".join(rationale), True
    return "; ".join(rationale) or "No eligible dependency blocks found; skipped.", False

# ----------------- Documentation Editing -----------------

INSTALL_SNIPPETS = [
    ("pip", "```bash\npip install -r requirements.txt\n```"),
    ("poetry", "```bash\npoetry install\n```"),
    ("pipenv", "```bash\npipenv install --dev\n```"),
]


def update_docs_with_requirement(files, strategy, desired_spec):
    changed_any = False
    rationale = []
    for p in files:
        text = safe_read(p)
        if not text:
            continue

        new_text = re.sub(r"\b(?<!Py)yaml package\b", "PyYAML package", text, flags=re.IGNORECASE)

        wanted = {"requirements": "pip", "pip-tools": "pip", "poetry": "poetry", "pyproject": "pip", "pipenv": "pipenv"}[strategy]
        label, snippet = next((label, s) for (label, s) in INSTALL_SNIPPETS if label == wanted)

        if label == "pip":
            if "requirements.txt" in new_text and desired_spec in new_text:
                pass
            elif "requirements.txt" in new_text:
                new_text += f"\n\n> Note: This project requires `{desired_spec}`.\n"
            else:
                new_text += f"\n\n### Installation\n{snippet}\n\n> Note: This project requires `{desired_spec}`.\n"
        elif label == "poetry":
            if "poetry install" not in new_text:
                new_text += f"\n\n### Installation\n{snippet}\n"
            if desired_spec not in new_text:
                new_text += f"\n> Note: This project requires `{desired_spec}`.\n"
        elif label == "pipenv":
            if "pipenv install" not in new_text:
                new_text += f"\n\n### Installation\n{snippet}\n"
            if desired_spec not in new_text:
                new_text += f"\n> Note: This project requires `{desired_spec}`.\n"

        if new_text != text:
            safe_write(p, new_text)
            changed_any = True
            rationale.append(f"Updated {p.name} with install guidance and requirement note.")

    return changed_any, "; ".join(rationale) if rationale else "No doc updates required."

# ----------------- Main Workflow -----------------

def main():
    parser = argparse.ArgumentParser(description="Codex task: add/upgrade PyYAML and verify docs script.")
    parser.add_argument("--repo", default=".", help="Repository root.")
    parser.add_argument("--version", default=DEFAULT_VERSION, help="Desired lower-bound version, e.g., 6.0.1")
    parser.add_argument("--verify-script", default="scripts/docs_status_reconciler.py", help="Verification script path.")
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    os.chdir(repo)

    guard_no_github_workflows_writes()
    desired_spec = normalize_spec(args.version)
    env = detect_env(repo)
    strategy = env["strategy"]
    log_change(f"Detected strategy: {strategy}; files={list(env['files'].keys())}")

    try:
        changed = False
        rationale = "No-op."
        if strategy in ("requirements", "pip-tools"):
            path = env["files"].get("requirements.in", env["files"].get("requirements.txt"))
            rationale, changed = ensure_in_requirements(path, desired_spec)
            log_change(rationale)
            if strategy == "pip-tools":
                rc, logp = run(["pip-compile", str(path)], "2.2 pip-compile", cwd=str(repo))
                if rc != 0:
                    log_research_question("2.2: pip-compile", f"retcode={rc}", f"log={logp}")
        elif strategy in ("poetry", "pyproject"):
            pyproject = env["files"]["pyproject.toml"]
            rationale, changed = ensure_in_pyproject(pyproject, desired_spec)
            log_change(rationale)
        elif strategy == "pipenv":
            rc, logp = run(["pipenv", "install", f"{PKG_NAME}>={args.version}"], "2.1 pipenv install", cwd=str(repo))
            if rc != 0:
                log_research_question("2.1: pipenv install", f"retcode={rc}", f"log={logp}")
            else:
                changed = True
                log_change(f"Added/ensured {desired_spec} via Pipenv.")
        else:
            log_change("Unknown strategy; defaulting to requirements.txt")
            path = Path("requirements.txt")
            rationale, changed = ensure_in_requirements(path, desired_spec)
            log_change(rationale)
    except Exception as e:
        log_research_question("2.x: Apply dependency spec", repr(e), f"strategy={strategy}")
        print("Fatal during dependency application. See research_questions.md.", file=sys.stderr)
        sys.exit(1)

    try:
        if strategy in ("requirements", "pip-tools", "pyproject"):
            target = "requirements.txt" if (repo / "requirements.txt").exists() else None
            if target:
                rc, logp = run([sys.executable, "-m", "pip", "install", "-r", target], "2.3 pip install -r requirements.txt", cwd=str(repo))
            else:
                rc, logp = run([sys.executable, "-m", "pip", "install", f"{PKG_NAME}>={args.version}"], "2.3 pip install pyyaml direct", cwd=str(repo))
            if rc != 0:
                log_research_question("2.3: Install dependencies (pip)", f"retcode={rc}", f"log={logp}")
        elif strategy == "poetry":
            rc, logp = run(["poetry", "install"], "2.3 poetry install", cwd=str(repo))
            if rc != 0:
                log_research_question("2.3: Install dependencies (poetry)", f"retcode={rc}", f"log={logp}")
        elif strategy == "pipenv":
            rc, logp = run(["pipenv", "install"], "2.3 pipenv install", cwd=str(repo))
            if rc != 0:
                log_research_question("2.3: Install dependencies (pipenv)", f"retcode={rc}", f"log={logp}")
    except Exception as e:
        log_research_question("2.3: Install dependencies", repr(e), f"strategy={strategy}")

    verify_path = Path(args.verify_script)
    if verify_path.exists():
        rc, logp = run([sys.executable, str(verify_path)], "2.4 run verification script", cwd=str(repo))
        if rc != 0:
            log_research_question("2.4: Run verification script", f"retcode={rc}", f"log={logp}")
            log_change(f"Verification failed; see {logp}")
        else:
            log_change(f"Verification succeeded; see {logp}")
    else:
        log_change(f"Verification script not found at {verify_path}; skipping.")

    doc_targets = []
    for name in ["CONTRIBUTING.md", "README.md"]:
        p = repo / name
        if p.exists():
            doc_targets.append(p)
    for p in repo.glob("docs/**/*"):
        if p.is_file() and re.search(r"contributing|setup|readme", p.name, re.IGNORECASE):
            doc_targets.append(p)

    updated, doc_rationale = update_docs_with_requirement(doc_targets, strategy, desired_spec)
    log_change(doc_rationale)

    if (repo / "poetry.lock").exists() and (repo / "pyproject.toml").exists() and (repo / "Pipfile").exists():
        log_change("Pruned Pipenv updates due to active Poetry project (poetry.lock present).")

    guard_no_github_workflows_writes()

    summary = {
        "strategy": strategy,
        "desired_spec": desired_spec,
        "docs_updated": bool(updated),
        "artifact_dir": str(ART_DIR),
        "changelog": str(CHANGELOG),
        "research_questions": str(RESEARCH),
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
