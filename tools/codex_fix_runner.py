#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
codex_fix_runner.py
End-to-end maintenance helper for:
  1) pytest.importorskip("yaml") with reason in policy_tests/conftest.py
  2) Replace datetime.utcnow() -> datetime.now(timezone.utc) in tests/*compliance*
  3) Update packaging config (pyproject.toml/setup.cfg) if a new script/module is intended
  4) Optional: README link stripping (turn [text](url) => text) to avoid dead refs
  5) Emit CHANGELOG_Codex.md, chatgpt5_questions.md, codex_run_report.json
  6) Compute Coverage score

Run:
  python tools/codex_fix_runner.py --install --strip-readme-links
"""
import os, re, json, sys, subprocess, shutil
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUTDIR = REPO / ".codex"
OUTDIR.mkdir(exist_ok=True)

CHANGELOG = REPO / "CHANGELOG_Codex.md"
QFILE = REPO / "chatgpt5_questions.md"
RUNREPORT = REPO / "codex_run_report.json"

RESULTS = {
    "steps": [],
    "coverage_items": {
        "yaml_importorskip": False,
        "packaging_configured": False,
        "datetime_utcnow_fixed": False,
    },
    "errors": [],
    "gaps": [],
    "notes": [],
}


def log_step(name, ok=True, detail=""):
    RESULTS["steps"].append({"name": name, "ok": ok, "detail": detail})


def research_prompt(step_number_desc, error_message, context):
    block = (
        "**Question for ChatGPT-5:**\n"
        "````\n"
        f"While performing {step_number_desc}, encountered the following error:\n"
        f"{error_message}\n"
        f"Context: {context}\n"
        "What are the possible causes, and how can this be resolved while preserving intended functionality?\n"
        "````\n"
    )
    with QFILE.open("a", encoding="utf-8") as f:
        f.write(block + "\n\n")
    RESULTS["errors"].append({
        "step": step_number_desc,
        "error": error_message,
        "context": context,
    })


def append_changelog(entry: str):
    with CHANGELOG.open("a", encoding="utf-8") as f:
        f.write(entry.rstrip() + "\n\n")


def safe_read_text(p: Path):
    try:
        return p.read_text(encoding="utf-8")
    except Exception as e:
        research_prompt("READ_FILE", str(e), f"path={p}")
        return None


def safe_write_text(p: Path, data: str):
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(data, encoding="utf-8")
        return True
    except Exception as e:
        research_prompt("WRITE_FILE", str(e), f"path={p}")
        return False


def find_conftest():
    target = REPO / "policy_tests" / "conftest.py"
    if target.exists():
        return target
    candidates = list(REPO.glob("**/conftest.py"))
    candidates = [c for c in candidates if "policy" in "/".join(c.parts)]
    if candidates:
        return candidates[0]
    return None


def ensure_importorskip(conftest_path: Path):
    src = safe_read_text(conftest_path)
    if src is None:
        return False, "Cannot read conftest"

    changed = False
    if "import pytest" not in src:
        src = "import pytest\n" + src
        changed = True

    if re.search(r"pytest\.importorskip\(\s*['\"]yaml['\"]\s*,\s*reason=", src):
        pass
    elif "pytest.importorskip(" in src:
        src = re.sub(
            r"pytest\.importorskip\(\s*(['\"])yaml\1\s*\)",
            "pytest.importorskip('yaml', reason='Requires PyYAML; install with `pip install pyyaml`.')",
            src,
        )
        changed = True
    else:
        insertion = (
            "yaml = pytest.importorskip('yaml', reason='Requires PyYAML; install with `pip install pyyaml`.')\n"
        )
        lines = src.splitlines(True)
        idx = 0
        while idx < len(lines) and (lines[idx].startswith("import ") or lines[idx].startswith("from ")):
            idx += 1
        lines.insert(idx, insertion)
        src = "".join(lines)
        changed = True

    if changed:
        ok = safe_write_text(conftest_path, src)
        if ok:
            append_changelog(
                f"- Added/normalized `pytest.importorskip('yaml', reason=...)` in `{conftest_path}`."
            )
        return ok, "updated"
    else:
        return True, "no-change"


