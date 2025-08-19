#!/usr/bin/env python3
# codex_workflow_report.py
# End-to-end workflow for: DB aggregation → CPS scoring → README sanitization → reports
# Never touches .github/, never writes to analytics.db/production.db.
# Requires: Python 3.9+, standard library only.

from __future__ import annotations

import argparse
import json
import logging
import re
import sqlite3
import sys
import textwrap
from datetime import datetime, timezone
from pathlib import Path


# ---------- Utilities ----------
def ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def open_sqlite_ro(db_path: Path) -> sqlite3.Connection:
    # Read-only via URI, per SQLite docs (mode=ro)
    # https://www.sqlite.org/uri.html ; Python sqlite3 uri=True
    uri = f"file:{db_path.as_posix()}?mode=ro"
    return sqlite3.connect(uri, uri=True, timeout=5.0)


def list_tables(conn: sqlite3.Connection) -> list[str]:
    try:
        cur = conn.execute("SELECT name FROM sqlite_schema WHERE type IN ('table','view')")
        return sorted(r[0] for r in cur.fetchall())
    except Exception:
        return []


def has_table(conn: sqlite3.Connection, name: str) -> bool:
    try:
        cur = conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=? LIMIT 1", (name,))
        return cur.fetchone() is not None
    except Exception:
        return False


def columns(conn: sqlite3.Connection, tbl: str) -> list[str]:
    try:
        return [r[1] for r in conn.execute(f"PRAGMA table_info({tbl})").fetchall()]
    except Exception:
        return []


def latest_row(
    conn: sqlite3.Connection,
    tbl: str,
    time_cols=("ts", "timestamp", "created_at", "inserted_at"),
) -> dict | None:
    cols = columns(conn, tbl)
    if not cols:
        return None
    # Find a reasonable time column
    for c in time_cols:
        if c in cols:
            sql = f"SELECT * FROM {tbl} ORDER BY {c} DESC LIMIT 1"
            row = conn.execute(sql).fetchone()
            if row:
                return dict(zip(cols, row))
    # fallback: first row
    row = conn.execute(f"SELECT * FROM {tbl} LIMIT 1").fetchone()
    return dict(zip(cols, row)) if row else None


def write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def sanitize_readme(md: str) -> str:
    # Remove markdown links but keep text: [txt](url) -> txt
    md = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", md)
    # Remove CI/GitHub Actions mentions heuristically
    md = re.sub(r"(?i)^.*actions.*$", "", md, flags=re.MULTILINE)
    return md.strip()


def norm_weights(weights: dict[str, float], available: set[str]) -> dict[str, float]:
    tot = sum(weights[k] for k in available if k in weights)
    if tot <= 0:  # Fallback equal weights
        return {k: 1 / len(available) for k in available}
    return {k: weights[k] / tot for k in available}


def safe_int(d: dict, *keys, default=None):
    for k in keys:
        if k in d and d[k] is not None:
            try:
                return int(d[k])
            except Exception:
                try:
                    return int(float(d[k]))
                except Exception:
                    pass
    return default


def safe_float(d: dict, *keys, default=None):
    for k in keys:
        if k in d and d[k] is not None:
            try:
                return float(d[k])
            except Exception:
                pass
    return default


# ---------- Error capture ----------
class ErrorSink:
    def __init__(self):
        self.items = []

    def add(self, step_num: str, step_desc: str, exc: Exception, context: str):
        self.items.append({
            "step": f"{step_num}:{step_desc}",
            "error": repr(exc),
            "context": context[:1000],
        })

    def render_md(self) -> str:
        out = ["# ERRORS_FOR_GPT5\n"]
        for it in self.items:
            out.append(
                textwrap.dedent(
                    f"""
                **Question for ChatGPT-5:**
                While performing **[{it['step']}]**, encountered the following error:
                **{it['error']}**
                **Context:** {it['context']}
                What are the possible causes, and how can this be resolved while preserving intended functionality?
                """
                ).strip()
            )
        return (
            "\n\n---\n\n".join(out) if self.items else "# ERRORS_FOR_GPT5\n\n_No errors captured._\n"
        )


