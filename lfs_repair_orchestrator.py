#!/usr/bin/env python3
# lfs_repair_orchestrator.py
# Purpose: Best-effort recovery of missing Git LFS objects with auditable logs/artifacts.
# Constraint: DO NOT ACTIVATE ANY GitHub Actions files (no writes under .github/workflows/).

import argparse
import hashlib
import json
import logging
import re
import shlex
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ---------- Utilities ----------

def run(cmd: List[str], cwd: Optional[Path] = None, env: Optional[Dict[str, str]] = None,
        log_path: Optional[Path] = None, allow_fail: bool = False) -> Tuple[int, str, str]:
    """Run a command, capture stdout/stderr, optionally append to a log file."""
    proc = subprocess.Popen(cmd, cwd=str(cwd) if cwd else None,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
    out, err = proc.communicate()
    if log_path:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as f:
            f.write(f"$ {' '.join(shlex.quote(c) for c in cmd)}\n{out}\n{err}\n")
    if proc.returncode != 0 and not allow_fail:
        raise RuntimeError(f"Command failed ({proc.returncode}): {' '.join(cmd)}\n{err.strip()}")
    return proc.returncode, out, err

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")

def safe_relpath(p: Path, root: Path) -> str:
    return str(p.resolve().relative_to(root.resolve()))

def write_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def append_text(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(text.rstrip() + "\n")

def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""

def write_text(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

# ---------- Parsing missing objects ----------

MISS_PATTERNS = [
    re.compile(r"missing object:?\s*([0-9a-f]{64})\s*(?:\((.*?)\))?", re.I),
    re.compile(r"missing:\s*(.+)$", re.I),
    re.compile(r"Object\s+([0-9a-f]{64})\s+not\s+found", re.I),
]

def parse_missing(log_text: str) -> List[Tuple[Optional[str], Optional[str]]]:
    """
    Returns list of (path, oid?) tuples.
    We try to glean either a path or an OID, sometimes both.
    """
    results = []
    for line in log_text.splitlines():
        line = line.strip()
        for pat in MISS_PATTERNS:
            m = pat.search(line)
            if m:
                if pat.pattern.startswith('missing object'):
                    oid = m.group(1)
                    path = m.group(2) if len(m.groups()) > 1 else None
                elif pat.pattern.startswith('missing:'):
                    path = m.group(1).strip()
                    oid = None
                else:
                    oid = m.group(1)
                    path = None
                results.append((path, oid))
                break
    return results

# ---------- README update ----------

def update_readme(readme_path: Path, summary: dict):
    stamp = now_iso()
    block = [
        "\n---",
        "## LFS Health & Recovery Status",
        f"_Last updated: {stamp}_",
        "",
        "- **Missing (initial):** {}".format(summary.get("missing_initial", 0)),
        "- **Recovered:** {}".format(summary.get("recovered", 0)),
        "- **Unrecovered:** {}".format(summary.get("unrecovered", 0)),
        "- **Integrity Check:** {}".format(summary.get("integrity_status", "unknown")),
        "",
        "Commands executed (high-level):",
        "```bash",
        "git lfs fsck",
        "git lfs track <path>",
        "git add <path>",
        "git commit -m \"Restore LFS object: <path> (oid:<oid>)\"",
        "git lfs push --all origin",
        "git lfs fetch --all && git lfs fsck",
        "```",
        "---",
        ""
    ]
    current = read_text(readme_path)
    new = re.sub(r"\n---\n## LFS Health & Recovery Status.*?---\n", "\n", current, flags=re.S)
    write_text(readme_path, new + "\n".join(block))

# ---------- Core workflow ----------

def main():
    ap = argparse.ArgumentParser(description="Best-effort Git LFS object repair (safe by default).")
    ap.add_argument("--repo", default=".", help="Path to repository root.")
    ap.add_argument("--backups", nargs="*", default=[], help="One or more backup directories to search.")
    ap.add_argument("--other-clone", default=None, help="Optional path to another clone to source files from.")
    ap.add_argument("--apply", action="store_true", help="Actually commit and push changes.")
    ap.add_argument("--skip-repair-sh", action="store_true", help="Skip running tools/lfs_repair.sh.")
    ap.add_argument("--verbose", action="store_true", help="Enable verbose logging.")
    args = ap.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format="%(levelname)s: %(message)s")

    repo = Path(args.repo).resolve()
    logs_dir = repo / "logs"
    artifacts_dir = repo / "artifacts"
    logs_dir.mkdir(parents=True, exist_ok=True)
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    context = {
        "timestamp": now_iso(),
        "repo": str(repo),
        "apply": args.apply,
        "backups": [str(Path(p).resolve()) for p in args.backups],
        "other_clone": str(Path(args.other_clone).resolve()) if args.other_clone else None,
    }

    # Phase 1: Preparation
    try:
        _, gitver, _ = run(["git", "--version"], cwd=repo, log_path=logs_dir / "sys.log")
        _, lfsver, _ = run(["git", "lfs", "version"], cwd=repo, log_path=logs_dir / "sys.log")
        context["git_version"] = gitver.strip()
        context["git_lfs_version"] = lfsver.strip()
    except Exception as e:
        append_text(logs_dir / "research_questions.md", f"""Question for ChatGPT-5:
While performing [1.1: Verify prerequisites], encountered the following error:
{str(e)}
Context: Ensuring git and git-lfs are installed and accessible in PATH.
What are the possible causes, and how can this be resolved while preserving intended functionality?
""")
        raise

    workflows_dir = repo / ".github" / "workflows"
    if workflows_dir.exists():
        logging.info("Guardrail active: .github/workflows exists; script will not write to it.")

    lfs_repair_log = logs_dir / "lfs_repair.log"
    if not args.skip_repair_sh and (repo / "tools" / "lfs_repair.sh").exists():
        try:
            run(["bash", "tools/lfs_repair.sh"], cwd=repo, log_path=lfs_repair_log, allow_fail=True)
        except Exception as e:
            append_text(logs_dir / "research_questions.md", f"""Question for ChatGPT-5:
While performing [2.1: Run tools/lfs_repair.sh], encountered the following error:
{str(e)}
Context: Attempting to execute the repo-provided helper to list/repair LFS issues.
What are the possible causes, and how can this be resolved while preserving intended functionality?
""")
    else:
        append_text(lfs_repair_log, "tools/lfs_repair.sh not present or skipped.\n")

    rc, fsck_out, fsck_err = run(["git", "lfs", "fsck"], cwd=repo, log_path=logs_dir / "lfs_fsck.log", allow_fail=True)
    missing = parse_missing(read_text(lfs_repair_log) + "\n" + fsck_out + "\n" + fsck_err)

    rc, lsfiles_out, _ = run(["git", "lfs", "ls-files", "--all"], cwd=repo, log_path=logs_dir / "lfs_lsfiles.log", allow_fail=True)
    path_to_oid = {}
    for line in lsfiles_out.splitlines():
        m = re.match(r"([0-9a-f]{64})\s+\*\s+(.*)", line.strip())
        if m:
            path_to_oid[m.group(2)] = m.group(1)

    miss_items: List[Tuple[Optional[str], Optional[str]]] = []
    seen: set = set()
    for p, o in missing:
        p = p.strip() if p else None
        o = o.lower() if o else (path_to_oid.get(p) if p in path_to_oid else None)
        key = (p or f"oid:{o}", o or f"path:{p}")
        if key not in seen:
            miss_items.append((p, o))
            seen.add(key)

    initial_missing_count = len(miss_items)
    logging.info("Detected %d missing LFS artifacts.", initial_missing_count)

    recovered = []
    unrecovered = []
    search_roots = [Path(p) for p in args.backups]
    if args.other_clone:
        search_roots.append(Path(args.other_clone))

    def search_candidates(target_path: Optional[str], target_oid: Optional[str]) -> Optional[Path]:
        for root in search_roots:
            if target_path:
                candidate = root / target_path
                if candidate.exists():
                    if target_oid:
                        try:
                            if sha256_file(candidate) == target_oid:
                                return candidate
                        except Exception:
                            pass
                    else:
                        return candidate
        if target_path:
            name = Path(target_path).name
            for root in search_roots:
                for p in root.rglob(name):
                    if p.is_file():
                        if target_oid:
                            try:
                                if sha256_file(p) == target_oid:
                                    return p
                            except Exception:
                                continue
                        else:
                            return p
        if target_oid:
            for root in search_roots:
                for p in root.rglob("*"):
                    if p.is_file():
                        try:
                            if sha256_file(p) == target_oid:
                                return p
                        except Exception:
                            continue
        return None

    change_log = []

    for idx, (path_rel, oid) in enumerate(miss_items, start=1):
        step_id = f"3.2[{idx}]"
        try:
            candidate = search_candidates(path_rel, oid)
            if not candidate:
                unrecovered.append((path_rel, oid, "No matching candidate found in provided sources."))
                change_log.append(f"- {path_rel or oid}: recovery attempt exhausted; no candidate located.")
                continue

            if path_rel:
                run(["git", "lfs", "track", path_rel], cwd=repo, log_path=logs_dir / "commands.log", allow_fail=True)
            else:
                if oid:
                    path_rel = f"recovered/{oid}"
                else:
                    path_rel = f"recovered/unknown_{idx}"
                (repo / Path(path_rel)).parent.mkdir(parents=True, exist_ok=True)

            dest = (repo / Path(path_rel))
            dest.parent.mkdir(parents=True, exist_ok=True)

            data = candidate.read_bytes()
            dest.write_bytes(data)

            if ".github/workflows/" in dest.as_posix():
                raise RuntimeError("Refusing to add/modify files under .github/workflows/")

            run(["git", "add", path_rel], cwd=repo, log_path=logs_dir / "commands.log", allow_fail=False)

            msg = f"Restore LFS object: {path_rel}"
            if oid:
                msg += f" (oid:{oid})"

            if args.apply:
                run(["git", "commit", "-m", msg], cwd=repo, log_path=logs_dir / "commands.log", allow_fail=False)
                logging.info("Committed restored file: %s", path_rel)
            else:
                logging.info("[dry-run] Prepared to commit: %s", path_rel)
                run(["git", "reset", "HEAD", path_rel], cwd=repo, log_path=logs_dir / "commands.log", allow_fail=True)

            recovered.append((path_rel, oid, safe_relpath(candidate, candidate.parents[len(candidate.parts)-1] if candidate.is_absolute() else candidate.parent)))

        except Exception as e:
            unrecovered.append((path_rel, oid, f"Exception during recovery: {str(e)}"))
            append_text(logs_dir / "research_questions.md", f"""Question for ChatGPT-5:
While performing [{step_id}: Best-effort restore {path_rel or oid}], encountered the following error:
{str(e)}
Context: Attempting to track, copy, and stage a recovered candidate for an LFS-managed file.
What are the possible causes, and how can this be resolved while preserving intended functionality?
""")

    integrity_status = "unknown"
    if args.apply:
        try:
            run(["git", "lfs", "push", "--all", "origin"], cwd=repo, log_path=logs_dir / "commands.log", allow_fail=False)
        except Exception as e:
            append_text(logs_dir / "research_questions.md", f"""Question for ChatGPT-5:
While performing [3.3: git lfs push --all origin], encountered the following error:
{str(e)}
Context: Pushing all LFS objects to the default remote to ensure availability.
What are the possible causes, and how can this be resolved while preserving intended functionality?
""")

    rc, out, err = run(["git", "lfs", "fetch", "--all"], cwd=repo, log_path=logs_dir / "commands.log", allow_fail=True)
    rc, fsck2_out, fsck2_err = run(["git", "lfs", "fsck"], cwd=repo, log_path=logs_dir / "integrity_after_repair.log", allow_fail=True)
    missing_after = parse_missing(fsck2_out + "\n" + fsck2_err)
    integrity_status = "pass" if len(missing_after) == 0 else "fail"

    for path_rel, oid, reason in unrecovered:
        change_log.append(f"- UNRECOVERED {path_rel or oid}: {reason}. Deferred pruning; requires operator decision.")

    write_text(logs_dir / "change_log.md", "# Change Log\n\n" + "\n".join(change_log) + "\n")

    summary = {
        "missing_initial": initial_missing_count,
        "recovered": len(recovered),
        "unrecovered": len(unrecovered),
        "integrity_status": integrity_status,
        "dry_run": (not args.apply),
        "timestamp": now_iso(),
    }
    write_json(artifacts_dir / "integrity_report.json", summary)
    update_readme(repo / "README.md", summary)

    try:
        _, rev, _ = run(["git", "rev-parse", "HEAD"], cwd=repo, allow_fail=True)
        context["commit_after"] = rev.strip()
    except Exception:
        context["commit_after"] = None

    write_json(logs_dir / "context.json", context)

    print(json.dumps({
        "initial_missing": initial_missing_count,
        "recovered": len(recovered),
        "unrecovered": len(unrecovered),
        "integrity": integrity_status,
        "dry_run": (not args.apply),
        "logs_dir": str(logs_dir),
        "artifacts_dir": str(artifacts_dir),
    }, indent=2))

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        repo = Path(".").resolve()
        logs_dir = repo / "logs"
        append_text(logs_dir / "research_questions.md", f"""Question for ChatGPT-5:
While performing [GLOBAL: lfs_repair_orchestrator.py], encountered the following error:
{str(e)}
Context: Unhandled exception at top level; stack trace available in runtime context.
What are the possible causes, and how can this be resolved while preserving intended functionality?
""")
        raise
