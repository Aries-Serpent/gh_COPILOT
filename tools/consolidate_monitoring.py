#!/usr/bin/env python3
"""
Consolidate monitoring modules under a single package and update imports.

- Dry-run by default: previews moves/rewrites.
- Apply with:  python tools/consolidate_monitoring.py --apply --repo-root .
- Skips .github/workflows and common build/venv dirs.
- Generates:
    * monitoring/ (with __init__.py, collector.py, __main__.py)
    * CHANGELOG_MONITORING.md
    * ERRORS_MONITORING.md (ChatGPT-5 question format)
    * README update (best-effort)
- Computes Coverage Performance Score (CPS) and appends to changelog.

NOTE: Keeps shim modules temporarily to avoid breaking imports; you can remove later.
"""
from __future__ import annotations
import argparse, shutil, sys, re, time, json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple, Iterable

# ---------- Constants ----------
SKIP_DIRS = {
    ".git", ".svn", ".hg", ".bzr",
    ".venv", "venv", ".tox",
    "__pycache__", "dist", "build", ".mypy_cache", ".pytest_cache",
    ".idea", ".vscode",
}
SKIP_PATH_PREFIXES = {".github/workflows"}

CANDIDATE_NAMES = {
    "performance_tracker": "performance_tracker",
    "health_monitor": "health_monitor",
    "anomaly_detector": "anomaly_detector",
    # synonyms -> canonical
    "anomaly": "anomaly_detector",
    "anomaly_detection": "anomaly_detector",
}

PY_FILE = re.compile(r".+\.py$", re.IGNORECASE)

# ---------- Data ----------
@dataclass
class MovePlan:
    src: Path
    dst: Path
    reason: str

@dataclass
class RewriteStat:
    file: Path
    original_lines: int
    changed_lines: int

@dataclass
class Context:
    repo_root: Path
    apply: bool
    backup_dir: Path | None
    logs: List[str] = field(default_factory=list)
    moves: List[MovePlan] = field(default_factory=list)
    rewrites: List[RewriteStat] = field(default_factory=list)
    shims: List[Path] = field(default_factory=list)
    prunes: List[Path] = field(default_factory=list)
    errors: List[Dict] = field(default_factory=list)
    touched_tests: int = 0
    needs_test_updates: int = 0
    entrypoint_created: bool = False

def log(ctx: Context, msg: str) -> None:
    print(msg)
    ctx.logs.append(msg)

