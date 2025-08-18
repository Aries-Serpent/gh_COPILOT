#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Codex Gap Uplift — README alignment with best-effort construction before pruning.

Implements the sequential phases:
- Preparation
- Search & Mapping
- Best-Effort Construction (Combined checks, Monitoring API ref, Performance monitoring)
- Controlled Pruning (only after construction)
- Error Capture as ChatGPT-5 research questions
- Finalization

Grounding ref: Aries-Serpent/gh_COPILOT v0.4.6-alpha release notes mention:
- docs: note run_checks.py uses Pyright
- docs: replace collect_metrics reference
- feat: add monitoring command stubs
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import textwrap
from datetime import datetime
from pathlib import Path

ROOT = Path(".").resolve()
README = ROOT / "README.md"
BACKUP = Path(os.environ.get("GH_COPILOT_BACKUP_ROOT", "/tmp")).resolve() / "README.md.bak"
CODEX_DIR = ROOT / ".codex"
INDEX = CODEX_DIR / "index_paths.txt"
GAP_LOG = CODEX_DIR / "gap_changelog.md"

def sh(cmd: str) -> tuple[int, str, str]:
    """Run shell command, return (rc, out, err)."""
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = p.communicate()
    return p.returncode, out, err

def append_gap_question(phase_step: str, error_msg: str, context: str):
    CODEX_DIR.mkdir(parents=True, exist_ok=True)
    with GAP_LOG.open("a", encoding="utf-8") as f:
        f.write("\n" + "="*80 + "\n")
        f.write("Question for ChatGPT-5:\n")
        f.write(f"While performing {phase_step}, encountered the following error:\n")
        f.write(f"{error_msg.strip()}\n")
        f.write(f"Context: {context.strip()}\n")
        f.write("What are the possible causes, and how can this be resolved while preserving intended functionality?\n")
        f.write("="*80 + "\n")

def safe_readme_text() -> str:
    if not README.exists():
        append_gap_question("Phase 1:Preparation:README presence", "README.md not found",
                            f"cwd={ROOT}, files={os.listdir('.')[:50]}")
        raise FileNotFoundError("README.md not found")
    return README.read_text(encoding="utf-8", errors="replace")

def write_readme(text: str):
    README.write_text(text, encoding="utf-8")

def ensure_backup():
    try:
        BACKUP.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(README, BACKUP)
    except Exception as e:
        append_gap_question("Phase 1:Preparation:backup", str(e),
                            "Attempting to copy README.md to backup root")
        raise

def build_index():
    CODEX_DIR.mkdir(parents=True, exist_ok=True)
    rc, out, _ = sh("fd -t f . scripts docs 2>/dev/null || find scripts docs -type f 2>/dev/null")
    paths = sorted([p.strip() for p in out.splitlines() if p.strip()])
    INDEX.write_text("\n".join(paths), encoding="utf-8")
    return set(paths)

def find_candidates(stem_tokens: list[str], files: set[str]) -> list[str]:
    toks = [t.lower() for t in stem_tokens if t]
    out = []
    for p in files:
        low = p.lower()
        if all(t in low for t in toks):
            out.append(p)
    return out

def normalize_collect_metrics(text: str) -> tuple[str, bool]:
    pat = r"UnifiedMonitoringOptimizationSystem\.collect_metrics"
    new_text, n = re.subn(pat, "unified_monitoring_optimization_system.collect_metrics", text)
    changed = n > 0
    pat2 = r"Unified[_ ]?Monitoring[_ ]?Optimization[_ ]?System\.collect_metrics"
    new_text2, n2 = re.subn(pat2, "unified_monitoring_optimization_system.collect_metrics", new_text)
    return new_text2, changed or (n2 > 0)

def ensure_combined_checks_mentions_pyright(text: str) -> tuple[str, bool]:
    changed = False
    if re.search(r"(?i)combined checks", text):
        def _patch(m):
            blk = m.group(0)
            if re.search(r"Pyright", blk, re.I):
                return blk
            return re.sub(r"(Ruff.*?pytest)", r"Ruff, Pyright, and pytest", blk, flags=re.I|re.S)
        new_text = re.sub(r"(#+\s*.*combined checks[\s\S]{0,400})", _patch, text, flags=re.I)
        changed = new_text != text
        return new_text, changed
    else:
        inject = textwrap.dedent("""

### Combined checks
```bash
python scripts/run_checks.py  # runs Ruff, Pyright, pytest
```
""")
        new_text = text + inject
        return new_text, True