# ---------- Aggregators ----------
def agg_lint(conn_an: sqlite3.Connection, errors: ErrorSink, strict: bool) -> tuple[float, dict]:
    # Try direct score first
    try:
        if has_table(conn_an, "code_quality_metrics"):
            cols = columns(conn_an, "code_quality_metrics")
            score_cols = [c for c in cols if "lint" in c and "score" in c]
            if score_cols:
                row = conn_an.execute(
                    f"SELECT {score_cols[0]} FROM code_quality_metrics ORDER BY rowid DESC LIMIT 1"
                ).fetchone()
                if row and row[0] is not None:
                    return float(row[0]), {"source": "code_quality_metrics." + score_cols[0]}
    except Exception as e:
        errors.add(
            "3.1",
            "Read code_quality_metrics for lint score",
            e,
            "Attempted direct lint score",
        )

    # Else compute from issues
    issues = None
    try:
        if has_table(conn_an, "ruff_issue_log"):
            issues = conn_an.execute("SELECT COUNT(*) FROM ruff_issue_log").fetchone()[0]
            src = "ruff_issue_log"
        elif has_table(conn_an, "flake8_violations"):
            issues = conn_an.execute("SELECT COUNT(*) FROM flake8_violations").fetchone()[0]
            src = "flake8_violations"
        else:
            if strict:
                raise RuntimeError("No lint tables found")
            return 0.0, {"source": "none", "note": "no lint table"}
        # Heuristic normalization: fewer issues → higher score (cap at 0)
        L = max(0.0, 100.0 - 0.5 * float(issues))
        return L, {"source": src, "issues": int(issues), "method": "100 - 0.5*issues"}
    except Exception as e:
        errors.add("3.1", "Compute L from lint logs", e, "ruff_issue_log/flake8_violations")
        if strict:
            raise
        return 0.0, {"source": "error"}


def agg_placeholders(
    conn_an: sqlite3.Connection, errors: ErrorSink, strict: bool
) -> tuple[float, dict]:
    try:
        tbls = list_tables(conn_an)
        cand = None
        for t in (
            "placeholder_audit_snapshots",
            "code_audit_log",
            "todo_fixme_tracking",
        ):
            if t in tbls:
                cand = t
                break
        if not cand:
            if strict:
                raise RuntimeError("No placeholder tables found")
            return 0.0, {"source": "none", "note": "no placeholder table"}

        row = latest_row(conn_an, cand) or {}
        # Try several column name conventions
        total = safe_int(
            row,
            "total",
            "total_placeholders",
            "placeholders_total",
            default=None,
        )
        resolved = safe_int(
            row,
            "resolved",
            "resolved_placeholders",
            "placeholders_resolved",
            default=None,
        )
        pending = safe_int(
            row,
            "pending",
            "open",
            "open_count",
            default=None,
        )

        if total is None and resolved is not None and pending is not None:
            total = resolved + pending
        if total is None and pending is not None:
            total = pending
        if total is None:
            # Last resort: count rows if row-based
            total = 1
        if resolved is None and total is not None and pending is not None:
            resolved = max(0, total - pending)
        if resolved is None:
            resolved = 0

        P = 0.0 if total <= 0 else (resolved / total) * 100.0
        return P, {"source": cand, "total": total, "resolved": resolved}
    except Exception as e:
        errors.add("3.1", "Compute P from placeholder snapshot", e, "schema inference")
        if strict:
            raise
        return 0.0, {"source": "error"}


def agg_sessions(
    conn_pr: sqlite3.Connection, errors: ErrorSink, strict: bool
) -> tuple[float, dict]:
    try:
        tbls = list_tables(conn_pr)
        t = "unified_wrapup_sessions" if "unified_wrapup_sessions" in tbls else None
        if not t:
            if strict:
                raise RuntimeError("No unified_wrapup_sessions table")
            return 0.0, {"source": "none", "note": "no session table"}

        cols = columns(conn_pr, t)
        # Count total
        total = conn_pr.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        # Attempt robust success detection
        success = 0
        if any(c.lower() == "status" for c in cols):
            success = conn_pr.execute(
                f"SELECT COUNT(*) FROM {t} WHERE lower(status) IN ('success','completed','ok')"
            ).fetchone()[0]
        elif any(c.lower() == "ended" for c in cols):
            success = conn_pr.execute(
                f"SELECT COUNT(*) FROM {t} WHERE ended=1"
            ).fetchone()[0]
        elif any(c.lower().endswith("_end") or c.lower().endswith("end_ts") for c in cols):
            # any ended timestamp present?
            success = conn_pr.execute(
                f"SELECT COUNT(*) FROM {t} WHERE COALESCE(end_ts, end_time, finished_at) IS NOT NULL"
            ).fetchone()[0]
        S = 0.0 if total == 0 else (success / total) * 100.0
        return S, {"source": t, "total": int(total), "success": int(success)}
    except Exception as e:
        errors.add("3.1", "Compute S from sessions", e, "unified_wrapup_sessions")
        if strict:
            raise
        return 0.0, {"source": "error"}