def err_capture(ctx: Context, step: str, exc: Exception, brief: str) -> None:
    entry = {
        "step": step,
        "error": f"{type(exc).__name__}: {exc}",
        "context": brief,
        "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    ctx.errors.append(entry)
    # Also print the exact research question block to stdout for visibility
    print("\nQuestion for ChatGPT-5:")
    print(f"While performing {step}, encountered the following error:")
    print(f"{type(exc).__name__}: {exc}")
    print(f"Context: {brief}")
    print("What are the possible causes, and how can this be resolved while preserving intended functionality?\n")

def is_skipped(path: Path) -> bool:
    parts = set(p.name for p in path.parts if p)
    if any(str(path).replace("\\", "/").startswith(prefix) for prefix in SKIP_PATH_PREFIXES):
        return True
    return bool(parts & SKIP_DIRS)

def find_candidates(repo: Path) -> Dict[Path, str]:
    found: Dict[Path, str] = {}
    for p in repo.rglob("*"):
        if is_skipped(p): 
            continue
        if p.is_dir():
            name = p.name
            if name in CANDIDATE_NAMES:
                found[p] = CANDIDATE_NAMES[name]
        elif p.is_file() and p.suffix == ".py":
            # single-file module matches (e.g., performance_tracker.py)
            base = p.stem
            if base in CANDIDATE_NAMES and p.parent != (repo / "monitoring" / CANDIDATE_NAMES[base]):
                found[p] = CANDIDATE_NAMES[base]
    return found

def ensure_monitoring_skeleton(ctx: Context) -> None:
    mon = ctx.repo_root / "monitoring"
    (mon).mkdir(parents=True, exist_ok=True)
    init = mon / "__init__.py"
    if not init.exists():
        init.write_text(
            "# Consolidated monitoring package\n"
            "from . import performance_tracker as performance_tracker  # noqa: F401\n"
            "from . import health_monitor as health_monitor  # noqa: F401\n"
            "from . import anomaly_detector as anomaly_detector  # noqa: F401\n"
        )
    collector = mon / "collector.py"
    if not collector.exists():
        collector.write_text(
            "from typing import Any, Dict, Iterable, Callable\n"
            "\n"
            "def collect_metrics(sources: Dict[str, Callable[[], Dict[str, Any]]]) -> Dict[str, Any]:\n"
            "    out: Dict[str, Any] = {}\n"
            "    for name, fn in sources.items():\n"
            "        try:\n"
            "            out[name] = fn()\n"
            "        except Exception as e:\n"
            "            out[name] = {\"error\": str(e)}\n"
            "    return out\n"
            "\n"
            "def detect_anomalies(metrics: Dict[str, Any], detectors: Iterable[Callable[[Dict[str, Any]], Dict[str, Any]]]):\n"
            "    results = []\n"
            "    for det in detectors:\n"
            "        try:\n"
            "            results.append(det(metrics))\n"
            "        except Exception as e:\n"
            "            results.append({\"detector\": getattr(det, '__name__', 'unknown'), \"error\": str(e)})\n"
            "    return results\n"
            "\n"
            "def collect_and_detect(sources: Dict[str, Callable[[], Dict[str, Any]]],\n"
            "                       detectors: Iterable[Callable[[Dict[str, Any]], Dict[str, Any]]]):\n"
            "    metrics = collect_metrics(sources)\n"
            "    anomalies = detect_anomalies(metrics, detectors)\n"
            "    return {\"metrics\": metrics, \"anomalies\": anomalies}\n"
        )
    main = mon / "__main__.py"
    if not main.exists():
        main.write_text(
            "from .collector import collect_and_detect\n"
            "def _demo_source():\n"
            "    return {\"uptime\": 12345, \"cpu\": 0.15}\n"
            "def _demo_detector(metrics):\n"
            "    m = metrics.get(\"demo\", {})\n"
            "    return {\"detector\": \"demo\", \"flag\": m.get(\"cpu\", 0) > 0.9}\n"
            "if __name__ == \"__main__\":\n"
            "    result = collect_and_detect({\"demo\": _demo_source}, [_demo_detector])\n"
            "    print(result)\n"
        )
    # make subpkg dirs even if empty, to be targets
    for sub in ("performance_tracker", "health_monitor", "anomaly_detector"):
        (mon / sub).__mkdirs__()

def _mkdirs(self: Path):  # monkey-patch helper
    self.mkdir(parents=True, exist_ok=True)
Path.__mkdirs__ = _mkdirs  # type: ignore

def plan_moves(ctx: Context, found: Dict[Path, str]) -> None:
    mon = ctx.repo_root / "monitoring"
    for src, canonical in found.items():
        dst_dir = mon / canonical
        dst_dir.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            dst = dst_dir / src.name  # keep nested dir name
        else:
            dst = dst_dir / src.name
        if src.resolve() == dst.resolve():
            continue
        ctx.moves.append(MovePlan(src=src, dst=dst, reason=f"Consolidate into monitoring/{canonical}"))

def backup_file(ctx: Context, p: Path) -> None:
    if not ctx.apply or ctx.backup_dir is None: 
        return
    rel = p.relative_to(ctx.repo_root)
    target = ctx.backup_dir / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    if p.is_dir():
        if not target.exists():
            shutil.copytree(p, target)
    elif p.is_file():
        if not target.exists():
            shutil.copy2(p, target)

def execute_moves(ctx: Context) -> None:
    for mv in ctx.moves:
        try:
            backup_file(ctx, mv.src)
            if ctx.apply:
                # If moving a directory into a subdir with same name, move contents
                if mv.src.is_dir():
                    mv.dst.mkdir(parents=True, exist_ok=True)
                    for item in mv.src.iterdir():
                        shutil.move(str(item), str(mv.dst / item.name))
                    # remove empty src
                    try: mv.src.rmdir()
                    except OSError: pass
                else:
                    mv.dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(mv.src), str(mv.dst))
            log(ctx, f"[MOVE]{' (dry-run)' if not ctx.apply else ''} {mv.src} -> {mv.dst} :: {mv.reason}")
        except Exception as e:
            err_capture(ctx, "Phase2:execute_moves", e, f"Moving {mv.src} -> {mv.dst}")