def replace_utcnow():
    paths = []
    for p in REPO.glob("tests/**/*"):
        if "compliance" in "/".join(p.parts) and p.suffix == ".py":
            paths.append(p)
    if not paths:
        RESULTS["gaps"].append(
            "No tests/*compliance* python files found for utcnow replacement."
        )
        append_changelog(
            "- GAP: No `tests/*compliance*` files found. Skipped datetime fixes."
        )
        return False, 0

    replacements = 0
    for p in paths:
        s = safe_read_text(p)
        if s is None:
            continue

        orig = s
        needs_timezone_import = False
        if "datetime.utcnow(" in s:
            s = s.replace("datetime.utcnow(", "datetime.now(timezone.utc)(")
            needs_timezone_import = True

        s = re.sub(
            r"(\b[\w_]+)\.datetime\.utcnow\(",
            r"\1.datetime.now(\1.timezone.utc)(",
            s,
        )

        if s != orig:
            if needs_timezone_import and "timezone" not in s:
                if re.search(
                    r"from datetime import datetime(\s*,\s*timezone)?", s
                ):
                    s = re.sub(
                        r"from datetime import datetime(\s*,\s*timezone)?",
                        "from datetime import datetime, timezone",
                        s,
                        count=1,
                    )
                elif "from datetime import datetime" in s:
                    s = s.replace(
                        "from datetime import datetime",
                        "from datetime import datetime, timezone",
                        1,
                    )
                elif "import datetime as dt" in s:
                    pass
                elif "import datetime" in s:
                    pass
                else:
                    s = "from datetime import timezone\n" + s

            if safe_write_text(p, s):
                replacements += 1
                append_changelog(
                    f"- Replaced `utcnow()` → `now(timezone.utc)` in `{p}`."
                )

    return (replacements > 0), replacements


def update_packaging_config():
    pyproject = REPO / "pyproject.toml"
    setupcfg = REPO / "setup.cfg"
    updated = False

    intended_script_name = os.environ.get("CODEX_SCRIPT_NAME", "").strip()
    intended_entry = os.environ.get("CODEX_SCRIPT_ENTRY", "").strip()

    if not pyproject.exists() and not setupcfg.exists():
        RESULTS["gaps"].append(
            "No pyproject.toml or setup.cfg found; cannot register scripts."
        )
        append_changelog(
            "- GAP: No packaging config found; skipped script registration."
        )
        return False, "no-config"

    if intended_script_name and intended_entry:
        if pyproject.exists():
            content = safe_read_text(pyproject)
            if content is None:
                return False, "pyproject-unreadable"
            if "[project.scripts]" not in content:
                content += "\n[project.scripts]\n"
            if not re.search(
                rf"^\s*{re.escape(intended_script_name)}\s*=", content, re.M
            ):
                content += f'{intended_script_name} = "{intended_entry}"\n'
                updated = True
            if updated and not safe_write_text(pyproject, content):
                return False, "pyproject-write-failed"
        elif setupcfg.exists():
            content = safe_read_text(setupcfg)
            if content is None:
                return False, "setupcfg-unreadable"
            if "[options.entry_points]" not in content:
                content += "\n[options.entry_points]\nconsole_scripts =\n"
            if "console_scripts" not in content:
                content += "\nconsole_scripts =\n"
            if not re.search(
                rf"^\s*{re.escape(intended_script_name)}\s*=", content, re.M
            ):
                content = re.sub(
                    r"(console_scripts\s*=\s*\n?)",
                    rf"\1    {intended_script_name} = {intended_entry}\n",
                    content,
                    count=1,
                )
                updated = True
            if updated and not safe_write_text(setupcfg, content):
                return False, "setupcfg-write-failed"

    if updated:
        append_changelog(
            f"- Updated packaging entries for script `{intended_script_name}` → `{intended_entry}`."
        )
        return True, "updated"
    else:
        append_changelog(
            "- No script registration requested; validated packaging files exist."
        )
        return True, "validated"