def create_monitoring_stub_if_needed(files: set[str]) -> tuple[bool, str]:
    desired = "scripts/monitoring/performance_monitor.py"
    if desired in files:
        return False, desired
    near = find_candidates(["monitor", "engine"], files) + find_candidates(["database", "event", "monitor"], files)
    if near:
        return False, near[0]
    path = ROOT / desired
    path.parent.mkdir(parents=True, exist_ok=True)
    stub = '''#!/usr/bin/env python3
"""Performance Monitor (Preview Stub)
Collects basic system metrics on an interval and prints them; intended to integrate
with unified_monitoring_optimization_system.collect_metrics.
"""
import time, argparse, json, sys

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--interval', type=int, default=60)
    ns = ap.parse_args()
    print('[stub] starting performance monitor; interval=', ns.interval)
    try:
        while True:
            payload = {'timestamp': time.time(), 'cpu_usage_percent': 0.0, 'memory_usage_percent': 0.0}
            print(json.dumps(payload))
            time.sleep(ns.interval)
    except KeyboardInterrupt:
        print('[stub] stopped')

if __name__ == '__main__':
    sys.exit(main())
'''
    path.write_text(stub, encoding="utf-8")
    os.chmod(path, 0o755)
    return True, desired

def patch_readme(text: str, files: set[str]) -> tuple[str, list[str]]:
    actions = []
    try:
        text, changed = ensure_combined_checks_mentions_pyright(text)
        if changed:
            actions.append("Updated Combined checks to include Ruff, Pyright, pytest.")
    except Exception as e:
        append_gap_question("Phase 3.1:Ensure Combined checks", repr(e), "Updating Combined checks block")
    try:
        text, changed = normalize_collect_metrics(text)
        if changed:
            actions.append("Normalized collect_metrics reference to module-level function.")
    except Exception as e:
        append_gap_question("Phase 3.2:Normalize collect_metrics", repr(e), "Replacing class-style ref")
    perf_refs = [
        "scripts/monitoring/performance_monitor.py",
        "scripts/monitoring/performance_analyzer.py",
        "scripts/monitoring/regression_detector.py",
        "scripts/monitoring/resource_tracker.py",
    ]
    if any(ref in text for ref in perf_refs):
        created_stub, mapped_path = create_monitoring_stub_if_needed(files)
        try:
            for ref in perf_refs:
                if ref in text:
                    text = text.replace(ref, mapped_path)
            if created_stub:
                text = re.sub(r"(Performance Monitoring[^\n]*\n)", r"\1> Note: performance monitor provided via stub.\n", text, flags=re.I)
                actions.append(f"Created monitoring stub at {mapped_path} and updated README references.")
            else:
                actions.append(f"Mapped Performance Monitoring references to existing utility {mapped_path}.")
        except Exception as e:
            append_gap_question("Phase 3.3:Map/Stub Performance Monitoring", repr(e),
                                f"mapped_path={mapped_path}, created_stub={created_stub}")
    return text, actions

def prune_with_rationale(text: str, files: set[str]) -> tuple[str, list[str]]:
    actions = []
    def maybe_prune(marker: str, token_list: list[str], friendly: str):
        nonlocal text, actions
        tokens = [t.lower() for t in token_list]
        candidates = find_candidates(tokens, files)
        if candidates:
            return
        before = text
        text = re.sub(rf".*{re.escape(marker)}.*\n?", "", text)
        if before != text:
            rationale = (f"Pruned reference '{marker}' after exhausting mapping attempts; stubbing deemed non-valuable or duplicative.")
            actions.append(rationale)
            with GAP_LOG.open("a", encoding="utf-8") as f:
                f.write(f"\n- {rationale}")
    maybe_prune("scripts/monitoring/regression_detector.py", ["regression","monitor"], "Regression Detector")
    return text, actions

def main():
    try:
        ensure_backup()
        files = build_index()
        text = safe_readme_text()
        text, actions1 = patch_readme(text, files)
        text, actions2 = prune_with_rationale(text, files)
        write_readme(text)
        CODEX_DIR.mkdir(parents=True, exist_ok=True)
        with GAP_LOG.open("a", encoding="utf-8") as f:
            f.write(f"\n## Gap Resolution Log — {datetime.utcnow().isoformat()}Z\n")
            for a in actions1 + actions2:
                f.write(f"- {a}\n")
        checks = {
            "combined_checks_mentions_pyright": bool(re.search(r"(?i)Ruff.*Pyright.*pytest", text)),
            "collect_metrics_normalized": "unified_monitoring_optimization_system.collect_metrics" in text,
        }
        print(json.dumps({"status": "ok", "checks": checks, "gap_log": str(GAP_LOG)}, indent=2))
    except Exception as e:
        append_gap_question("Finalization:Unhandled", repr(e), "Top-level failure in codex_gap_uplift.py")
        print(json.dumps({"status": "error", "message": repr(e), "gap_log": str(GAP_LOG)}))
        sys.exit(2)

if __name__ == "__main__":
    main()