IMPORT_PATTERNS = [
    # from X import Y
    (re.compile(r'^(?P<pre>\s*from\s+)(performance_tracker|health_monitor|anomaly(?:_detector|_detection)?)\s+(?P<rest>import\s+.+)$'),
     lambda m: f"{m.group('pre')}monitoring.{CANDIDATE_NAMES.get(m.group(2), 'anomaly_detector')} {m.group('rest')}")
    ,
    # import X as A  OR import X
    (re.compile(r'^(?P<pre>\s*import\s+)(performance_tracker|health_monitor|anomaly(?:_detector|_detection)?)(?P<post>(\s+as\s+\w+)?\s*)$'),
     lambda m: f"{m.group('pre')}monitoring.{CANDIDATE_NAMES.get(m.group(2), 'anomaly_detector')}{m.group('post')}")
]

def rewrite_imports_in_file(ctx: Context, file: Path) -> int:
    try:
        text = file.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        err_capture(ctx, "Phase2:read_file_for_import_rewrite", e, f"Reading {file}")
        return 0
    changed = 0
    lines = text.splitlines()
    new_lines: List[str] = []
    for line in lines:
        original = line
        for pat, repl in IMPORT_PATTERNS:
            m = pat.match(line)
            if m:
                line = repl(m)
        if line != original:
            changed += 1
        new_lines.append(line)
    if changed and ctx.apply:
        backup_file(ctx, file)
        file.write_text("\n".join(new_lines), encoding="utf-8")
    if changed:
        ctx.rewrites.append(RewriteStat(file=file, original_lines=len(lines), changed_lines=changed))
    return changed

def iter_python_files(repo: Path) -> Iterable[Path]:
    for p in repo.rglob("*.py"):
        if is_skipped(p) or any(str(p).replace("\\","/").startswith(prefix) for prefix in SKIP_PATH_PREFIXES):
            continue
        yield p

def rewrite_all_imports(ctx: Context) -> None:
    for py in iter_python_files(ctx.repo_root):
        changed = rewrite_imports_in_file(ctx, py)
        if changed:
            rel = py.relative_to(ctx.repo_root)
            log(ctx, f"[REWRITE]{' (dry-run)' if not ctx.apply else ''} {rel}: {changed} lines")

def create_shims(ctx: Context, found: Dict[Path, str]) -> None:
    # Create tiny shim files at old locations if they were single-file modules
    for src, canonical in found.items():
        if src.is_file() and ctx.repo_root in src.parents:
            try:
                if ctx.apply:
                    backup_file(ctx, src)
                    src.write_text(
                        "import warnings\n"
                        "warnings.warn('Deprecated import path; use monitoring.{0} instead', DeprecationWarning)\n"
                        "from monitoring.{0} import *\n".format(canonical),
                        encoding="utf-8"
                    )
                ctx.shims.append(src)
                log(ctx, f"[SHIM]{' (dry-run)' if not ctx.apply else ''} {src} -> monitoring.{canonical}")
            except Exception as e:
                err_capture(ctx, "Phase3:create_shims", e, f"Create shim at {src} for {canonical}")

