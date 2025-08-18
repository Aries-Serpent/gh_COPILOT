#!/usr/bin/env python3
"""
Guard 'pwsh --version' calls behind presence checks across shell/PowerShell scripts,
log changes, capture errors as ChatGPT-5 research questions, and finalize outputs.

Policy: DO NOT ACTIVATE ANY GitHub Actions files.
"""

import os
import re
import json
import shutil
from datetime import datetime
from pathlib import Path

# -------- Config --------
REPO_ROOT = Path(os.getcwd())
GLOBS = ["**/*.sh", "**/*.bash", "**/*.zsh", "**/*.ps1", "**/*.psm1"]
EXCLUDES = [".git", os.path.join(".github", "workflows")]  # DO NOT TOUCH ACTIONS
LOG_DIR = REPO_ROOT / "logs"
CHANGELOG = LOG_DIR / "pwsh_version_guard_changelog.md"
ERRORS = LOG_DIR / "error_register_chatgpt5.md"
RUNLOG = LOG_DIR / "pwsh_version_guard_run.log"
BACKUP_SUFFIX = ".bak"

# Patterns
PWSH_VERSION_REGEX = re.compile(r"(?<![A-Za-z0-9_])pwsh\s+--version(?![A-Za-z0-9_-])")

# Shell replacement blocks
SHELL_DIRECT_BLOCK = (
    "if command -v pwsh >/dev/null 2>&1; then\n"
    "  pwsh --version\n"
    "else\n"
    "  echo \"PowerShell not installed\"\n"
    "fi"
)

# PowerShell replacement blocks
POWERSHELL_DIRECT_BLOCK = (
    "$pwshPath = (Get-Command pwsh -ErrorAction SilentlyContinue)\n"
    "if ($pwshPath) {\n"
    "  pwsh --version\n"
    "} else {\n"
    "  Write-Output \"PowerShell not installed\"\n"
    "}"
)

# Interpolated patterns (shell-like)
SHELL_INTERP_PATTERNS = [
    (re.compile(r"\$\(\s*pwsh\s+--version\s*\)"), "$( _pwv )"),
    (re.compile(r"`pwsh\s+--version`"), "$(_pwv)"),
]

# -------- Utilities --------
def ensure_logs():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    if not CHANGELOG.exists():
        CHANGELOG.write_text("# pwsh Version Guard — Change Log\n\n| File | Lines Changed | Action | Notes |\n|---|---:|---|---|\n", encoding="utf-8")
    if not ERRORS.exists():
        ERRORS.write_text("# Error Register (ChatGPT-5 Research Questions)\n\n", encoding="utf-8")
    if not RUNLOG.exists():
        RUNLOG.write_text("", encoding="utf-8")

def log_run(msg: str):
    with RUNLOG.open("a", encoding="utf-8") as fh:
        fh.write(f"[{datetime.utcnow().isoformat()}Z] {msg}\n")

def append_changelog(file_path: Path, lines_changed: str, action: str, notes: str):
    with CHANGELOG.open("a", encoding="utf-8") as fh:
        fh.write(f"| {file_path} | {lines_changed} | {action} | {notes} |\n")

def append_error(step_number: str, step_desc: str, error_message: str, context: str):
    with ERRORS.open("a", encoding="utf-8") as fh:
        fh.write("**Question for ChatGPT-5:**\n")
        fh.write(f"While performing [{step_number}:{step_desc}], encountered the following error:\n")
        fh.write(f"`{error_message}`\n")
        fh.write(f"Context: {context}\n")
        fh.write("What are the possible causes, and how can this be resolved while preserving intended functionality?\n\n")

def is_excluded(path: Path) -> bool:
    parts = [p.lower() for p in path.parts]
    for ex in EXCLUDES:
        ex_parts = [p.lower() for p in Path(ex).parts]
        # exclude if 'ex' is a subsequence in parts
        for i in range(0, len(parts) - len(ex_parts) + 1):
            if parts[i:i+len(ex_parts)] == ex_parts:
                return True
    return False

def backup_once(file_path: Path):
    bak = file_path.with_suffix(file_path.suffix + BACKUP_SUFFIX)
    if not bak.exists():
        shutil.copy2(file_path, bak)

def detect_shell(file_path: Path) -> bool:
    return file_path.suffix in {".sh", ".bash", ".zsh"}

def detect_powershell(file_path: Path) -> bool:
    return file_path.suffix in {".ps1", ".psm1"}

