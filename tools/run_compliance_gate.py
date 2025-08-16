#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Compliance Gate Workflow.

This script calculates lint, test, placeholder, and session metrics
and computes a composite score. It writes results to docs/status_index.json
and updates governance and changelog files.
"""

import argparse
import importlib.util
import json
import os
import re
import subprocess
import sys
import textwrap
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
TARGET_MODULE = REPO_ROOT / "scripts" / "compliance" / "update_compliance_metrics.py"
STATUS_INDEX = REPO_ROOT / "docs" / "status_index.json"
GOVERNANCE_DOC = REPO_ROOT / "docs" / "governance" / "COMPLIANCE.md"
CHANGELOG = REPO_ROOT / "CHANGELOG_COMPLIANCE.md"
ERROR_LOG = REPO_ROOT / "errors_for_chatgpt5.md"
README = REPO_ROOT / "README.md"
GH_WORKFLOWS_DIR = REPO_ROOT / ".github" / "workflows"

W_L, W_T, W_P, W_SE = 0.30, 0.40, 0.15, 0.15
THRESHOLD = 85.0

PLACEHOLDER_RX = re.compile(r"(TODO|FIXME|PLACEHOLDER|XXX)", re.IGNORECASE)
EXCLUDE_DIRS = {
    ".git",
    ".venv",
    ".mypy_cache",
    ".pytest_cache",
    "__pycache__",
    ".github/workflows",
}


def now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def safe_rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def append_error(step: str, desc: str, err: str, ctx: str) -> None:
    ERROR_LOG.parent.mkdir(parents=True, exist_ok=True)
    block = textwrap.dedent(
        f"""
        Question for ChatGPT-5:
        While performing [{step}:{desc}], encountered the following error:
        {err}
        Context: {ctx}
        What are the possible causes, and how can this be resolved while preserving intended functionality?
        """
    ).lstrip() + "\n"
    with open(ERROR_LOG, "a", encoding="utf-8") as fh:
        fh.write(block)


def append_changelog(line: str) -> None:
    CHANGELOG.parent.mkdir(parents=True, exist_ok=True)
    ts = now_iso()
    with open(CHANGELOG, "a", encoding="utf-8") as fh:
        fh.write(f"- {ts} — {line}\n")


def load_json(path: Path) -> Dict[str, Any]:
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except Exception as e:  # pragma: no cover
            append_error("0.0", "Load status_index.json", str(e), f"path={safe_rel(path)}")
    return {}


def save_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, sort_keys=True)
        fh.write("\n")
    tmp.replace(path)


def run_cmd(cmd: List[str], cwd: Path) -> Tuple[int, str, str]:
    if GH_WORKFLOWS_DIR.exists() and str(cwd).startswith(str(GH_WORKFLOWS_DIR)):
        return 1, "", "Refusing to execute inside .github/workflows"
    try:
        proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
        return proc.returncode, proc.stdout, proc.stderr
    except FileNotFoundError as e:
        return 127, "", str(e)
    except Exception as e:  # pragma: no cover
        return 1, "", str(e)


def which(exe: str) -> Optional[str]:
    for p in os.environ.get("PATH", "").split(os.pathsep):
        cand = Path(p) / exe
        if cand.exists() and os.access(cand, os.X_OK):
            return str(cand)
    return None


def discover_ingestion_files() -> List[Path]:
    patterns = ("ingestion", "metrics", "collect", "update_")
    res: List[Path] = []
    for root, dirs, files in os.walk(REPO_ROOT):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for fn in files:
            if not fn.endswith(".py"):
                continue
            p = Path(root) / fn
            rel = safe_rel(p)
            if rel.startswith(".github/workflows"):
                continue
            name = fn.lower()
            if any(k in name for k in patterns):
                res.append(p)
    return res


def try_import_module(path: Path) -> Optional[Any]:
    try:
        spec = importlib.util.spec_from_file_location(path.stem, str(path))
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)  # type: ignore
            return mod
    except Exception as e:
        append_error("1.1", "Import ingestion module", str(e), f"file={safe_rel(path)}")
    return None


def best_metric_callable(mod: Any) -> Optional[str]:
    for name in ["compute_compliance_metrics", "collect_metrics", "main"]:
        if hasattr(mod, name) and callable(getattr(mod, name)):
            return name
    for name in dir(mod):
        if name.startswith("_"):
            continue
        obj = getattr(mod, name)
        if callable(obj):
            return name
    return None


def normalize_metric_dict(d: Dict[str, Any]) -> Dict[str, float]:
    aliases = {
        "lint": ["lint", "lints", "ruff", "code_quality"],
        "tests": ["tests", "test", "pytest", "coverage_pct", "test_pass_pct"],
        "placeholders": ["placeholders", "todo", "todos", "fixme", "tech_debt"],
        "sessions": ["sessions", "session", "runtime_sessions", "stability"],
    }
    out = {"lint": None, "tests": None, "placeholders": None, "sessions": None}
    for k, v in d.items():
        lk = k.lower()
        for canon, keys in aliases.items():
            if lk in keys:
                try:
                    val = float(v)
                    out[canon] = max(0.0, min(100.0, val))
                except Exception:
                    pass
    return out


def ruff_score() -> Tuple[float, Dict[str, Any]]:
    exe = which("ruff")
    meta = {"tool": "ruff", "available": bool(exe), "violations": None}
    if not exe:
        append_changelog("Ruff not found; using neutral L=80")
        return 80.0, meta
    code, out, err = run_cmd([exe, "check", "--exit-zero", "--format=json", "."], REPO_ROOT)
    if code != 0:
        append_error("2.2", "Run ruff", f"exit={code} stderr={err[:4000]}", "cmd=ruff check --exit-zero --format=json .")
        return 70.0, meta
    try:
        data = json.loads(out or "[]")
        v = len(data)
        meta["violations"] = v
        return max(0.0, 100.0 - 1.0 * v), meta
    except Exception as e:
        append_error("2.2", "Parse ruff json", str(e), f"json_len={len(out)}")
        return 75.0, meta


def pytest_score() -> Tuple[float, Dict[str, Any]]:
    exe = which("pytest")
    meta = {"tool": "pytest", "available": bool(exe), "passed": None, "total": None}
    if not exe:
        append_changelog("Pytest not found; using conservative T=50")
        return 50.0, meta
    code, out, err = run_cmd([exe, "-q"], REPO_ROOT)
    text = out + "\n" + err
    m = re.search(r"(\d+)\s+passed.*?(\d+)\s+failed|(\d+)\s+passed", text, re.IGNORECASE | re.DOTALL)
    try:
        if m:
            if m.group(1) and m.group(2):
                passed = int(m.group(1))
                failed = int(m.group(2))
                total = passed + failed
            else:
                passed = int(m.group(3))
                col = re.search(r"collected\s+(\d+)\s+item", text)
                total = int(col.group(1)) if col else passed
            meta["passed"], meta["total"] = passed, total
            if total <= 0:
                return 50.0, meta
            return (passed / total) * 100.0, meta
        if code == 0:
            return 100.0, meta
        append_error("2.2", "Run pytest parse", f"exit={code}", text[:2000])
        return 50.0, meta
    except Exception as e:  # pragma: no cover
        append_error("2.2", "Run pytest exception", str(e), text[:2000])
        return 50.0, meta


def count_placeholders() -> Tuple[float, Dict[str, Any]]:
    hits = 0
    loc = 0
    for root, dirs, files in os.walk(REPO_ROOT):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for fn in files:
            p = Path(root) / fn
            if p.is_dir():
                continue
            if any(fn.lower().endswith(ext) for ext in (".png", ".jpg", ".jpeg", ".gif", ".pdf", ".ico", ".lock", ".min.js", ".db", ".sqlite", ".sqlite3")):
                continue
            try:
                with open(p, "r", encoding="utf-8", errors="ignore") as fh:
                    content = fh.read()
                loc += content.count("\n") + 1
                hits += len(PLACEHOLDER_RX.findall(content))
            except Exception:
                continue
    kloc = max(1.0, loc / 1000.0)
    h = hits / kloc
    meta = {"hits": hits, "loc": loc, "h_per_kloc": h}
    return max(0.0, 100.0 - 10.0 * h), meta


def session_score() -> Tuple[float, Dict[str, Any]]:
    candidates = []
    for pat in ("logs/session", "metrics", "docs/metrics", "docs/sessions"):
        d = REPO_ROOT / pat
        if d.exists():
            candidates.extend([p for p in d.rglob("*.json") if "workflow" not in str(p).lower()])
    if not candidates:
        append_changelog("No session metric source found; using neutral S_e=80")
        return 80.0, {"source": None}
    ok = total = 0
    for p in candidates:
        try:
            data = json.load(open(p, "r", encoding="utf-8"))
            items = data if isinstance(data, list) else data.get("events") or data.get("sessions") or []
            for it in items:
                total += 1
                if isinstance(it, dict) and not it.get("error"):
                    ok += 1
        except Exception as e:
            append_error("2.2", "Parse session json", str(e), f"file={safe_rel(p)}")
    if total == 0:
        return 80.0, {"source": [safe_rel(c) for c in candidates], "ratio": None}
    ratio = ok / total
    return max(0.0, min(100.0, ratio * 100.0)), {"source": [safe_rel(c) for c in candidates], "ratio": ratio}


def compute_composite(L: float, T: float, P: float, SE: float) -> float:
    return 100.0 * (W_L * (L / 100.0) + W_T * (T / 100.0) + W_P * (P / 100.0) + W_SE * (SE / 100.0))


def prune_unmappable(mappings: List[Tuple[Path, Optional[str]]]) -> List[Path]:
    pruned: List[Path] = []
    for p, cname in mappings:
        if cname is None:
            pruned.append(p)
            append_changelog(f"Pruned {safe_rel(p)} — no viable callable discovered.")
    return pruned


def update_status_index(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    data = load_json(STATUS_INDEX)
    data.setdefault("compliance", {})
    data["compliance"]["latest"] = snapshot
    v = int(data["compliance"].get("version", 0)) + 1
    data["compliance"]["version"] = v
    save_json(STATUS_INDEX, data)
    return data


def update_enforcement_flag(data: Dict[str, Any], blocked: bool, score: float) -> None:
    data.setdefault("compliance", {})
    data["compliance"]["enforcement"] = {
        "blocked": bool(blocked),
        "threshold": THRESHOLD,
        "score": round(score, 2),
        "timestamp": now_iso(),
    }
    save_json(STATUS_INDEX, data)


def ensure_governance_doc() -> None:
    GOVERNANCE_DOC.parent.mkdir(parents=True, exist_ok=True)
    section = textwrap.dedent(
        r"""
        # Compliance Model & Enforcement

        **Composite Score (𝓢)**
        \[
          \mathcal{S} = 100 \times \left(
            0.30 \cdot \frac{L}{100} +
            0.40 \cdot \frac{T}{100} +
            0.15 \cdot \frac{P}{100} +
            0.15 \cdot \frac{S_e}{100}
          \right)
        \]

        **Threshold:** \( \mathcal{S} \ge 85 \)

        **Signals:**
        - **L (Lint):** Ruff violations mapped to score
        - **T (Tests):** Pytest pass ratio
        - **P (Placeholders):** TODO/FIXME density per KLOC (lower is better)
        - **S_e (Sessions):** % session entries without error (if source present; neutral otherwise)

        **Enforcement Semantics:**
        - Block when score < 85 (exit code 2), record in `docs/status_index.json`.
        - Never modify or activate `.github/workflows/*`.
        """
    ).strip() + "\n"
    if GOVERNANCE_DOC.exists():
        txt = GOVERNANCE_DOC.read_text(encoding="utf-8")
        if "Compliance Model & Enforcement" not in txt:
            txt += "\n\n" + section
            GOVERNANCE_DOC.write_text(txt, encoding="utf-8")
    else:
        GOVERNANCE_DOC.write_text(section, encoding="utf-8")
    append_changelog(f"Governance doc ensured/updated at {safe_rel(GOVERNANCE_DOC)}")


def update_readme_references() -> None:
    if not README.exists():
        return
    txt = README.read_text(encoding="utf-8")
    updated = re.sub(r"docs/status\.json", "docs/status_index.json", txt)
    if "docs/governance/COMPLIANCE.md" not in updated:
        updated += "\n\nSee **Compliance Model**: `docs/governance/COMPLIANCE.md`.\n"
    if updated != txt:
        README.write_text(updated, encoding="utf-8")
        append_changelog("README references updated for compliance artifacts.")


def attempt_primary_metrics() -> Dict[str, Optional[float]]:
    out = {"lint": None, "tests": None, "placeholders": None, "sessions": None}
    if TARGET_MODULE.exists():
        mod = try_import_module(TARGET_MODULE)
        if mod:
            name = best_metric_callable(mod)
            if name:
                try:
                    res = getattr(mod, name)()
                    if isinstance(res, dict):
                        out.update(normalize_metric_dict(res))
                except Exception as e:
                    append_error("2.1", "Invoke primary metric function", str(e), f"module={safe_rel(TARGET_MODULE)}, func={name}")
    return out


def fill_secondary_metrics(current: Dict[str, Optional[float]]) -> Tuple[Dict[str, float], Dict[str, Any]]:
    meta: Dict[str, Any] = {"lint": {}, "tests": {}, "placeholders": {}, "sessions": {}}
    if current["lint"] is None:
        L, m = ruff_score()
        current["lint"] = L
        meta["lint"] = m
    if current["tests"] is None:
        T, m = pytest_score()
        current["tests"] = T
        meta["tests"] = m
    if current["placeholders"] is None:
        P, m = count_placeholders()
        current["placeholders"] = P
        meta["placeholders"] = m
    if current["sessions"] is None:
        Se, m = session_score()
        current["sessions"] = Se
        meta["sessions"] = m
    final = {k: float(max(0.0, min(100.0, v if v is not None else 0.0))) for k, v in current.items()}
    return final, meta


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Compliance Gate")
    parser.add_argument("--write-only", action="store_true", help="Compute and write without enforcement")
    args = parser.parse_args(argv)

    ingestion = discover_ingestion_files()
    mappings: List[Tuple[Path, Optional[str]]] = []
    for p in ingestion:
        mod = try_import_module(p)
        cname = best_metric_callable(mod) if mod else None
        mappings.append((p, cname))
    pruned = prune_unmappable(mappings)

    prim = attempt_primary_metrics()
    metrics, meta = fill_secondary_metrics(prim)
    L, T, P, SE = metrics["lint"], metrics["tests"], metrics["placeholders"], metrics["sessions"]
    S = compute_composite(L, T, P, SE)

    snapshot = {
        "timestamp": now_iso(),
        "metrics": {"lint": L, "tests": T, "placeholders": P, "sessions": SE, "composite": round(S, 2)},
        "meta": meta,
        "mappings": [{"file": safe_rel(p), "callable": cname} for p, cname in mappings],
        "pruned": [safe_rel(p) for p in pruned],
    }
    status = update_status_index(snapshot)

    ensure_governance_doc()
    update_readme_references()

    if args.write_only:
        append_changelog(f"Compliance computed (write-only). 𝓢={S:.2f}")
        print(f"[INFO] Composite score (write-only): {S:.2f}")
        update_enforcement_flag(status, blocked=False, score=S)
        return 0

    blocked = S < THRESHOLD
    update_enforcement_flag(status, blocked=blocked, score=S)
    if blocked:
        msg = f"ENFORCEMENT BLOCKED: composite score {S:.2f} < threshold {THRESHOLD:.1f}"
        print(msg, file=sys.stderr)
        append_changelog(f"{msg}. See docs/status_index.json and errors_for_chatgpt5.md if present.")
        return 2
    msg = f"ENFORCEMENT PASS: composite score {S:.2f} >= {THRESHOLD:.1f}"
    print(msg)
    append_changelog(f"{msg}. Artifacts updated.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # pragma: no cover
        append_error("X.X", "Top-level exception", str(e), "script=run_compliance_gate.py")
        print(f"[FATAL] Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)
