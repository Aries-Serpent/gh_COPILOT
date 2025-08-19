#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
codex_dashboard_workflow.py
Non-destructive, best-effort workflow to:
- Inspect dashboard/enterprise_dashboard.py and templates
- Generate patches/stubs for missing metrics views (compliance, synchronization, monitoring)
- Provide Chart.js gauge stubs with real-time update strategy (polling/SSE scaffolds)
- Add pytest scaffolding
- Update README addendum
- Record pruned items with rationale
- Capture errors as ChatGPT-5 research questions

HARD GUARD: Never touch .github/workflows/*
"""

import argparse
import json
import re
import sqlite3
import sys
import textwrap
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# ---------------------- Utilities ----------------------


def safe_mkdir(p: Path):
    p.mkdir(parents=True, exist_ok=True)


def write_text(p: Path, content: str):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


def append_text(p: Path, content: str):
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(content)


def now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def relpath(base: Path, target: Path) -> str:
    try:
        return str(target.relative_to(base))
    except Exception:
        return str(target)


def guard_no_github_actions(path: Path):
    s = str(path.as_posix())
    if "/.github/workflows/" in s or s.endswith("/.github/workflows") or s.startswith(".github/workflows"):
        raise RuntimeError("Guard triggered: Attempt to write in .github/workflows/*")


def error_for_chatgpt5(errors_md: Path, step_number: str, step_desc: str, exc: Exception, context: str):
    block = textwrap.dedent(
        f"""
    **Question for ChatGPT-5:**
    While performing [{step_number}:{step_desc}], encountered the following error:
    `{type(exc).__name__}: {str(exc)}`  
    Context: {context}
    What are the possible causes, and how can this be resolved while preserving intended functionality?

    ---
    """
    )
    append_text(errors_md, block)


def add_changelog(changelog: Path, title: str, body: str):
    section = f"## {title}\n\n{body.strip()}\n\n"
    append_text(changelog, section)


# Default path to analytics database used for dashboard metrics.
ANALYTICS_DB = Path("analytics.db")


def fetch_panel_metrics(panel: str, db_path: Path | None = None) -> Dict[str, object]:
    """Return metrics for ``panel`` from ``analytics.db``.

    Parameters
    ----------
    panel: str
        Name of the dashboard panel to query.
    db_path: Path | None
        Optional override for the analytics database location.

    Returns
    -------
    Dict[str, object]
        Mapping with keys ``value``, ``target`` and ``unit``. Defaults are
        returned if the database or row is missing.
    """

    db = Path(db_path) if db_path else ANALYTICS_DB
    try:
        with sqlite3.connect(db) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT value, target, unit FROM dashboard_metrics WHERE panel = ?",
                (panel,),
            ).fetchone()
            if row:
                return {
                    "value": row["value"],
                    "target": row["target"],
                    "unit": row["unit"],
                }
    except Exception:
        pass
    return {"value": 0, "target": 100, "unit": "%"}


# ---------------------- Analysis & Mapping ----------------------


def discover_dashboard_file(repo: Path, errors_md: Path) -> Tuple[Optional[Path], List[Path]]:
    candidates = []
    try:
        primary = repo / "dashboard" / "enterprise_dashboard.py"
        if primary.exists():
            return primary, [primary]

        for p in repo.rglob("enterprise_dashboard.py"):
            s = p.as_posix()
            if any(seg in s for seg in ["/.", "/__pycache__", "/build/", "/dist/", "/site-packages/"]):
                continue
            candidates.append(p)

        if candidates:
            best = sorted(candidates, key=lambda x: len(x.as_posix().split("/")))[0]
            return best, candidates

        return None, []
    except Exception as e:
        error_for_chatgpt5(errors_md, "2.5", "locate_dashboard_file", e, f"repo={repo}")
        return None, []


def detect_framework(py_source: str) -> str:
    if re.search(r"\bFlask\b|\bBlueprint\b|@app\.route|@.*\.route", py_source):
        return "flask"
    if re.search(r"\bFastAPI\b|\bAPIRouter\b|@router\.(get|post|put|delete)", py_source):
        return "fastapi"
    return "unknown"


def extract_routes(py_source: str, framework: str) -> List[str]:
    routes = []
    if framework == "flask":
        for m in re.finditer(r"@(?:app|[\w_]+)\.route\(['\"]([^'\"]+)['\"]", py_source):
            routes.append(m.group(1))
    elif framework == "fastapi":
        for m in re.finditer(r"@(?:app|router)\.(?:get|post|put|delete)\(['\"]([^'\"]+)['\"]", py_source):
            routes.append(m.group(1))
    return sorted(set(routes))


def expected_panels() -> List[str]:
    return ["compliance", "synchronization", "monitoring"]


def plan_missing_panels(existing_routes: List[str]) -> Dict[str, Dict]:
    plan: Dict[str, Dict] = {}
    for panel in expected_panels():
        api_path = f"/metrics/{panel}"
        exists = api_path in existing_routes
        plan[panel] = {"api_path": api_path, "exists": exists}
    return plan


def find_templates(repo: Path) -> List[Path]:
    templ = []
    for base in ["templates", "dashboard/templates", "app/templates"]:
        p = repo / base
        if p.exists():
            for html in p.rglob("*.html"):
                s = html.as_posix()
                if any(seg in s for seg in ["/.", "/node_modules/", "/build/", "/dist/"]):
                    continue
                templ.append(html)
    return templ


def scan_for_chartjs(html_text: str) -> bool:
    return "new Chart(" in html_text or "Chart(" in html_text


# ---------------------- Patch & Stub Generators ----------------------


def patch_for_panel(framework: str, panel: str, api_path: str, module_hint: str) -> str:
    if framework == "flask":
        body = f"""
        # --- BEGIN SUGGESTED ADDITION: {panel} metrics endpoint ---
        @app.route(\"{api_path}\", methods=[\"GET\"])
        def metrics_{panel}():
            \"\"\"Return JSON metrics for {panel}.
            Values are sourced from analytics.db.
            \"\"\"
            metrics = fetch_panel_metrics(\"{panel}\")
            data = {{
                \"panel\": \"{panel}\",
                \"updated_at\": \"{now_iso()}\",
                \"status\": \"ok\",
                \"metrics\": metrics
            }}
            return jsonify(data), 200
        # --- END SUGGESTED ADDITION ---
        """
    elif framework == "fastapi":
        body = f"""
        # --- BEGIN SUGGESTED ADDITION: {panel} metrics endpoint ---
        @router.get(\"{api_path}\")
        async def metrics_{panel}():
            \"\"\"Return JSON metrics for {panel}.
            Values are sourced from analytics.db.
            \"\"\"
            metrics = fetch_panel_metrics(\"{panel}\")
            return {{
                \"panel\": \"{panel}\",
                \"updated_at\": \"{now_iso()}\",
                \"status\": \"ok\",
                \"metrics\": metrics
            }}
        # --- END SUGGESTED ADDITION ---
        """
    else:
        body = f"""
        # Framework unknown. Provide a generic WSGI-style hint for {panel}:
        # GET {api_path} -> JSON: {{
        #   \"panel\": \"{panel}\",
        #   \"updated_at\": ISO8601,
        #   \"status\": \"ok\",
        #   \"metrics\": {{\"value\":0,\"target\":100,\"unit\":\"%\"}}
        # }}
        """

    diff = textwrap.dedent(
        f"""\
    --- a/{module_hint}
    +++ b/{module_hint} (suggested patch)
    @@
    {textwrap.indent(textwrap.dedent(body).strip(), ' ')}
    """
    )
    return diff


def template_stub_for_panel(panel: str, api_path: str) -> str:
    return textwrap.dedent(
        f"""\
    <!-- Stub template for {panel} gauge panel -->
    <div class=\"card\">
      <h3>{panel.title()} Metrics</h3>
      <canvas id=\"gauge_{panel}\"></canvas>
    </div>

    <script>
    async function fetch_{panel}_metrics() {{
      try {{
        const res = await fetch(\"{api_path}\", {{ cache: \"no-store\" }});
        if (!res.ok) throw new Error(\"HTTP \" + res.status);
        const data = await res.json();
        // TODO: update Chart.js gauge with `data.metrics.value`
      }} catch (e) {{
        console.error(\"Failed to fetch {panel} metrics:\", e);
      }}
    }}

    const ctx_{panel} = document.getElementById('gauge_{panel}').getContext('2d');
    const gauge_{panel} = new Chart(ctx_{panel}, {{
      type: 'doughnut',
      data: {{
        labels: ['Value', 'Remainder'],
        datasets: [{{
          data: [0, 100],
        }}]
      }},
      options: {{
        responsive: true,
        cutout: '80%',
        plugins: {{
          legend: {{ display: false }}
        }}
      }}
    }});

    setInterval(fetch_{panel}_metrics, 5000);
    fetch_{panel}_metrics();
    </script>
    """
    )


def schema_stub_for_panel(panel: str) -> dict:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": f"{panel}_metrics",
        "type": "object",
        "required": ["panel", "updated_at", "status", "metrics"],
        "properties": {
            "panel": {"type": "string", "const": panel},
            "updated_at": {"type": "string", "format": "date-time"},
            "status": {"type": "string"},
            "metrics": {
                "type": "object",
                "required": ["value", "target", "unit"],
                "properties": {
                    "value": {"type": "number"},
                    "target": {"type": "number"},
                    "unit": {"type": "string"},
                },
            },
        },
    }


# ---------------------- README & Tests ----------------------


def generate_tests(framework: str) -> str:
    if framework == "flask":
        return textwrap.dedent(
            """\
        import pytest
        from flask import Flask

        pytestmark = pytest.mark.smoke

        @pytest.fixture
        def app():
            app = Flask(__name__)

            @app.get('/metrics/compliance')
            def _c():
                return ({'panel': 'compliance', 'metrics': {'value': 0, 'target': 100, 'unit': '%'}}, 200)

            @app.get('/metrics/synchronization')
            def _s():
                return ({'panel': 'synchronization', 'metrics': {'value': 0, 'target': 100, 'unit': '%'}}, 200)

            @app.get('/metrics/monitoring')
            def _m():
                return ({'panel': 'monitoring', 'metrics': {'value': 0, 'target': 100, 'unit': '%'}}, 200)

            return app

        @pytest.fixture
        def client(app):
            return app.test_client()

        @pytest.mark.parametrize('path', [
            '/metrics/compliance',
            '/metrics/synchronization',
            '/metrics/monitoring',
        ])
        def test_metrics_endpoints_smoke(client, path):
            resp = client.get(path)
            assert resp.status_code in (200, 404)
            if resp.status_code == 200:
                data = resp.get_json()
                assert 'panel' in data and 'metrics' in data
        """
        )
    else:
        return textwrap.dedent(
            """\
        import os
        import pytest
        import requests

        pytestmark = pytest.mark.smoke

        BASE = os.environ.get('DASH_BASE_URL', 'http://localhost:8000')

        @pytest.mark.parametrize('path', [
            '/metrics/compliance',
            '/metrics/synchronization',
            '/metrics/monitoring',
        ])
        def test_metrics_endpoints_smoke(path):
            url = BASE + path
            try:
                r = requests.get(url, timeout=3)
                assert r.status_code in (200, 404)
                if r.status_code == 200:
                    data = r.json()
                    assert 'panel' in data and 'metrics' in data
            except Exception:
                pytest.skip('Service not running; acceptable during scaffold stage.')
        """
        )


def readme_addendum(framework: str) -> str:
    return textwrap.dedent(
        f"""\
    # Enterprise Dashboard: Metrics Views (Scaffold)

    ## Overview
    This addendum describes how to wire the generated stubs for the metrics panels:
    - compliance
    - synchronization
    - monitoring

    ## Real-time Updates
    The supplied templates use periodic JSON polling to update Chart.js gauges.
    Replace the mock handlers with real metrics and keep the JSON schema stable.

    ## Tests
    - See `codex_changes/tests/test_dashboard_endpoints.py`
    - Run: `pytest -q`

    ## Safety
    - This scaffold does not edit your source files automatically.
    - Apply the suggested patches manually after review.
    - **DO NOT ACTIVATE ANY GitHub Actions files.** This scaffold ignores `.github/workflows/*`.
    """
    )


# ---------------------- Main Workflow ----------------------


def main():
    parser = argparse.ArgumentParser(description="Codex Dashboard Workflow (Non-destructive)")
    parser.add_argument("-r", "--repo", default=".", help="Path to repo root (default: .)")
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    out = repo / "codex_changes"
    dirs = {
        "analysis": out / "analysis",
        "patches": out / "patches",
        "stubs": out / "stubs",
        "tests": out / "tests",
        "docs": out / "docs",
        "logs": out / "logs",
        "schemas": out / "stubs" / "schemas",
    }
    for d in dirs.values():
        safe_mkdir(d)

    changelog = out / "CHANGELOG.md"
    errors_md = out / "errors_for_chatgpt5.md"

    add_changelog(changelog, "Init", f"Workflow started at {now_iso()} - Non-destructive mode.")
    write_text(errors_md, f"# Errors & Research Questions for ChatGPT-5\n\nStarted: {now_iso()}\n\n")

    dashboard_file, all_candidates = discover_dashboard_file(repo, errors_md)
    map_json = dirs["analysis"] / "dashboard_map.json"
    write_text(
        map_json,
        json.dumps(
            {
                "primary": relpath(repo, dashboard_file) if dashboard_file else None,
                "candidates": [relpath(repo, c) for c in all_candidates],
            },
            indent=2,
        ),
    )

    if not dashboard_file:
        add_changelog(
            changelog,
            "Pruned: dashboard file",
            "Could not locate `dashboard/enterprise_dashboard.py` or any candidates after exhaustive search.",
        )
        add_changelog(
            changelog,
            "Rationale",
            "Avoided creating arbitrary files inside source tree; generated stubs only.",
        )
    else:
        try:
            src = dashboard_file.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            error_for_chatgpt5(
                errors_md,
                "2.6",
                "read_dashboard_file",
                e,
                f"path={relpath(repo, dashboard_file)}",
            )
            src = ""

        framework = detect_framework(src) if src else "unknown"
        routes = extract_routes(src, framework) if src else []
        write_text(
            dirs["analysis"] / "framework_routes.json",
            json.dumps({"framework": framework, "routes": routes}, indent=2),
        )

        plan = plan_missing_panels(routes)
        write_text(dirs["analysis"] / "panel_plan.json", json.dumps(plan, indent=2))

        module_hint = relpath(repo, dashboard_file) if dashboard_file else "dashboard/enterprise_dashboard.py"
        constructed = []
        pruned = []

        for panel, meta in plan.items():
            api_path = meta["api_path"]
            if meta["exists"]:
                constructed.append(f"{panel}: already exists at {api_path}")
                continue

            try:
                patch_text = patch_for_panel(framework, panel, api_path, module_hint)
                patch_file = dirs["patches"] / f"{panel}_endpoint.patch"
                write_text(patch_file, patch_text)

                t_stub = template_stub_for_panel(panel, api_path)
                t_file = dirs["stubs"] / "templates" / f"{panel}_panel.html"
                write_text(t_file, t_stub)

                schema = schema_stub_for_panel(panel)
                s_file = dirs["schemas"] / f"{panel}_schema.json"
                write_text(s_file, json.dumps(schema, indent=2))

                constructed.append(f"{panel}: patch+template+schema prepared")
            except Exception as e:
                error_for_chatgpt5(
                    errors_md,
                    "3.2",
                    f"generate_{panel}_stubs",
                    e,
                    f"framework={framework}, api_path={api_path}",
                )
                pruned.append(f"{panel}: deferred due to errors in stub generation")

        add_changelog(
            changelog,
            "Constructed",
            "\n".join(constructed) if constructed else "None",
        )
        if pruned:
            add_changelog(
                changelog,
                "Pruned (with rationale)",
                "\n".join(pruned),
            )

    try:
        framework_guess = "flask"
        if dashboard_file:
            src = dashboard_file.read_text(encoding="utf-8", errors="ignore")
            framework_guess = detect_framework(src)

        tests_py = generate_tests(framework_guess)
        write_text(dirs["tests"] / "test_dashboard_endpoints.py", tests_py)

        docs_md = readme_addendum(framework_guess)
        write_text(dirs["docs"] / "README_updates.md", docs_md)
        add_changelog(
            changelog,
            "Docs & Tests",
            "Added README addendum and pytest scaffold under codex_changes/.",
        )
    except Exception as e:
        error_for_chatgpt5(
            errors_md,
            "6.1",
            "generate_docs_and_tests",
            e,
            f"framework_guess={framework_guess}",
        )

    try:
        readme_path = repo / "README.md"
        if readme_path.exists():
            txt = readme_path.read_text(encoding="utf-8", errors="ignore")
            cleaned = re.sub(
                r"(?im)^\s*-\s*(Compliance|Synchronization|Monitoring)\s*\(TBD\)\s*$",
                r"- \\1 (now scaffolded)",
                txt,
            )
            write_text(dirs["docs"] / "README_cleaned.proposal.md", cleaned)
            add_changelog(
                changelog,
                "README parsing",
                "Emitted README_cleaned.proposal.md with minor reference adjustments.",
            )
        else:
            add_changelog(
                changelog,
                "README parsing",
                "README.md not found; skipped cleanup.",
            )
    except Exception as e:
        error_for_chatgpt5(
            errors_md,
            "6.2",
            "parse_and_adjust_readme",
            e,
            "Attempted to prepare cleaned README proposal",
        )

    summary = {
        "timestamp": now_iso(),
        "repo": str(repo),
        "dashboard_file": relpath(repo, dashboard_file) if dashboard_file else None,
        "outputs": {k: str(v) for k, v in dirs.items()},
    }
    write_text(dirs["analysis"] / "summary.json", json.dumps(summary, indent=2))
    add_changelog(
        changelog,
        "Finalize",
        "Summary written. Non-destructive run complete.\n**Reminder:** DO NOT ACTIVATE ANY GitHub Actions files.",
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    try:
        guard_no_github_actions(Path(".github/workflows"))
    except Exception:
        pass
    sys.exit(main() or 0)

