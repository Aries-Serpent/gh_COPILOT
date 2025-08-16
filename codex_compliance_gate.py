#!/usr/bin/env python3
"""
codex_compliance_gate.py

Implements a constructive-first compliance composite and enforcement gate:
- Searches and maps likely metric sources.
- Best-effort adapters for lint, tests, placeholder, session metrics.
- Composite scoring and enforcement threshold check.
- README/doc updates (status index + governance changelog).
- Error capture into ChatGPT-5 research questions format.

Requires: Python 3.9+, lxml (for JUnit XML parsing).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# -------------------------
# Utilities & Boilerplate
# -------------------------

ROOT = Path(".").resolve()
CODEX_DIR = ROOT / ".codex"
ERROR_DIR = CODEX_DIR / "errors"
LOG_DIR = CODEX_DIR / "logs"
OUT_JSON = CODEX_DIR / "compliance_gate.json"
STATUS_JSON = ROOT / "docs" / "status_index.json"
GOV_CHANGELOG = ROOT / "docs" / "governance" / "CHANGELOG_COMPLIANCE.md"

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def safe_mkdir(p: Path):
    p.mkdir(parents=True, exist_ok=True)

def write_research_question(step_num: str, step_desc: str, error_msg: str, context: str):
    safe_mkdir(ERROR_DIR)
    with open(ERROR_DIR / "research_questions.md", "a", encoding="utf-8") as fh:
        fh.write(
            "Question for ChatGPT-5:\n"
            f"While performing [{step_num}:{step_desc}], encountered the following error:\n"
            f"{error_msg}\n"
            f"Context: {context}\n"
            "What are the possible causes, and how can this be resolved while preserving intended functionality?\n\n"
        )

def read_text_if_exists(p: Path) -> Optional[str]:
    try:
        return p.read_text(encoding="utf-8") if p.exists() else None
    except Exception as e:
        write_research_question("RX01", f"read {p}", str(e), "Accessing candidate file")
        return None

def write_json(p: Path, data: Dict[str, Any]):
    safe_mkdir(p.parent)
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def append_line(p: Path, line: str):
    safe_mkdir(p.parent)
    with open(p, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")

# -------------------------
# Adapters (Best-Effort)
# -------------------------

def score_lint() -> Tuple[float, Dict[str, Any]]:
    """
    Attempts:
      1) Parse Ruff summary from logs or artifacts.
      2) Parse Pyright summary (release noted README mentions Pyright; assume usage).  # v0.4.6-alpha notes. 
      3) Fallback heuristic: scan for 'E|W' patterns or assume medium score if no data.
    Scoring heuristic: 100 - (10*errors + 2*warnings), clamped [0,100].
    """
    candidates = [
        ROOT / ".codex" / "logs" / "ruff.log",
        ROOT / ".codex" / "logs" / "pyright.log",
        ROOT / "ruff.log",
        ROOT / "pyright.log",
    ]
    errors = 0
    warnings = 0
    evidence: List[str] = []
    try:
        for p in candidates:
            content = read_text_if_exists(p)
            if not content:
                continue
            evidence.append(str(p))
            errors += len(re.findall(r"\berror\b|\bE\d{3}\b", content, re.IGNORECASE))
            warnings += len(re.findall(r"\bwarning\b|\bW\d{3}\b", content, re.IGNORECASE))
    except Exception as e:
        write_research_question("A01", "score_lint()", str(e), "Parsing lint logs")
    raw = max(0, 100 - (10 * errors + 2 * warnings))
    return float(raw), {"errors": errors, "warnings": warnings, "sources": evidence}

def score_tests() -> Tuple[float, Dict[str, Any]]:
    """
    Attempts:
      1) Parse JUnit XML to compute pass rate.
      2) If coverage.xml present, map coverage% to score (bounded).
      3) Fallback to neutral 75 with 'needs-data' context.
    """
    junit_candidates = list(ROOT.rglob("junit*.xml"))
    coverage_candidates = list(ROOT.rglob("coverage*.xml"))
    evidence = []
    try:
        if junit_candidates:
            from lxml import etree  # requires lxml
            best = junit_candidates[0]
            evidence.append(str(best))
            tree = etree.parse(str(best))
            tests = int(tree.xpath("sum(//testsuite/@tests)"))
            failures = int(tree.xpath("sum(//testsuite/@failures)"))
            errors = int(tree.xpath("sum(//testsuite/@errors)"))
            skipped = int(tree.xpath("sum(//testsuite/@skipped)"))
            passed = max(0, tests - failures - errors - skipped)
            rate = 0.0 if tests == 0 else 100.0 * (passed / tests)
            return rate, {"tests": tests, "passed": passed, "failures": failures, "errors": errors, "skipped": skipped, "sources": evidence}
        if coverage_candidates:
            text = read_text_if_exists(coverage_candidates[0]) or ""
            evidence.append(str(coverage_candidates[0]))
            m = re.search(r'line-rate="([0-9.]+)"', text)
            if m:
                cov = float(m.group(1)) * 100.0
                return cov, {"coverage_percent": cov, "sources": evidence}
    except Exception as e:
        write_research_question("A02", "score_tests()", str(e), "Parsing JUnit/Coverage XML")
    return 75.0, {"note": "fallback (no JUnit/coverage found)", "sources": evidence}

def score_placeholder() -> Tuple[float, Dict[str, Any]]:
    """
    Penalize density of TODO/FIXME/[stub] across the repo using ripgrep for efficiency.
    Score: 100 - count, clipped [0,100].
    """
    count = 0
    evidence: List[str] = []
    try:
        import subprocess
        cmd = [
            "rg",
            "--hidden",
            "--follow",
            "--glob",
            "!*venv*",
            "TODO|FIXME|\\[stub\\]",
            str(ROOT)
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        lines = res.stdout.splitlines()
        count = len(lines)
        for line in lines[:10]:
            parts = line.split(":", 2)
            if parts:
                evidence.append(parts[0])
    except Exception as e:
        write_research_question("A03", "score_placeholder()", str(e), "Running ripgrep for placeholder markers")
    score = max(0.0, 100.0 - float(count))
    return score, {"placeholders": count, "sources": evidence}

def score_session() -> Tuple[float, Dict[str, Any]]:
    """
    Pull 'session' metric from monitoring artifacts (e.g., metrics/session.json written by monitoring stubs).
    Release v0.4.6-alpha added monitoring command stubs; honor metrics if present; otherwise neutral 80.  # release ref
    Expected format: {"session_health": 0..100, "...": ...}
    """
    candidates = [ROOT / "metrics" / "session.json", CODEX_DIR / "tmp" / "session.json"]
    for p in candidates:
        try:
            if p.exists():
                data = json.loads(p.read_text(encoding="utf-8"))
                if isinstance(data, dict) and "session_health" in data:
                    val = float(data["session_health"])
                    return max(0.0, min(100.0, val)), {"source": str(p), "raw": data}
        except Exception as e:
            write_research_question("A04", "score_session()", str(e), f"Reading {p}")
    return 80.0, {"note": "fallback (no session metrics found)"}

# -------------------------
# Composite & Enforcement
# -------------------------

def composite_score(
    lint: float, tests: float, placeholder: float, session: float,
    w_lint: float, w_tests: float, w_placeholder: float, w_session: float
) -> float:
    num = w_lint*lint + w_tests*tests + w_placeholder*placeholder + w_session*session
    denom = max(0.0001, (w_lint + w_tests + w_placeholder + w_session))
    return num / denom

def update_status_index(score: float, threshold: float, enforced: bool, inputs: Dict[str, Any]):
    safe_mkdir(STATUS_JSON.parent)
    payload = {
        "compliance_score": round(score, 2),
        "threshold": threshold,
        "enforced": enforced,
        "updated_at": now_iso(),
        "inputs": inputs
    }
    if STATUS_JSON.exists():
        try:
            existing = json.loads(STATUS_JSON.read_text(encoding="utf-8"))
            if isinstance(existing, dict):
                existing.update(payload)
                payload = existing
        except Exception as e:
            write_research_question("D01", "update_status_index()", str(e), "Merging docs/status_index.json")
    write_json(STATUS_JSON, payload)

def append_governance_log(score: float, threshold: float, passed: bool, notes: str):
    line = f"- {now_iso()} — score={score:.2f} threshold={threshold:.2f} enforced={passed} — {notes}"
    append_line(GOV_CHANGELOG, line)

# -------------------------
# Main
# -------------------------

def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--enforce-threshold", type=float, default=float(os.getenv("COMPLIANCE_THRESHOLD", "85")))
    ap.add_argument("--w-lint", type=float, default=float(os.getenv("W_LINT", "0.25")))
    ap.add_argument("--w-tests", type=float, default=float(os.getenv("W_TESTS", "0.45")))
    ap.add_argument("--w-placeholder", type=float, default=float(os.getenv("W_PLACEHOLDER", "0.15")))
    ap.add_argument("--w-session", type=float, default=float(os.getenv("W_SESSION", "0.15")))
    args = ap.parse_args(argv)

    safe_mkdir(LOG_DIR)
    (LOG_DIR / "mapping.log").write_text(
        "Mapping assumptions: lint from Ruff/Pyright logs; tests from JUnit or coverage; "
        "placeholder from TODO/[stub]; session from metrics/session.json.\n"
        "Release v0.4.6-alpha hints: compliance stubs + monitoring stubs + Pyright usage.\n",
        encoding="utf-8"
    )

    try:
        l_val, l_info = score_lint()
        t_val, t_info = score_tests()
        p_val, p_info = score_placeholder()
        s_val, s_info = score_session()
    except Exception as e:
        write_research_question("B00", "collect_metrics()", traceback.format_exc(), "Unexpected exception in metric adapters")
        l_val = t_val = p_val = s_val = 0.0
        l_info = t_info = p_info = s_info = {"note": "adapter failure"}

    comp = composite_score(l_val, t_val, p_val, s_val, args.w_lint, args.w_tests, args.w_placeholder, args.w_session)

    result = {
        "timestamp": now_iso(),
        "weights": {"lint": args.w_lint, "tests": args.w_tests, "placeholder": args.w_placeholder, "session": args.w_session},
        "scores": {"lint": l_val, "tests": t_val, "placeholder": p_val, "session": s_val, "composite": comp},
        "details": {"lint": l_info, "tests": t_info, "placeholder": p_info, "session": s_info}
    }
    write_json(OUT_JSON, result)

    threshold = float(args.enforce_threshold)
    passed = comp >= threshold
    if not passed:
        msg = (f"[ENFORCEMENT] FAIL — Composite {comp:.2f} below threshold {threshold:.2f}. "
               f"See {OUT_JSON} for details.")
        print(msg, file=sys.stderr)
    else:
        print(f"[ENFORCEMENT] PASS — Composite {comp:.2f} >= threshold {threshold:.2f}.")

    try:
        update_status_index(comp, threshold, passed, result["details"])
        append_governance_log(comp, threshold, passed, "composite gate run")
    except Exception as e:
        write_research_question("D02", "docs update", str(e), "Writing status_index.json / CHANGELOG_COMPLIANCE.md")

    return 0 if passed else 2

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as ex:
        write_research_question("Z99", "main()", traceback.format_exc(), "Top-level failure")
        print("[FATAL] compliance gate crashed; research question emitted.", file=sys.stderr)
        sys.exit(3)