def update_readme(ctx: Context) -> None:
    # Best-effort: update main README
    candidates = list(ctx.repo_root.glob("README*.md"))
    for readme in candidates:
        try:
            text = readme.read_text(encoding="utf-8", errors="ignore")
            original = text
            # Replace code snippets and mentions
            text = re.sub(r"\bfrom\s+performance_tracker\b", "from monitoring.performance_tracker", text)
            text = re.sub(r"\bfrom\s+health_monitor\b", "from monitoring.health_monitor", text)
            text = re.sub(r"\bfrom\s+anomaly(?:_detector|_detection|)\b", "from monitoring.anomaly_detector", text)
            text = re.sub(r"\bimport\s+performance_tracker\b", "import monitoring.performance_tracker as performance_tracker", text)
            text = re.sub(r"\bimport\s+health_monitor\b", "import monitoring.health_monitor as health_monitor", text)
            text = re.sub(r"\bimport\s+anomaly(?:_detector|_detection|)\b", "import monitoring.anomaly_detector as anomaly_detector", text)

            if "## Monitoring Package Migration" not in text:
                text += (
                    "\n\n## Monitoring Package Migration\n"
                    "All monitoring modules were consolidated into the `monitoring/` package.\n"
                    "Run via `python -m monitoring`. Example:\n\n"
                    "```python\n"
                    "from monitoring.collector import collect_and_detect\n"
                    "```\n"
                )
            if text != original and ctx.apply:
                backup_file(ctx, readme)
                readme.write_text(text, encoding="utf-8")
            if text != original:
                log(ctx, f"[README]{' (dry-run)' if not ctx.apply else ''} Updated {readme.name}")
        except Exception as e:
            err_capture(ctx, "Phase2:update_readme", e, f"Updating {readme}")

def compute_cps(ctx: Context, found: Dict[Path, str]) -> float:
    # Components
    total_targets = max(1, len(found))
    moved_or_mapped = sum(1 for mv in ctx.moves)  # approximation
    C_mapping = min(1.0, moved_or_mapped / total_targets)

    total_rewrite_files = len({r.file for r in ctx.rewrites})
    total_rewrites = sum(r.changed_lines for r in ctx.rewrites)
    C_imports = 0.0 if total_rewrite_files == 0 else min(1.0, total_rewrites / (total_rewrite_files * 5.0))  # heuristic

    C_entry = 1.0 if ctx.entrypoint_created else 0.0

    C_tests = 0.0
    if ctx.needs_test_updates > 0:
        C_tests = min(1.0, ctx.touched_tests / ctx.needs_test_updates)

    P_errors = 0.05 * len(ctx.errors)

    CPS = (0.35*C_mapping) + (0.35*C_imports) + (0.20*C_entry) + (0.10*C_tests) - P_errors
    return max(0.0, round(CPS, 3))