def agg_tests(conn_an: sqlite3.Connection, errors: ErrorSink) -> tuple[float | None, dict]:
    try:
        if not has_table(conn_an, "test_run_stats"):
            return None, {"source": "none"}
        row = conn_an.execute(
            "SELECT SUM(passed), SUM(total) FROM test_run_stats"
        ).fetchone()
        passed, total = row or (0, 0)
        if not total:
            return 0.0, {"source": "test_run_stats", "total": 0}
        T = (float(passed) / float(total)) * 100.0
        return T, {
            "source": "test_run_stats",
            "passed": int(passed),
            "total": int(total),
        }
    except Exception as e:
        errors.add("3.1", "Compute T from test_run_stats", e, "aggregation")
        return None, {"source": "error"}


# ---------- Recommendations ----------
def recommendations(L: float, P: float, S: float, T: float | None) -> list[str]:
    rec = []
    if L < 90:
        rec.append("Address top files with clustered lint issues; run ruff autofix where safe.")
    if P < 95:
        rec.append(
            "Resolve remaining TODO/FIXME; re-run placeholder audit to refresh snapshot."
        )
    if S < 98:
        rec.append(
            "Stabilize session wrap-up flow; ensure start/end are always recorded."
        )
    if T is not None and T < 95:
        rec.append(
            "Increase deterministic tests; gate merges on pass-rate regression."
        )
    return rec or ["All signals healthy; monitor trends via dashboard."]