def pip_install_editable(run_install: bool):
    if not run_install:
        return True, "skipped"
    try:
        cmd = [sys.executable, "-m", "pip", "install", "-e", "."]
        subprocess.run(cmd, cwd=str(REPO), check=True, capture_output=True)
        return True, "installed"
    except subprocess.CalledProcessError as e:
        research_prompt(
            "10:Editable install verification",
            e.stderr.decode("utf-8", errors="ignore"),
            "pip install -e . failed",
        )
        return False, "install-failed"


def readme_parse(strip_links: bool):
    readme = None
    for name in ("README.md", "readme.md", "ReadMe.md"):
        p = REPO / name
        if p.exists():
            readme = p
            break
    if not readme:
        RESULTS["notes"].append("README not found; skipping parsing.")
        return

    content = safe_read_text(readme)
    if content is None:
        return

    if strip_links:
        new_content = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", content)
        if new_content != content and safe_write_text(readme, new_content):
            append_changelog(
                f"- Stripped markdown links in `{readme.name}` to avoid dead refs."
            )
    else:
        RESULTS["notes"].append("README link stripping disabled.")


def run_pytest_quiet():
    try:
        out = subprocess.run([
            "pytest",
            "-q",
        ], cwd=str(REPO), capture_output=True, text=True)
        (OUTDIR / "pytest_after.txt").write_text(
            out.stdout + "\n" + out.stderr, encoding="utf-8"
        )
        ok = out.returncode == 0
        if not ok:
            research_prompt(
                "11:Unit test validation",
                f"pytest exit {out.returncode}",
                "see .codex/pytest_after.txt",
            )
        return ok, out.returncode
    except FileNotFoundError:
        RESULTS["gaps"].append("pytest not found in environment.")
        research_prompt(
            "11:Unit test validation",
            "FileNotFoundError: pytest",
            "Install dev deps or run inside the project venv.",
        )
        return False, 127


def compute_coverage():
    total = len(RESULTS["coverage_items"])
    done = sum(1 for v in RESULTS["coverage_items"].values() if v)
    score = done / total if total else 0.0
    RESULTS["coverage"] = {
        "completed": done,
        "total": total,
        "score": round(score, 3),
    }
    return score


def main():
    conftest = find_conftest()
    if conftest is None:
        RESULTS["gaps"].append(
            "policy_tests/conftest.py not found; attempted to locate alternatives but none matched."
        )
        append_changelog(
            "- GAP: `policy_tests/conftest.py` not found; skipping YAML importorskip injection."
        )
        log_step("7:yaml_importorskip", ok=False, detail="conftest missing")
    else:
        ok, detail = ensure_importorskip(conftest)
        log_step("7:yaml_importorskip", ok=ok, detail=detail)
        RESULTS["coverage_items"]["yaml_importorskip"] = ok

    ok, count = replace_utcnow()
    log_step("8:datetime_utcnow_replacements", ok=ok, detail=f"files_updated={count}")
    RESULTS["coverage_items"]["datetime_utcnow_fixed"] = ok

    ok, detail = update_packaging_config()
    log_step("9:packaging_config", ok=ok, detail=detail)
    RESULTS["coverage_items"]["packaging_configured"] = ok

    run_install = "--install" in sys.argv
    ok, detail = pip_install_editable(run_install)
    log_step("10:pip_editable_install", ok=ok, detail=detail)

    readme_parse(strip_links="--strip-readme-links" in sys.argv)

    ok, code = run_pytest_quiet()
    log_step("11:pytest_validation", ok=ok, detail=f"exit={code}")

    score = compute_coverage()

    with RUNREPORT.open("w", encoding="utf-8") as f:
        json.dump(RESULTS, f, indent=2, ensure_ascii=False)

    if not CHANGELOG.exists() or CHANGELOG.stat().st_size == 0:
        append_changelog("# CHANGELOG_Codex")
    append_changelog(
        f"**Coverage Performance:** {RESULTS['coverage']['completed']}/{RESULTS['coverage']['total']} = {RESULTS['coverage']['score']:.3f}"
    )

    print(f"[codex_fix_runner] Completed. Coverage score={score:.3f}")
    print(f"- Changelog: {CHANGELOG}")
    print(f"- Research Qs: {QFILE} (if any)")
    print(f"- Report: {RUNREPORT}")


if __name__ == "__main__":
    main()