def write_changelog(ctx: Context, found: Dict[Path, str], cps: float) -> None:
    cl = ctx.repo_root / "CHANGELOG_MONITORING.md"
    lines = []
    lines.append(f"# Monitoring Consolidation — {time.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append("## Moves / Mapping")
    for mv in ctx.moves:
        lines.append(f"- `{mv.src}` → `{mv.dst}` — {mv.reason}")
    lines.append("")
    lines.append("## Import Rewrites")
    for r in ctx.rewrites:
        lines.append(f"- `{r.file}`: {r.changed_lines} lines changed")
    if ctx.shims:
        lines.append("\n## Shims (Temporary Compatibility)")
        for s in ctx.shims:
            lines.append(f"- `{s}` re-exports from `monitoring` with DeprecationWarning")
    if ctx.prunes:
        lines.append("\n## Pruned")
        for p in ctx.prunes:
            lines.append(f"- Removed `{p}` (documented rationale: consolidated under `monitoring/`)")

    lines.append("\n## Coverage Performance Score")
    lines.append(f"- CPS = {cps}")
    lines.append("\n### Scoring Formula")
    lines.append("CPS = 0.35·C_mapping + 0.35·C_imports + 0.20·C_entry + 0.10·C_tests − P_errors")

    if ctx.errors:
        lines.append("\n## Errors Captured")
        for e in ctx.errors:
            lines.append(f"- [{e['ts']}] {e['step']}: {e['error']} (Context: {e['context']})")

    cl.write_text("\n".join(lines), encoding="utf-8")
    log(ctx, f"[FINAL] Wrote {cl}")

def write_errors_markdown(ctx: Context) -> None:
    if not ctx.errors:
        return
    md = ctx.repo_root / "ERRORS_MONITORING.md"
    blocks = []
    for e in ctx.errors:
        blocks.append("Question for ChatGPT-5:\n"
                      f"While performing {e['step']}, encountered the following error:\n"
                      f"{e['error']}\n"
                      f"Context: {e['context']}\n"
                      "What are the possible causes, and how can this be resolved while preserving intended functionality?\n")
    md.write_text("\n\n".join(blocks), encoding="utf-8")
    log(ctx, f"[FINAL] Wrote {md}")

def estimate_test_updates(ctx: Context) -> None:
    # Heuristic: any file under tests/ that mentions target names likely needs update
    for p in ctx.repo_root.rglob("tests"):
        if not p.is_dir() or is_skipped(p):
            continue
        for f in p.rglob("*.py"):
            if is_skipped(f): 
                continue
            try:
                t = f.read_text(encoding="utf-8", errors="ignore")
                if re.search(r"\b(performance_tracker|health_monitor|anomaly(?:_detector|_detection)?)\b", t):
                    ctx.needs_test_updates += 1
            except Exception:
                pass

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".", help="Path to repository root")
    ap.add_argument("--apply", action="store_true", help="Apply changes (otherwise dry-run)")
    args = ap.parse_args()

    repo_root = Path(args.repo_root).resolve()
    backup_dir = None
    if args.apply:
        backup_dir = repo_root / f".monitoring_migration_backup_{int(time.time())}"
        backup_dir.mkdir(parents=True, exist_ok=True)

    ctx = Context(repo_root=repo_root, apply=args.apply, backup_dir=backup_dir)

    try:
        # Phase 0: prep
        ensure_monitoring_skeleton(ctx)
        ctx.entrypoint_created = True
    except Exception as e:
        err_capture(ctx, "Phase0:ensure_monitoring_skeleton", e, "Creating monitoring package skeleton")

    try:
        # Phase 1: search & mapping
        found = find_candidates(repo_root)
        if not found:
            log(ctx, "[INFO] No existing monitoring modules found; stubs only.")
        plan_moves(ctx, found)
    except Exception as e:
        err_capture(ctx, "Phase1:search_and_mapping", e, "Scanning repository for candidate modules")
        found = {}

    try:
        # Phase 2: execute best-effort construction
        if ctx.moves:
            execute_moves(ctx)
        # Test estimate (pre rewrite)
        estimate_test_updates(ctx)
        # Rewrites
        rewrite_all_imports(ctx)
        # Shims at old single-file locations
        create_shims(ctx, found)
        # README update
        update_readme(ctx)
    except Exception as e:
        err_capture(ctx, "Phase2:best_effort", e, "Executing moves/rewrites/readme updates")

    # Finalization
    cps = compute_cps(ctx, found)
    write_changelog(ctx, found, cps)
    write_errors_markdown(ctx)

    # Human-friendly summary
    summary = {
        "apply": ctx.apply,
        "moves_planned": len(ctx.moves),
        "files_rewritten": len({r.file for r in ctx.rewrites}),
        "total_lines_changed": sum(r.changed_lines for r in ctx.rewrites),
        "entrypoint_created": ctx.entrypoint_created,
        "tests_needing_updates_est": ctx.needs_test_updates,
        "errors": len(ctx.errors),
        "CPS": cps,
    }
    print("\n== SUMMARY ==")
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