# ---------- Main ----------
def main():
    ap = argparse.ArgumentParser(
        description="Aggregate metrics from production.db & analytics.db; generate reports."
    )
    ap.add_argument("--repo-root", default=".", help="Path to repository root")
    ap.add_argument(
        "--output-dir",
        default=None,
        help="Directory for outputs (default codex_out/<timestamp>)",
    )
    ap.add_argument(
        "--strict", action="store_true", help="Fail if expected tables are missing"
    )
    ap.add_argument(
        "--test-mode",
        action="store_true",
        help="Relaxed behavior; continue on partial data",
    )
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(message)s",
    )
    errors = ErrorSink()

    repo = Path(args.repo_root).resolve()
    outdir = (
        Path(args.output_dir) if args.output_dir else repo / "codex_out" / ts()
    )
    ensure_dir(outdir)

    db_prod = repo / "databases" / "production.db"
    db_an = repo / "databases" / "analytics.db"

    # README sanitization
    readme_in = repo / "README.md"
    readme_out = outdir / "README_sanitized.md"
    if readme_in.exists():
        try:
            write_text(readme_out, sanitize_readme(readme_in.read_text(encoding="utf-8")))
        except Exception as e:
            errors.add(
                "3.3", "Sanitize README.md", e, f"path={readme_in}"
            )

    # Connect read-only
    try:
        conn_an = open_sqlite_ro(db_an)
    except Exception as e:
        errors.add(
            "1.2", "Open analytics.db read-only", e, f"path={db_an}"
        )
        if args.strict:
            raise
        conn_an = None
    try:
        conn_pr = open_sqlite_ro(db_prod)
    except Exception as e:
        errors.add(
            "1.2", "Open production.db read-only", e, f"path={db_prod}"
        )
        if args.strict:
            raise
        conn_pr = None

    # Aggregate
    L, Lmeta = (0.0, {"source": "none"})
    P, Pmeta = (0.0, {"source": "none"})
    S, Smeta = (0.0, {"source": "none"})
    T, Tmeta = (None, {"source": "none"})

    if conn_an:
        L, Lmeta = agg_lint(conn_an, errors, args.strict)
        P, Pmeta = agg_placeholders(conn_an, errors, args.strict)
        T, Tmeta = agg_tests(conn_an, errors)
    if conn_pr:
        S, Smeta = agg_sessions(conn_pr, errors, args.strict)

    # Weights: prefer documented default when all available (L,T,P,S)
    base_weights = {"L": 0.3, "T": 0.4, "P": 0.2, "S": 0.1}
    available = {"L", "P", "S"} | ({"T"} if T is not None else set())
    W = norm_weights(base_weights, available)

    CPS = W["L"] * L + W["P"] * P + W["S"] * S + (W["T"] * T if T is not None else 0.0)

    # Recommendations
    recs = recommendations(L, P, S, T)

    # Reports
    summary = {
        "timestamp_utc": ts(),
        "repo_root": str(repo),
        "sources": {
            "lint": Lmeta,
            "placeholders": Pmeta,
            "sessions": Smeta,
            "tests": Tmeta,
        },
        "metrics": {
            "L_lint_score": round(L, 2),
            "P_placeholder_resolution_pct": round(P, 2),
            "S_session_success_pct": round(S, 2),
            **({"T_test_pass_pct": round(T, 2)} if T is not None else {}),
        },
        "weights_used": W,
        "coverage_performance_score": round(CPS, 2),
        "recommendations": recs,
        "notes": [
            "DBs opened in read-only URI mode",
            "If primary tables absent, heuristics used and recorded in changelog",
        ],
    }

    # Write JSON + Markdown
    json_path = outdir / f"report_{ts()}.json"
    write_text(json_path, json.dumps(summary, indent=2))

    md = [
        "# Coverage Performance Report",
        f"- Timestamp (UTC): `{summary['timestamp_utc']}`",
        f"- Repo: `{summary['repo_root']}`",
        "\n## Metrics",
        f"- Lint (L): **{summary['metrics']['L_lint_score']}**",
        f"- Placeholders (P): **{summary['metrics']['P_placeholder_resolution_pct']}%**",
        f"- Sessions (S): **{summary['metrics']['S_session_success_pct']}%**",
    ]
    if "T_test_pass_pct" in summary["metrics"]:
        md.append(f"- Tests (T): **{summary['metrics']['T_test_pass_pct']}%**")
    md += [
        "\n## Coverage Performance Score (CPS)",
        f"**{summary['coverage_performance_score']}**  (weights used: {W})",
        "\n## Recommendations",
        *[f"- {r}" for r in recs],
        "\n## Sources",
        f"- L: {Lmeta}",
        f"- P: {Pmeta}",
        f"- S: {Smeta}",
        f"- T: {Tmeta}",
    ]
    write_text(outdir / f"report_{ts()}.md", "\n".join(md))

    # Changelog
    changelog = outdir / "CHANGELOG_EXECUTION.md"
    write_text(
        changelog,
        textwrap.dedent(
            f"""
    # Execution Changelog
    - Time (UTC): {summary['timestamp_utc']}
    - Read-only DB URIs used for analytics & production.
    - Tables present: analytics={list_tables(conn_an) if conn_an else []}; production={list_tables(conn_pr) if conn_pr else []}
    - L mapping: {Lmeta}
    - P mapping: {Pmeta}
    - S mapping: {Smeta}
    - T mapping: {Tmeta}
    - Heuristics: {'NONE' if not errors.items else 'See ERRORS_FOR_GPT5.md'}.
    """
        ).strip(),
    )

    # Error file
    write_text(outdir / "ERRORS_FOR_GPT5.md", errors.render_md())

    # Close DBs
    for c in (conn_an, conn_pr):
        try:
            if c:
                c.close()
        except Exception:
            pass

    # Console summary
    print(
        json.dumps(
            {
                "CPS": summary["coverage_performance_score"],
                "L": L,
                "P": P,
                "S": S,
                **({"T": T} if T is not None else {}),
                "weights": W,
                "output_dir": str(outdir),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # Last-chance error capture to STDOUT for CI visibility (not writing to DB)
        sys.stderr.write(f"FATAL ERROR: {e}\n")
        sys.exit(2)