def guard_shell_content(content: str) -> (str, int, str):
    """
    Replace direct 'pwsh --version' with guarded block.
    For interpolations, introduce _pwv variable and advise usage.
    Returns (new_content, replacements, note).
    """
    replacements = 0
    note_parts = []

    # Interpolation handling: precompute _pwv when interpolation exists
    had_interp = False
    new_content = content

    for pat, _ in SHELL_INTERP_PATTERNS:
        if pat.search(new_content):
            had_interp = True

    if had_interp:
        # Inject guard block that sets _pwv near the top (after shebang if present)
        preamble = (
            "if command -v pwsh >/dev/null 2>&1; then\n"
            "  _pwv=\"$(pwsh --version 2>/dev/null)\"\n"
            "else\n"
            "  _pwv=\"PowerShell not installed\"\n"
            "fi\n"
        )
        if new_content.startswith("#!"):
            # Insert after first line
            lines = new_content.splitlines()
            if len(lines) > 1:
                lines.insert(1, preamble)
                new_content = "\n".join(lines)
            else:
                new_content = new_content + "\n" + preamble
        else:
            new_content = preamble + new_content
        note_parts.append("Added `_pwv` preamble for interpolated usage")
        # Replace interpolations with $_pwv (already set)
        for pat, repl in SHELL_INTERP_PATTERNS:
            new_content, n = pat.subn("$_pwv", new_content)
            replacements += n

    # Direct replacements
    if PWSH_VERSION_REGEX.search(new_content):
        new_content, n = PWSH_VERSION_REGEX.subn(SHELL_DIRECT_BLOCK, new_content)
        replacements += n
        if n > 0:
            note_parts.append("Replaced direct calls with guarded block")

    return new_content, replacements, "; ".join(note_parts) if note_parts else "No change"

def guard_powershell_content(content: str) -> (str, int, str):
    replacements = 0
    new_content = content
    if PWSH_VERSION_REGEX.search(new_content):
        new_content, n = PWSH_VERSION_REGEX.subn(POWERSHELL_DIRECT_BLOCK, new_content)
        replacements += n
        note = "Replaced direct calls with presence guard via Get-Command"
    else:
        note = "No change"
    return new_content, replacements, note

def process_file(f: Path, counters: dict):
    try:
        text = f.read_text(encoding="utf-8")
    except Exception as e:
        counters["errors"] += 1
        append_error(
            "2", "Search & Mapping: open file",
            str(e), f"File={f}"
        )
        return

    if detect_shell(f):
        new_text, n, note = guard_shell_content(text)
    elif detect_powershell(f):
        new_text, n, note = guard_powershell_content(text)
    else:
        return  # not a target file type

    if n > 0:
        try:
            backup_once(f)
            f.write_text(new_text, encoding="utf-8")
            counters["modified"] += 1
            append_changelog(f, "auto", "guarded", note)
            log_run(f"Modified {f} ({n} replacement(s)): {note}")
        except Exception as e:
            counters["errors"] += 1
            append_error(
                "3", "Best-Effort Construction: write file",
                str(e), f"File={f}"
            )
    else:
        counters["scanned_no_change"] += 1

def linux_probe():
    # Dry-run presence probe
    present = shutil.which("pwsh") is not None
    msg = "pwsh present on PATH" if present else "pwsh NOT present on PATH (Linux probe)"
    log_run(f"Linux probe: {msg}")
    return present

def parse_readme():
    # Minimal README parsing: strip or rewrite stale references to unguarded 'pwsh --version'
    rd = REPO_ROOT / "README.md"
    if not rd.exists():
        return False, "README.md not found"
    try:
        txt = rd.read_text(encoding="utf-8")
        # Note: non-destructive; add a guidance section if missing.
        if "pwsh --version" in txt and "command -v pwsh" not in txt:
            guidance = (
                "\n\n### Environment Logging — PowerShell Version Guard\n"
                "Use a presence check before invoking `pwsh --version`:\n\n"
                "```bash\n"
                "if command -v pwsh >/dev/null 2>&1; then\n"
                "  pwsh --version\n"
                "else\n"
                "  echo \"PowerShell not installed\"\n"
                "fi\n"
                "```\n"
            )
            txt = txt + guidance
            rd.write_text(txt, encoding="utf-8")
            append_changelog(rd, "append", "README updated", "Added guard guidance section")
            log_run("README updated with guard guidance")
            return True, "README updated"
        else:
            log_run("README already aligned or no reference found")
            return False, "No README update needed"
    except Exception as e:
        append_error("1", "Preparation: parse README", str(e), "README.md")
        return False, f"README parse error: {e}"

def main():
    ensure_logs()
    log_run("START pwsh version guard run")

    readme_changed, readme_note = parse_readme()

    counters = {
        "scanned": 0,
        "modified": 0,
        "errors": 0,
        "scanned_no_change": 0,
        "pruned": 0,  # We avoid pruning unless clearly dead; not auto-pruned here
    }

    # Scan files
    for pat in GLOBS:
        for f in REPO_ROOT.glob(pat):
            if f.is_dir():
                continue
            if is_excluded(f):
                continue
            counters["scanned"] += 1
            process_file(f, counters)

    # Linux probe
    present = linux_probe()

    # Finalization summary
    summary = {
        "scanned": counters["scanned"],
        "modified": counters["modified"],
        "no_change": counters["scanned_no_change"],
        "errors": counters["errors"],
        "pruned": counters["pruned"],
        "pwsh_present_probe": present,
        "readme_changed": readme_changed,
        "readme_note": readme_note,
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
    }
    log_run("SUMMARY: " + json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))

    log_run("END pwsh version guard run")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        ensure_logs()
        append_error(
            "6", "Finalization",
            str(e),
            "Unhandled exception at top-level"
        )
        raise

